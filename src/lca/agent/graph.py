from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

from langgraph.graph import END, StateGraph

from lca.agent.reasoning import enforce_surcharge_budget, extract_brief, propose_configuration
from lca.agent.state import DEFAULT_REGION, ConciergeState, initial_state
from lca.config import get_settings
from lca.data import get_repository
from lca.llm import stream_sales_summary
from lca.rag import ChromaKnowledgeRetriever, LocalKnowledgeRetriever
from lca.tools import (
    check_availability,
    configure_vehicle,
    estimate_price,
    recommend_complementary_options,
)


class LuxuryConciergeAgent:
    def __init__(self, retriever: LocalKnowledgeRetriever | None = None):
        self.retriever = retriever or _default_retriever()
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(ConciergeState)
        graph.add_node("understand_intent", self._understand_intent)
        graph.add_node("retrieve_context", self._retrieve_context)
        graph.add_node("propose_configuration", self._propose_configuration)
        graph.add_node("call_tools", self._call_tools)
        graph.add_node("evaluate_and_respond", self._evaluate_and_respond)

        graph.set_entry_point("understand_intent")
        graph.add_edge("understand_intent", "retrieve_context")
        graph.add_edge("retrieve_context", "propose_configuration")
        graph.add_edge("propose_configuration", "call_tools")
        # The graph is not a straight line: an over-budget commission goes back
        # to be reconfigured against the client's stated ceiling, once. This is
        # the loop that makes a graph the right shape for the problem.
        graph.add_conditional_edges(
            "call_tools",
            self._route_after_pricing,
            {"revise": "propose_configuration", "respond": "evaluate_and_respond"},
        )
        graph.add_edge("evaluate_and_respond", END)
        return graph.compile()

    # Counts proposals, not revisions: the first pass through the graph makes
    # proposal 1, so allowing 2 permits exactly one re-configuration.
    MAX_PROPOSALS = 2

    def _route_after_pricing(self, state: ConciergeState) -> str:
        """Re-configure when the estimate breaks a stated budget."""
        over_budget = state["price"].get("budget_fit") == "over_budget"
        if over_budget and state["revisions"] < self.MAX_PROPOSALS:
            return "revise"
        return "respond"

    def invoke(self, user_input: str, memory: list[dict[str, str]] | None = None) -> dict[str, Any]:
        """Run the full deterministic pipeline and return the result immediately.

        This never blocks on a local/remote LLM call: `response` is always the
        fast, template-built summary. Call `stream_response` afterward if you
        want a progressively-generated, model-refined version of the text.
        """
        return dict(self.graph.invoke(initial_state(user_input, memory)))

    def stream_response(self, result: dict[str, Any]) -> Iterator[str]:
        """Stream a model-refined sales summary for an already-computed result.

        Falls back to yielding the existing deterministic `response` in one
        piece when the configured provider isn't a local/streaming model.
        """
        yield from stream_sales_summary(result, result["response"])

    def _understand_intent(self, state: ConciergeState) -> ConciergeState:
        user_input = state["user_input"]
        # Only the client's own turns describe the client. Folding assistant turns
        # in lets our own boilerplate ("...region, usage, cabin mood...") be read
        # back as client intent on every follow-up message.
        history = [
            message["content"]
            for message in state["messages"]
            if message.get("role") == "user"
        ]
        conversation = " ".join(history[-6:])
        profile = f"{conversation} {user_input}".strip()
        profile_lower = profile.lower()

        # Deterministic baseline first, so there is always a complete answer.
        region = _detect_region(profile_lower)
        preferred_model = None
        for model in ["Phantom", "Ghost", "Cullinan", "Spectre"]:
            if re.search(rf"\b{model.lower()}\b", profile_lower):
                preferred_model = model
                break
        budget = _extract_budget_eur(profile)
        timeline = _extract_timeline_months(profile)

        # Then let the model improve on it. It understands "summers in the Gulf"
        # and "needs it before the wedding next spring"; regexes never will.
        brief, source = extract_brief(user_input, history)
        if brief is not None:
            region = brief.region or region
            preferred_model = brief.preferred_model or preferred_model
            budget = brief.budget_eur or budget
            timeline = brief.timeline_months or timeline

        state["client_profile"] = profile
        state["region"] = region
        state["preferred_model"] = preferred_model
        state["budget_eur"] = budget
        state["timeline_months"] = timeline
        state["brief_source"] = source
        return state

    def _retrieve_context(self, state: ConciergeState) -> ConciergeState:
        state["context"] = self.retriever.retrieve(state["client_profile"])
        return state

    def _propose_configuration(self, state: ConciergeState) -> ConciergeState:
        state["revisions"] += 1
        # Deterministic proposal is the floor, never skipped.
        fallback = configure_vehicle(
            client_profile=state["client_profile"],
            preferred_model=state.get("preferred_model"),
            region=state["region"],
        )

        # Guidance is only meaningful on a re-entry, which is signalled by the
        # previous pass having priced the commission over the client's budget.
        repo = get_repository()
        guidance = None
        surcharge_budget = None
        total = state["price"].get("estimated_total")
        budget = state.get("budget_eur")
        if (
            state["price"].get("budget_fit") == "over_budget"
            and isinstance(total, int)
            and isinstance(budget, int)
        ):
            guidance = (
                f"The previous configuration came to EUR {total:,} against a stated budget of "
                f"EUR {budget:,}. Propose a less expensive configuration that still answers the "
                "brief: prefer a house-palette finish, fewer options, and a simpler veneer. "
                "Do not change the model unless there is no other way."
            )
            # Headroom is what remains once the fixed model base and the regional
            # uplift are accounted for. Solving for the pre-uplift surcharge
            # keeps the arithmetic in Python; the model only has to stay under it.
            model_row = repo.model(fallback["model"]) or {}
            base = int(model_row.get("base_price_eur", 0))
            factor = float(state["price"].get("regional_factor", 1.0)) or 1.0
            surcharge_budget = max(int(budget / factor) - base, 0)

        proposal, source, rejected = propose_configuration(
            brief_text=state["client_profile"],
            repo=repo,
            context=state.get("context"),
            guidance=guidance,
            surcharge_budget=surcharge_budget,
        )

        if proposal is None:
            state["configuration"] = fallback
        else:
            # A named model in the brief is a client instruction, not a
            # suggestion, so it outranks whatever the model preferred.
            chosen_model = state.get("preferred_model") or proposal.model
            state["configuration"] = {
                "model": chosen_model,
                "exterior_finish": proposal.exterior_finish,
                "interior_leather": proposal.interior_leather,
                "veneer": proposal.veneer,
                "wheel": proposal.wheel,
                "signature_options": proposal.options[:6],
                "rationale": proposal.rationale
                or f"Selected for a {state['region']} client profile: {state['client_profile']}",
            }

        if surcharge_budget is not None:
            removed = enforce_surcharge_budget(state["configuration"], repo, surcharge_budget)
            state["removed_for_budget"] = removed
            if removed:
                # The rationale was written before the trim, so it can claim an
                # item the client no longer has. Left alone it contradicts the
                # specification directly above it on the page.
                state["configuration"]["rationale"] += (
                    f" Budget then required removing {', '.join(removed)}, so the"
                    " specification above supersedes any earlier mention of them."
                )

        state["config_source"] = source
        state["rejected_items"] = rejected
        return state

    def _call_tools(self, state: ConciergeState) -> ConciergeState:
        """Call the mocked commercial tools defensively: a single tool failure
        should degrade gracefully rather than crash the whole conversation."""
        configuration = state["configuration"]

        try:
            state["price"] = estimate_price(configuration, region=state["region"])
        except Exception:  # noqa: BLE001 - tool boundary, must not crash the graph
            state["price"] = {
                "currency": "EUR",
                "estimated_total": None,
                "confidence": "unavailable",
                "error": "Pricing tool failed; showing the configuration without an estimate.",
            }

        try:
            state["availability"] = check_availability(
                model=configuration["model"],
                region=state["region"],
                timeline_months=state.get("timeline_months"),
            )
        except Exception:  # noqa: BLE001 - tool boundary, must not crash the graph
            state["availability"] = {
                "model": configuration.get("model"),
                "region": state["region"],
                "status": "unknown",
                "lead_time": "unknown",
                "timeline_fit": "unknown",
                "error": "Availability check failed.",
            }

        try:
            state["complementary_options"] = recommend_complementary_options(
                configuration=configuration,
                client_profile=state["client_profile"],
            )
        except Exception:  # noqa: BLE001 - tool boundary, must not crash the graph
            state["complementary_options"] = {
                "recommended_options": [],
                "reason": "Complementary options are unavailable right now.",
            }

        budget = state.get("budget_eur")
        total = state["price"].get("estimated_total")
        if budget and isinstance(total, int):
            state["price"]["budget_fit"] = "fits" if total <= budget else "over_budget"

        return state

    def _evaluate_and_respond(self, state: ConciergeState) -> ConciergeState:
        config = state["configuration"]
        price = state["price"]
        availability = state["availability"]
        options = state["complementary_options"]["recommended_options"]
        sources = [item["source"] for item in state.get("context", [])]

        total = price.get("estimated_total")
        total_text = f"EUR {total:,}" if isinstance(total, int) else "unavailable"

        timeline_note = ""
        timeline_fit = availability.get("timeline_fit")
        if timeline_fit == "at risk":
            timeline_note = " The client's requested timeline is at risk against this lead time."
        elif timeline_fit == "fits":
            timeline_note = " The client's requested timeline fits this lead time."

        budget = state.get("budget_eur")
        budget_line = ""
        if budget:
            fit = price.get("budget_fit")
            if fit == "fits":
                budget_line = f"\nStated budget: EUR {budget:,} - the estimate fits within budget."
            elif fit == "over_budget":
                budget_line = (
                    f"\nStated budget: EUR {budget:,} - the estimate is above the stated budget; "
                    "flag this for a scope or trim-level discussion before proposing."
                )
                # Distinguish "specified too richly" from "wrong car". When the
                # base alone clears the budget, no amount of reconfiguring helps
                # and continuing to shave options wastes the client's time.
                base = next(
                    (
                        line["price_eur"]
                        for line in price.get("line_items", [])
                        if line["category"] == "base"
                    ),
                    0,
                )
                factor = float(price.get("regional_factor", 1.0)) or 1.0
                if int(base * factor) > budget:
                    budget_line += (
                        f"\nNote: the {config['model']} base price alone is above this budget in "
                        f"{state['region']}, so no specification of this model will fit. A "
                        "different model tier is the only route to the stated figure."
                    )
            else:
                budget_line = f"\nStated budget: EUR {budget:,}."

        removed = state.get("removed_for_budget") or []
        if removed:
            budget_line += (
                f"\nRemoved to meet the budget: {', '.join(removed)}. Raise these with the "
                "client before proposing - they were part of the brief."
            )

        fallback = (
            f"Recommended configuration: {config['model']} in {config['exterior_finish']} "
            f"with {config['interior_leather']} and {config['veneer']}.\n\n"
            f"Why this fits: {config['rationale']} The selection balances the stated client "
            f"usage, cabin mood, and regional availability.\n\n"
            f"Availability: {availability['status']} in {availability['region']}, expected lead time "
            f"{availability['lead_time']}.{timeline_note}"
            f"\nEstimated investment: {total_text} ({price.get('confidence', 'unavailable')})."
            f"{budget_line}\n\n"
            f"Complementary options: {', '.join(options) if options else 'none available'}.\n\n"
            f"Knowledge used: {', '.join(sources) if sources else 'No matching KB documents found.'}"
        )
        state["response"] = fallback
        return state


# Ordered by precedence: the first region with a cue in the brief wins.
_REGION_CUES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("UK", ("uk", "united kingdom", "london")),
    ("US", ("usa", "united states", "new york", "california")),
    ("GCC", ("gcc", "uae", "dubai", "abu dhabi", "riyadh", "doha")),
)


def _detect_region(profile_lower: str, default: str = DEFAULT_REGION) -> str:
    """Match region cues on word boundaries.

    A plain substring test silently misroutes commissions: "usage" contains
    "usa", so any brief mentioning usage was priced and stocked as US.
    """
    for region, cues in _REGION_CUES:
        for cue in cues:
            if re.search(rf"\b{re.escape(cue)}\b", profile_lower):
                return region
    return default


def _extract_budget_eur(text: str) -> int | None:
    text_lower = text.lower()
    patterns = [
        r"budget[^\d]{0,20}(\d[\d,]*\.?\d*)\s*(k|thousand|m|million)?",
        r"(?:eur|usd|gbp|[$€£])\s*(\d[\d,]*\.?\d*)\s*(k|thousand|m|million)?\s*budget",
    ]
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if not match:
            continue
        amount = float(match.group(1).replace(",", ""))
        suffix = match.group(2)
        if suffix in ("k", "thousand"):
            amount *= 1_000
        elif suffix in ("m", "million"):
            amount *= 1_000_000
        if amount > 0:
            return int(amount)
    return None


def _extract_timeline_months(text: str) -> int | None:
    tokens = text.lower().replace("-", " ").split()
    for index, token in enumerate(tokens[:-1]):
        if token.isdigit() and tokens[index + 1].startswith("month"):
            return int(token)
    return None


def _default_retriever():
    settings = get_settings()
    if settings.retriever_backend.lower() == "chroma":
        return ChromaKnowledgeRetriever()
    return LocalKnowledgeRetriever()

from __future__ import annotations

from typing import Any

from langgraph.graph import END, StateGraph

from lca.agent.state import ConciergeState
from lca.config import get_settings
from lca.llm import synthesize_with_optional_llm
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
        graph.add_edge("call_tools", "evaluate_and_respond")
        graph.add_edge("evaluate_and_respond", END)
        return graph.compile()

    def invoke(self, user_input: str, memory: list[dict[str, str]] | None = None) -> dict[str, Any]:
        state: ConciergeState = {
            "messages": memory or [],
            "user_input": user_input,
        }
        return dict(self.graph.invoke(state))

    def _understand_intent(self, state: ConciergeState) -> ConciergeState:
        user_input = state["user_input"]
        conversation = " ".join(message["content"] for message in state.get("messages", [])[-6:])
        profile = f"{conversation} {user_input}".strip()
        region = "EU"
        profile_lower = profile.lower()
        if "uk" in profile_lower or "london" in profile_lower:
            region = "UK"
        elif "usa" in profile_lower or "new york" in profile_lower or "california" in profile_lower:
            region = "US"
        elif "dubai" in profile_lower or "gcc" in profile_lower or "riyadh" in profile_lower:
            region = "GCC"

        preferred_model = None
        for model in ["Phantom", "Ghost", "Cullinan", "Spectre"]:
            if model.lower() in profile_lower:
                preferred_model = model
                break

        state["client_profile"] = profile
        state["region"] = region
        state["preferred_model"] = preferred_model
        return state

    def _retrieve_context(self, state: ConciergeState) -> ConciergeState:
        state["context"] = self.retriever.retrieve(state["client_profile"])
        return state

    def _propose_configuration(self, state: ConciergeState) -> ConciergeState:
        state["configuration"] = configure_vehicle(
            client_profile=state["client_profile"],
            preferred_model=state.get("preferred_model"),
            region=state["region"],
        )
        return state

    def _call_tools(self, state: ConciergeState) -> ConciergeState:
        configuration = state["configuration"]
        state["price"] = estimate_price(configuration, region=state["region"])
        state["availability"] = check_availability(
            model=configuration["model"],
            region=state["region"],
            timeline_months=_extract_timeline_months(state["client_profile"]),
        )
        state["complementary_options"] = recommend_complementary_options(
            configuration=configuration,
            client_profile=state["client_profile"],
        )
        return state

    def _evaluate_and_respond(self, state: ConciergeState) -> ConciergeState:
        config = state["configuration"]
        price = state["price"]
        availability = state["availability"]
        options = state["complementary_options"]["recommended_options"]
        sources = [item["source"] for item in state.get("context", [])]

        fallback = (
            f"Recommended configuration: {config['model']} in {config['exterior_finish']} "
            f"with {config['interior_leather']} and {config['veneer']}.\n\n"
            f"Why this fits: {config['rationale']} The selection balances the stated client "
            f"usage, cabin mood, and regional availability.\n\n"
            f"Availability: {availability['status']} in {availability['region']}, expected lead time "
            f"{availability['lead_time']}."
            f"\nEstimated investment: EUR {price['estimated_total']:,} "
            f"({price['confidence']}).\n\n"
            f"Complementary options: {', '.join(options)}.\n\n"
            f"Knowledge used: {', '.join(sources) if sources else 'No matching KB documents found.'}"
        )
        state["response"] = synthesize_with_optional_llm(dict(state), fallback)
        return state


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

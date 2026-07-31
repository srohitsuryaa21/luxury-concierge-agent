from typing import Any, TypedDict

# Region used until a brief says otherwise; also the fallback in `_detect_region`.
DEFAULT_REGION = "EU"


class ConciergeState(TypedDict):
    """State threaded through the LangGraph pipeline.

    Every key is required. `LuxuryConciergeAgent.invoke` seeds the whole schema
    up front and each node overwrites its own fields as the graph advances, so
    a node never observes a half-built state. Keeping this total (rather than
    `total=False`) means a typo in a state key is a type error instead of a
    `KeyError` discovered at runtime, mid-conversation.
    """

    messages: list[dict[str, str]]
    user_input: str
    context: list[dict[str, Any]]
    client_profile: str
    region: str
    preferred_model: str | None
    budget_eur: int | None
    timeline_months: int | None
    configuration: dict[str, Any]
    price: dict[str, Any]
    availability: dict[str, Any]
    complementary_options: dict[str, Any]
    response: str
    # Provenance of each decision, surfaced in the UI trace: "llm" when the model
    # produced it, "rules" when the deterministic fallback did. A demo that can
    # show which half of the system acted is worth more than one that cannot.
    brief_source: str
    config_source: str
    rejected_items: list[str]
    # Items the budget forced out of the specification. Surfaced in the summary:
    # a client must never discover a silent downgrade at handover.
    removed_for_budget: list[str]
    revisions: int


def initial_state(user_input: str, memory: list[dict[str, str]] | None = None) -> ConciergeState:
    """Build a fully-populated starting state for a single conversation turn."""
    return ConciergeState(
        messages=memory or [],
        user_input=user_input,
        context=[],
        client_profile="",
        region=DEFAULT_REGION,
        preferred_model=None,
        budget_eur=None,
        timeline_months=None,
        configuration={},
        price={},
        availability={},
        complementary_options={"recommended_options": [], "reason": ""},
        response="",
        brief_source="rules",
        config_source="rules",
        rejected_items=[],
        removed_for_budget=[],
        revisions=0,
    )

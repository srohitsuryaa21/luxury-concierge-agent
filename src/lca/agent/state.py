from typing import Any, TypedDict


class ConciergeState(TypedDict, total=False):
    messages: list[dict[str, str]]
    user_input: str
    context: list[dict[str, Any]]
    client_profile: str
    region: str
    preferred_model: str | None
    configuration: dict[str, Any]
    price: dict[str, Any]
    availability: dict[str, Any]
    complementary_options: dict[str, Any]
    response: str


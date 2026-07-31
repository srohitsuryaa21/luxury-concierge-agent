from typing import Literal

from pydantic import BaseModel, Field

ModelName = Literal["Phantom", "Ghost", "Cullinan", "Spectre"]


class ClientPreferences(BaseModel):
    usage: str | None = None
    region: str | None = None
    palette: str | None = None
    cabin_mood: str | None = None
    performance_tone: str | None = None
    sustainability: bool | None = None
    budget_eur: int | None = None
    timeline_months: int | None = None


class VehicleConfiguration(BaseModel):
    model: ModelName
    exterior_finish: str
    interior_leather: str
    veneer: str
    wheel: str
    signature_options: list[str] = Field(default_factory=list)
    rationale: str


class ToolResult(BaseModel):
    name: str
    payload: dict


class ExtractedBrief(BaseModel):
    """What the model is allowed to infer from a client conversation.

    Deliberately narrow: these are observations about the client, never
    commercial conclusions. No price, lead time or availability field appears
    here, because the model must not be able to assert one.
    """

    region: Literal["EU", "UK", "US", "GCC"] | None = None
    preferred_model: ModelName | None = None
    budget_eur: int | None = Field(default=None, ge=0)
    timeline_months: int | None = Field(default=None, ge=0, le=120)
    usage: str | None = None
    cabin_mood: str | None = None
    colour_direction: str | None = None
    sustainability: bool | None = None
    chauffeur_driven: bool | None = None


class ProposedConfiguration(BaseModel):
    """A configuration proposed by the model, before catalogue validation."""

    model: ModelName
    exterior_finish: str
    interior_leather: str
    veneer: str
    wheel: str
    options: list[str] = Field(default_factory=list)
    rationale: str = ""


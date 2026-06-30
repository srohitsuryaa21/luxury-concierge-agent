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


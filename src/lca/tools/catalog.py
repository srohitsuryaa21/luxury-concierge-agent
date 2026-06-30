from __future__ import annotations

from dataclasses import dataclass

from lca.domain import VehicleConfiguration


@dataclass(frozen=True)
class PriceBand:
    base_eur: int
    option_floor_eur: int
    option_ceiling_eur: int


PRICE_BANDS = {
    "Phantom": PriceBand(520_000, 65_000, 170_000),
    "Ghost": PriceBand(365_000, 45_000, 120_000),
    "Cullinan": PriceBand(410_000, 55_000, 145_000),
    "Spectre": PriceBand(430_000, 50_000, 135_000),
}

REGIONAL_AVAILABILITY = {
    "EU": {"Phantom": "limited", "Ghost": "available", "Cullinan": "available", "Spectre": "available"},
    "UK": {"Phantom": "limited", "Ghost": "available", "Cullinan": "limited", "Spectre": "available"},
    "US": {"Phantom": "limited", "Ghost": "available", "Cullinan": "available", "Spectre": "limited"},
    "GCC": {"Phantom": "available", "Ghost": "available", "Cullinan": "available", "Spectre": "limited"},
}


def configure_vehicle(
    client_profile: str,
    preferred_model: str | None = None,
    region: str = "EU",
) -> dict:
    profile = client_profile.lower()
    if preferred_model in PRICE_BANDS:
        model = preferred_model
    elif "electric" in profile or "quiet" in profile or "sustain" in profile:
        model = "Spectre"
    elif "family" in profile or "mountain" in profile or "estate" in profile:
        model = "Cullinan"
    elif "driver" in profile or "discreet" in profile:
        model = "Ghost"
    else:
        model = "Phantom"

    exterior = "Commissioned Midnight Sapphire"
    if "green" in profile or "forest" in profile:
        exterior = "Bespoke Emerald Aurora"
    elif "white" in profile or "wedding" in profile:
        exterior = "Arctic White with hand-painted coachline"
    elif "black" in profile or "formal" in profile:
        exterior = "Black Diamond over Anthracite"

    leather = "Grace White full-grain leather"
    if "warm" in profile or "brown" in profile:
        leather = "Ardent Tan natural-grain leather"
    elif "vegan" in profile or "sustain" in profile:
        leather = "Scivaro Grey technical textile and responsibly sourced leather accents"

    config = VehicleConfiguration(
        model=model,  # type: ignore[arg-type]
        exterior_finish=exterior,
        interior_leather=leather,
        veneer="Open-pore Circassian walnut" if "warm" in profile else "Piano Black technical veneer",
        wheel="22-inch part-polished forged wheel",
        signature_options=[
            "Starlight headliner",
            "Bespoke audio tuning",
            "Rear theatre configuration",
        ],
        rationale=f"Selected for a {region} client profile: {client_profile}",
    )
    return config.model_dump()


def estimate_price(configuration: dict, region: str = "EU") -> dict:
    model = configuration.get("model", "Ghost")
    band = PRICE_BANDS.get(model, PRICE_BANDS["Ghost"])
    option_count = len(configuration.get("signature_options", []))
    option_estimate = band.option_floor_eur + min(option_count * 18_000, band.option_ceiling_eur)
    regional_factor = 1.03 if region.upper() in {"GCC", "US"} else 1.0
    total = int((band.base_eur + option_estimate) * regional_factor)
    return {
        "currency": "EUR",
        "base_price": band.base_eur,
        "options_estimate": option_estimate,
        "regional_factor": regional_factor,
        "estimated_total": total,
        "confidence": "directional estimate for sales discovery, not a binding quote",
    }


def check_availability(model: str, region: str = "EU", timeline_months: int | None = None) -> dict:
    region_key = region.upper()
    status = REGIONAL_AVAILABILITY.get(region_key, REGIONAL_AVAILABILITY["EU"]).get(model, "limited")
    lead_time = {
        "available": "6-9 months",
        "limited": "9-14 months",
        "waitlist": "14-18 months",
    }[status]
    timeline_fit = "unknown"
    if timeline_months is not None:
        minimum = int(lead_time.split("-")[0])
        timeline_fit = "fits" if timeline_months >= minimum else "at risk"
    return {
        "model": model,
        "region": region_key,
        "status": status,
        "lead_time": lead_time,
        "timeline_fit": timeline_fit,
    }


def recommend_complementary_options(configuration: dict, client_profile: str) -> dict:
    profile = client_profile.lower()
    options = ["Illuminated fascia", "Contrast stitching matched to coachline"]
    if "chauffeur" in profile or "rear" in profile:
        options.extend(["Privacy suite", "Champagne cooler", "Rear picnic tables"])
    if "sustain" in profile or configuration.get("model") == "Spectre":
        options.extend(["Regenerative drive briefing", "Responsible material provenance pack"])
    if "performance" in profile or "driver" in profile:
        options.extend(["Dynamic drive package", "Driver-focused seat contouring"])
    return {
        "recommended_options": list(dict.fromkeys(options)),
        "reason": "Options are selected to reinforce the stated usage pattern and cabin mood.",
    }


from __future__ import annotations

import re
from typing import Any, cast

from lca.data import get_repository
from lca.domain import ModelName, VehicleConfiguration

# Model names remain a literal tuple because they are a closed domain type; the
# prices, availability and every other catalogue value now live in the database.
KNOWN_MODELS = ("Phantom", "Ghost", "Cullinan", "Spectre")

# A rule is (trigger words, resulting value). Tables are ordered most specific
# first and the first rule that matches wins, so a brief mentioning both
# "burgundy" and "black" resolves to the more distinctive of the two.
Rule = tuple[tuple[str, ...], str]
OptionRule = tuple[tuple[str, ...], tuple[str, ...]]


def _mentions(profile: str, words: tuple[str, ...]) -> bool:
    """Word-boundary keyword test.

    Substring matching is what made "usage" resolve to the USA in the intent
    parser, and the same trap lives in a catalogue: a bare `"tan" in profile`
    matches "instant", `"red"` matches "hundred", `"art"` matches "particular".
    Every trigger here is matched as a whole word, with morphological variants
    spelled out explicitly rather than relying on prefixes.
    """
    return any(re.search(rf"\b{re.escape(word)}\b", profile) for word in words)


def _select(profile: str, rules: tuple[Rule, ...], default: str) -> str:
    for words, value in rules:
        if _mentions(profile, words):
            return value
    return default


_SUSTAINABILITY_WORDS = (
    "sustainable",
    "sustainably",
    "sustainability",
    "sustain",
    "responsible",
    "responsibly",
    "eco",
    "vegan",
    "cruelty-free",
    "plant-based",
)

_MODEL_RULES: tuple[Rule, ...] = (
    (("electric", "ev", "quiet", "silent", "zero-emission", *_SUSTAINABILITY_WORDS), "Spectre"),
    (
        ("family", "children", "kids", "mountain", "mountains", "estate", "off-road",
         "terrain", "safari", "adventure", "outdoors"),
        "Cullinan",
    ),
    # "driving" is deliberately absent: it fires on "chauffeur driving" and
    # "snow driving", neither of which describes an owner-driver.
    (("driver", "discreet", "understated", "entrepreneur", "executive"), "Ghost"),
)
_DEFAULT_MODEL = "Phantom"

_EXTERIOR_RULES: tuple[Rule, ...] = (
    (("burgundy", "oxblood", "claret", "wine"), "Bespoke Burgundy Nocturne"),
    (("navy", "marine", "ocean", "cobalt", "nautical"), "Salamanca Blue over Andalusian White"),
    (("crimson", "scarlet", "ruby"), "Magma Red single-tone"),
    (("amethyst", "violet", "purple"), "Amethyst Twilight with pearlescent flake"),
    (("bronze", "copper", "autumn"), "Bronze Patina with hand-polished brightwork"),
    (("champagne", "desert", "dune", "sand", "gold", "golden"), "Desert Gold satin"),
    (("silver", "platinum", "gunmetal", "graphite", "slate"), "English White over Silver Sand"),
    (("pearl", "bone", "taupe", "oyster"), "Oyster Pearl with tonal coachline"),
    # The four rules below are pinned by the eval suite - keep their relative order.
    (("green", "forest", "emerald", "nature", "woodland"), "Bespoke Emerald Aurora"),
    (("white", "wedding", "arctic", "ivory", "bridal"), "Arctic White with hand-painted coachline"),
    (("black", "formal", "onyx", "ceremonial"), "Black Diamond over Anthracite"),
)
_DEFAULT_EXTERIOR = "Commissioned Midnight Sapphire"

_LEATHER_RULES: tuple[Rule, ...] = (
    (("warm", "brown", "tan", "cognac", "caramel", "chestnut"), "Ardent Tan natural-grain leather"),
    (
        _SUSTAINABILITY_WORDS,
        "Scivaro Grey technical textile and responsibly sourced leather accents",
    ),
    (("cream", "ivory", "seashell", "bone"), "Seashell Cream full-grain leather"),
    (("navy", "blue", "cobalt"), "Navy Blue full-grain leather"),
    (("crimson", "scarlet", "hotspur", "burgundy", "oxblood"), "Hotspur Red full-grain leather"),
    (("charcoal", "slate", "anthracite", "grey", "gray"), "Anthracite Slate full-grain leather"),
    (("black", "onyx", "noir"), "Black Grace full-grain leather"),
    (("forest", "emerald", "green"), "Forest Green full-grain leather"),
)
_DEFAULT_LEATHER = "Grace White full-grain leather"

_VENEER_RULES: tuple[Rule, ...] = (
    (("warm", "walnut", "brown", "chestnut"), "Open-pore Circassian walnut"),
    (("bamboo", *_SUSTAINABILITY_WORDS), "Sustainably harvested bamboo veneer"),
    (("carbon", "technical", "sport", "sports", "performance", "dynamic"), "Technical carbon-fibre twill"),
    (("oak", "burr", "heritage", "traditional", "classic"), "Burr Oak with mirror-matched book leaves"),
    (("pale", "light", "nordic", "obeche", "blonde"), "Pale Obeche open-pore veneer"),
    (("piano", "gloss", "black", "formal", "onyx"), "Piano Black technical veneer"),
)
_DEFAULT_VENEER = "Piano Black technical veneer"

_WHEEL_RULES: tuple[Rule, ...] = (
    # Terrain outranks performance: an estate client who mentions both wants a
    # wheel that survives gravel, not one that sharpens turn-in.
    (
        ("mountain", "mountains", "terrain", "off-road", "estate", "safari", "adventure",
         "snow", "alpine", "winter", "ski"),
        "22-inch all-terrain forged wheel with protective finish",
    ),
    (("performance", "dynamic", "sport", "sports", "driver"), "23-inch forged alloy in gloss black"),
    (("electric", "ev", "quiet", "aero", "efficiency"), "23-inch aero-optimised forged wheel"),
    (("formal", "ceremonial", "chauffeur", "wedding", "bridal"), "21-inch part-polished disc wheel"),
)
_DEFAULT_WHEEL = "22-inch part-polished forged wheel"

# Pricing scales with the number of signature options, so a commission always
# carries exactly three. Variety comes from *which* three, not how many - that
# keeps the estimate comparable across briefs instead of drifting with wording.
SIGNATURE_OPTION_COUNT = 3

_SIGNATURE_RULES: tuple[OptionRule, ...] = (
    (("star", "starlight", "night", "constellation"), ("Starlight headliner with bespoke constellation",)),
    (("audio", "music", "sound", "concert"), ("Bespoke 18-speaker audio tuning",)),
    (("chauffeur", "rear", "privacy"), ("Rear theatre configuration", "Privacy glass to rear compartment")),
    (("performance", "dynamic", "driver"), ("Dynamic drive calibration", "Sports exhaust voicing")),
    (("family", "children", "kids"), ("Rear entertainment tablets", "Child-seat anchor provisioning")),
    (("electric", "quiet", *_SUSTAINABILITY_WORDS), ("Silent-cabin acoustic package", "Regenerative braking calibration")),
    (("art", "gallery", "collector", "curator"), ("Gallery commission by a named artist",)),
    (("monogram", "initials", "crest", "heraldry"), ("Hand-painted monogram and door crests",)),
)
_DEFAULT_SIGNATURES: tuple[str, ...] = (
    "Starlight headliner",
    "Bespoke audio tuning",
    "Rear theatre configuration",
)

_COMPLEMENTARY_BASE: tuple[str, ...] = (
    "Illuminated fascia",
    "Contrast stitching matched to coachline",
)

_COMPLEMENTARY_RULES: tuple[OptionRule, ...] = (
    (("chauffeur", "rear", "passenger"), ("Privacy suite", "Champagne cooler", "Rear picnic tables")),
    (_SUSTAINABILITY_WORDS, ("Regenerative drive briefing", "Responsible material provenance pack")),
    (("performance", "driver", "dynamic"), ("Dynamic drive package", "Driver-focused seat contouring")),
    (("family", "children", "kids"), ("Rear child-seat provisioning", "Cabin partition storage")),
    (
        ("mountain", "mountains", "terrain", "off-road", "estate", "safari", "adventure"),
        ("All-terrain tyre package", "Elevated ride-height calibration", "Boot-mounted viewing suite"),
    ),
    (("wedding", "bridal", "ceremonial", "ceremony"), ("Ceremonial coachline in hand-painted gold", "Rear step illumination")),
    (("touring", "tour", "travel", "weekend", "road-trip"), ("Extended touring luggage set", "Rear refrigeration compartment")),
    (("audio", "music", "sound", "concert"), ("Bespoke 18-speaker audio calibration",)),
    (("privacy", "discreet", "security", "confidential"), ("Laminated privacy glazing", "Discreet-arrival lighting mode")),
    (("pet", "pets", "dog", "dogs", "hound"), ("Cabin pet suite with washable lining",)),
    (("golf", "polo", "sport", "sports"), ("Fitted golf-bag housing",)),
    (("art", "gallery", "collector", "curator"), ("Gallery commission by a named artist",)),
    (
        ("desert", "dune", "dubai", "riyadh", "doha", "gcc", "heat", "sun"),
        ("Heat-reflective glazing", "Sand-sealed underbody protection"),
    ),
    (("winter", "snow", "alpine", "cold", "ski"), ("Cold-climate pack with heated everything",)),
    (("business", "executive", "work", "corporate"), ("Rear business console", "Secure document safe")),
    (("night", "evening", "gala", "event"), ("Illuminated treadplates", "Welcome-light projection")),
)


def _collect_options(profile: str, rules: tuple[OptionRule, ...]) -> list[str]:
    collected: list[str] = []
    for words, options in rules:
        if _mentions(profile, words):
            collected.extend(options)
    return collected


def configure_vehicle(
    client_profile: str,
    preferred_model: str | None = None,
    region: str = "EU",
) -> dict:
    profile = client_profile.lower()

    if preferred_model in KNOWN_MODELS:
        model = preferred_model
    else:
        model = _select(profile, _MODEL_RULES, _DEFAULT_MODEL)

    signatures = _collect_options(profile, _SIGNATURE_RULES)
    signatures.extend(_DEFAULT_SIGNATURES)

    config = VehicleConfiguration(
        model=cast(ModelName, model),
        exterior_finish=_select(profile, _EXTERIOR_RULES, _DEFAULT_EXTERIOR),
        interior_leather=_select(profile, _LEATHER_RULES, _DEFAULT_LEATHER),
        veneer=_select(profile, _VENEER_RULES, _DEFAULT_VENEER),
        wheel=_select(profile, _WHEEL_RULES, _DEFAULT_WHEEL),
        signature_options=list(dict.fromkeys(signatures))[:SIGNATURE_OPTION_COUNT],
        rationale=f"Selected for a {region} client profile: {client_profile}",
    )
    return config.model_dump()


def estimate_price(configuration: dict, region: str = "EU") -> dict:
    """Itemise the commission from catalogue prices.

    Every line comes from the database, so a configuration the model proposed
    costs exactly what those catalogue items cost. There is no path by which a
    language model can influence this number.
    """
    repo = get_repository()
    model_name = configuration.get("model", "Ghost")
    model_row = repo.model(model_name) or repo.model("Ghost")
    base = int(model_row["base_price_eur"]) if model_row else 0

    lines: list[dict[str, Any]] = [{"item": model_name, "category": "base", "price_eur": base}]
    for table, key, category in (
        ("paints", "exterior_finish", "paint"),
        ("leathers", "interior_leather", "leather"),
        ("veneers", "veneer", "veneer"),
        ("wheels", "wheel", "wheel"),
    ):
        name = configuration.get(key)
        if name:
            lines.append(
                {"item": name, "category": category, "price_eur": repo.price_of(table, name)}
            )
    for name in configuration.get("signature_options", []):
        lines.append(
            {"item": name, "category": "option", "price_eur": repo.price_of("options", name)}
        )

    subtotal = sum(int(line["price_eur"]) for line in lines)
    region_row = repo.region(region.upper()) or repo.region("EU")
    regional_factor = float(region_row["uplift_factor"]) if region_row else 1.0
    total = int(subtotal * regional_factor)

    return {
        "currency": "EUR",
        "base_price": base,
        "options_estimate": subtotal - base,
        "line_items": lines,
        "subtotal": subtotal,
        "regional_factor": regional_factor,
        "estimated_total": total,
        "confidence": "directional estimate for sales discovery, not a binding quote",
    }


def check_availability(model: str, region: str = "EU", timeline_months: int | None = None) -> dict:
    repo = get_repository()
    region_key = region.upper()
    row = repo.availability(model, region_key) or repo.availability(model, "EU")
    if row is None:
        status, lead_min, lead_max = "limited", 9, 14
    else:
        status = str(row["status"])
        lead_min, lead_max = int(row["lead_min_months"]), int(row["lead_max_months"])

    lead_time = f"{lead_min}-{lead_max} months"
    timeline_fit = "unknown"
    if timeline_months is not None:
        timeline_fit = "fits" if timeline_months >= lead_min else "at risk"
    return {
        "model": model,
        "region": region_key,
        "status": status,
        "lead_time": lead_time,
        "lead_min_months": lead_min,
        "timeline_fit": timeline_fit,
    }


def recommend_complementary_options(configuration: dict, client_profile: str) -> dict:
    profile = client_profile.lower()
    options = list(_COMPLEMENTARY_BASE)
    options.extend(_collect_options(profile, _COMPLEMENTARY_RULES))
    if configuration.get("model") == "Spectre":
        options.extend(["Regenerative drive briefing", "Responsible material provenance pack"])
    return {
        "recommended_options": list(dict.fromkeys(options)),
        "reason": "Options are selected to reinforce the stated usage pattern and cabin mood.",
    }

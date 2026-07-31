"""The model-driven half of the agent.

Two decisions are delegated to the LLM: understanding the brief, and proposing a
configuration. Both are constrained on the way out - the brief is validated by a
Pydantic schema that contains no commercial fields, and every item in a proposal
must already exist in the catalogue database. Anything the model returns that
fails validation is discarded and the deterministic rules take over.

The model therefore contributes judgement, and can contribute nothing else.
"""

from __future__ import annotations

import re
from typing import Any

from pydantic import ValidationError

from lca.data import CatalogRepository
from lca.domain import ExtractedBrief, ProposedConfiguration
from lca.llm import complete_json

_EXTRACT_SYSTEM = """You read luxury vehicle sales conversations and extract
structured facts about the client. Return a single JSON object with these keys:

  region: one of "EU", "UK", "US", "GCC", or null
  preferred_model: one of "Phantom", "Ghost", "Cullinan", "Spectre", or null
  budget_eur: integer or null
  timeline_months: integer or null
  usage: short phrase or null
  cabin_mood: short phrase or null
  colour_direction: short phrase or null
  sustainability: true, false or null
  chauffeur_driven: true, false or null

Rules. Infer the region from where the car will be delivered or driven, not from
nationality: Dubai, Riyadh, Doha and Abu Dhabi are GCC; London is UK; New York
and California are US. Only set preferred_model if the client named a model.
Use null whenever the conversation does not say. Never guess a budget."""

_PROPOSE_SYSTEM = """You are a luxury vehicle configuration specialist. Choose a
configuration for the client from the supplied catalogue.

Return a single JSON object with keys: model, exterior_finish, interior_leather,
veneer, wheel, options (array of strings), rationale (one or two sentences).

Every value MUST be copied exactly from the catalogue lists you are given. Do not
invent names, do not paraphrase, do not translate. Choose at most 6 options.
Never mention prices, lead times or availability - you are not given them and you
must not assert them. Explain your choice in the rationale by referring to what
the client actually asked for.

Restraint is part of the job. Where the client has expressed no preference on a
dimension, choose the house default rather than something expressive: exterior
"Commissioned Midnight Sapphire", interior "Grace White full-grain leather",
veneer "Piano Black technical veneer", wheel "22-inch part-polished forged
wheel". Only depart from a default when something in the brief calls for it. A
client who did not ask for a rare colour has not agreed to one."""


def extract_brief(user_input: str, history: list[str]) -> tuple[ExtractedBrief | None, str]:
    """Extract client facts with the LLM. Returns (brief, source)."""
    conversation = "\n".join([*history[-6:], user_input]).strip()
    payload = complete_json(_EXTRACT_SYSTEM, f"Conversation:\n{conversation}")
    if payload is None:
        return None, "rules"
    try:
        return ExtractedBrief.model_validate(payload), "llm"
    except ValidationError:
        # A malformed extraction is worth nothing; the rules parser is reliable.
        return None, "rules"


def propose_configuration(
    brief_text: str,
    repo: CatalogRepository,
    context: list[dict[str, Any]] | None = None,
    guidance: str | None = None,
) -> tuple[ProposedConfiguration | None, str, list[str]]:
    """Ask the LLM to configure from the catalogue.

    Returns (proposal, source, rejected) where `rejected` lists any values the
    model produced that are not in the catalogue. A proposal is only returned
    when every core field validates, so a partially-hallucinated configuration
    is discarded rather than silently patched.
    """
    catalogue = {
        "models": repo.names("models"),
        "exterior_finishes": repo.names("paints"),
        "interior_leathers": repo.names("leathers"),
        "veneers": repo.names("veneers"),
        "wheels": repo.names("wheels"),
        # The option catalogue is by far the largest list and most of it is
        # irrelevant to any one brief. Shortlisting by keyword before the call
        # cuts the prompt roughly in half and improves the choice: the model
        # ranks a focused candidate set instead of scanning everything.
        "options": _shortlist_options(repo, brief_text.lower()),
    }
    knowledge = "\n\n".join(
        f"[{item['source']}] {item['content'][:400]}" for item in (context or [])[:2]
    )
    catalogue_text = "\n".join(f"{key}: {' | '.join(values)}" for key, values in catalogue.items())
    user = (
        f"Client brief:\n{brief_text}\n\n"
        f"Catalogue (choose only from these):\n{catalogue_text}\n\n"
        f"Relevant product knowledge:\n{knowledge or 'none'}"
    )
    if guidance:
        user += f"\n\nAdditional instruction:\n{guidance}"

    payload = complete_json(_PROPOSE_SYSTEM, user)
    if payload is None:
        return None, "rules", []

    try:
        proposal = ProposedConfiguration.model_validate(payload)
    except ValidationError:
        return None, "rules", []

    rejected = _validate_against_catalogue(proposal, catalogue)
    core_rejected = [item for item in rejected if not item.startswith("option:")]
    if core_rejected:
        # The model picked a finish or material that does not exist. Discard the
        # whole proposal - a configuration is a coherent set, not a bag of parts.
        return None, "rules", rejected

    proposal.options = [name for name in proposal.options if name in set(catalogue["options"])]
    return proposal, "llm", rejected


_STAPLE_OPTIONS = (
    "Illuminated fascia",
    "Starlight headliner",
    "Bespoke audio tuning",
    "Contrast stitching matched to coachline",
)


def _shortlist_options(repo: CatalogRepository, brief_lower: str, limit: int = 20) -> list[str]:
    """Rank catalogue options by keyword overlap with the brief.

    This is a retrieval step, not a decision: it narrows what the model is shown,
    and the model still chooses. A handful of staples are always included so a
    brief that matches nothing still has something sensible to offer.
    """
    scored: list[tuple[int, str]] = []
    for row in repo.options():
        keywords = [word.strip() for word in row["keywords"].split(",") if word.strip()]
        hits = sum(
            1 for word in keywords if re.search(rf"\b{re.escape(word)}\b", brief_lower)
        )
        if hits:
            scored.append((hits, row["name"]))

    scored.sort(key=lambda item: (-item[0], item[1]))
    names = [name for _, name in scored[:limit]]
    for staple in _STAPLE_OPTIONS:
        if len(names) >= limit:
            break
        if staple not in names:
            names.append(staple)
    return names


def _validate_against_catalogue(
    proposal: ProposedConfiguration, catalogue: dict[str, list[str]]
) -> list[str]:
    rejected: list[str] = []
    checks = (
        ("exterior_finish", proposal.exterior_finish, "exterior_finishes"),
        ("interior_leather", proposal.interior_leather, "interior_leathers"),
        ("veneer", proposal.veneer, "veneers"),
        ("wheel", proposal.wheel, "wheels"),
    )
    for field, value, key in checks:
        if value not in set(catalogue[key]):
            rejected.append(f"{field}: {value}")
    known_options = set(catalogue["options"])
    rejected.extend(f"option: {name}" for name in proposal.options if name not in known_options)
    return rejected

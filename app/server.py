"""HTTP layer for the concierge.

A hand-written front end rather than a dashboard framework: this is a
client-facing sales tool for a luxury marque, and framework chrome reads as a
template. The server stays thin - it exposes the agent's structured state and
lets the page present it.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from lca.agent import LuxuryConciergeAgent
from lca.config import get_settings
from lca.data import ConversationStore, get_repository
from lca.llm import get_usage, provider_status

STATIC = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Luxury Concierge Agent", docs_url="/api/docs")
app.mount("/static", StaticFiles(directory=STATIC), name="static")

_agent: LuxuryConciergeAgent | None = None


def agent() -> LuxuryConciergeAgent:
    """Built once: the retriever loads and indexes the knowledge table."""
    global _agent
    if _agent is None:
        _agent = LuxuryConciergeAgent()
    return _agent


_store: ConversationStore | None = None


def store() -> ConversationStore:
    global _store
    if _store is None:
        _store = ConversationStore(get_settings().conversations_db_path)
    return _store


class BriefRequest(BaseModel):
    brief: str = Field(min_length=1, max_length=4000)
    # Omit to start a new conversation; the server returns the id to continue.
    conversation_id: str | None = None


SAMPLES = [
    {
        "title": "The inference test",
        "note": "No region word, no digits, no month count",
        "brief": (
            "My client spends her winters in the Emirates and wants something for the "
            "dunes. She is happy up to about three quarters of a million euro and needs "
            "it before next autumn."
        ),
    },
    {
        "title": "Over budget",
        "note": "Triggers a second, cheaper proposal",
        "brief": (
            "London client wants a Ghost, gallery artwork, bespoke commissioned paint "
            "and rear theatre, budget 430000, 12-month timeline."
        ),
    },
    {
        "title": "Wrong car entirely",
        "note": "Base price alone clears the budget",
        "brief": (
            "Riyadh client, ceremonial black flagship Phantom, gallery artwork, "
            "budget 450000, 12-month timeline."
        ),
    },
    {
        "title": "Restraint",
        "note": "Should not upsell a rare colour",
        "brief": "A client wants something bespoke and elegant, no particular preferences stated.",
    },
]

# Rendering swatches from the paint's family column keeps the page honest: the
# colour shown is derived from the catalogue, not hand-maintained in CSS.
FAMILY_SWATCH = {
    "black": "#1A1B1E",
    "white": "#EDE9E2",
    "silver": "#B9BCC0",
    "grey": "#6E7276",
    "blue": "#1F3A5F",
    "green": "#1F4437",
    "red": "#6E2029",
    "purple": "#463055",
    "bronze": "#7A5230",
    "gold": "#B08C4F",
}


def _swatch(paint_name: str) -> str:
    for row in get_repository().paints():
        if row["name"] == paint_name:
            return FAMILY_SWATCH.get(row["family"], "#4A4D52")
    return "#4A4D52"


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/api/bootstrap")
def bootstrap() -> JSONResponse:
    settings = get_settings()
    counts = get_repository().counts()
    return JSONResponse(
        {
            "samples": SAMPLES,
            "status": provider_status(),
            "retriever": settings.retriever_backend,
            "catalogue": counts,
            "usage": get_usage().as_dict(),
        }
    )


@app.get("/api/conversations")
def conversations() -> JSONResponse:
    return JSONResponse({"conversations": store().list()})


@app.get("/api/conversations/{conversation_id}")
def conversation(conversation_id: str) -> JSONResponse:
    transcript = store().transcript(conversation_id)
    if transcript is None:
        return JSONResponse({"error": "No such conversation."}, status_code=404)
    return JSONResponse(transcript)


@app.delete("/api/conversations/{conversation_id}")
def remove_conversation(conversation_id: str) -> JSONResponse:
    if not store().delete(conversation_id):
        return JSONResponse({"error": "No such conversation."}, status_code=404)
    return JSONResponse({"deleted": conversation_id})


@app.post("/api/brief")
def submit(request: BriefRequest) -> JSONResponse:
    conversations = store()
    conversation_id = request.conversation_id
    if conversation_id and conversations.transcript(conversation_id) is None:
        conversation_id = None
    # Memory comes from the database, not the browser: the client should not be
    # able to rewrite what the agent believes was said earlier in the sale.
    memory = conversations.memory(conversation_id) if conversation_id else []
    if conversation_id is None:
        conversation_id = conversations.start(request.brief)

    result: dict[str, Any] = agent().invoke(request.brief, memory=memory)
    config = result["configuration"]
    price = result["price"]

    payload = {
        "conversation_id": conversation_id,
        "summary": result["response"],
        "region": result["region"],
        "budget_eur": result.get("budget_eur"),
        "timeline_months": result.get("timeline_months"),
        "configuration": config,
        "swatch": _swatch(config.get("exterior_finish", "")),
        "price": price,
        "availability": result["availability"],
        "complementary": result["complementary_options"]["recommended_options"],
        "knowledge": [
            {"source": item["source"], "category": item.get("category", "")}
            for item in result.get("context", [])
        ],
        "provenance": {
            "brief": result.get("brief_source"),
            "configuration": result.get("config_source"),
            "proposals": result.get("revisions"),
            "rejected": result.get("rejected_items", []),
            "removed_for_budget": result.get("removed_for_budget", []),
        },
        "usage": get_usage().as_dict(),
    }

    conversations.record_turn(conversation_id, request.brief, payload)
    return JSONResponse(payload)

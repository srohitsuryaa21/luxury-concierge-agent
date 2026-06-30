from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from lca.config import get_settings


def synthesize_with_optional_llm(state: dict[str, Any], fallback: str) -> str:
    settings = get_settings()
    if settings.model_provider.lower() != "ollama":
        return fallback

    prompt = _build_sales_summary_prompt(state)
    try:
        return _call_ollama(prompt).strip() or fallback
    except (OSError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return fallback


def _call_ollama(prompt: str) -> str:
    settings = get_settings()
    url = f"{settings.ollama_base_url.rstrip('/')}/api/generate"
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2},
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=settings.ollama_timeout_seconds) as response:
        body = json.loads(response.read().decode("utf-8"))
    return str(body.get("response", ""))


def _build_sales_summary_prompt(state: dict[str, Any]) -> str:
    return f"""You are a luxury automotive sales concierge.
Write a concise, sales-ready recommendation summary. Keep it grounded in the data.

Client profile:
{state.get("client_profile")}

Configuration:
{json.dumps(state.get("configuration", {}), indent=2)}

Availability:
{json.dumps(state.get("availability", {}), indent=2)}

Price:
{json.dumps(state.get("price", {}), indent=2)}

Complementary options:
{json.dumps(state.get("complementary_options", {}), indent=2)}

Knowledge context:
{json.dumps(state.get("context", []), indent=2)}
"""

"""Model access.

One provider abstraction over OpenAI-compatible chat endpoints. Grok (xAI) is
the default.

Every function here is failure-tolerant by design: the commercial answer is
computed deterministically before any model is called, so a model that is slow,
unauthorised or offline costs wording - never correctness. That tolerance is
also a hazard, because a broken key looks exactly like a working demo, so every
call and every failure is metered and surfaced in the UI.
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from lca.config import get_settings

# Cap generation length so a slow model can never hang a request for the full
# timeout window. A sales summary needs a few hundred tokens, and bounding it
# keeps worst-case latency predictable.
MAX_SUMMARY_TOKENS = 320

SALES_SYSTEM_PROMPT = (
    "You are a luxury automotive sales concierge. Rewrite the supplied "
    "configuration data into a warm, concise, sales-ready summary. Every number, "
    "material, lead time and availability status must be taken verbatim from the "
    "data given to you. Never invent a price, a date or an option. If the data "
    "says the estimate is over budget or the timeline is at risk, say so plainly."
)

# Any provider speaking the OpenAI chat-completions protocol works: xAI, Groq,
# Gemini's compatibility endpoint, OpenRouter, OpenAI itself. These are the
# environment variable names each conventionally uses for its key.
_KEY_VARIABLES = (
    "LLM_API_KEY",
    "XAI_API_KEY",
    "GROQ_API_KEY",
    "GEMINI_API_KEY",
    "OPENROUTER_API_KEY",
    "OPENAI_API_KEY",
)


@dataclass
class Usage:
    """Per-process meter for model consumption.

    Deliberately counts failures alongside successes: an agent that quietly
    degrades to its deterministic fallback still looks like it is working, and
    the only way to notice is to show how often the model was actually reached.
    """

    calls: int = 0
    failures: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    # Reporting "every call failed" without saying why is not much better than
    # failing silently, so the most recent error is kept for display.
    last_error: str = ""

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    def as_dict(self) -> dict[str, Any]:
        return {
            "calls": self.calls,
            "failures": self.failures,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "last_error": self.last_error,
        }


def _record_failure(exc: BaseException | None = None, note: str = "") -> None:
    _USAGE.failures += 1
    if exc is not None:
        _USAGE.last_error = f"{type(exc).__name__}: {exc}"[:400]
    elif note:
        _USAGE.last_error = note


_USAGE = Usage()

# Evals and tests exercise the deterministic layer, which is the layer that must
# never regress. Letting them call the model spends a daily quota on a result
# they do not assert against, so they turn this on and the model is skipped
# outright - not counted as a failure, because choosing not to call is not one.
_OFFLINE = False


def set_offline(offline: bool) -> None:
    global _OFFLINE
    _OFFLINE = offline


def is_offline() -> bool:
    return _OFFLINE


def get_usage() -> Usage:
    return _USAGE


def reset_usage() -> None:
    global _USAGE
    _USAGE = Usage()


def _record_usage(usage: Any) -> None:
    """Fold an API usage object into the running meter."""
    if usage is None:
        return
    _USAGE.prompt_tokens += int(getattr(usage, "prompt_tokens", 0) or 0)
    _USAGE.completion_tokens += int(getattr(usage, "completion_tokens", 0) or 0)


def provider_status() -> dict[str, Any]:
    """Whether a model is configured, for display. Does not call the API."""
    base_url, api_key, model, _ = _provider_config()
    return {
        "provider": get_settings().model_provider,
        "model": model,
        "base_url": base_url,
        "ready": bool(api_key),
        "detail": "Key loaded." if api_key else "No API key found in .env.",
    }


def _api_key() -> str:
    """First configured key wins, so a user sets only the variable their
    provider names."""
    for name in _KEY_VARIABLES:
        value = os.getenv(name)
        if value:
            return value
    return ""


def _provider_config() -> tuple[str, str, str, int]:
    """Resolve (base_url, api_key, model, timeout) for the configured endpoint."""
    settings = get_settings()
    return settings.llm_base_url, _api_key(), settings.llm_model, settings.llm_timeout_seconds


def _client(base_url: str, api_key: str, timeout: int):
    if not api_key:
        raise RuntimeError(
            f"No API key found. Set one of {', '.join(_KEY_VARIABLES)} in .env."
        )
    from openai import OpenAI

    return OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)


def synthesize_with_optional_llm(state: dict[str, Any], fallback: str) -> str:
    """Non-streaming helper for programmatic callers (tests, evals, scripts)."""
    return "".join(stream_sales_summary(state, fallback))


def stream_sales_summary(state: dict[str, Any], fallback: str) -> Iterator[str]:
    if _OFFLINE:
        yield fallback
        return
    config = _provider_config()
    if config is None:
        yield fallback
        return
    base_url, api_key, model, timeout = config

    produced_any = False
    _USAGE.calls += 1
    try:
        client = _client(base_url, api_key, timeout)
        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SALES_SYSTEM_PROMPT},
                {"role": "user", "content": _build_sales_summary_prompt(state)},
            ],
            max_tokens=MAX_SUMMARY_TOKENS,
            temperature=0.2,
            stream=True,
            # Usage only arrives on a streamed response if it is asked for, and
            # it comes in a final chunk that carries no choices.
            stream_options={"include_usage": True},
        )
        for chunk in stream:
            _record_usage(getattr(chunk, "usage", None))
            if not chunk.choices:
                continue
            piece = chunk.choices[0].delta.content
            if piece:
                produced_any = True
                yield piece
        if not produced_any:
            _record_failure(note="Model returned an empty stream.")
            yield fallback
    except Exception as exc:  # noqa: BLE001 - model boundary, must never kill the turn
        _record_failure(exc)
        if produced_any:
            yield "\n\n(Model connection interrupted; summary may be incomplete.)"
        else:
            yield fallback


def complete_json(system: str, user: str) -> dict[str, Any] | None:
    """Ask the provider for one JSON object, or None if that is not possible.

    Returns None whenever the model is unavailable, unauthorised, slow, or
    produces something unparseable. Every caller must have a deterministic
    fallback: the agent degrades to rules rather than failing the turn.
    """
    if _OFFLINE:
        return None
    config = _provider_config()
    if config is None:
        return None
    base_url, api_key, model, timeout = config

    _USAGE.calls += 1
    try:
        client = _client(base_url, api_key, timeout)
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
            max_tokens=700,
        )
        _record_usage(completion.usage)
        raw = completion.choices[0].message.content
    except Exception as exc:  # noqa: BLE001 - model boundary; caller falls back to rules
        _record_failure(exc)
        return None

    parsed = _parse_json_object(raw)
    if parsed is None:
        _record_failure(note=f"Unparseable JSON reply: {(raw or '')[:200]!r}")
    return parsed


def _parse_json_object(raw: str | None) -> dict[str, Any] | None:
    """Parse a JSON object, tolerating fenced or prose-wrapped model output."""
    if not raw:
        return None
    text = raw.strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        parsed = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _build_sales_summary_prompt(state: dict[str, Any]) -> str:
    return f"""Write the client-facing recommendation summary.

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

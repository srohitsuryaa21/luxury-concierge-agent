"""Scenario evaluation over the agent's structured output.

The previous harness asserted substrings in the final prose, which passed for
the wrong reasons: the summary echoes the client's own brief, so a case could
match on words the client supplied rather than on anything the agent decided.
These checks read the state the agent actually produced - chosen model, region,
materials, budget verdict, retrieval categories, proposal count - and fall back
to prose matching only where the assertion really is about the wording.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer

from lca.agent import LuxuryConciergeAgent
from lca.data import get_repository

app = typer.Typer(add_completion=False)


def _check(result: dict[str, Any], expect: dict[str, Any]) -> list[str]:
    """Return human-readable failures for one case; empty means it passed."""
    failures: list[str] = []
    config = result.get("configuration", {})
    price = result.get("price", {})
    availability = result.get("availability", {})

    def compare(label: str, actual: Any, wanted: Any) -> None:
        if actual != wanted:
            failures.append(f"{label}={actual!r} wanted {wanted!r}")

    def contains(label: str, actual: str, needle: str) -> None:
        if needle.lower() not in (actual or "").lower():
            failures.append(f"{label}={actual!r} missing {needle!r}")

    if "model" in expect:
        compare("model", config.get("model"), expect["model"])
    if "region" in expect:
        compare("region", result.get("region"), expect["region"])
    if "budget_eur" in expect:
        compare("budget_eur", result.get("budget_eur"), expect["budget_eur"])
    if "budget_fit" in expect:
        compare("budget_fit", price.get("budget_fit"), expect["budget_fit"])
    if "timeline_fit" in expect:
        compare("timeline_fit", availability.get("timeline_fit"), expect["timeline_fit"])
    if "proposals" in expect:
        compare("proposals", result.get("revisions"), expect["proposals"])
    if "paint_contains" in expect:
        contains("paint", config.get("exterior_finish", ""), expect["paint_contains"])
    if "leather_contains" in expect:
        contains("leather", config.get("interior_leather", ""), expect["leather_contains"])
    if "veneer_contains" in expect:
        contains("veneer", config.get("veneer", ""), expect["veneer_contains"])

    if expect.get("leather_vegan"):
        vegan = {row["name"] for row in get_repository().leathers() if row["vegan"]}
        chosen = config.get("interior_leather")
        if chosen not in vegan:
            failures.append(f"leather={chosen!r} is not a vegan option")

    if expect.get("all_line_items_priced"):
        # Guards the core safety property: a configuration may only contain
        # catalogue items. Membership is checked by name, not by price - house
        # defaults such as Midnight Sapphire legitimately cost nothing, so
        # treating a zero as "unknown item" reports a bug that does not exist.
        repo = get_repository()
        tables = {
            "base": "models",
            "paint": "paints",
            "leather": "leathers",
            "veneer": "veneers",
            "wheel": "wheels",
            "option": "options",
        }
        for line in price.get("line_items", []):
            table = tables.get(line["category"])
            if table and line["item"] not in set(repo.names(table)):
                failures.append(f"line item {line['item']!r} is not in {table}")

    if "knowledge_categories" in expect:
        found = {item.get("category") for item in result.get("context", [])}
        for wanted in expect["knowledge_categories"]:
            if wanted not in found:
                failures.append(f"retrieval missed category {wanted!r}, got {sorted(found)}")

    response = result.get("response", "")
    for needle in expect.get("response_contains", []):
        if needle.lower() not in response.lower():
            failures.append(f"response missing {needle!r}")

    return failures


@app.command()
def main(cases_path: Path = Path("src/lca/evals/cases.json"), verbose: bool = False) -> None:
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    agent = LuxuryConciergeAgent()
    results = []

    for case in cases:
        result = agent.invoke(case["input"])
        results.append({"id": case["id"], "failures": _check(result, case.get("expect", {}))})

    passed = sum(1 for item in results if not item["failures"])
    typer.echo(f"Passed {passed}/{len(cases)} eval cases")
    for item in results:
        if item["failures"]:
            typer.echo(f"FAIL {item['id']}")
            for failure in item["failures"]:
                typer.echo(f"       {failure}")
        elif verbose:
            typer.echo(f"PASS {item['id']}")

    if passed < len(cases):
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()

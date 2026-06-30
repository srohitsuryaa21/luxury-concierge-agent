from __future__ import annotations

import json
from pathlib import Path

import typer

from lca.agent import LuxuryConciergeAgent

app = typer.Typer(add_completion=False)


@app.command()
def main(cases_path: Path = Path("src/lca/evals/cases.json")) -> None:
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    agent = LuxuryConciergeAgent()
    passed = 0
    results = []

    for case in cases:
        output = agent.invoke(case["input"])["response"]
        missing = [term for term in case["must_include"] if term.lower() not in output.lower()]
        ok = not missing
        passed += int(ok)
        results.append({"id": case["id"], "passed": ok, "missing": missing})

    typer.echo(f"Passed {passed}/{len(cases)} eval cases")
    for result in results:
        marker = "PASS" if result["passed"] else "FAIL"
        typer.echo(f"{marker} {result['id']} missing={result['missing']}")


if __name__ == "__main__":
    app()


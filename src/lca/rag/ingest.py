from __future__ import annotations

from pathlib import Path

import typer

from lca.config import get_settings
from lca.rag.chroma_store import ChromaKnowledgeStore

app = typer.Typer(add_completion=False)


@app.command()
def main(kb_dir: Path | None = None) -> None:
    """Ingest markdown knowledge-base documents into local Chroma."""

    settings = get_settings()
    source_dir = kb_dir or settings.kb_dir
    count = ChromaKnowledgeStore().ingest_markdown(source_dir)
    typer.echo(f"Ingested {count} documents from {source_dir} into {settings.chroma_dir}.")


if __name__ == "__main__":
    app()

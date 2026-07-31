from __future__ import annotations

import typer

from lca.config import get_settings
from lca.rag.chroma_store import ChromaKnowledgeStore

app = typer.Typer(add_completion=False)


@app.command()
def main() -> None:
    """Embed the knowledge table into the local Chroma store."""
    settings = get_settings()
    count = ChromaKnowledgeStore().ingest()
    typer.echo(f"Embedded {count} knowledge passages into {settings.chroma_dir}.")


if __name__ == "__main__":
    app()

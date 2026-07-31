from __future__ import annotations

import os
from collections.abc import Sequence
from itertools import zip_longest
from typing import Any

import chromadb
from chromadb.api.types import Metadata
from chromadb.utils import embedding_functions

from lca.config import get_settings
from lca.data import get_repository


def _first_row(rows: Sequence[Sequence[Any]] | None) -> list[Any]:
    """Return the first result row from a Chroma query field.

    Chroma sets unrequested fields to `None` rather than omitting the key, so
    `results.get("documents", [[]])` still hands back `None` and indexing it
    raises. Normalising here keeps the retriever from crashing a conversation.
    """
    if not rows:
        return []
    return list(rows[0])


def _embedding_function():
    """Build the embedding function named by `LCA_EMBEDDING_BACKEND`.

    Defaults to `local`, which runs a small ONNX model on-device. That keeps
    semantic retrieval usable with no API key and no running LLM server, which
    matters because the rest of this project is deliberately runnable offline.
    """
    settings = get_settings()
    backend = settings.embedding_backend.lower()

    if backend == "local":
        return embedding_functions.DefaultEmbeddingFunction()

    if backend == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required for Chroma OpenAI embeddings.")
        return embedding_functions.OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name=settings.embedding_model,
        )

    raise RuntimeError(
        f"Unknown LCA_EMBEDDING_BACKEND '{settings.embedding_backend}'. "
        "Expected one of: local, openai."
    )


class ChromaKnowledgeStore:
    def __init__(self):
        settings = get_settings()
        self.client = chromadb.PersistentClient(path=str(settings.chroma_dir))
        self.collection = self.client.get_or_create_collection(
            name=settings.collection_name,
            # chromadb's own embedding helpers are typed over Documents while the
            # parameter is typed over the wider Embeddable (text or images), so
            # they do not satisfy their own protocol. Upstream variance bug, not
            # a defect here - text embedding works at runtime.
            embedding_function=_embedding_function(),  # pyright: ignore[reportArgumentType]
        )

    def ingest(self) -> int:
        """Embed every knowledge passage from the database.

        One row becomes one embedding. Both retrievers therefore index exactly
        the same passages, so switching backends changes retrieval quality and
        nothing else.
        """
        rows = get_repository().knowledge()
        ids = [row["title"] for row in rows]
        # Keywords are embedded with the prose so a passage can be reached by
        # vocabulary a client would use but the passage does not contain.
        docs = [f"{row['title']}. {row['content']} Topics: {row['keywords']}" for row in rows]
        metadatas: list[Metadata] = [
            {"source": row["title"], "category": row["category"]} for row in rows
        ]
        if docs:
            self.collection.upsert(ids=ids, documents=docs, metadatas=metadatas)
        return len(docs)

    def query(self, query: str, k: int | None = None) -> list[dict]:
        settings = get_settings()
        results = self.collection.query(query_texts=[query], n_results=k or settings.retrieval_k)
        documents = _first_row(results.get("documents"))
        metadatas = _first_row(results.get("metadatas"))
        distances = _first_row(results.get("distances"))
        # zip_longest, not zip: a missing metadata/distance field should degrade
        # those columns, not silently discard every retrieved document.
        return [
            {
                "source": metadata.get("source", "chroma") if metadata else "chroma",
                "content": document[:1400],
                "score": distance,
            }
            for document, metadata, distance in zip_longest(documents, metadatas, distances)
            if document is not None
        ]


class ChromaKnowledgeRetriever:
    def __init__(self):
        self.store = ChromaKnowledgeStore()

    def retrieve(self, query: str) -> list[dict]:
        return self.store.query(query)


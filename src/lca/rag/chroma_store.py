from __future__ import annotations

import os
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

from lca.config import get_settings


def _openai_embedding_function():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for Chroma OpenAI embeddings.")
    settings = get_settings()
    return embedding_functions.OpenAIEmbeddingFunction(
        api_key=api_key,
        model_name=settings.embedding_model,
    )


class ChromaKnowledgeStore:
    def __init__(self):
        settings = get_settings()
        self.client = chromadb.PersistentClient(path=str(settings.chroma_dir))
        self.collection = self.client.get_or_create_collection(
            name=settings.collection_name,
            embedding_function=_openai_embedding_function(),
        )

    def ingest_markdown(self, kb_dir: Path | None = None) -> int:
        settings = get_settings()
        source_dir = kb_dir or settings.kb_dir
        paths = sorted(source_dir.glob("*.md"))
        ids = [path.stem for path in paths]
        docs = [path.read_text(encoding="utf-8") for path in paths]
        metadatas = [{"source": str(path)} for path in paths]
        if docs:
            self.collection.upsert(ids=ids, documents=docs, metadatas=metadatas)
        return len(docs)

    def query(self, query: str, k: int | None = None) -> list[dict]:
        settings = get_settings()
        results = self.collection.query(query_texts=[query], n_results=k or settings.retrieval_k)
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        return [
            {
                "source": metadata.get("source", "chroma") if metadata else "chroma",
                "content": document[:1400],
                "score": distance,
            }
            for document, metadata, distance in zip(documents, metadatas, distances)
        ]


class ChromaKnowledgeRetriever:
    def __init__(self):
        self.store = ChromaKnowledgeStore()

    def retrieve(self, query: str) -> list[dict]:
        return self.store.query(query)


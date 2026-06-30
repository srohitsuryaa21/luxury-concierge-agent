from __future__ import annotations

import hashlib
from pathlib import Path

from lca.config import get_settings


class LocalKnowledgeRetriever:
    """Small dependency-light retriever for offline development and tests.

    Chroma ingestion is provided separately. This lexical retriever keeps the app useful
    before dependencies are installed or API keys are configured.
    """

    def __init__(self, kb_dir: Path | None = None, k: int | None = None):
        settings = get_settings()
        self.kb_dir = kb_dir or settings.kb_dir
        self.k = k or settings.retrieval_k
        self.documents = self._load_documents()

    def _load_documents(self) -> list[dict]:
        docs = []
        if not self.kb_dir.exists():
            return docs
        for path in sorted(self.kb_dir.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            docs.append(
                {
                    "id": hashlib.sha1(str(path).encode()).hexdigest()[:12],
                    "source": str(path),
                    "text": text,
                    "terms": set(text.lower().replace("-", " ").split()),
                }
            )
        return docs

    def retrieve(self, query: str) -> list[dict]:
        query_terms = set(query.lower().replace("-", " ").split())
        ranked = []
        for doc in self.documents:
            score = len(query_terms & doc["terms"])
            if score:
                ranked.append((score, doc))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [
            {"source": doc["source"], "content": doc["text"][:1400], "score": score}
            for score, doc in ranked[: self.k]
        ]


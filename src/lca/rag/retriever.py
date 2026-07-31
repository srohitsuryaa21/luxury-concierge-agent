from __future__ import annotations

import math
import re

from lca.config import get_settings
from lca.data import get_repository

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "for", "with", "without", "to", "of",
    "in", "on", "at", "is", "are", "was", "were", "be", "been", "being", "it", "its", "this",
    "that", "these", "those", "as", "by", "from", "into", "about", "over", "under", "not", "no",
    "so", "such", "than", "too", "very", "can", "will", "would", "should", "could", "they",
    "them", "their", "he", "she", "his", "her", "we", "our", "you", "your", "i", "my", "me",
    "us", "do", "does", "did", "has", "have", "had", "just", "also", "more", "most", "want",
    "wants", "client",
}

_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return [
        term
        for term in _TOKEN_PATTERN.findall(text.lower())
        if term not in STOPWORDS and len(term) > 1
    ]


class LocalKnowledgeRetriever:
    """Lexical TF-IDF retriever over the knowledge table.

    Knowledge lives in the database as one row per passage rather than as
    markdown documents, so retrieval returns a focused passage instead of a
    multi-topic document. The curated keyword column is indexed alongside the
    prose, which lets a passage be found by vocabulary a client would use even
    when the passage itself does not contain that word.
    """

    def __init__(self, k: int | None = None):
        settings = get_settings()
        self.k = k or settings.retrieval_k
        self.documents = self._load_documents()
        self._idf = self._compute_idf()

    def _load_documents(self) -> list[dict]:
        docs = []
        for row in get_repository().knowledge():
            # Keywords are weighted by inclusion, not by a multiplier: they are
            # search vocabulary, not additional content.
            tokens = _tokenize(f"{row['title']} {row['content']} {row['keywords']}")
            term_counts: dict[str, int] = {}
            for term in tokens:
                term_counts[term] = term_counts.get(term, 0) + 1
            docs.append(
                {
                    "source": row["title"],
                    "category": row["category"],
                    "text": row["content"],
                    "term_counts": term_counts,
                    "length": len(tokens) or 1,
                }
            )
        return docs

    def _compute_idf(self) -> dict[str, float]:
        doc_freq: dict[str, int] = {}
        for doc in self.documents:
            for term in doc["term_counts"]:
                doc_freq[term] = doc_freq.get(term, 0) + 1
        n_docs = max(len(self.documents), 1)
        return {term: math.log((1 + n_docs) / (1 + df)) + 1 for term, df in doc_freq.items()}

    def retrieve(self, query: str) -> list[dict]:
        query_terms = _tokenize(query)
        if not query_terms:
            return []
        scored = []
        for doc in self.documents:
            score = 0.0
            for term in query_terms:
                tf = doc["term_counts"].get(term, 0)
                if tf:
                    score += (tf / doc["length"]) * self._idf.get(term, 0.0)
            if score > 0:
                scored.append((score, doc))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            {
                "source": doc["source"],
                "category": doc["category"],
                "content": doc["text"],
                "score": round(score, 4),
            }
            for score, doc in scored[: self.k]
        ]

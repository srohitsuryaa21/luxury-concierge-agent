from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LCA_", extra="ignore")

    # grok | openai. Any other value means "no model": the agent then runs on
    # its deterministic fallbacks and reports the failure rather than hiding it.
    model_provider: str = Field(default="grok")
    openai_model: str = Field(default="gpt-4o-mini")
    # Most hosted providers expose an OpenAI-compatible chat endpoint, so the
    # whole integration is a base URL, a model id and a key. Switching provider
    # is configuration, not code - see LLM_API_KEY resolution in llm.py.
    llm_base_url: str = Field(default="https://api.x.ai/v1")
    llm_model: str = Field(default="grok-3-mini")
    llm_timeout_seconds: int = Field(default=60)
    db_path: Path = Field(default=Path("data/catalog.db"))
    # Separate file on purpose: catalog.db is dropped and reseeded on rebuild,
    # and conversations are the only data here that cannot be regenerated.
    conversations_db_path: Path = Field(default=Path("data/conversations.db"))
    chroma_dir: Path = Field(default=Path(".chroma"))
    collection_name: str = Field(default="lca_knowledge")
    retrieval_k: int = Field(default=4)
    retriever_backend: str = Field(default="lexical")
    # "local" runs an on-device ONNX model and needs no API key. xAI has no
    # embeddings endpoint, so Grok cannot serve this and local stays the default.
    embedding_backend: str = Field(default="local")
    embedding_model: str = Field(default="text-embedding-3-small")


@lru_cache
def get_settings() -> Settings:
    return Settings()

from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LCA_", extra="ignore")

    model_provider: str = Field(default="mock")
    openai_model: str = Field(default="gpt-4o-mini")
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="llama3.1:8b")
    ollama_timeout_seconds: int = Field(default=90)
    chroma_dir: Path = Field(default=Path(".chroma"))
    collection_name: str = Field(default="lca_knowledge")
    kb_dir: Path = Field(default=Path("kb"))
    retrieval_k: int = Field(default=4)
    retriever_backend: str = Field(default="lexical")
    embedding_model: str = Field(default="text-embedding-3-small")


@lru_cache
def get_settings() -> Settings:
    return Settings()

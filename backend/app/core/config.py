"""Application settings loaded from environment variables.

Other leads: add new settings here as needed (e.g. API keys for the
Ask Ekiti / RAG pipeline) rather than reading os.environ directly
elsewhere in the app.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central app configuration.

    Values are read from environment variables (or a local .env file).
    Defaults keep the app runnable out of the box with zero setup.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "EKITI@30 DIGITAL API"

    # SQLite by default so nobody is blocked locally; set DATABASE_URL to a
    # Postgres URL (e.g. postgresql://user:pass@localhost:5432/ekiti30) in
    # .env or docker-compose to use Postgres instead.
    #
    # Note: the Ask Ekiti knowledge base (app/models/knowledge.py) uses a
    # pgvector column for embeddings, which requires Postgres with the
    # pgvector extension (see docker-compose.yml). Running locally against
    # the SQLite default means vector search won't work — that's expected;
    # switch to the Dockerized Postgres to use it.
    DATABASE_URL: str = "sqlite:///./dev.db"

    # Comma-separated list of allowed CORS origins for the frontend, e.g.
    # "http://localhost:3000,https://staging.example.com". Use
    # `cors_origins` (below) to get this parsed into a list.
    FRONTEND_ORIGIN: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        """FRONTEND_ORIGIN split on commas, with whitespace stripped."""
        return [origin.strip() for origin in self.FRONTEND_ORIGIN.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

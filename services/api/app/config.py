from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    database_url: str = "sqlite:///./caregrove.db"
    jwt_secret: str = "dev-only-change-me"
    jwt_days: int = 30
    frontend_url: str = "http://localhost:3000"
    render_external_url: str = ""
    monthly_price_usd: str = ""
    allow_demo_payments: bool = True

    @property
    def public_origin(self) -> str:
        return (self.render_external_url or self.frontend_url).rstrip("/")

    @property
    def sqlalchemy_url(self) -> str:
        url = self.database_url
        if url.startswith("postgres://"):
            return "postgresql+psycopg://" + url[len("postgres://") :]
        if url.startswith("postgresql://") and "+psycopg" not in url:
            return "postgresql+psycopg://" + url[len("postgresql://") :]
        return url

    @property
    def price_set(self) -> bool:
        raw = (self.monthly_price_usd or "").strip()
        if not raw:
            return False
        try:
            return float(raw) > 0
        except ValueError:
            return False


@lru_cache
def get_settings() -> Settings:
    return Settings()

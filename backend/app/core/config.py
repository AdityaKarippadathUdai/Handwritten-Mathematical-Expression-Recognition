from typing import Any, List, Optional
from pydantic import BeforeValidator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated
from sqlalchemy.engine import make_url

def parse_cors(v: Any) -> List[str]:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list):
        return v
    raise ValueError(v)


def parse_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        normalized = v.strip().lower()
        if normalized in {"1", "true", "yes", "on", "debug", "development"}:
            return True
        if normalized in {"0", "false", "no", "off", "release", "production"}:
            return False
    return bool(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local", ".env.development"),
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=True,
    )
    
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Handwritten Mathematical Expression Recognition"
    
    # CORS Origins: can be set as comma-separated values or JSON array
    BACKEND_CORS_ORIGINS: Annotated[
        List[str], BeforeValidator(parse_cors)
    ] = Field(default=["http://localhost", "http://localhost:3000", "http://localhost:5173"])

    DATABASE_URL: Optional[str] = None
    DATABASE_DRIVER: str = "postgresql+psycopg2"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "hmer"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres"
    APP_RUNTIME: str = "local"
    PIX2TEX_CACHE_DIR: str = "/app/.cache/pix2tex"
    YOLO_MODEL_PATH: str = "ml_models/yolo/best.pt"
    
    ENVIRONMENT: str = "development"
    DEBUG: Annotated[bool, BeforeValidator(parse_bool)] = False

    @property
    def effective_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL

        host = "db" if self.APP_RUNTIME.lower() in {"docker", "compose", "container"} else self.DATABASE_HOST
        return (
            f"{self.DATABASE_DRIVER}://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{host}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    @property
    def safe_database_url(self) -> str:
        return str(make_url(self.effective_database_url).render_as_string(hide_password=True))

settings = Settings()


from typing import Any, List
from pydantic import BeforeValidator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated

def parse_cors(v: Any) -> List[str]:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list):
        return v
    raise ValueError(v)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
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

    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/hmer"
    PIX2TEX_CACHE_DIR: str = "/app/.cache/pix2tex"
    YOLO_MODEL_PATH: str = "ml_models/yolo/best.pt"
    
    ENVIRONMENT: str = "production"
    DEBUG: bool = False

settings = Settings()


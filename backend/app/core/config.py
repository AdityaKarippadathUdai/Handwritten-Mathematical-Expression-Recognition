from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Handwritten Mathematical Expression Recognition"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost", "http://localhost:3000", "http://localhost:5173"]

    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/hmer"
    YOLO_MODEL_PATH: str = "ml_models/yolo/best.pt"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

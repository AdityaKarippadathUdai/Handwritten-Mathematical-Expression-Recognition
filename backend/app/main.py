import logging
from contextlib import asynccontextmanager
from typing import Any, Dict
from pathlib import Path
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from app.api import deps
from app.api.v1.endpoints import auth, expression, history, model, predict
from app.core.config import settings
from app.services.pix2tex_service import get_pix2tex_service

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("application_startup_begin")
    get_pix2tex_service().initialize()
    logger.info("application_startup_complete")
    yield
    logger.info("application_shutdown")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Set CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

@app.get("/", tags=["root"])
def read_root() -> Dict[str, str]:
    return {"status": "ok", "app": settings.PROJECT_NAME}

@app.get("/health", tags=["health"])
def health_check(db: Session = Depends(deps.get_db)) -> Dict[str, Any]:
    health_status: Dict[str, Any] = {
        "status": "healthy",
        "database": "untested",
        "model": get_pix2tex_service().health_status(),
        "environment": settings.ENVIRONMENT,
    }
    try:
        # Verify db connectivity by executing a basic select statement
        db.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = f"error: {str(e)}"

    if not health_status["model"]["loaded"]:
        health_status["status"] = "unhealthy"
    
    return health_status

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(predict.router, prefix=settings.API_V1_STR, tags=["prediction"])
app.include_router(history.router, prefix=f"{settings.API_V1_STR}/history", tags=["history"])
app.include_router(expression.router, prefix=f"{settings.API_V1_STR}/expressions", tags=["expressions"])
app.include_router(model.router, prefix=f"{settings.API_V1_STR}/model", tags=["model"])



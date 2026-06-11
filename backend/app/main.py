from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import auth, expression, model
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(expression.router, prefix=f"{settings.API_V1_STR}/expressions", tags=["expressions"])
app.include_router(model.router, prefix=f"{settings.API_V1_STR}/model", tags=["model"])

@app.get("/")
def read_root():
    return {"status": "ok", "app": settings.PROJECT_NAME}

from typing import Any, Dict

from fastapi import APIRouter

from app.services.pix2tex_service import get_pix2tex_service

router = APIRouter()


@router.get("/status")
def get_model_status() -> Dict[str, Any]:
    return get_pix2tex_service().health_status()

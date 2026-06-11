from fastapi import APIRouter
from app.services.yolo_service import YoloService

router = APIRouter()

@router.get("/status")
def get_model_status():
    yolo = YoloService()
    return {"loaded": yolo.is_model_loaded(), "config": yolo.get_config()}

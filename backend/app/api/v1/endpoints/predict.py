import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.prediction import PredictionResult
from app.services.predict_service import PredictService

router = APIRouter()
logger = logging.getLogger(__name__)

def get_predict_service(db: Session = Depends(deps.get_db)) -> PredictService:
    return PredictService(db=db)

@router.post("/predict", response_model=PredictionResult)
async def predict_expression(
    image: UploadFile = File(..., description="The handwritten mathematical expression image file (JPG, PNG, WEBP)"),
    service: PredictService = Depends(get_predict_service)
) -> PredictionResult:
    """
    Upload a handwritten equation image. The endpoint validates format and sizes,
    preprocesses it for Pix2Tex, runs LaTeX-OCR inference, saves history, and
    returns render-ready LaTeX with timing metadata.
    """
    try:
        return await service.process_prediction(image)
    except HTTPException as exc:
        logger.exception("predict_endpoint_http_exception", extra={"status_code": exc.status_code})
        if exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE and isinstance(exc.detail, dict):
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
        raise

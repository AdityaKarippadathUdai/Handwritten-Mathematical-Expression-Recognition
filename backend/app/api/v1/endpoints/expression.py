import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.prediction import PredictionResult
from app.services.predict_service import PredictService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/recognize", response_model=PredictionResult)
async def recognize_expression(
    image: UploadFile = File(..., description="Handwritten mathematical expression image"),
    db: Session = Depends(deps.get_db),
) -> PredictionResult:
    service = PredictService(db=db)
    try:
        return await service.process_prediction(image)
    except HTTPException as exc:
        logger.exception("expression_endpoint_http_exception", extra={"status_code": exc.status_code})
        if exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE and isinstance(exc.detail, dict):
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
        raise

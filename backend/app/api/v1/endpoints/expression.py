from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.prediction import PredictionResult
from app.services.predict_service import PredictService

router = APIRouter()


@router.post("/recognize", response_model=PredictionResult)
async def recognize_expression(
    image: UploadFile = File(..., description="Handwritten mathematical expression image"),
    db: Session = Depends(deps.get_db),
) -> PredictionResult:
    service = PredictService(db=db)
    return await service.process_prediction(image)

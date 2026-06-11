from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.prediction import PredictionResult
from app.services.predict_service import PredictService

router = APIRouter()

def get_predict_service(db: Session = Depends(deps.get_db)) -> PredictService:
    return PredictService(db=db)

@router.post("/predict", response_model=PredictionResult)
async def predict_expression(
    image: UploadFile = File(..., description="The handwritten mathematical expression image file (JPG, PNG, WEBP)"),
    service: PredictService = Depends(get_predict_service)
) -> PredictionResult:
    """
    Upload a handwritten equation image. The endpoint validates format and sizes,
    saves the image, identifies mathematical symbol components using YOLOv11, 
    and returns a structured LaTeX mathematical expression.
    """
    return await service.process_prediction(image)

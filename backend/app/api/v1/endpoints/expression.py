from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.api import deps
from app.services.expression_service import ExpressionService

router = APIRouter()

@router.post("/recognize")
async def recognize_expression(
    image: UploadFile = File(...),
    db: Session = Depends(deps.get_db)
):
    # Call service to preprocess, detect via YOLO and parse expressions
    service = ExpressionService(db)
    result = await service.process_handwritten_image(image)
    return result

from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.services.yolo_service import YoloService
from app.utils.latex_parser import LatexParser
from app.utils.image_processing import preprocess_image
from app.crud.crud_expression import crud_expression
from app.schemas.expression import ExpressionCreate

class ExpressionService:
    def __init__(self, db: Session):
        self.db = db
        self.yolo_service = YoloService()
        self.latex_parser = LatexParser()

    async def process_handwritten_image(self, upload_file: UploadFile):
        # 1. Read file and preprocess image
        image_bytes = await upload_file.read()
        processed_image = preprocess_image(image_bytes)

        # 2. Run YOLOv11 inference to get symbols and boxes
        boxes, classes = self.yolo_service.detect_symbols(processed_image)

        # 3. Parse geometric coordinates and symbols into LaTeX
        latex_str = self.latex_parser.generate_latex(boxes, classes)

        # 4. Save to db
        db_obj = ExpressionCreate(raw_image_path=f"uploads/{upload_file.filename}", latex_result=latex_str)
        crud_expression.create(self.db, obj_in=db_obj)

        return {"latex": latex_str, "symbols_detected": len(boxes)}

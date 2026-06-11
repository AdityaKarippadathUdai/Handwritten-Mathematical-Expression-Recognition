from pydantic import BaseModel
from datetime import datetime

class ExpressionBase(BaseModel):
    latex_result: str

class ExpressionCreate(ExpressionBase):
    raw_image_path: str

class Expression(ExpressionBase):
    id: int
    raw_image_path: str
    created_at: datetime

    class Config:
        from_attributes = True

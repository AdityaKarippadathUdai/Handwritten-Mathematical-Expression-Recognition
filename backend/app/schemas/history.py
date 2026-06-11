from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class EquationHistoryBase(BaseModel):
    image_path: str = Field(..., description="Path or URL for the uploaded prediction image")
    latex_output: str = Field(..., description="Generated LaTeX output")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Average prediction confidence")


class EquationHistoryCreate(EquationHistoryBase):
    pass


class EquationHistoryItem(EquationHistoryBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class EquationHistoryPage(BaseModel):
    items: List[EquationHistoryItem]
    total: int
    page: int
    page_size: int
    total_pages: int

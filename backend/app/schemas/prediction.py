from pydantic import BaseModel, Field
from typing import List

class PredictionResult(BaseModel):
    """
    PredictionResult validates the math formula prediction outputs.
    Follows Pydantic v2 schema structures.
    """
    latex: str = Field(..., description="The parsed mathematical LaTeX string representation")
    confidence: float = Field(..., description="YOLOv11 model confidence score (between 0.0 and 1.0)", ge=0.0, le=1.0)
    symbols: List[str] = Field(..., description="List of individual mathematical glyph symbols identified")

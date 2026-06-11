from pydantic import BaseModel, Field

class PredictionResult(BaseModel):
    """
    PredictionResult validates the math formula prediction outputs.
    Follows Pydantic v2 schema structures.
    """
    latex: str = Field(..., description="The parsed mathematical LaTeX string representation")
    confidence: float = Field(..., description="YOLOv11 model confidence score (between 0.0 and 1.0)", ge=0.0, le=1.0)
    symbols_detected: int = Field(..., description="Number of mathematical glyph symbols identified", ge=0)
    processing_time_ms: int = Field(..., description="Total OCR pipeline execution time in milliseconds", ge=0)

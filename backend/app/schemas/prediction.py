from datetime import datetime

from pydantic import BaseModel, Field

class PredictionResult(BaseModel):
    """
    Response returned by the Pix2Tex handwritten math OCR workflow.
    """
    prediction_id: str = Field(..., description="Unique identifier for this prediction request")
    image_path: str = Field(..., description="Path to the stored uploaded image")
    latex: str = Field(..., description="Pix2Tex generated LaTeX string")
    confidence: float = Field(..., description="OCR confidence value or documented placeholder", ge=0.0, le=1.0)
    confidence_source: str = Field(..., description="How confidence was produced")
    processing_time_ms: int = Field(..., description="Total OCR pipeline execution time in milliseconds", ge=0)
    preprocessing_time_ms: int = Field(..., description="Image preprocessing execution time in milliseconds", ge=0)
    ocr_time_ms: int = Field(..., description="Pix2Tex inference execution time in milliseconds", ge=0)
    created_at: datetime = Field(..., description="Prediction timestamp in UTC")

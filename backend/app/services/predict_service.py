import inspect
import logging
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional, Protocol

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.crud.crud_history import crud_history
from app.schemas.history import EquationHistoryCreate
from app.schemas.prediction import PredictionResult
from app.services.image_preprocessing import ImagePreprocessingService
from app.services.pix2tex_service import (
    Pix2TexInputError,
    Pix2TexModelError,
    Pix2TexOCRService,
    get_pix2tex_service,
)

logger = logging.getLogger(__name__)


class Pix2TexPreprocessor(Protocol):
    def preprocess_for_pix2tex(self, image_source: bytes, **kwargs: Any) -> Any:
        ...


class PredictService:
    """
    Coordinates the production OCR prediction pipeline:
    upload bytes -> validation -> Pix2Tex-compatible preprocessing -> Pix2Tex OCR
    -> history persistence -> API response.
    """

    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    allowed_content_types = {"image/jpeg", "image/png", "image/webp"}
    max_file_size = 10 * 1024 * 1024

    def __init__(
        self,
        preprocessor: Optional[Pix2TexPreprocessor] = None,
        ocr_service: Optional[Pix2TexOCRService] = None,
        db: Optional[Session] = None,
        upload_dir: str = "uploads/predictions",
    ) -> None:
        self.preprocessor = preprocessor or ImagePreprocessingService()
        self.ocr_service = ocr_service or get_pix2tex_service()
        self.db = db
        self.upload_dir = Path(upload_dir)

    async def process_prediction(self, file: UploadFile) -> PredictionResult:
        total_start = time.perf_counter()
        prediction_id = str(uuid.uuid4())
        created_at = datetime.now(UTC)

        logger.info(
            "prediction_request_received",
            extra={"prediction_id": prediction_id, "upload_filename": file.filename},
        )

        self._validate_upload(file)
        image_bytes = await self._read_upload(file)

        try:
            image_path = self._save_upload(image_bytes, file.filename or "prediction.png", prediction_id)

            preprocessing_start = time.perf_counter()
            processed_image = await self._maybe_await(
                self.preprocessor.preprocess_for_pix2tex(image_bytes)
            )
            preprocessing_time_ms = self._elapsed_ms(preprocessing_start)

            ocr_result = await self._maybe_await(self.ocr_service.predict(processed_image))

            result = PredictionResult(
                prediction_id=prediction_id,
                image_path=image_path,
                latex=ocr_result.latex,
                confidence=ocr_result.confidence,
                confidence_source=ocr_result.confidence_source,
                processing_time_ms=self._elapsed_ms(total_start),
                preprocessing_time_ms=preprocessing_time_ms,
                ocr_time_ms=ocr_result.ocr_time_ms,
                created_at=created_at,
            )
            self._record_history(image_path=image_path, result=result)
            logger.info(
                "prediction_request_completed",
                extra={
                    "prediction_id": prediction_id,
                    "processing_time_ms": result.processing_time_ms,
                    "preprocessing_time_ms": preprocessing_time_ms,
                    "ocr_time_ms": ocr_result.ocr_time_ms,
                },
            )
            return result
        except HTTPException:
            raise
        except Pix2TexInputError as exc:
            logger.warning("prediction_invalid_image", extra={"prediction_id": prediction_id, "error": str(exc)})
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc
        except Pix2TexModelError as exc:
            logger.exception("prediction_ocr_failed", extra={"prediction_id": prediction_id})
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc
        except ValueError as exc:
            logger.warning("prediction_validation_failed", extra={"prediction_id": prediction_id, "error": str(exc)})
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid image data: {exc}",
            ) from exc
        except Exception as exc:
            logger.exception("prediction_pipeline_failed", extra={"prediction_id": prediction_id})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Prediction pipeline failed. Please try again later.",
            ) from exc

    def _validate_upload(self, file: UploadFile) -> None:
        filename = file.filename or ""
        extension = self._extension(filename)

        if extension not in self.allowed_extensions:
            allowed = ", ".join(sorted(self.allowed_extensions))
            logger.warning("upload_extension_rejected", extra={"upload_filename": filename, "extension": extension})
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '{extension or 'unknown'}'. Allowed: {allowed}.",
            )

        if file.content_type and file.content_type not in self.allowed_content_types:
            logger.warning("upload_mime_rejected", extra={"upload_filename": filename, "content_type": file.content_type})
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported image MIME type. Allowed: image/jpeg, image/png, image/webp.",
            )

        if file.size is not None and file.size > self.max_file_size:
            logger.warning("upload_size_rejected", extra={"upload_filename": filename, "size": file.size})
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds the 10 MB maximum limit.",
            )

    async def _read_upload(self, file: UploadFile) -> bytes:
        try:
            await file.seek(0)
            image_bytes = await file.read()
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unable to read uploaded image: {exc}",
            ) from exc

        if not image_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded image is empty.",
            )

        if len(image_bytes) > self.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds the 10 MB maximum limit.",
            )

        return image_bytes

    def _elapsed_ms(self, start_time: float) -> int:
        return int(round((time.perf_counter() - start_time) * 1000))

    def _extension(self, filename: str) -> str:
        dot_index = filename.rfind(".")
        if dot_index == -1:
            return ""
        return filename[dot_index:].lower()

    def _save_upload(self, image_bytes: bytes, filename: str, prediction_id: str) -> str:
        extension = self._extension(filename) or ".png"
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        stored_name = f"{prediction_id}{extension}"
        stored_path = self.upload_dir / stored_name
        stored_path.write_bytes(image_bytes)
        return f"/uploads/predictions/{stored_name}"

    def _record_history(self, *, image_path: str, result: PredictionResult) -> None:
        if self.db is None:
            return

        try:
            crud_history.create(
                self.db,
                obj_in=EquationHistoryCreate(
                    image_path=image_path,
                    latex_output=result.latex,
                    confidence=result.confidence,
                ),
            )
            logger.info("prediction_history_saved", extra={"prediction_id": result.prediction_id})
        except Exception:
            logger.exception("prediction_history_save_failed", extra={"prediction_id": result.prediction_id})
            raise

    async def _maybe_await(self, value: Any) -> Any:
        if inspect.isawaitable(value):
            return await value
        return value

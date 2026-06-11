import inspect
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Protocol, Sequence

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.crud.crud_history import crud_history
from app.schemas.prediction import PredictionResult
from app.schemas.history import EquationHistoryCreate
from app.services.expression_parser import ExpressionParser
from app.services.image_preprocessing import ImagePreprocessingService
from app.services.latex_generator import LatexGenerator
from app.services.symbol_detection import SymbolDetectionService


class ImagePreprocessor(Protocol):
    def preprocess(self, image_source: bytes, **kwargs: Any) -> Any:
        ...


class SymbolDetector(Protocol):
    def detect(self, image: Any, confidence_threshold: float = 0.25) -> List[Dict[str, Any]]:
        ...


class ExpressionParserProtocol(Protocol):
    def parse(self, symbols_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        ...


class LatexGeneratorProtocol(Protocol):
    def generate(self, ast: Optional[Dict[str, Any]]) -> str:
        ...


class PredictionPipelineError(RuntimeError):
    """Raised when OCR pipeline execution fails after request validation."""


class PredictService:
    """
    Coordinates the complete OCR prediction pipeline:
    upload bytes -> preprocessing -> YOLO detection -> expression parsing -> LaTeX generation.
    """

    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    max_file_size = 10 * 1024 * 1024

    def __init__(
        self,
        preprocessor: Optional[ImagePreprocessor] = None,
        detector: Optional[Any] = None,
        parser: Optional[ExpressionParserProtocol] = None,
        latex_generator: Optional[LatexGeneratorProtocol] = None,
        db: Optional[Session] = None,
        confidence_threshold: float = 0.25,
        upload_dir: str = "uploads/predictions",
    ) -> None:
        self.preprocessor = preprocessor or ImagePreprocessingService()
        self.detector = detector or SymbolDetectionService()
        self.parser = parser or ExpressionParser()
        self.latex_generator = latex_generator or LatexGenerator()
        self.db = db
        self.confidence_threshold = confidence_threshold
        self.upload_dir = Path(upload_dir)

    async def process_prediction(self, file: UploadFile) -> PredictionResult:
        start_time = time.perf_counter()

        self._validate_upload(file)
        image_bytes = await self._read_upload(file)

        try:
            image_path = self._save_upload(image_bytes, file.filename or "prediction.png")
            processed_image = await self._maybe_await(self.preprocessor.preprocess(image_bytes))
            detections = await self._detect_symbols(processed_image)
            ast = await self._maybe_await(self.parser.parse(detections))
            latex = await self._maybe_await(self.latex_generator.generate(ast))

            if detections and not latex:
                raise PredictionPipelineError("Detected symbols could not be converted to LaTeX.")

            result = PredictionResult(
                latex=latex,
                confidence=self._calculate_confidence(detections),
                symbols_detected=len(detections),
                processing_time_ms=self._elapsed_ms(start_time),
            )
            self._record_history(image_path=image_path, result=result)
            return result
        except HTTPException:
            raise
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid image or expression data: {exc}",
            ) from exc
        except PredictionPipelineError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Prediction pipeline failed: {exc}",
            ) from exc

    def _validate_upload(self, file: UploadFile) -> None:
        filename = file.filename or ""
        extension = self._extension(filename)

        if extension not in self.allowed_extensions:
            allowed = ", ".join(sorted(self.allowed_extensions))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '{extension or 'unknown'}'. Allowed: {allowed}.",
            )

        if file.size is not None and file.size > self.max_file_size:
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

    async def _detect_symbols(self, processed_image: Any) -> List[Dict[str, Any]]:
        detector_fn = getattr(self.detector, "detect", None)
        if detector_fn is not None:
            detections = await self._call_detector(detector_fn, processed_image)
            return self._normalize_detections(detections)

        legacy_detector_fn = getattr(self.detector, "detect_symbols", None)
        if legacy_detector_fn is not None:
            detections = await self._maybe_await(legacy_detector_fn(processed_image))
            return self._normalize_detections(detections)

        raise PredictionPipelineError("Detector must provide detect() or detect_symbols().")

    async def _call_detector(self, detector_fn: Any, processed_image: Any) -> Any:
        try:
            return await self._maybe_await(
                detector_fn(processed_image, confidence_threshold=self.confidence_threshold)
            )
        except TypeError as exc:
            if "confidence_threshold" not in str(exc):
                raise
            return await self._maybe_await(detector_fn(processed_image))

    def _normalize_detections(self, detections: Any) -> List[Dict[str, Any]]:
        if detections is None:
            return []

        if self._is_legacy_detection_tuple(detections):
            boxes, classes = detections
            return [
                {
                    "symbol": str(symbol),
                    "confidence": 1.0,
                    "bbox": self._bbox_to_list(box),
                }
                for box, symbol in zip(boxes, classes)
            ]

        normalized = []
        for detection in detections:
            if not isinstance(detection, dict):
                raise PredictionPipelineError("Detector returned an unsupported detection item.")

            symbol = detection.get("symbol")
            bbox = detection.get("bbox")
            if symbol is None or bbox is None:
                raise PredictionPipelineError("Each detection must include symbol and bbox.")

            normalized.append(
                {
                    "symbol": str(symbol),
                    "confidence": float(detection.get("confidence", 1.0)),
                    "bbox": self._bbox_to_list(bbox),
                }
            )

        return normalized

    def _calculate_confidence(self, detections: Sequence[Dict[str, Any]]) -> float:
        if not detections:
            return 0.0

        confidence_sum = sum(float(detection.get("confidence", 0.0)) for detection in detections)
        return round(confidence_sum / len(detections), 4)

    def _elapsed_ms(self, start_time: float) -> int:
        return int(round((time.perf_counter() - start_time) * 1000))

    def _extension(self, filename: str) -> str:
        dot_index = filename.rfind(".")
        if dot_index == -1:
            return ""
        return filename[dot_index:].lower()

    def _save_upload(self, image_bytes: bytes, filename: str) -> str:
        extension = self._extension(filename) or ".png"
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        stored_name = f"{uuid.uuid4()}{extension}"
        stored_path = self.upload_dir / stored_name
        stored_path.write_bytes(image_bytes)
        return f"/uploads/predictions/{stored_name}"

    def _record_history(self, *, image_path: str, result: PredictionResult) -> None:
        if self.db is None:
            return

        crud_history.create(
            self.db,
            obj_in=EquationHistoryCreate(
                image_path=image_path,
                latex_output=result.latex,
                confidence=result.confidence,
            ),
        )

    def _bbox_to_list(self, bbox: Iterable[Any]) -> List[float]:
        values = list(bbox)
        if len(values) != 4:
            raise PredictionPipelineError("Detection bbox must contain four coordinates.")
        return [float(value) for value in values]

    def _is_legacy_detection_tuple(self, detections: Any) -> bool:
        return (
            isinstance(detections, tuple)
            and len(detections) == 2
            and not inspect.isawaitable(detections[0])
        )

    async def _maybe_await(self, value: Any) -> Any:
        if inspect.isawaitable(value):
            return await value
        return value

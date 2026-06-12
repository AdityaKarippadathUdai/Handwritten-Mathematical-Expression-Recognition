import logging
import threading
import time
from dataclasses import dataclass
from typing import Any, Optional

from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)


class Pix2TexModelError(RuntimeError):
    """Raised when the Pix2Tex model cannot be initialized or used."""


class Pix2TexInputError(ValueError):
    """Raised when an image cannot be used for OCR inference."""


@dataclass(frozen=True)
class Pix2TexPrediction:
    latex: str
    confidence: float
    confidence_source: str
    ocr_time_ms: int


class Pix2TexOCRService:
    """
    Thread-safe singleton wrapper around Pix2Tex/LaTeX-OCR.

    Pix2Tex does not expose a stable per-prediction confidence score. Until a
    calibrated confidence model is added, successful non-empty OCR responses use
    a neutral placeholder confidence so downstream history/API contracts remain
    compatible with older records.
    """

    _instance: Optional["Pix2TexOCRService"] = None
    _instance_lock = threading.Lock()

    def __new__(cls) -> "Pix2TexOCRService":
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
                cls._instance._model = None
                cls._instance._load_error = None
                cls._instance._inference_lock = threading.Lock()
        return cls._instance

    def initialize(self) -> None:
        if self._initialized:
            return

        with self._instance_lock:
            if self._initialized:
                return

            logger.info("pix2tex_startup_begin")
            try:
                from pix2tex.cli import LatexOCR

                self._model = LatexOCR()
                self._initialized = True
                self._load_error = None
                logger.info("pix2tex_startup_complete")
            except Exception as exc:
                self._model = None
                self._initialized = False
                self._load_error = str(exc)
                logger.exception("pix2tex_startup_failed")
                raise Pix2TexModelError(f"Pix2Tex model failed to load: {exc}") from exc

    @property
    def is_loaded(self) -> bool:
        return self._initialized and self._model is not None

    def health_status(self) -> dict[str, Any]:
        return {
            "engine": "pix2tex",
            "loaded": self.is_loaded,
            "load_error": self._load_error,
            "confidence": "placeholder_until_pix2tex_confidence_available",
        }

    def predict(self, image: Image.Image) -> Pix2TexPrediction:
        self.initialize()
        pil_image = self._validate_image(image)

        start_time = time.perf_counter()
        try:
            with self._inference_lock:
                latex = self._model(pil_image)  # type: ignore[misc]
        except Exception as exc:
            logger.exception("pix2tex_inference_failed")
            raise Pix2TexModelError(f"Pix2Tex inference failed: {exc}") from exc

        latex = str(latex or "").strip()
        if not latex:
            raise Pix2TexModelError("Pix2Tex returned an empty LaTeX result.")

        return Pix2TexPrediction(
            latex=latex,
            confidence=0.80,
            confidence_source="placeholder_success_default",
            ocr_time_ms=int(round((time.perf_counter() - start_time) * 1000)),
        )

    def _validate_image(self, image: Image.Image) -> Image.Image:
        if not isinstance(image, Image.Image):
            raise Pix2TexInputError("Pix2Tex OCR requires a PIL image.")

        try:
            image.load()
        except (OSError, UnidentifiedImageError) as exc:
            raise Pix2TexInputError("Uploaded image is malformed or corrupted.") from exc

        if image.width <= 0 or image.height <= 0:
            raise Pix2TexInputError("Uploaded image has invalid dimensions.")

        if image.mode not in {"RGB", "L"}:
            image = image.convert("RGB")

        return image


def get_pix2tex_service() -> Pix2TexOCRService:
    return Pix2TexOCRService()

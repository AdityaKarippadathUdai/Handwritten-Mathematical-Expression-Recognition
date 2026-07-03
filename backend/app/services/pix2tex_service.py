import logging
import os
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import numpy as np
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
                import pix2tex
                from pix2tex.cli import LatexOCR

                self._verify_pix2tex_files(Path(pix2tex.__file__).resolve().parent)
                self._model = LatexOCR()
                self._initialized = True
                self._load_error = None
                logger.info("pix2tex_startup_complete", extra=self._model_diagnostics())
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
        logger.info("pix2tex_inference_started")
        self.initialize()
        pil_image = self._validate_image(image)
        self._validate_image_content(pil_image)

        start_time = time.perf_counter()
        try:
            with self._inference_lock:
                latex = self._model(pil_image)  # type: ignore[misc]
        except Exception as exc:
            import traceback

            logger.error("========== PIX2TEX INFERENCE ERROR ==========")
            logger.error(traceback.format_exc())
            logger.exception("pix2tex_inference_failed")
            raise Pix2TexModelError(f"Pix2Tex inference failed: {exc}") from exc

        latex = str(latex or "").strip()
        if not latex:
            raise Pix2TexModelError("Pix2Tex returned an empty LaTeX result.")
        ocr_time_ms = int(round((time.perf_counter() - start_time) * 1000))
        logger.info(
            "pix2tex_inference_finished",
            extra={"latex": latex, "ocr_time_ms": ocr_time_ms},
        )

        return Pix2TexPrediction(
            latex=latex,
            confidence=0.80,
            confidence_source="placeholder_success_default",
            ocr_time_ms=ocr_time_ms,
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

        logger.info(
            "pix2tex_input_validated",
            extra={
                "image_type": type(image).__name__,
                "mode": image.mode,
                "size": image.size,
                "format": image.format,
            },
        )
        return image

    def _validate_image_content(self, image: Image.Image) -> None:
        gray = image.convert("L")
        pixels = np.asarray(gray)
        median = float(np.median(pixels))
        contrast = int(pixels.max()) - int(pixels.min())
        foreground_ratio = float(np.mean(np.abs(pixels.astype(np.int16) - median) > 10))

        logger.info(
            "pix2tex_input_content_checked",
            extra={
                "contrast": contrast,
                "foreground_ratio": round(foreground_ratio, 6),
                "dtype": str(pixels.dtype),
                "channels": 1,
            },
        )

        if contrast < 10 or foreground_ratio < 0.0005:
            raise Pix2TexInputError(
                "Uploaded image does not contain enough visible handwriting for OCR."
            )

    def _verify_pix2tex_files(self, package_dir: Path) -> None:
        model_dir = package_dir / "model"
        required_files = [
            model_dir / "checkpoints" / "weights.pth",
            model_dir / "checkpoints" / "image_resizer.pth",
            model_dir / "dataset" / "tokenizer.json",
            model_dir / "settings" / "config.yaml",
        ]
        missing = [str(path) for path in required_files if not path.exists()]

        logger.info(
            "pix2tex_cache_checked",
            extra={
                "pix2tex_model_dir": str(model_dir),
                "pix2tex_cache_dir": os.getenv("PIX2TEX_CACHE_DIR"),
                "huggingface_cache": os.getenv("HF_HOME") or os.getenv("HUGGINGFACE_HUB_CACHE"),
                "torch_cache": os.getenv("TORCH_HOME"),
                "missing_files": missing,
            },
        )

        if missing:
            raise Pix2TexModelError(
                "Pix2Tex required files are missing: " + ", ".join(missing)
            )

    def _model_diagnostics(self) -> dict[str, Any]:
        model = self._model
        args = getattr(model, "args", None)
        wrapped_model = getattr(model, "model", None)
        encoder = getattr(wrapped_model, "encoder", None)
        decoder = getattr(wrapped_model, "decoder", None)

        return {
            "model_class": type(model).__name__ if model is not None else None,
            "device": getattr(args, "device", None) if args is not None else None,
            "weights_location": getattr(args, "checkpoint", None) if args is not None else None,
            "cache_directory": os.getenv("PIX2TEX_CACHE_DIR"),
            "tokenizer_loaded": getattr(model, "tokenizer", None) is not None,
            "encoder_loaded": encoder is not None,
            "decoder_loaded": decoder is not None,
            "wrapped_model_class": type(wrapped_model).__name__ if wrapped_model is not None else None,
        }


def get_pix2tex_service() -> Pix2TexOCRService:
    return Pix2TexOCRService()

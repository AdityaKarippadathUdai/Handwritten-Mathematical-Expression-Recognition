import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from app.services.symbol_detection import SymbolDetectionService


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the Singleton before and after every test for full isolation."""
    SymbolDetectionService._instance = None
    yield
    SymbolDetectionService._instance = None


# ──────────────────────────────────────────────────────────────
# 1. Singleton
# ──────────────────────────────────────────────────────────────

def test_singleton_pattern():
    """Two calls to the constructor must return the exact same object."""
    with patch("app.services.symbol_detection.YOLO") as mock_yolo:
        service1 = SymbolDetectionService(model_path="dummy_path.pt")
        service2 = SymbolDetectionService(model_path="dummy_path.pt")

        assert service1 is service2
        mock_yolo.assert_called_once_with("dummy_path.pt")


# ──────────────────────────────────────────────────────────────
# 2. Device selection
# ──────────────────────────────────────────────────────────────

@patch("app.services.symbol_detection.torch.cuda.is_available")
@patch("app.services.symbol_detection.YOLO")
def test_device_gpu_loading(mock_yolo, mock_cuda_available):
    """When CUDA is available the model should be moved to the GPU."""
    mock_cuda_available.return_value = True

    mock_model_instance = MagicMock()
    mock_yolo.return_value = mock_model_instance

    service = SymbolDetectionService(model_path="dummy_path.pt")

    assert service.device == "cuda"
    mock_model_instance.to.assert_called_once_with("cuda")


@patch("app.services.symbol_detection.torch.cuda.is_available")
@patch("app.services.symbol_detection.YOLO")
def test_device_cpu_fallback(mock_yolo, mock_cuda_available):
    """When CUDA is NOT available the model should stay on CPU."""
    mock_cuda_available.return_value = False

    mock_model_instance = MagicMock()
    mock_yolo.return_value = mock_model_instance

    service = SymbolDetectionService(model_path="dummy_path.pt")

    assert service.device == "cpu"
    # .to() should never be called; model already lives on CPU by default
    mock_model_instance.to.assert_not_called()


@patch("app.services.symbol_detection.torch.cuda.is_available")
@patch("app.services.symbol_detection.YOLO")
def test_device_gpu_failure_fallback(mock_yolo, mock_cuda_available):
    """If GPU transfer raises, the service must fall back to CPU gracefully."""
    mock_cuda_available.return_value = True

    mock_model_instance = MagicMock()
    mock_model_instance.to.side_effect = RuntimeError("CUDA Out of memory")
    mock_yolo.return_value = mock_model_instance

    service = SymbolDetectionService(model_path="dummy_path.pt")

    assert service.device == "cpu"
    mock_model_instance.to.assert_any_call("cuda")
    mock_model_instance.to.assert_any_call("cpu")


# ──────────────────────────────────────────────────────────────
# 3. Detection output format
# ──────────────────────────────────────────────────────────────

@patch("app.services.symbol_detection.YOLO")
def test_detect_formatting(mock_yolo):
    """detect() must return a list of dicts with 'symbol', 'confidence', 'bbox'."""
    mock_model_instance = MagicMock()
    mock_model_instance.names = {0: "(", 1: ")", 2: "x", 3: "+"}

    mock_box1 = MagicMock()
    mock_box1.xyxy = [np.array([10.0, 20.0, 50.0, 60.0])]
    mock_box1.conf  = [0.95]
    mock_box1.cls   = [2]   # "x"

    mock_box2 = MagicMock()
    mock_box2.xyxy = [np.array([70.0, 80.0, 100.0, 110.0])]
    mock_box2.conf  = [0.88]
    mock_box2.cls   = [0]   # "("

    mock_result = MagicMock()
    mock_result.boxes = [mock_box1, mock_box2]
    mock_model_instance.return_value = [mock_result]
    mock_yolo.return_value = mock_model_instance

    service = SymbolDetectionService(model_path="dummy_path.pt")
    dummy_image = np.zeros((100, 100), dtype=np.uint8)

    detections = service.detect(dummy_image, confidence_threshold=0.5)

    # Verify inference was called with the right kwargs
    mock_model_instance.assert_called_once()
    _, kwargs = mock_model_instance.call_args
    assert kwargs["device"] == service.device
    assert kwargs["conf"]   == 0.5

    # Verify output structure and values
    assert len(detections) == 2

    assert detections[0]["symbol"]     == "x"
    assert detections[0]["confidence"] == 0.95
    assert detections[0]["bbox"]       == [10.0, 20.0, 50.0, 60.0]

    assert detections[1]["symbol"]     == "("
    assert detections[1]["confidence"] == 0.88
    assert detections[1]["bbox"]       == [70.0, 80.0, 100.0, 110.0]


# ──────────────────────────────────────────────────────────────
# 4. Error handling
# ──────────────────────────────────────────────────────────────

@patch("app.services.symbol_detection.YOLO")
def test_detect_raises_when_model_not_loaded(mock_yolo):
    """RuntimeError must be raised when model weights failed to load."""
    mock_yolo.side_effect = Exception("Weights file corrupted")

    service = SymbolDetectionService(model_path="bad_path.pt")
    assert service.model is None

    with pytest.raises(RuntimeError, match="YOLO model is not loaded"):
        service.detect(np.zeros((100, 100), dtype=np.uint8))


# ──────────────────────────────────────────────────────────────
# 5. Image format handling
# ──────────────────────────────────────────────────────────────

@patch("app.services.symbol_detection.YOLO")
def test_detect_accepts_normalized_float_image(mock_yolo):
    """
    detect() must accept float32 [0.0-1.0] images (e.g. output of
    ImagePreprocessingService.preprocess()) and convert them to uint8
    before passing to the model.
    """
    mock_model_instance = MagicMock()
    mock_model_instance.names = {0: "pi"}
    mock_result = MagicMock()
    mock_result.boxes = []
    mock_model_instance.return_value = [mock_result]
    mock_yolo.return_value = mock_model_instance

    service = SymbolDetectionService(model_path="dummy_path.pt")

    # Normalized (H, W, 1) float32 — direct output of the preprocessing pipeline
    float_image = np.ones((640, 640, 1), dtype=np.float32) * 0.5
    detections = service.detect(float_image)

    assert isinstance(detections, list)

    passed_image = mock_model_instance.call_args[0][0]
    assert passed_image.dtype       == np.uint8
    assert passed_image.shape       == (640, 640, 3)
    # 0.5 * 255 rounds to 127
    assert int(passed_image[0, 0, 0]) == 127


@patch("app.services.symbol_detection.YOLO")
def test_detect_accepts_single_channel_2d_image(mock_yolo):
    """detect() must accept a (H, W) 2-D grayscale array and expand it to 3 channels."""
    mock_model_instance = MagicMock()
    mock_model_instance.names = {0: "sqrt"}
    mock_result = MagicMock()
    mock_result.boxes = []
    mock_model_instance.return_value = [mock_result]
    mock_yolo.return_value = mock_model_instance

    service = SymbolDetectionService(model_path="dummy_path.pt")

    gray_2d = np.zeros((320, 320), dtype=np.uint8)
    detections = service.detect(gray_2d)

    assert isinstance(detections, list)

    passed_image = mock_model_instance.call_args[0][0]
    assert passed_image.ndim        == 3
    assert passed_image.shape[2]    == 3
    assert passed_image.dtype       == np.uint8


@patch("app.services.symbol_detection.YOLO")
def test_detect_accepts_hwc1_image(mock_yolo):
    """detect() must accept a (H, W, 1) array and convert it to 3-channel."""
    mock_model_instance = MagicMock()
    mock_model_instance.names = {0: "inf"}
    mock_result = MagicMock()
    mock_result.boxes = []
    mock_model_instance.return_value = [mock_result]
    mock_yolo.return_value = mock_model_instance

    service = SymbolDetectionService(model_path="dummy_path.pt")

    hwc1_image = np.zeros((320, 320, 1), dtype=np.uint8)
    detections = service.detect(hwc1_image)

    assert isinstance(detections, list)

    passed_image = mock_model_instance.call_args[0][0]
    assert passed_image.shape == (320, 320, 3)


# ──────────────────────────────────────────────────────────────
# 6. Edge cases
# ──────────────────────────────────────────────────────────────

@patch("app.services.symbol_detection.YOLO")
def test_detect_empty_result(mock_yolo):
    """detect() must return an empty list when result.boxes is None."""
    mock_model_instance = MagicMock()
    mock_model_instance.names = {}
    mock_result = MagicMock()
    mock_result.boxes = None
    mock_model_instance.return_value = [mock_result]
    mock_yolo.return_value = mock_model_instance

    service = SymbolDetectionService(model_path="dummy_path.pt")
    detections = service.detect(np.zeros((100, 100), dtype=np.uint8), confidence_threshold=0.9)

    assert detections == []


@patch("app.services.symbol_detection.YOLO")
def test_detect_all_required_symbols_in_config_names(mock_yolo):
    """
    All symbols required by the task spec must be present as values in the
    class-name dict that mirrors config.yaml.
    """
    # Task-specified required symbols (√→sqrt, ∫→int, ∑→sum, π→pi, ∞→inf)
    required = {"(", ")", "[", "]", "{", "}", "sqrt", "int", "sum", "pi", "inf"}

    names = {
        19: "(", 20: ")", 21: "[", 22: "]", 23: "{", 24: "}",
        25: "sqrt", 26: "int", 27: "sum", 28: "pi", 29: "inf",
    }

    mock_model_instance = MagicMock()
    mock_model_instance.names = names
    mock_yolo.return_value = mock_model_instance

    SymbolDetectionService(model_path="dummy_path.pt")

    for symbol in required:
        assert symbol in names.values(), \
            f"Required symbol '{symbol}' is missing from the class-name map"


@patch("app.services.symbol_detection.YOLO")
def test_detect_unknown_class_id_uses_fallback_name(mock_yolo):
    """
    If the model returns a class ID not in the names dict the service must
    not crash — it falls back to 'class_<id>'.
    """
    mock_model_instance = MagicMock()
    mock_model_instance.names = {0: "x"}  # only class 0 is known

    mock_box = MagicMock()
    mock_box.xyxy = [np.array([0.0, 0.0, 10.0, 10.0])]
    mock_box.conf = [0.70]
    mock_box.cls  = [99]  # unknown class

    mock_result = MagicMock()
    mock_result.boxes = [mock_box]
    mock_model_instance.return_value = [mock_result]
    mock_yolo.return_value = mock_model_instance

    service = SymbolDetectionService(model_path="dummy_path.pt")
    detections = service.detect(np.zeros((100, 100), dtype=np.uint8))

    assert len(detections) == 1
    assert detections[0]["symbol"] == "class_99"
    assert detections[0]["confidence"] == pytest.approx(0.70)

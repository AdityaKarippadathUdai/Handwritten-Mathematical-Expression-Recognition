"""
Lightweight conftest that stubs out heavy third-party dependencies
(torch, ultralytics, fastapi, sqlalchemy, pydantic-settings, etc.)
so that the unit tests for image_preprocessing and symbol_detection
can be collected and run without those packages being installed
in the test environment.

pytest collects this file automatically when it lives at the root of
the test session (invoked with --rootdir=. from backend/).
"""
import sys
import types
from unittest.mock import MagicMock


def _make_stub(name: str) -> types.ModuleType:
    """Return a MagicMock-based module stub registered in sys.modules."""
    stub = types.ModuleType(name)
    stub.__spec__ = None  # type: ignore[assignment]
    # Module-level __getattr__ only takes the attribute name (no self)
    stub.__getattr__ = lambda item: MagicMock()  # type: ignore[assignment]
    sys.modules[name] = stub
    return stub


# ── Heavy ML dependencies ────────────────────────────────────────────────────

# torch — only cuda.is_available() is exercised; everything else is mocked.
torch_stub = _make_stub("torch")
torch_stub.cuda = MagicMock()
torch_stub.cuda.is_available = MagicMock(return_value=False)

_make_stub("ultralytics")
ultralytics_stub = sys.modules["ultralytics"]
ultralytics_stub.YOLO = MagicMock()

# ── App configuration ────────────────────────────────────────────────────────

app_stub         = _make_stub("app")
core_stub        = _make_stub("app.core")
config_stub      = _make_stub("app.core.config")
settings_mock    = MagicMock()
settings_mock.YOLO_MODEL_PATH = "ml_models/yolo/best.pt"
config_stub.settings = settings_mock

# ── Web framework stubs (only needed if conftest.py is also loaded) ──────────

for mod in (
    "fastapi",
    "fastapi.testclient",
    "sqlalchemy",
    "sqlalchemy.orm",
    "sqlalchemy.exc",
    "pydantic",
    "pydantic_settings",
    "app.main",
    "app.core.database",
    "app.api",
    "app.api.deps",
):
    _make_stub(mod)

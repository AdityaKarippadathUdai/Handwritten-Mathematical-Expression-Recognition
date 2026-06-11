"""
sitecustomize.py — executed by Python at every interpreter startup.

Stubs out packages that are NOT installed in the lightweight test venv so that
  • the service modules (symbol_detection, image_preprocessing) can be imported
  • the conftest fixtures can be collected by pytest

Only stubs if the real package is absent; a proper install always takes priority.
"""
import sys
import types
from unittest.mock import MagicMock


def _stub(dotted_name: str, **attrs) -> types.ModuleType:
    """Register a thin stub for `dotted_name` (and bare parent names) in sys.modules."""
    # Ensure all parent packages exist
    parts = dotted_name.split(".")
    for depth in range(1, len(parts)):
        parent = ".".join(parts[:depth])
        if parent not in sys.modules:
            p = types.ModuleType(parent)
            p.__spec__  = None          # type: ignore[assignment]
            p.__path__  = []            # mark as package
            p.__getattr__ = lambda n: MagicMock()  # type: ignore[assignment]
            sys.modules[parent] = p

    # The leaf module
    mod = types.ModuleType(dotted_name)
    mod.__spec__ = None                 # type: ignore[assignment]
    mod.__getattr__ = lambda n: MagicMock()  # type: ignore[assignment]
    for k, v in attrs.items():
        setattr(mod, k, v)
    sys.modules[dotted_name] = mod

    # Attach as attribute on the direct parent
    if len(parts) > 1:
        parent_mod = sys.modules.get(".".join(parts[:-1]))
        if parent_mod is not None:
            setattr(parent_mod, parts[-1], mod)

    return mod


import importlib.util

# ── torch ─────────────────────────────────────────────────────────────────────
if importlib.util.find_spec("torch") is None:
    _cuda = MagicMock()
    _cuda.is_available = MagicMock(return_value=False)
    _stub("torch", cuda=_cuda)

# ── ultralytics ───────────────────────────────────────────────────────────────
if importlib.util.find_spec("ultralytics") is None:
    _stub("ultralytics", YOLO=MagicMock())

# ── pydantic / pydantic_settings (used by app.core.config) ───────────────────
if importlib.util.find_spec("pydantic") is None:
    _pydantic = _stub("pydantic")
    # Provide the symbols that app.core.config imports
    _pydantic.BeforeValidator = MagicMock()
    _pydantic.Field           = MagicMock()

if importlib.util.find_spec("pydantic_settings") is None:
    _ps = _stub("pydantic_settings")
    # BaseSettings must be sub-classable, so give it a real class
    class _BaseSettings:
        model_config = {}
        def __init__(self, **kw):
            for k, v in kw.items():
                setattr(self, k, v)
    class _SettingsConfigDict(dict): pass
    _ps.BaseSettings       = _BaseSettings
    _ps.SettingsConfigDict = _SettingsConfigDict

if importlib.util.find_spec("typing_extensions") is None:
    _te = _stub("typing_extensions")
    _te.Annotated = MagicMock()

# NOTE: Do NOT stub 'app', 'app.core', or 'app.core.config' here.
# Those are real packages on disk and must be imported normally.
# They are stubbed inside app/tests/conftest.py where sys.path is already set.

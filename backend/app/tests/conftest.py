"""
app/tests/conftest.py

Bootstraps sys.path and stubs heavy packages before any test module is imported.
This runs with whatever Python interpreter pytest uses.
"""
import sys
import os
import types
from unittest.mock import MagicMock
import pytest

# ── Ensure backend/ is on sys.path so `from app.services import ...` works ───
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)


def _stub(dotted_name: str, **attrs) -> types.ModuleType:
    """Register a minimal stub for dotted_name without overwriting real packages."""
    if dotted_name in sys.modules:
        return sys.modules[dotted_name]
    mod = types.ModuleType(dotted_name)
    mod.__spec__ = None                          # type: ignore[assignment]
    mod.__getattr__ = lambda n: MagicMock()      # type: ignore[assignment]
    for k, v in attrs.items():
        setattr(mod, k, v)
    sys.modules[dotted_name] = mod
    # Attach to parent
    parts = dotted_name.split(".")
    if len(parts) > 1:
        parent = sys.modules.get(".".join(parts[:-1]))
        if parent is not None:
            setattr(parent, parts[-1], mod)
    return mod


# ── torch ─────────────────────────────────────────────────────────────────────
try:
    import torch
except ImportError:
    _cuda = MagicMock()
    _cuda.is_available = MagicMock(return_value=False)
    _stub("torch", cuda=_cuda)

# ── ultralytics ───────────────────────────────────────────────────────────────
try:
    import ultralytics
except ImportError:
    _stub("ultralytics", YOLO=MagicMock())

# ── pydantic + pydantic_settings (pulled in by app.core.config) ──────────────
try:
    import pydantic
except ImportError:
    _pyd = _stub("pydantic")
    _pyd.BeforeValidator = MagicMock()
    _pyd.Field           = MagicMock()

try:
    import pydantic_settings
except ImportError:
    class _BaseSettings:
        model_config = {}
        def __init__(self, **kw):
            for k, v in kw.items():
                setattr(self, k, v)
    class _SettingsConfigDict(dict):
        pass
    _ps = _stub("pydantic_settings")
    _ps.BaseSettings       = _BaseSettings
    _ps.SettingsConfigDict = _SettingsConfigDict

try:
    import typing_extensions
except ImportError:
    _te = _stub("typing_extensions")
    _te.Annotated = MagicMock()


# ── Full-stack fixtures (FastAPI/SQLAlchemy) — optional ───────────────────────
try:
    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.main import app as _app
    from app.core.database import Base
    from app.api import deps
    _FULL_STACK = True
except Exception:
    _FULL_STACK = False

if _FULL_STACK:
    _DB_URL = "sqlite:///./test.db"
    _engine = create_engine(_DB_URL, connect_args={"check_same_thread": False})
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

    @pytest.fixture(scope="module")
    def db():
        Base.metadata.create_all(bind=_engine)
        session = _SessionLocal()
        try:
            yield session
        finally:
            session.close()
            Base.metadata.drop_all(bind=_engine)

    @pytest.fixture(scope="module")
    def client(db):
        def _override():
            try:
                yield db
            finally:
                pass
        _app.dependency_overrides[deps.get_db] = _override
        with TestClient(_app) as c:
            yield c

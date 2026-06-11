"""
app/tests/conftest.py

Provides shared test fixtures. The full-stack fixtures (client, db) are only
constructed when FastAPI, SQLAlchemy, and the app modules are importable.
Unit-level tests (symbol_detection, image_preprocessing) do NOT require them.
"""
import pytest

try:
    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.main import app
    from app.core.database import Base
    from app.api import deps
    _FULL_STACK_AVAILABLE = True
except Exception:
    _FULL_STACK_AVAILABLE = False


if _FULL_STACK_AVAILABLE:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    @pytest.fixture(scope="module")
    def db():
        Base.metadata.create_all(bind=engine)
        db_session = TestingSessionLocal()
        try:
            yield db_session
        finally:
            db_session.close()
            Base.metadata.drop_all(bind=engine)

    @pytest.fixture(scope="module")
    def client(db):
        def override_get_db():
            try:
                yield db
            finally:
                pass
        app.dependency_overrides[deps.get_db] = override_get_db
        with TestClient(app) as c:
            yield c

from sqlalchemy.exc import OperationalError

from app.core.config import Settings


def test_local_database_url_uses_localhost():
    settings = Settings(
        _env_file=None,
        APP_RUNTIME="local",
        DATABASE_HOST="localhost",
        DATABASE_USER="postgres",
        DATABASE_PASSWORD="postgres",
        DATABASE_NAME="hmer",
    )

    assert "@localhost:5432/hmer" in settings.effective_database_url
    assert "postgres:***@" in settings.safe_database_url


def test_docker_database_url_uses_compose_hostname():
    settings = Settings(
        _env_file=None,
        APP_RUNTIME="docker",
        DATABASE_HOST="localhost",
        DATABASE_USER="postgres",
        DATABASE_PASSWORD="postgres",
        DATABASE_NAME="hmer",
    )

    assert "@db:5432/hmer" in settings.effective_database_url


def test_history_returns_database_unavailable(client):
    from app.api import deps
    from app.main import app

    class BrokenSession:
        def query(self, *_args, **_kwargs):
            raise OperationalError("SELECT 1", {}, Exception("offline"))

        def close(self):
            pass

    def broken_db():
        yield BrokenSession()

    original_override = app.dependency_overrides.get(deps.get_db)
    app.dependency_overrides[deps.get_db] = broken_db
    try:
        response = client.get("/api/v1/history")
    finally:
        if original_override is not None:
            app.dependency_overrides[deps.get_db] = original_override
        else:
            app.dependency_overrides.pop(deps.get_db, None)

    assert response.status_code == 503
    assert response.json() == {"success": False, "message": "Database unavailable"}


def test_prediction_persistence_database_unavailable(client):
    from io import BytesIO

    from PIL import Image, ImageDraw
    from sqlalchemy.exc import OperationalError

    from app.api import deps
    from app.main import app

    class BrokenSession:
        def add(self, *_args, **_kwargs):
            pass

        def commit(self):
            raise OperationalError("INSERT", {}, Exception("offline"))

        def close(self):
            pass

    def broken_db():
        yield BrokenSession()

    image = Image.new("RGB", (120, 48), "white")
    ImageDraw.Draw(image).line((15, 24, 90, 24), fill="black", width=3)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    original_override = app.dependency_overrides.get(deps.get_db)
    app.dependency_overrides[deps.get_db] = broken_db
    try:
        response = client.post(
            "/api/v1/predict",
            files={"image": ("equation.png", buffer.getvalue(), "image/png")},
        )
    finally:
        if original_override is not None:
            app.dependency_overrides[deps.get_db] = original_override
        else:
            app.dependency_overrides.pop(deps.get_db, None)

    assert response.status_code == 503
    assert response.json() == {"success": False, "message": "Database unavailable"}

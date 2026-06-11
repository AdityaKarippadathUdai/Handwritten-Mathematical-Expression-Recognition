# Import all models here so that Alembic can detect modifications
# and auto-generate migrations correctly.

from app.core.database import Base  # noqa
from app.models.expression import Expression  # noqa
from app.models.history import EquationHistory  # noqa
from app.models.user import User  # noqa

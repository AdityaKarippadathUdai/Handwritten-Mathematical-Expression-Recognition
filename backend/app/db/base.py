# Import all models here so that Alembic can detect modifications
# and auto-generate migrations correctly.

from app.core.database import Base  # noqa
from app.db.models import EquationHistory, Expression, User  # noqa

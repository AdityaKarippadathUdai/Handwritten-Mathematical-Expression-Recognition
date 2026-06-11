from datetime import datetime
from sqlalchemy import String, Float, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class EquationHistory(Base):
    """
    EquationHistory stores the history of expressions uploaded, their recognized
    LaTeX format, and the prediction confidence score from the YOLOv11 model.
    """
    __tablename__ = "equation_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    latex_output: Mapped[str] = mapped_column(String(2000), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class Expression(Base):
    """
    Expression represents mathematical symbols parsed from the canvas drawings.
    """
    __tablename__ = "expressions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    raw_image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    latex_result: Mapped[str] = mapped_column(String(2000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class User(Base):
    """
    User represents application users and accounts for login.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

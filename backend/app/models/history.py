from datetime import datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class EquationHistory(Base):
    __tablename__ = "equation_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    latex_output: Mapped[str] = mapped_column(String(2000), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.core.database import Base

class Expression(Base):
    __tablename__ = "expressions"

    id = Column(Integer, primary_key=True, index=True)
    raw_image_path = Column(String, nullable=False)
    latex_result = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

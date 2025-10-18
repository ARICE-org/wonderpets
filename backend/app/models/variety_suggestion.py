import uuid
from sqlalchemy import UUID, Column, Boolean, DateTime, ForeignKey, func
from app.db import Base

class VarietySuggestion(Base):
    __tablename__ = "variety_suggestion"
    variety_sugg_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rice_variety_id = Column(UUID(as_uuid=True), ForeignKey("rice_variety.rice_variety_id"), nullable=False)
    feedback = Column(Boolean, nullable=True)
    created_date = Column(DateTime(timezone=True), default=func.now())

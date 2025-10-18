import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, UUID
from app.db import Base

class RiceVariety(Base):
    __tablename__ = "rice_variety"
    rice_variety_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    season_id = Column(UUID(as_uuid=True), ForeignKey("season.season_id"), nullable=False)
    rice_name = Column(String(100), nullable=False)
    growth_duration = Column(Integer, nullable=False)
    color = Column(String(20), nullable=False)

import uuid
from sqlalchemy import UUID, Column, String
from app.db import Base

class Season(Base):
    __tablename__ = "season"
    season_id = Column(UUID (as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)

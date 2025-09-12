import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql.base import UUID
from sqlalchemy.sql.functions import func
from app.db import Base

class User(Base):
    __tablename__ = 'user'

    uuid = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
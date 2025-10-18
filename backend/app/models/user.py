import uuid
from sqlalchemy import UUID, Column, String, DateTime, func
from app.db import Base

class User(Base):
    __tablename__ = 'users'

    user_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    email = Column(String(320), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    phone_number = Column(String(15), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
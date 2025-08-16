from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False, index=True)
    middle_name = Column(String, nullable=True)
    last_name = Column(String, nullable=False, index=True)
    address = Column(String, nullable=False, server_default="pacol,nagacity")
    phone_number = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from app.db import Base
from sqlalchemy.dialects.postgresql import UUID

class Farmer(Base):
    __tablename__ = "farmer"

    farmer_id = Column(UUID(as_uuid=True), ForeignKey("user.uuid"), primary_key=True)
    first_name = Column(String, nullable=False, index=True)
    middle_name = Column(String, nullable=True)
    last_name = Column(String, nullable=False, index=True)
    address = Column(String, nullable=False, server_default="Pacol,Naga City")
    phone_number = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

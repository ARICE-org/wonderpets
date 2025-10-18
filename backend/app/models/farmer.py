from sqlalchemy import UUID, Column, String, ForeignKey
from app.db import Base

class Farmer(Base):
    __tablename__ = "farmer"

    farmer_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), primary_key=True)
    first_name = Column(String, nullable=False, index=True)
    middle_name = Column(String, nullable=True)
    last_name = Column(String, nullable=False, index=True)
    address = Column(String, nullable=False, server_default="Pacol,Naga City")
    

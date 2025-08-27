from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from app.db import Base

# Base = declarative_base()

class Season(Base):
    __tablename__ = "season"
    season_id = Column(String(20), primary_key=True)
    name = Column(String(50), nullable=False)

from sqlalchemy import Column, String, TIMESTAMP, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from app.db import Base

# Base = declarative_base()

class VarietySuggestion(Base):
    __tablename__ = "variety_suggestion"
    variety_sugg_id = Column(String(20), primary_key=True)
    rice_variety_id = Column(String(20), ForeignKey("rice_variety.rice_variety_id"), nullable=False)
    date_generated = Column(TIMESTAMP, nullable=False)
    feedback = Column(Boolean, nullable=False)

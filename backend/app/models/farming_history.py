from sqlalchemy import Column, String, Date, Numeric, ForeignKey
from .farmer import Farmer
from sqlalchemy.ext.declarative import declarative_base
from app.db import Base

# Base = declarative_base()

class FarmingHistory(Base):
    __tablename__ = "farming_history"
    history_id = Column(String(20), primary_key=True)
    farmer_id = Column(String(20), ForeignKey("farmer.farmer_id"), nullable=False)
    history_date = Column(Date)
    history_title = Column(String(100))
    yields = Column(Numeric)

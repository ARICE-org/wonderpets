from sqlalchemy import Column, String, Date, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db import Base

class FarmingHistory(Base):
    __tablename__ = "farming_history"
    history_id = Column(String(20), primary_key=True)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmer.farmer_id"), nullable=False)
    history_date = Column(Date)
    history_title = Column(String(100))
    yields = Column(Numeric)

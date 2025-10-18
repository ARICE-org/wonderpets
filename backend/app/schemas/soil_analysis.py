from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SoilAnalysisBase(BaseModel):
    soil_id: UUID = Field(..., alias="soilId")
    analysis_date: datetime = Field(..., alias="analysisDate")
    soil_health_summary: str = Field(..., alias="soilHealthSummary")
    recommendations: str = Field(..., alias="recommendations")

    model_config = {
        "populate_by_name": True,
    }

class SoilAnalysisCreate(SoilAnalysisBase):
    pass

class SoilAnalysisUpdate(BaseModel):
    soil_id: Optional[UUID] = Field(None, alias="soilId")
    analysis_date: Optional[datetime] = Field(None, alias="analysisDate")
    soil_health_summary: Optional[str] = Field(None, alias="soilHealthSummary")
    recommendations: Optional[str] = Field(None, alias="recommendations")

    model_config = {
        "populate_by_name": True,
    }

class SoilAnalysisInDB(SoilAnalysisBase):
    analysis_id: UUID = Field(..., alias="analysisId")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

class SoilAnalysis(SoilAnalysisInDB):
    pass

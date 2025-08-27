from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SoilAnalysisBase(BaseModel):
    soil_id: str = Field(..., alias="soilId")
    analysis_date: datetime = Field(..., alias="analysisDate")
    soil_health_summary: str = Field(..., alias="soilHealthSummary")
    recommendations: str

    model_config = {
        "populate_by_name": True,
    }

class SoilAnalysisCreate(SoilAnalysisBase):
    pass

class SoilAnalysisUpdate(BaseModel):
    soil_id: Optional[str] = Field(None, alias="soilId")
    analysis_date: Optional[datetime] = Field(None, alias="analysisDate")
    soil_health_summary: Optional[str] = Field(None, alias="soilHealthSummary")
    recommendations: Optional[str] = None

    model_config = {
        "populate_by_name": True,
    }

class SoilAnalysisInDB(SoilAnalysisBase):
    analysis_id: str = Field(..., alias="analysisId")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

class SoilAnalysis(SoilAnalysisInDB):
    pass

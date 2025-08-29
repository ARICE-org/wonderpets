from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class WeatherDataBase(BaseModel):
    datetime: datetime = Field(..., alias="datetime")
    max_temp: float = Field(..., alias="maxTemp")
    min_temp: float = Field(..., alias="minTemp")
    rainfall: float = Field(..., alias="rainfall")
    humidity: float = Field(..., alias="humidity")
    wind_speed: float = Field(..., alias="windSpeed")
    wind_direct: str = Field(..., alias="windDirect")

    model_config = {
        "populate_by_name": True,
    }

class WeatherDataCreate(WeatherDataBase):
    pass

class WeatherDataUpdate(BaseModel):
    datetime: Optional[datetime] = Field(None, alias="datetime")
    max_temp: Optional[float] = Field(None, alias="maxTemp")
    min_temp: Optional[float] = Field(None, alias="minTemp")
    rainfall: Optional[float] = Field(None, alias="rainfall")
    humidity: Optional[float] = Field(None, alias="humidity")
    wind_speed: Optional[float] = Field(None, alias="windSpeed")
    wind_direct: Optional[str] = Field(None, alias="windDirect")

    model_config = {
        "populate_by_name": True,
    }

class WeatherDataInDB(WeatherDataBase):
    weather_id: str = Field(..., alias="weatherId")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

class WeatherData(WeatherDataInDB):
    pass

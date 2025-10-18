from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.weather_data import WeatherData as WeatherDataModel
from app.schemas.weather_data import WeatherData, WeatherDataBase, WeatherDataCreate, WeatherDataUpdate


router = APIRouter(prefix="/weather", tags=["Weather"])

@router.get("/", response_model=List[WeatherDataBase])
def get_weather_data(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(WeatherDataModel).offset(skip).limit(limit).all()

@router.get("/{weather_id}", response_model=WeatherData)
def get_weather_record(weather_id: UUID, db: Session = Depends(get_db)):
    weather = db.get(WeatherDataModel, weather_id)
    if not weather:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weather data not found")
    return weather

@router.post("/", response_model=WeatherData, status_code=status.HTTP_201_CREATED)
def create_weather_record(payload: WeatherDataCreate, db: Session = Depends(get_db)):
    weather = WeatherDataModel(
        date=payload.date,
        max_temp=payload.max_temp,
        min_temp=payload.min_temp,
        rainfall=payload.rainfall,
        humidity=payload.humidity,
        wind_speed=payload.wind_speed,
        wind_direct=payload.wind_direct,
    )
    db.add(weather)
    db.commit()
    db.refresh(weather)
    return weather

@router.put("/{weather_id}", response_model=WeatherData)
def update_weather_record(weather_id: UUID, payload: WeatherDataUpdate, db: Session = Depends(get_db)):
    weather = db.get(WeatherDataModel, weather_id)
    if not weather:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weather data not found")

    data = payload.model_dump(exclude_unset=True)
    # Since we used aliases (camelCase), ensure we access by field names
    for field, value in data.items():
        setattr(weather, field, value)

    db.add(weather)
    db.commit()
    db.refresh(weather)
    return weather

@router.delete("/{weather_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_weather_record(weather_id: UUID, db: Session = Depends(get_db)):
    weather = db.get(WeatherDataModel, weather_id)
    if not weather:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weather data not found")
    db.delete(weather)
    db.commit()
    db.refresh(weather)

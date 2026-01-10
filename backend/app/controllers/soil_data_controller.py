import io
from sqlalchemy.orm import Session 
from typing import List, Optional
import uuid
from datetime import datetime
from .. import models
from app.schemas.soil_data import (
    SoilDataBase, 
    SoilData, 
    SoilDataCreate, 
    SoilDataUpdate,
    SoilDataBulkUploadRequest,
    SoilReadingItem,
)
import pandas as pd
from fastapi import UploadFile, File
from datetime import date
from app.controllers.soil_forecast_controller import soil_forecast_controller
from app.schemas.soil_forecast import UploadSensorDataRequest, SensorReading
import logging


def get_soil_data(db: Session, soil_id: uuid.UUID) -> Optional[models.SoilData]:
    """Get a single SoilData record by its UUID.

    Args:
        db: Session - Database session.
        soil_id: uuid.UUID - The UUID of the SoilData to retrieve.

    Returns:
        Optional[models.SoilData]: The matching SoilData instance or ``None`` if
            no record is found.
    """
    return db.query(models.SoilData).filter(models.SoilData.soil_id == soil_id).first()

def get_all_soil_data(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[bool] = None
) -> List[models.SoilData]:
    """Retrieve SoilData records with optional pagination and status filter.

    Args:
        db: Session - Database session.
        skip: int - Number of records to skip (offset).
        limit: int - Maximum number of records to return.
        status: Optional[bool] - Optional status filter. When provided, the
            query is filtered accordingly.

    Returns:
        List[models.SoilData]: A list of SoilData records matching the query.
    """
    query = db.query(models.SoilData)
    if status is not None: 
        query = query.filter(models.SoilSensorDevice.sensor_id == status)
    return query.offset(skip).limit(limit).all()


def create_soil_data(
    db: Session, 
    soil_data: SoilDataCreate
) -> models.SoilData:
    """Create a new SoilData record from a schema object.

    Args:
        db: Session - Database session.
        soil_data: SoilDataCreate - Data transfer object containing fields to
            create the SoilData record.

    Returns:
        models.SoilData: The newly created SoilData instance.
    """
    db_soil_data = models.SoilData(
        sensor_id=soil_data.sensor_id,
        datetimestamp=soil_data.datetimestamp,
        soil_moisture=soil_data.soil_moisture,
        soil_ph=soil_data.soil_ph,
        nitrogen_level=soil_data.nitrogen_level,
        phosphorus_level=soil_data.phosphorus_level,
        potassium_level=soil_data.potassium_level,
    )
    db.add(db_soil_data)
    db.commit()
    db.refresh(db_soil_data)
    return db_soil_data


def aggregate_readings(readings: List[SoilReadingItem]) -> dict:
    """Aggregate multiple readings into a single average record.
    
    Args:
        readings: List of SoilReadingItem objects from CSV parsing.
        
    Returns:
        dict with averaged values for all soil parameters.
    """
    if not readings:
        raise ValueError("No readings provided for aggregation")
    
    # Filter out invalid/None values and calculate averages
    def safe_avg(values: List[Optional[float]]) -> float:
        valid = [v for v in values if v is not None and v >= 0]
        if not valid:
            return 0.0
        return round(sum(valid) / len(valid), 2)
    
    representative_timestamp = max((r.timestamp for r in readings), default=datetime.utcnow())

    return {
        "datetimestamp": representative_timestamp,
        "soil_moisture": safe_avg([r.moisture for r in readings]),
        "soil_ph": safe_avg([r.pH for r in readings]),
        "nitrogen_level": safe_avg([r.nitrogen for r in readings]),
        "phosphorus_level": safe_avg([r.phosphorus for r in readings]),
        "potassium_level": safe_avg([r.potassium for r in readings]),
        "organic_matter": safe_avg([r.organic_matter for r in readings]),
        "temperature": safe_avg([r.temperature for r in readings]),
        "reading_count": len(readings),
    }


async def bulk_upload_soil_data(
    db: Session,
    request: SoilDataBulkUploadRequest
) -> dict:
    """Process bulk CSV data: aggregate, save, and chain to soil-forecast.
    
    Args:
        db: Session - Database session.
        request: SoilDataBulkUploadRequest - Parsed CSV readings with metadata.
        
    Returns:
        dict containing saved soil_data, forecast response, and message.
    """
    # 1. Aggregate readings to get averages
    aggregated = aggregate_readings(request.readings)
    
    # 2. Create aggregated soil data record
    soil_data_create = SoilDataCreate(
        dateTimeStamp=aggregated["datetimestamp"],
        soilMoisture=aggregated["soil_moisture"],
        soilPh=aggregated["soil_ph"],
        nitrogenLevel=aggregated["nitrogen_level"],
        phosphorusLevel=aggregated["phosphorus_level"],
        potassiumLevel=aggregated["potassium_level"],
        sensorId=request.sensor_id,
    )
    
    db_soil_data = create_soil_data(db, soil_data_create)
    
    # 3. Create forecast (must succeed)
    logging.getLogger("uvicorn").info(
        f"[SoilData] Creating forecast for farmer={request.farmer_id} sensor={request.sensor_id} plantingDate={request.planting_date}"
    )
    forecast_response = await chain_to_soil_forecast(
        db=db,
        farmer_id=request.farmer_id,
        sensor_id=request.sensor_id,
        planting_date=request.planting_date,
        aggregated_data=aggregated,
    )
    
    return {
        "soil_data": db_soil_data,
        "forecast": forecast_response,
        "message": f"Successfully processed {aggregated['reading_count']} readings",
    }


async def chain_to_soil_forecast(
    db: Session,
    farmer_id: uuid.UUID,
    sensor_id: uuid.UUID,
    planting_date: str,
    aggregated_data: dict,
) -> dict:
    """Create forecast by calling the soil-forecast controller directly.
    
    Args:
        farmer_id: UUID of the farmer.
        sensor_id: UUID of the sensor.
        planting_date: Planting date string (YYYY-MM-DD).
        aggregated_data: Aggregated soil data.
        readings: Original readings list for detailed forecast.
        
    Returns:
        dict with forecast response.
    """
    # IMPORTANT: Send a single aggregated reading (1 row) so the forecast is
    # based on the same aggregated soil_data that was persisted.
    ts: datetime = aggregated_data.get("datetimestamp") or datetime.utcnow()
    planting_dt = datetime.strptime(planting_date, "%Y-%m-%d").date()

    request = UploadSensorDataRequest(
        farmerId=farmer_id,
        sensorId=sensor_id,
        plantingDate=planting_dt,
        readingDate=ts.date(),
        readings=[
            SensorReading(
                timestamp=ts,
                moisture=aggregated_data.get("soil_moisture", 0.0),
                nitrogen=aggregated_data.get("nitrogen_level", 0.0),
                phosphorus=aggregated_data.get("phosphorus_level", 0.0),
                potassium=aggregated_data.get("potassium_level", 0.0),
                pH=aggregated_data.get("soil_ph", 0.0),
                organicMatter=aggregated_data.get("organic_matter", 3.0),
                temperature=aggregated_data.get("temperature", None),
            )
        ],
    )

    response = await soil_forecast_controller.process_sensor_reading(db=db, request=request)
    # Return as plain dict (frontend expects JSON)
    return response.model_dump(by_alias=True)


def bulk_create_soil_data(
    db: Session,
    soil_data_list: List[SoilDataCreate]
) -> List[models.SoilData]:
    """Create multiple SoilData records in a single operation.

    Args:
        db: Session - Database session.
        soil_data_list: List[SoilDataCreate] - List of DTOs describing each
            SoilData to create.

    Returns:
        List[models.SoilData]: The list of created SoilData instances.
    """
    db_soil_data_list = []
    for soil_data in soil_data_list:
        db_soil_data = models.SoilData(
            sensor_id=soil_data.sensor_id,
            datetimestamp=soil_data.datetimestamp,
            soil_moisture=soil_data.soil_moisture,
            soil_ph=soil_data.soil_ph,
            nitrogen_level=soil_data.nitrogen_level,
            phosphorus_level=soil_data.phosphorus_level,
            potassium_level=soil_data.potassium_level,
        )
        db.add(db_soil_data)
        db_soil_data_list.append(db_soil_data)
    db.commit()
    for db_soil_data in db_soil_data_list:
        db.refresh(db_soil_data)
    return db_soil_data_list

def delete_soil_data(
    db: Session, 
    db_soil_data: models.SoilData
) -> models.SoilData:
    """Delete an existing SoilData record.

    Args:
        db: Session - Database session.
        db_soil_data: models.SoilData - The SoilData instance to delete.

    Returns:
        models.SoilData: The deleted SoilData instance as it existed prior to
            deletion.
    """
    db.delete(db_soil_data)
    db.commit()
    return db_soil_data


async def upload_soil_data_csv(
       db: Session,
       file: UploadFile,
       farmer_id: uuid.UUID,
       planting_date: str,
       sensor_id: Optional[uuid.UUID] = None,
   ) -> dict:
       """Upload a CSV file, aggregate into ONE SoilData row, then generate a forecast.

       This endpoint matches the intended flow:
       1) Upload CSV
       2) Aggregate readings (average)
       3) Save one aggregated SoilData row
       4) Call /api/soil-forecast/readings using the aggregated payload
       """

       contents = await file.read()
       df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

       # Resolve sensor_id: either provided via form, or from CSV column.
       resolved_sensor_id = sensor_id
       if resolved_sensor_id is None:
           for col in ["sensor_id", "sensorId", "sensor"]:
               if col in df.columns and df[col].notna().any():
                   resolved_sensor_id = uuid.UUID(str(df[col].dropna().iloc[0]))
                   break

       if resolved_sensor_id is None:
           raise ValueError("sensorId is required (provide as form field or include sensor_id column in CSV)")

       readings: List[SoilReadingItem] = []
       for _, row in df.iterrows():
           # Timestamp is optional for CSV upload; if missing, use current time.
           ts_raw = row.get("timestamp", row.get("dateTimeStamp", row.get("date_time", None)))
           try:
               ts = pd.to_datetime(ts_raw) if ts_raw is not None else pd.Timestamp.utcnow()
           except Exception:
               ts = pd.Timestamp.utcnow()

           readings.append(
               SoilReadingItem(
                   timestamp=ts.to_pydatetime(),
                   moisture=float(row.get("moisture", row.get("moisture_level", 0)) or 0),
                   pH=float(row.get("pH", row.get("pH_level", 0)) or 0),
                   nitrogen=float(row.get("nitrogen", row.get("nitrogen_level", 0)) or 0),
                   phosphorus=float(row.get("phosphorus", row.get("phosphorus_level", 0)) or 0),
                   potassium=float(row.get("potassium", row.get("potassium_level", 0)) or 0),
                   organicMatter=(
                       float(row.get("organicMatter", row.get("organic_matter", 0)) or 0)
                       if ("organicMatter" in row or "organic_matter" in row)
                       else None
                   ),
                   temperature=(float(row.get("temperature", 0)) if "temperature" in row else None),
               )
           )

       if not readings:
           raise ValueError("No readings found in CSV")

       # Reuse the same aggregation + save + chaining logic
       bulk_request = SoilDataBulkUploadRequest(
           sensorId=resolved_sensor_id,
           farmerId=farmer_id,
           plantingDate=planting_date,
           readings=readings,
       )
       return await bulk_upload_soil_data(db=db, request=bulk_request)

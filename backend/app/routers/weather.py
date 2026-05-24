"""Forecast endpoints for Weather Service."""

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query

from app.services.mongo_client import get_mongo_client
from app.config.settings import settings

router = APIRouter(prefix="/weather", tags=["Weather"])


def _station_query(station_name: str) -> dict:
    """Build query for station name with backward compatibility."""
    return {"$or": [{"station.name": station_name}, {"station": station_name}]}


def _nearest_run_for_lat_lon(db, latitude: float, longitude: float) -> dict | None:
    """Find the nearest forecast run based on lat/lon coordinates."""
    pipeline = [
        {"$match": {"station.lat": {"$type": "number"}, "station.lon": {"$type": "number"}}},
        {
            "$addFields": {
                "_dist2": {
                    "$add": [
                        {"$pow": [{"$subtract": ["$station.lat", latitude]}, 2]},
                        {"$pow": [{"$subtract": ["$station.lon", longitude]}, 2]},
                    ]
                }
            }
        },
        {"$sort": {"_dist2": 1, "created_at": -1}},
        {"$limit": 1},
        {"$project": {"_dist2": 0}},
    ]
    # Use fuxi_final_forecasts collection (stored by fuxis2s_model)
    docs = list(db.fuxi_final_forecasts.aggregate(pipeline))
    return docs[0] if docs else None


@router.get("/latest")
async def get_latest_forecast(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude coordinate"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude coordinate"),
    days: int = Query(7, ge=1, le=42, description="Number of forecast days")
):
    """
    Get latest forecast for a location.
    Returns ensemble mean + bias-corrected values.
    """
    try:
        client = get_mongo_client()
        db = client[settings.mongo_db]

        # Find nearest run based on lat/lon
        latest_run = _nearest_run_for_lat_lon(db, latitude=latitude, longitude=longitude)

        if not latest_run:
            raise HTTPException(404, "No forecasts found for the provided coordinates")

        run_id = latest_run.get("run_id") or latest_run.get("_id")
        if not run_id:
            raise HTTPException(500, "Malformed run document: missing run identifier")

        # Get forecasts from fuxi_final_forecasts collection
        forecasts = list(
            db.fuxi_final_forecasts.find(
                {"run_id": run_id, "lead_time_days": {"$lte": days}},
                {"_id": 0},
            ).sort("lead_time_days", 1)
        )

        station_obj = latest_run.get("station")
        station_name = None
        if isinstance(station_obj, dict):
            station_name = station_obj.get("name")

        return {
            "run_id": run_id,
            "init_time": latest_run.get("init_time"),
            "created_at": latest_run.get("created_at"),
            "station": station_name,
            "station_details": station_obj if isinstance(station_obj, dict) else None,
            "requested_location": {"lat": latitude, "lon": longitude},
            "forecast_days": len(forecasts),
            "forecasts": forecasts,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Database error: {str(e)}")


@router.get("/by-date")
async def get_forecast_by_date(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude coordinate"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude coordinate"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)")
):
    """
    Get forecasts for a specific date range.
    Finds the best available run that covers the requested dates.
    """
    try:
        client = get_mongo_client()
        db = client[settings.mongo_db]

        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        # Resolve nearest stored station/grid point via runs collection
        nearest_run = _nearest_run_for_lat_lon(db, latitude=latitude, longitude=longitude)
        if not nearest_run:
            raise HTTPException(404, "No forecasts found for the provided coordinates")

        station_obj = nearest_run.get("station")
        station_name = station_obj.get("name") if isinstance(station_obj, dict) else None
        if not station_name:
            raise HTTPException(500, "Malformed run document: missing station metadata")

        # Find forecasts in date range for the resolved point
        forecasts = list(
            db.fuxi_final_forecasts.find(
                {
                    **_station_query(station_name),
                    "valid_time": {"$gte": start, "$lte": end},
                },
                {"_id": 0},
            ).sort("valid_time", 1)
        )

        if not forecasts:
            raise HTTPException(404, f"No forecasts found between {start_date} and {end_date}")

        return {
            "station": station_name,
            "station_details": station_obj,
            "requested_location": {"lat": latitude, "lon": longitude},
            "date_range": {"start": start_date, "end": end_date},
            "forecast_count": len(forecasts),
            "forecasts": forecasts,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Database error: {str(e)}")


@router.get("/runs")
async def list_runs(
    latitude: Optional[float] = Query(None, ge=-90, le=90, description="Latitude coordinate"),
    longitude: Optional[float] = Query(None, ge=-180, le=180, description="Longitude coordinate"),
    station: Optional[str] = Query(None, description="(Deprecated) Filter by station name"),
    limit: int = Query(10, ge=1, le=100)
):
    """List recent forecast runs."""
    try:
        client = get_mongo_client()
        db = client[settings.mongo_db]

        query: dict = {}

        # Prefer lat/lon (new behavior). If not provided, fall back to station filter.
        if latitude is not None or longitude is not None:
            if latitude is None or longitude is None:
                raise HTTPException(400, "Provide both latitude and longitude")
            nearest = _nearest_run_for_lat_lon(db, latitude=latitude, longitude=longitude)
            if not nearest:
                return {"runs": []}
            station_obj = nearest.get("station")
            station_name = station_obj.get("name") if isinstance(station_obj, dict) else None
            if station_name:
                query = _station_query(station_name)
        elif station:
            query = _station_query(station)

        # Get unique runs from fuxi_final_forecasts
        pipeline = [
            {"$match": query} if query else {"$match": {}},
            {"$group": {
                "_id": "$run_id",
                "run_id": {"$first": "$run_id"},
                "init_time": {"$first": "$init_time"},
                "created_at": {"$first": "$created_at"},
                "station": {"$first": "$station"}
            }},
            {"$sort": {"created_at": -1}},
            {"$limit": limit}
        ]
        runs = list(db.fuxi_final_forecasts.aggregate(pipeline))

        # Convert ObjectId to string for JSON serialization
        for run in runs:
            if "_id" in run:
                run["_id"] = str(run["_id"])

        payload: dict[str, Any] = {"runs": runs}
        if latitude is not None and longitude is not None:
            payload["requested_location"] = {"lat": latitude, "lon": longitude}
        return payload
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Database error: {str(e)}")


@router.get("/stations")
async def list_stations():
    """List all available forecast stations."""
    try:
        client = get_mongo_client()
        db = client[settings.mongo_db]

        # Stations are seeded into their own collection during Mongo init.
        stations = list(db.stations.find({}, {"_id": 0}).sort("name", 1))
        
        return {"stations": stations, "count": len(stations)}
    except Exception as e:
        raise HTTPException(500, f"Database error: {str(e)}")

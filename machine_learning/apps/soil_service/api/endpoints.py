"""
Soil Analysis API Endpoints

Endpoints for soil health scoring, hybrid forecasting, and forecast realignment.
These endpoints are called by the Backend service, not directly by the Frontend.
"""

import time
from fastapi import APIRouter, HTTPException, Depends

from apps.common.utils.logging_utils import (
    logger,
    log_error,
    log_request,
    log_response,
    log_ml_prediction,
)
from apps.common.exceptions import (
    MLServiceError,
    ValidationError,
    ForecastError,
    AnalysisError,
    RealignmentError,
    HealthScoreError,
)
from apps.soil_service.api.schemas.requests import (
    SoilAnalysisRequest,
    HybridForecastRequest,
    RealignForecastRequest,
)
from apps.soil_service.api.schemas.responses import (
    SoilHealthResponse,
    HybridForecastResponse,
    RealignForecastResponse,
)
from apps.soil_service.api.dependencies import get_soil_service
from apps.soil_service.services.soil_analysis_service import SoilAnalysisService

router = APIRouter()


@router.post("/analyze", response_model=SoilHealthResponse)
async def analyze_soil_health(
    request: SoilAnalysisRequest,
    service: SoilAnalysisService = Depends(get_soil_service)
):
    """
    Analyze soil health and generate overall health score.
    
    Args:
        request: Soil analysis request with sensor data
    
    Returns:
        Overall health score (0-100) with parameter breakdown
    """
    start_time = time.time()
    log_request("/api/soil/analyze", "POST", {"request_type": "soil_analysis"})
    
    try:
        response = await service.analyze_health(request)
        
        duration_ms = (time.time() - start_time) * 1000
        log_response("/api/soil/analyze", 200, duration_ms=duration_ms)
        return response
    except ValueError as e:
        error_info = log_error(ValidationError(str(e)), {"endpoint": "/analyze"})
        raise HTTPException(status_code=400, detail=error_info)
    except MLServiceError as e:
        error_info = log_error(e, {"endpoint": "/analyze"})
        raise HTTPException(status_code=e.status_code, detail=error_info)
    except Exception as e:
        error_info = log_error(AnalysisError(f"Analysis error: {str(e)}"), {"endpoint": "/analyze"})
        raise HTTPException(status_code=500, detail=error_info)


@router.post("/health-score-detailed")
async def get_detailed_health_score(
    request: SoilAnalysisRequest,
    service: SoilAnalysisService = Depends(get_soil_service)
):
    """
    Get detailed health scoring with parameter breakdown and explanations.
    """
    start_time = time.time()
    log_request("/api/soil/health-score-detailed", "POST", {"request_type": "detailed_health_score"})
    
    try:
        response = await service.get_detailed_score(request)
        
        duration_ms = (time.time() - start_time) * 1000
        log_response("/api/soil/health-score-detailed", 200, duration_ms=duration_ms)
        return response
    except ValueError as e:
        error_info = log_error(ValidationError(str(e)), {"endpoint": "/health-score-detailed"})
        raise HTTPException(status_code=400, detail=error_info)
    except MLServiceError as e:
        error_info = log_error(e, {"endpoint": "/health-score-detailed"})
        raise HTTPException(status_code=e.status_code, detail=error_info)
    except Exception as e:
        error_info = log_error(HealthScoreError(f"Health score error: {str(e)}"), {"endpoint": "/health-score-detailed"})
        raise HTTPException(status_code=500, detail=error_info)


@router.post("/hybrid-forecast", response_model=HybridForecastResponse)
async def get_hybrid_forecast(
    request: HybridForecastRequest,
    service: SoilAnalysisService = Depends(get_soil_service)
):
    """
    Get hybrid soil forecast combining Rule-Based and ML approaches.
    """
    start_time = time.time()
    log_request("/api/soil/hybrid-forecast", "POST", {
        "request_type": "hybrid_forecast",
        "forecast_horizon": request.forecast_horizon_days
    })
    
    try:
        response = await service.hybrid_forecast(request)
        
        duration_ms = (time.time() - start_time) * 1000
        soil_data = request.current_soil_data
        log_ml_prediction(
            model_name="HybridSoilForecast",
            input_summary=f"pH={getattr(soil_data, 'ph', 'N/A')}, N={getattr(soil_data, 'nitrogen', 'N/A')}",
            prediction_summary=f"Generated {request.forecast_horizon_days}-day forecast",
            duration_ms=duration_ms
        )
        log_response("/api/soil/hybrid-forecast", 200, duration_ms=duration_ms)
        return response
    except ValueError as e:
        error_info = log_error(ValidationError(str(e)), {"endpoint": "/hybrid-forecast"})
        raise HTTPException(status_code=400, detail=error_info)
    except MLServiceError as e:
        error_info = log_error(e, {"endpoint": "/hybrid-forecast"})
        raise HTTPException(status_code=e.status_code, detail=error_info)
    except Exception as e:
        error_info = log_error(ForecastError(f"Hybrid forecast error: {str(e)}", "hybrid"), {"endpoint": "/hybrid-forecast"})
        raise HTTPException(status_code=500, detail=error_info)


@router.post("/realign-forecast", response_model=RealignForecastResponse)
async def realign_forecast(
    request: RealignForecastRequest,
    service: SoilAnalysisService = Depends(get_soil_service)
):
    """
    Realign existing forecast with new sensor data.
    """
    start_time = time.time()
    log_request("/api/soil/realign-forecast", "POST", {"request_type": "realign_forecast"})
    
    try:
        response = await service.realign_forecast(request)
        
        duration_ms = (time.time() - start_time) * 1000
        log_response("/api/soil/realign-forecast", 200, duration_ms=duration_ms)
        return response
    except ValueError as e:
        error_info = log_error(ValidationError(str(e)), {"endpoint": "/realign-forecast"})
        raise HTTPException(status_code=400, detail=error_info)
    except MLServiceError as e:
        error_info = log_error(e, {"endpoint": "/realign-forecast"})
        raise HTTPException(status_code=e.status_code, detail=error_info)
    except Exception as e:
        error_info = log_error(RealignmentError(f"Realignment error: {str(e)}"), {"endpoint": "/realign-forecast"})
        raise HTTPException(status_code=500, detail=error_info)


@router.get("/status")
async def get_soil_service_status(
    service: SoilAnalysisService = Depends(get_soil_service)
):
    """Check soil analysis service status."""
    return {
        "status": "healthy" if service.is_ready() else "degraded",
        "service": "soil_analysis",
        "models": {
            "health_model": service.health_model is not None,
            "hybrid_forecast_model": service.hybrid_forecast_model is not None
        }
    }

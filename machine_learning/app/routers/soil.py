"""
Soil Analysis API Router

Endpoints for soil health scoring, forecasting, and hybrid ML predictions.
These endpoints are called by the Backend service, not directly by the Frontend.
"""

import time
from fastapi import APIRouter, HTTPException
from typing import Optional

from app.common import (
    logger,
    log_error,
    log_request,
    log_response,
    log_ml_prediction,
    ErrorCode,
    MLServiceError,
    ValidationError,
    ForecastError,
    AnalysisError,
    RealignmentError,
    HealthScoreError,
)
from app.schemas.soil import (
    SoilAnalysisRequest,
    SoilHealthResponse,
    SoilForecastRequest,
    SoilForecastResponse,
    HybridForecastRequest,
    HybridForecastResponse,
    RealignForecastRequest,
    RealignForecastResponse,
    HealthScoreRequest,
    HealthScoreResponse as MLHealthScoreResponse
)
from app.services.soil_analysis_service import SoilAnalysisService
from app.services.forecast_realigner import forecast_realigner

router = APIRouter()

# Service instance
soil_service = SoilAnalysisService()


@router.post("/analyze", response_model=SoilHealthResponse)
async def analyze_soil_health(request: SoilAnalysisRequest):
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
        response = await soil_service.analyze_health(request)
        
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
async def get_detailed_health_score(request: SoilAnalysisRequest):
    """
    Get detailed health scoring with parameter breakdown and explanations.
    
    Args:
        request: Soil analysis request with sensor data
    
    Returns:
        Detailed scoring with interpretations for each parameter
    """
    start_time = time.time()
    log_request("/api/soil/health-score-detailed", "POST", {"request_type": "detailed_health_score"})
    
    try:
        response = await soil_service.get_detailed_score(request)
        
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


@router.post("/forecast", response_model=SoilForecastResponse)
async def get_soil_forecast(request: SoilForecastRequest):
    """
    Get 3-month soil condition forecast for rice planting season.
    
    Args:
        request: Forecast request with historical data and planting date
    
    Returns:
        Seasonal forecast with weekly summaries and growth stage alignment
    """
    start_time = time.time()
    log_request("/api/soil/forecast", "POST", {"request_type": "soil_forecast"})
    
    try:
        response = await soil_service.forecast_season(request)
        
        duration_ms = (time.time() - start_time) * 1000
        log_response("/api/soil/forecast", 200, duration_ms=duration_ms)
        return response
    except ValueError as e:
        error_info = log_error(ValidationError(str(e)), {"endpoint": "/forecast"})
        raise HTTPException(status_code=400, detail=error_info)
    except MLServiceError as e:
        error_info = log_error(e, {"endpoint": "/forecast"})
        raise HTTPException(status_code=e.status_code, detail=error_info)
    except Exception as e:
        error_info = log_error(ForecastError(f"Forecast error: {str(e)}", "soil_forecast"), {"endpoint": "/forecast"})
        raise HTTPException(status_code=500, detail=error_info)


@router.post("/seasonal-forecast")
async def get_seasonal_soil_forecast(request: SoilForecastRequest):
    """
    Get soil forecast aligned with rice growth stages.
    
    Args:
        request: Forecast request with planting date
    
    Returns:
        Forecast with growth stage timeline and stage-specific alerts
    """
    start_time = time.time()
    log_request("/api/soil/seasonal-forecast", "POST", {"request_type": "seasonal_forecast"})
    
    try:
        response = await soil_service.get_seasonal_forecast(request)
        
        duration_ms = (time.time() - start_time) * 1000
        log_response("/api/soil/seasonal-forecast", 200, duration_ms=duration_ms)
        return response
    except ValueError as e:
        error_info = log_error(ValidationError(str(e)), {"endpoint": "/seasonal-forecast"})
        raise HTTPException(status_code=400, detail=error_info)
    except MLServiceError as e:
        error_info = log_error(e, {"endpoint": "/seasonal-forecast"})
        raise HTTPException(status_code=e.status_code, detail=error_info)
    except Exception as e:
        error_info = log_error(ForecastError(f"Seasonal forecast error: {str(e)}", "seasonal"), {"endpoint": "/seasonal-forecast"})
        raise HTTPException(status_code=500, detail=error_info)


# =============================================================================
# HYBRID FORECAST ENDPOINTS
# =============================================================================

@router.post("/hybrid-forecast", response_model=HybridForecastResponse)
async def get_hybrid_forecast(request: HybridForecastRequest):
    """
    Get hybrid soil forecast combining Rule-Based and ML approaches.

    
    Args:
        request: Hybrid forecast request with soil data and parameters
    
    Returns:
        HybridForecastResponse with predictions from all three approaches:
        - Rule-Based (soil science knowledge)
        - Pure ML (Random Forest)
        - Hybrid (Rule + ML residual correction)
    """
    start_time = time.time()
    log_request("/api/soil/hybrid-forecast", "POST", {
        "request_type": "hybrid_forecast",
        "approach": request.approach,
        "forecast_horizon": request.forecast_horizon_days
    })
    
    try:
        response = await soil_service.hybrid_forecast(request)
        
        duration_ms = (time.time() - start_time) * 1000
        # Access Pydantic model attributes directly (not dict .get())
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


@router.post("/recommendations")
async def get_soil_recommendations(request: SoilAnalysisRequest):
    """
    Get soil improvement recommendations based on current conditions.
    
    Args:
        request: Soil analysis request
    
    Returns:
        Prioritized recommendations with expected improvements
    """
    start_time = time.time()
    log_request("/api/soil/recommendations", "POST", {"request_type": "recommendations"})
    
    try:
        response = await soil_service.get_recommendations(request)
        
        duration_ms = (time.time() - start_time) * 1000
        log_response("/api/soil/recommendations", 200, duration_ms=duration_ms)
        return response
    except ValueError as e:
        error_info = log_error(ValidationError(str(e)), {"endpoint": "/recommendations"})
        raise HTTPException(status_code=400, detail=error_info)
    except MLServiceError as e:
        error_info = log_error(e, {"endpoint": "/recommendations"})
        raise HTTPException(status_code=e.status_code, detail=error_info)
    except Exception as e:
        error_info = log_error(AnalysisError(f"Recommendations error: {str(e)}"), {"endpoint": "/recommendations"})
        raise HTTPException(status_code=500, detail=error_info)


@router.get("/status")
async def get_soil_service_status():
    """
    Check soil analysis service status.
    
    Returns:
        Service status and model information
    """
    return {
        "service": "soil_analysis",
        "ready": soil_service.is_ready(),
        "health_model_loaded": soil_service.health_model is not None if hasattr(soil_service, 'health_model') else False,
        "forecast_model_loaded": soil_service.forecast_model is not None if hasattr(soil_service, 'forecast_model') else False,
        "hybrid_model_loaded": soil_service.hybrid_forecast_model is not None and soil_service.hybrid_forecast_model.is_trained if hasattr(soil_service, 'hybrid_forecast_model') else False,
        "hybrid_model_version": soil_service.hybrid_forecast_model.version if hasattr(soil_service, 'hybrid_forecast_model') and soil_service.hybrid_forecast_model else None
    }

@router.post("/realign-forecast", response_model=RealignForecastResponse)
async def realign_forecast(request: RealignForecastRequest):
    """
    Realign an existing forecast based on new sensor data.
    
    Args:
        request: RealignForecastRequest with current data, existing forecast, and week
    
    Returns:
        RealignForecastResponse with updated forecast and deviation info
    """
    start_time = time.time()
    log_request("/api/soil/realign-forecast", "POST", {
        "request_type": "realign_forecast",
        "current_week": request.current_week
    })
    
    try:
        # Use the forecast realigner service
        result = forecast_realigner.realign_forecast(
            active_forecast=request.existing_forecast,
            new_reading=request.current_data,
            current_week=request.current_week
        )
        
        # Get health category from score
        health_score = result.get("health_score", 50.0)
        health_category = _get_health_category(health_score)
        
        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"Forecast realigned: week={request.current_week}, health_score={health_score:.1f}, requires_reforecast={result.get('requires_reforecast', False)}")
        log_response("/api/soil/realign-forecast", 200, duration_ms=duration_ms)
        
        return RealignForecastResponse(
            health_score=health_score,
            health_category=health_category,
            realignment_date=result.get("realignment_date", ""),
            week_of_realignment=result.get("week_of_realignment", request.current_week),
            requires_reforecast=result.get("requires_reforecast", False),
            deviations=result.get("deviations", {}),
            corrections_applied=result.get("corrections_applied", {}),
            forecast=result.get("updated_forecast", {}),
            weekly_summary=result.get("weekly_summary", [])
        )
    except ValueError as e:
        error_info = log_error(ValidationError(str(e)), {"endpoint": "/realign-forecast", "week": request.current_week})
        raise HTTPException(status_code=400, detail=error_info)
    except MLServiceError as e:
        error_info = log_error(e, {"endpoint": "/realign-forecast", "week": request.current_week})
        raise HTTPException(status_code=e.status_code, detail=error_info)
    except Exception as e:
        error_info = log_error(RealignmentError(f"Realignment error: {str(e)}"), {"endpoint": "/realign-forecast", "week": request.current_week})
        raise HTTPException(status_code=500, detail=error_info)


@router.post("/health-score", response_model=MLHealthScoreResponse)
async def calculate_health_score(request: HealthScoreRequest):
    """
    Calculate soil health score from provided data.
    
    This endpoint is called by the Backend to get a health score
    without generating a full forecast.
    
    Args:
        request: HealthScoreRequest with soil data
    
    Returns:
        HealthScoreResponse with score and category
    """
    start_time = time.time()
    log_request("/api/soil/health-score", "POST", {"request_type": "health_score"})
    
    try:
        # Calculate health score
        score = forecast_realigner._calculate_health_score(request.soil_data)
        category = _get_health_category(score)
        
        # Calculate individual parameter scores
        param_scores = {}
        for param in forecast_realigner.TARGET_PARAMETERS:
            value = forecast_realigner._extract_actual_value(request.soil_data, param)
            if value is not None:
                param_scores[param] = round(
                    forecast_realigner._param_score(
                        value,
                        forecast_realigner.OPTIMAL_RANGES.get(param, {
                            "min": 0, "max": 100, "optimal": 50
                        }) if hasattr(forecast_realigner, 'OPTIMAL_RANGES') else {
                            "min": 0, "max": 100, "optimal": 50
                        }
                    ) * 100, 1
                )
        
        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"Health score calculated: score={score:.1f}, category={category}")
        log_response("/api/soil/health-score", 200, duration_ms=duration_ms)
        
        return MLHealthScoreResponse(
            health_score=score,
            health_category=category,
            parameter_scores=param_scores
        )
    except ValueError as e:
        error_info = log_error(ValidationError(str(e)), {"endpoint": "/health-score"})
        raise HTTPException(status_code=400, detail=error_info)
    except MLServiceError as e:
        error_info = log_error(e, {"endpoint": "/health-score"})
        raise HTTPException(status_code=e.status_code, detail=error_info)
    except Exception as e:
        error_info = log_error(HealthScoreError(f"Health score error: {str(e)}"), {"endpoint": "/health-score"})
        raise HTTPException(status_code=500, detail=error_info)


def _get_health_category(score: float) -> str:
    """Get health category from score."""
    if score >= 85:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 55:
        return "Moderate"
    elif score >= 40:
        return "Poor"
    else:
        return "Critical"

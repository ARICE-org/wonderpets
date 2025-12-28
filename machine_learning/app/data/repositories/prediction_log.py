"""
Prediction Log Repository

Repository for logging and tracking ML predictions.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import logging
import json

from app.data.connectors.database import DatabaseConnector

logger = logging.getLogger(__name__)


class PredictionLogRepository:
    """
    Repository for prediction logging.
    
    Handles:
    - Logging predictions for monitoring
    - Storing prediction inputs/outputs
    - Tracking prediction performance
    - Audit trail for predictions
    """
    
    def __init__(self, db_connector: Optional[DatabaseConnector] = None):
        """
        Initialize prediction log repository.
        
        Args:
            db_connector: Database connector instance
        """
        self.db = db_connector or DatabaseConnector()
        self._logs: List[Dict[str, Any]] = []  # In-memory fallback
    
    def log_prediction(
        self,
        model_type: str,
        model_version: str,
        input_data: Dict[str, Any],
        prediction: Any,
        confidence: Optional[float] = None,
        user_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log a prediction for monitoring and audit.
        
        Args:
            model_type: Type of model (recommendation, weather, soil)
            model_version: Version of model used
            input_data: Input data for prediction
            prediction: Model prediction output
            confidence: Optional confidence score
            user_id: Optional user who requested prediction
            metadata: Optional additional metadata
            
        Returns:
            Prediction log ID
        """
        import uuid
        
        log_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "id": log_id,
            "model_type": model_type,
            "model_version": model_version,
            "input_data": input_data,
            "prediction": prediction,
            "confidence": confidence,
            "user_id": user_id,
            "metadata": metadata or {},
            "timestamp": timestamp,
            "feedback": None,
            "actual_outcome": None
        }
        
        # Try to persist to database
        try:
            self._persist_log(log_entry)
        except Exception as e:
            logger.warning(f"Failed to persist prediction log: {e}")
            # Store in memory as fallback
            self._logs.append(log_entry)
        
        logger.info(f"Logged prediction {log_id} for {model_type}")
        return log_id
    
    def log_recommendation(
        self,
        model_version: str,
        soil_data: Dict[str, Any],
        weather_data: Optional[Dict[str, Any]],
        location: Dict[str, float],
        recommendations: List[Dict[str, Any]],
        user_id: Optional[int] = None
    ) -> str:
        """
        Log a recommendation prediction.
        
        Args:
            model_version: Model version
            soil_data: Soil sensor data
            weather_data: Weather data
            location: Location coordinates
            recommendations: List of recommendations
            user_id: User ID
            
        Returns:
            Log ID
        """
        return self.log_prediction(
            model_type="recommendation",
            model_version=model_version,
            input_data={
                "soil_data": soil_data,
                "weather_data": weather_data,
                "location": location
            },
            prediction=recommendations,
            confidence=recommendations[0].get("confidence") if recommendations else None,
            user_id=user_id
        )
    
    def log_weather_forecast(
        self,
        model_version: str,
        location: Dict[str, float],
        horizon_days: int,
        forecast: List[Dict[str, Any]],
        user_id: Optional[int] = None
    ) -> str:
        """
        Log a weather forecast prediction.
        
        Args:
            model_version: Model version
            location: Location coordinates
            horizon_days: Forecast horizon
            forecast: Forecast data
            user_id: User ID
            
        Returns:
            Log ID
        """
        return self.log_prediction(
            model_type="weather",
            model_version=model_version,
            input_data={
                "location": location,
                "horizon_days": horizon_days
            },
            prediction=forecast,
            user_id=user_id,
            metadata={"forecast_days": len(forecast)}
        )
    
    def log_soil_analysis(
        self,
        model_version: str,
        soil_data: Dict[str, Any],
        health_score: float,
        analysis: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> str:
        """
        Log a soil health analysis.
        
        Args:
            model_version: Model version
            soil_data: Soil sensor data
            health_score: Overall health score
            analysis: Full analysis result
            user_id: User ID
            
        Returns:
            Log ID
        """
        return self.log_prediction(
            model_type="soil_health",
            model_version=model_version,
            input_data=soil_data,
            prediction=analysis,
            confidence=health_score / 100,  # Normalize to 0-1
            user_id=user_id,
            metadata={"health_score": health_score}
        )
    
    def add_feedback(
        self,
        log_id: str,
        feedback: str,
        rating: Optional[int] = None
    ) -> bool:
        """
        Add user feedback to a prediction log.
        
        Args:
            log_id: Prediction log ID
            feedback: User feedback text
            rating: Optional rating (1-5)
            
        Returns:
            True if feedback was added successfully
        """
        try:
            # Update in database
            query = """
                UPDATE prediction_logs
                SET feedback = :feedback,
                    feedback_rating = :rating,
                    feedback_timestamp = :timestamp
                WHERE id = :log_id
            """
            self.db.execute_query(query, {
                "log_id": log_id,
                "feedback": feedback,
                "rating": rating,
                "timestamp": datetime.now().isoformat()
            })
            return True
        except Exception as e:
            logger.error(f"Failed to add feedback: {e}")
            
            # Try in-memory fallback
            for log in self._logs:
                if log["id"] == log_id:
                    log["feedback"] = {
                        "text": feedback,
                        "rating": rating,
                        "timestamp": datetime.now().isoformat()
                    }
                    return True
            
            return False
    
    def add_actual_outcome(
        self,
        log_id: str,
        actual_outcome: Any
    ) -> bool:
        """
        Add actual outcome for model evaluation.
        
        Args:
            log_id: Prediction log ID
            actual_outcome: What actually happened
            
        Returns:
            True if outcome was added successfully
        """
        try:
            query = """
                UPDATE prediction_logs
                SET actual_outcome = :outcome,
                    outcome_timestamp = :timestamp
                WHERE id = :log_id
            """
            self.db.execute_query(query, {
                "log_id": log_id,
                "outcome": json.dumps(actual_outcome),
                "timestamp": datetime.now().isoformat()
            })
            return True
        except Exception as e:
            logger.error(f"Failed to add outcome: {e}")
            return False
    
    def get_predictions(
        self,
        model_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        user_id: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get prediction logs.
        
        Args:
            model_type: Filter by model type
            start_date: Start date filter
            end_date: End date filter
            user_id: Filter by user
            limit: Maximum records to return
            
        Returns:
            List of prediction logs
        """
        try:
            query = "SELECT * FROM prediction_logs WHERE 1=1"
            params = {}
            
            if model_type:
                query += " AND model_type = :model_type"
                params["model_type"] = model_type
            
            if start_date:
                query += " AND timestamp >= :start_date"
                params["start_date"] = start_date
            
            if end_date:
                query += " AND timestamp <= :end_date"
                params["end_date"] = end_date
            
            if user_id:
                query += " AND user_id = :user_id"
                params["user_id"] = user_id
            
            query += f" ORDER BY timestamp DESC LIMIT {limit}"
            
            return self.db.execute_query(query, params)
        except Exception as e:
            logger.error(f"Failed to get predictions: {e}")
            
            # Return from in-memory cache
            filtered = self._logs
            
            if model_type:
                filtered = [l for l in filtered if l["model_type"] == model_type]
            
            return filtered[:limit]
    
    def get_prediction_stats(
        self,
        model_type: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get statistics for predictions.
        
        Args:
            model_type: Model type to analyze
            days: Number of days to analyze
            
        Returns:
            Statistics dictionary
        """
        start_date = (
            datetime.now() - __import__("datetime").timedelta(days=days)
        ).isoformat()
        
        predictions = self.get_predictions(
            model_type=model_type,
            start_date=start_date,
            limit=10000
        )
        
        if not predictions:
            return {
                "total_predictions": 0,
                "period_days": days
            }
        
        # Calculate statistics
        confidences = [
            p.get("confidence") for p in predictions 
            if p.get("confidence") is not None
        ]
        
        feedback_count = sum(
            1 for p in predictions 
            if p.get("feedback") is not None
        )
        
        return {
            "total_predictions": len(predictions),
            "period_days": days,
            "avg_confidence": sum(confidences) / len(confidences) if confidences else None,
            "predictions_with_feedback": feedback_count,
            "feedback_rate": feedback_count / len(predictions) if predictions else 0
        }
    
    def _persist_log(self, log_entry: Dict[str, Any]) -> None:
        """Persist log entry to database."""
        query = """
            INSERT INTO prediction_logs 
            (id, model_type, model_version, input_data, prediction, 
             confidence, user_id, metadata, timestamp)
            VALUES 
            (:id, :model_type, :model_version, :input_data, :prediction,
             :confidence, :user_id, :metadata, :timestamp)
        """
        
        self.db.execute_query(query, {
            "id": log_entry["id"],
            "model_type": log_entry["model_type"],
            "model_version": log_entry["model_version"],
            "input_data": json.dumps(log_entry["input_data"]),
            "prediction": json.dumps(log_entry["prediction"]),
            "confidence": log_entry["confidence"],
            "user_id": log_entry["user_id"],
            "metadata": json.dumps(log_entry["metadata"]),
            "timestamp": log_entry["timestamp"]
        })

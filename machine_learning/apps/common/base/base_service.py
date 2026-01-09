"""
Abstract base class for all ML services.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BaseMLService(ABC):
    """
    Abstract base class for ML services.
    
    All services must implement initialize and is_ready methods.
    """
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self._initialized = False
        self._models: Dict[str, Any] = {}
    
    @abstractmethod
    async def initialize(self, model_path: str) -> None:
        """
        Initialize the service with required models.
        
        Args:
            model_path: Path to model artifacts
        """
        pass
    
    @abstractmethod
    def is_ready(self) -> bool:
        """Check if service is ready to handle requests."""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status information."""
        return {
            "service": self.service_name,
            "initialized": self._initialized,
            "ready": self.is_ready(),
            "models_loaded": list(self._models.keys())
        }
    
    def register_model(self, name: str, model: Any) -> None:
        """Register a model with the service."""
        self._models[name] = model
        logger.info(f"Registered model '{name}' with {self.service_name}")
    
    def get_model(self, name: str) -> Optional[Any]:
        """Get a registered model by name."""
        return self._models.get(name)

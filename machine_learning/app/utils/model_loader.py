"""
Model Loader Utility

Handles loading, saving, and managing trained ML models.
"""

import os
import json
import logging
from typing import Any, Dict, Optional, Type
from pathlib import Path
import joblib

logger = logging.getLogger(__name__)


class ModelLoader:
    """
    Utility class for loading and managing ML models.
    
    Handles:
    - Loading models from disk
    - Model version management
    - Model registry tracking
    - Model caching
    """
    
    def __init__(self, base_path: str):
        """
        Initialize the model loader.
        
        Args:
            base_path: Base directory for trained models
        """
        self.base_path = Path(base_path)
        self._cache: Dict[str, Any] = {}
        self._registry: Dict[str, Dict] = {}
        
        # Load registries if available
        self._load_registries()
    
    def load_model(
        self, 
        model_type: str, 
        version: Optional[str] = None,
        use_cache: bool = True
    ) -> Any:
        """
        Load a trained model.
        
        Args:
            model_type: Type of model (recommendation, weather, soil_health, soil_forecast)
            version: Specific version to load (None for current version)
            use_cache: Whether to use cached model
            
        Returns:
            Loaded model object
        """
        cache_key = f"{model_type}_{version or 'current'}"
        
        # Check cache first
        if use_cache and cache_key in self._cache:
            logger.debug(f"Loading {model_type} model from cache")
            return self._cache[cache_key]
        
        # Get model path
        model_path = self._get_model_path(model_type, version)
        
        if not model_path or not model_path.exists():
            logger.warning(f"Model not found: {model_type} v{version}")
            return None
        
        try:
            model = joblib.load(model_path)
            
            if use_cache:
                self._cache[cache_key] = model
            
            logger.info(f"Loaded model: {model_type} from {model_path}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load model {model_type}: {e}")
            raise
    
    def save_model(
        self, 
        model: Any, 
        model_type: str, 
        version: str,
        metrics: Optional[Dict[str, float]] = None,
        set_as_current: bool = True
    ) -> Path:
        """
        Save a trained model to disk.
        
        Args:
            model: Trained model object
            model_type: Type of model
            version: Version string
            metrics: Optional training metrics
            set_as_current: Whether to set as current version
            
        Returns:
            Path to saved model
        """
        from datetime import datetime
        
        # Create model directory
        model_dir = self.base_path / model_type
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"{model_type}_v{version}_{date_str}.pkl"
        model_path = model_dir / filename
        
        # Save model
        joblib.dump(model, model_path)
        logger.info(f"Saved model to {model_path}")
        
        # Update registry
        self._update_registry(
            model_type, version, filename, metrics, set_as_current
        )
        
        return model_path
    
    def get_model_info(self, model_type: str) -> Dict[str, Any]:
        """
        Get information about a model.
        
        Args:
            model_type: Type of model
            
        Returns:
            Model information including version and metrics
        """
        registry = self._registry.get(model_type, {})
        
        return {
            "model_type": model_type,
            "current_version": registry.get("current_version"),
            "available_versions": [
                m["version"] for m in registry.get("models", [])
            ],
            "current_model": next(
                (m for m in registry.get("models", []) 
                 if m["version"] == registry.get("current_version")),
                None
            )
        }
    
    def list_available_models(self) -> Dict[str, Dict]:
        """
        List all available models.
        
        Returns:
            Dictionary of model types and their info
        """
        available = {}
        
        for model_type in ["recommendation", "weather", "soil_health", "soil_forecast"]:
            model_dir = self.base_path / model_type
            
            if model_dir.exists():
                files = list(model_dir.glob("*.pkl"))
                available[model_type] = {
                    "available": len(files) > 0,
                    "files": [f.name for f in files],
                    "info": self.get_model_info(model_type)
                }
            else:
                available[model_type] = {
                    "available": False,
                    "files": [],
                    "info": None
                }
        
        return available
    
    def clear_cache(self, model_type: Optional[str] = None) -> None:
        """
        Clear model cache.
        
        Args:
            model_type: Specific model type to clear (None for all)
        """
        if model_type:
            keys_to_remove = [k for k in self._cache if k.startswith(model_type)]
            for key in keys_to_remove:
                del self._cache[key]
        else:
            self._cache.clear()
        
        logger.info(f"Cleared cache for: {model_type or 'all models'}")
    
    def _get_model_path(
        self, 
        model_type: str, 
        version: Optional[str]
    ) -> Optional[Path]:
        """Get the path to a model file."""
        model_dir = self.base_path / model_type
        
        if not model_dir.exists():
            return None
        
        # If version specified, find that version
        if version:
            registry = self._registry.get(model_type, {})
            for model_info in registry.get("models", []):
                if model_info["version"] == version:
                    return model_dir / model_info["file"]
        
        # Otherwise, get current version from registry
        registry = self._registry.get(model_type, {})
        current_version = registry.get("current_version")
        
        if current_version:
            for model_info in registry.get("models", []):
                if model_info["version"] == current_version:
                    return model_dir / model_info["file"]
        
        # Fallback: get most recent .pkl file
        pkl_files = sorted(model_dir.glob("*.pkl"), reverse=True)
        if pkl_files:
            return pkl_files[0]
        
        return None
    
    def _load_registries(self) -> None:
        """Load model registries from disk."""
        for model_type in ["recommendation", "weather", "soil_health", "soil_forecast"]:
            registry_path = self.base_path / model_type / "model_registry.json"
            
            if registry_path.exists():
                try:
                    with open(registry_path, "r") as f:
                        self._registry[model_type] = json.load(f)
                except Exception as e:
                    logger.warning(f"Failed to load registry for {model_type}: {e}")
    
    def _update_registry(
        self,
        model_type: str,
        version: str,
        filename: str,
        metrics: Optional[Dict[str, float]],
        set_as_current: bool
    ) -> None:
        """Update model registry after saving."""
        from datetime import datetime
        
        if model_type not in self._registry:
            self._registry[model_type] = {
                "current_version": None,
                "models": []
            }
        
        registry = self._registry[model_type]
        
        # Add new model entry
        model_entry = {
            "version": version,
            "file": filename,
            "trained_date": datetime.now().strftime("%Y-%m-%d"),
            "metrics": metrics or {}
        }
        
        registry["models"].append(model_entry)
        
        if set_as_current:
            registry["current_version"] = version
        
        # Save registry to disk
        registry_path = self.base_path / model_type / "model_registry.json"
        with open(registry_path, "w") as f:
            json.dump(registry, f, indent=2)

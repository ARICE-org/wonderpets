"""
Model I/O utilities for loading, saving, and managing ML models.
"""

import os
import json
import logging
from typing import Any, Dict, Optional, Type
from pathlib import Path
import joblib

logger = logging.getLogger(__name__)


class ModelIO:
    """
    Utility class for model input/output operations.
    
    Handles:
    - Loading models from disk (pickle, joblib, h5)
    - Saving models to disk
    - Model version management
    - Model registry tracking
    """
    
    SUPPORTED_FORMATS = [".pkl", ".joblib", ".h5", ".keras"]
    
    @staticmethod
    def save(model: Any, path: str, metadata: Optional[Dict] = None) -> str:
        """
        Save a model to disk.
        
        Args:
            model: Model object to save
            path: Full path including filename
            metadata: Optional metadata to save with model
            
        Returns:
            Path where model was saved
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Determine format from extension
        ext = path.suffix.lower()
        
        if ext in [".pkl", ".joblib"]:
            save_data = {"model": model}
            if metadata:
                save_data["metadata"] = metadata
            joblib.dump(save_data, path)
        elif ext in [".h5", ".keras"]:
            model.save(path)
            if metadata:
                meta_path = path.with_suffix(".meta.json")
                with open(meta_path, "w") as f:
                    json.dump(metadata, f, indent=2)
        else:
            raise ValueError(f"Unsupported format: {ext}")
        
        logger.info(f"Saved model to {path}")
        return str(path)
    
    @staticmethod
    def load(path: str) -> Any:
        """
        Load a model from disk.
        
        Args:
            path: Full path to model file
            
        Returns:
            Loaded model object
        """
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Model not found: {path}")
        
        ext = path.suffix.lower()
        
        if ext in [".pkl", ".joblib"]:
            data = joblib.load(path)
            if isinstance(data, dict) and "model" in data:
                return data["model"]
            return data
        elif ext in [".h5", ".keras"]:
            try:
                from tensorflow import keras
                return keras.models.load_model(path)
            except ImportError:
                logger.error("TensorFlow not available for loading .h5 models")
                raise
        else:
            raise ValueError(f"Unsupported format: {ext}")
    
    @staticmethod
    def load_with_metadata(path: str) -> tuple:
        """
        Load a model with its metadata.
        
        Args:
            path: Full path to model file
            
        Returns:
            Tuple of (model, metadata)
        """
        path = Path(path)
        ext = path.suffix.lower()
        
        if ext in [".pkl", ".joblib"]:
            data = joblib.load(path)
            if isinstance(data, dict):
                return data.get("model", data), data.get("metadata", {})
            return data, {}
        elif ext in [".h5", ".keras"]:
            model = ModelIO.load(path)
            meta_path = path.with_suffix(".meta.json")
            metadata = {}
            if meta_path.exists():
                with open(meta_path) as f:
                    metadata = json.load(f)
            return model, metadata
        else:
            raise ValueError(f"Unsupported format: {ext}")
    
    @staticmethod
    def get_latest_version(model_dir: str, model_prefix: str) -> Optional[str]:
        """
        Find the latest version of a model in a directory.
        
        Args:
            model_dir: Directory containing model files
            model_prefix: Prefix of model filename
            
        Returns:
            Path to latest version or None if not found
        """
        model_dir = Path(model_dir)
        if not model_dir.exists():
            return None
        
        # Find all matching files
        matches = []
        for ext in ModelIO.SUPPORTED_FORMATS:
            matches.extend(model_dir.glob(f"{model_prefix}*{ext}"))
        
        if not matches:
            return None
        
        # Sort by modification time and return latest
        latest = max(matches, key=lambda p: p.stat().st_mtime)
        return str(latest)
    
    @staticmethod
    def list_models(model_dir: str) -> Dict[str, Dict]:
        """
        List all models in a directory.
        
        Args:
            model_dir: Directory to scan
            
        Returns:
            Dictionary of model info
        """
        model_dir = Path(model_dir)
        if not model_dir.exists():
            return {}
        
        models = {}
        for ext in ModelIO.SUPPORTED_FORMATS:
            for path in model_dir.glob(f"*{ext}"):
                models[path.stem] = {
                    "path": str(path),
                    "size_mb": path.stat().st_size / (1024 * 1024),
                    "modified": path.stat().st_mtime,
                }
        
        return models

"""
Configuration settings for FuXi-S2S Model Service
"""

import os
from dataclasses import dataclass


@dataclass
class Settings:
    """Application settings loaded from environment."""
    
    # MongoDB
    mongo_uri: str = os.environ.get("MONGO_DB_URI", "mongodb://mongodb:27017")
    mongo_db: str = os.environ.get("MONGO_DB", "arice")
    
    # Service
    service_name: str = "fuxis2s-model"
    service_port: int = int(os.environ.get("PORT", 8002))
    debug: bool = os.environ.get("DEBUG", "false").lower() == "true"
    
    # Model paths
    model_path: str = os.environ.get("MODEL_PATH", "/app/model/fuxi_s2s.onnx")
    data_dir: str = os.environ.get("DATA_DIR", "/app/data")
    output_dir: str = os.environ.get("OUTPUT_DIR", "/app/output")
    
    # Inference defaults
    default_members: int = int(os.environ.get("DEFAULT_MEMBERS", 11))
    default_steps: int = int(os.environ.get("DEFAULT_STEPS", 42))
    default_station: str = os.environ.get("DEFAULT_STATION", "Pacol, Naga City")
    
    # Regional crop defaults (Philippines)
    crop_lat: float = float(os.environ.get("CROP_LAT", 13.58))
    crop_lon: float = float(os.environ.get("CROP_LON", 123.28))
    crop_radius: float = float(os.environ.get("CROP_RADIUS", 10.0))
    
    # Device
    device: str = os.environ.get("DEVICE", "cuda")


settings = Settings()

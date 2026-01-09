"""
Base classes for ML services.
"""

from apps.common.base.base_model import BaseMLModel
from apps.common.base.base_service import BaseMLService
from apps.common.base.base_trainer import BaseTrainer

__all__ = ["BaseMLModel", "BaseMLService", "BaseTrainer"]

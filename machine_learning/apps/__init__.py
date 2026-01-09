"""
ARICE ML Services - Apps Package

This package contains the modular, domain-driven ML services:
- soil_service: Soil health analysis and forecasting
- weather_service: Weather forecasting
- recommendation_service: Rice variety recommendations
- common: Shared utilities and base classes
- middleware: Common middleware components
- config: Global configuration
"""

from apps.config.settings import settings

__version__ = "2.0.0"
__all__ = ["settings"]

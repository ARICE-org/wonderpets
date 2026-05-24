"""MongoDB client singleton for Weather Service."""

import os
from functools import lru_cache
from pymongo import MongoClient

from app.config.settings import settings


@lru_cache(maxsize=1)
def get_mongo_client() -> MongoClient:
    """Get or create MongoDB client singleton."""
    return MongoClient(settings.mongo_uri)


def close_mongo_client():
    """Close MongoDB client connection."""
    get_mongo_client.cache_clear()

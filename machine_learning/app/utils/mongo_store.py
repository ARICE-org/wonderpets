"""MongoDB persistence utilities for FuXi-S2S station forecasts.

This module is intentionally small and dependency-light (PyMongo only).
It supports:
- Ensuring required collections + indexes exist
- Upserting a forecast run metadata document
- Bulk upserting station forecast documents (member-level and final)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable

import os


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_datetime(value: Any) -> datetime | None:
    if value is None:
        return None

    # Pandas Timestamp has to_pydatetime(); datetime is accepted directly.
    if hasattr(value, "to_pydatetime"):
        value = value.to_pydatetime()

    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value

    # Best-effort parse for strings like "2020-06-02" or ISO.
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed
        except Exception:
            return None

    return None


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        if hasattr(value, "item"):
            value = value.item()
        return float(value)
    except Exception:
        return None


@dataclass(frozen=True)
class MongoConfig:
    uri: str
    db_name: str = "arice"
    runs_collection: str = "forecast_runs"
    member_collection: str = "station_forecasts_member"
    final_collection: str = "station_forecasts_final"


class MongoForecastStore:
    def __init__(self, config: MongoConfig):
        from pymongo import MongoClient

        self.config = config
        self.client = MongoClient(config.uri)
        self.db = self.client[config.db_name]

        self.runs = self.db[config.runs_collection]
        self.member_fcst = self.db[config.member_collection]
        self.final_fcst = self.db[config.final_collection]

    @staticmethod
    def from_env(env_var: str = "MONGO_DB_URI", db_name: str = "arice") -> "MongoForecastStore":
        # 1) Direct environment variables (container/runtime)
        uri = os.environ.get(env_var)

        # 2) Common aliases used in other stacks
        if not uri:
            uri = os.environ.get("MONGODB_URI") or os.environ.get("MONGO_URI")

        # 3) Pydantic settings (loads env_file without exporting to os.environ)
        if not uri:
            try:
                from app.config.settings import settings

                uri = getattr(settings, env_var, None) or settings.MONGO_DB_URI
                db_name = getattr(settings, "MONGO_DB_NAME", db_name) or db_name
            except Exception:
                # Fall back to the original error below
                pass

        if not uri:
            raise ValueError(
                "Missing MongoDB connection string. Set MONGO_DB_URI (or MONGODB_URI/MONGO_URI). "
                "If you're running the ML service locally, ensure the repo .env is present and readable."
            )

        return MongoForecastStore(MongoConfig(uri=uri, db_name=db_name))

    def close(self) -> None:
        self.client.close()

    def ensure_indexes(self) -> None:
        # forecast_runs
        # _id already has an implicit unique index
        self.runs.create_index([("_id", 1)])
        self.runs.create_index([("init_date", 1), ("created_at", -1)])

        # member-level station forecasts
        self.member_fcst.create_index(
            [("run_id", 1), ("station.name", 1), ("member", 1), ("valid_time", 1)],
            unique=True,
        )
        self.member_fcst.create_index([("station.name", 1), ("valid_time", 1)])

        # final station forecasts
        self.final_fcst.create_index(
            [("run_id", 1), ("station.name", 1), ("valid_time", 1)],
            unique=True,
        )
        self.final_fcst.create_index([("station.name", 1), ("valid_time", 1)])

    def upsert_run(self, run_doc: dict[str, Any]) -> None:
        run_id = run_doc.get("_id")
        if not run_id:
            raise ValueError("run_doc must contain an '_id'")

        # Normalize timestamps
        for key in ("created_at", "init_time"):
            if key in run_doc:
                dt = _ensure_datetime(run_doc[key])
                if dt is not None:
                    run_doc[key] = dt

        self.runs.update_one({"_id": run_id}, {"$set": run_doc}, upsert=True)

    def bulk_upsert_member_forecasts(self, docs: Iterable[dict[str, Any]], batch_size: int = 2000) -> int:
        return self._bulk_upsert(self.member_fcst, docs, unique_keys=("run_id", "station.name", "member", "valid_time"), batch_size=batch_size)

    def bulk_upsert_final_forecasts(self, docs: Iterable[dict[str, Any]], batch_size: int = 2000) -> int:
        return self._bulk_upsert(self.final_fcst, docs, unique_keys=("run_id", "station.name", "valid_time"), batch_size=batch_size)

    def _bulk_upsert(self, collection, docs: Iterable[dict[str, Any]], unique_keys: tuple[str, ...], batch_size: int) -> int:
        from pymongo import UpdateOne

        ops: list[UpdateOne] = []
        total = 0

        def flush() -> None:
            nonlocal total, ops
            if not ops:
                return
            result = collection.bulk_write(ops, ordered=False)
            total += int(result.upserted_count) + int(result.modified_count)
            ops = []

        for doc in docs:
            normalized = self._normalize_forecast_doc(doc)

            filt: dict[str, Any] = {}
            for key in unique_keys:
                # support dotted keys like station.name
                if "." in key:
                    root, leaf = key.split(".", 1)
                    if root in normalized and isinstance(normalized[root], dict) and leaf in normalized[root]:
                        filt[key] = normalized[root][leaf]
                    else:
                        filt[key] = None
                else:
                    filt[key] = normalized.get(key)

            ops.append(UpdateOne(filt, {"$set": normalized}, upsert=True))
            if len(ops) >= batch_size:
                flush()

        flush()
        return total

    def _normalize_forecast_doc(self, doc: dict[str, Any]) -> dict[str, Any]:
        out = dict(doc)

        # Normalize common datetime fields
        for key in ("init_time", "valid_time"):
            if key in out:
                dt = _ensure_datetime(out[key])
                if dt is not None:
                    out[key] = dt

        # Ensure station numeric types are basic floats
        if "station" in out and isinstance(out["station"], dict):
            st = dict(out["station"])
            if "lat" in st:
                st["lat"] = _as_float(st.get("lat"))
            if "lon" in st:
                st["lon"] = _as_float(st.get("lon"))
            out["station"] = st

        return out

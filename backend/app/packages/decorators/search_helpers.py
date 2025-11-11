"""
Flexible search utilities for endpoints.

Provides a `searchable` decorator that extracts a `search` query parameter
and applies it to the function's return value. Works with:

- SQLAlchemy Query-like objects: returns a filtered Query (no .all() call)
- Python iterables/lists: returns a filtered list

The decorator is intentionally conservative: if it cannot infer entity/fields
for a SQLAlchemy Query it leaves the query unchanged. For lists it will
attempt to match fields on dicts or object attributes, or will fall back to
a string containment check on the whole item.

Example usage (FastAPI):

    from fastapi import APIRouter, Depends
    from sqlalchemy.orm import Session
    from app.dependencies import get_db
    from app.packages.decorators.search_helpers import searchable
    from app.models.soil_data import SoilData

    router = APIRouter()

    @router.get("/soil-data")
    @searchable(fields=["sensor_id"], mode="ilike")
    def list_soil(db: Session = Depends(get_db), search: str = None):
        # return a Query so that pagination can be applied later
        return db.query(SoilData)

Notes:
- The decorator only extracts the search value from the wrapped endpoint's
  kwargs (so the endpoint should accept a `search` query parameter).
- For SQLAlchemy-based filtering it prefers `ilike` when available.
"""
from functools import wraps
from typing import Any, Callable, Iterable, List, Optional
import inspect

try:
    # Use SQLAlchemy constructs when available
    from sqlalchemy import or_
    # ORM Query and core Select detection
    try:
        from sqlalchemy.orm import Query as SAQuery
    except Exception:
        SAQuery = None
    try:
        from sqlalchemy.sql import Select as SASelect
    except Exception:
        SASelect = None
    # common string-like column types
    try:
        from sqlalchemy import String, Text
    except Exception:
        String = Text = None

    SA_AVAILABLE = True
except Exception:
    SA_AVAILABLE = False


def _is_sa_query(obj: Any) -> bool:
    """Rudimentary check for a SQLAlchemy Query/Select-like object.

    Tries to detect common SQLAlchemy query/select objects. Falls back to a
    heuristic for objects exposing `column_descriptions` and `filter`.
    """
    if not SA_AVAILABLE:
        return False

    try:
        # Prefer isinstance checks when available
        if SAQuery is not None and isinstance(obj, SAQuery):
            return True
        # Core Select (sqlalchemy.select(...)) detection
        if SASelect is not None and isinstance(obj, SASelect):
            return True
    except Exception:
        pass

    # Fallback heuristic
    return hasattr(obj, "column_descriptions") and hasattr(obj, "filter")


def searchable(
    fields: Optional[List[str]] = None,
    mode: str = "ilike",
    param_name: str = "search",
    model: Optional[type] = None,
) -> Callable:
    """
    Decorator factory that applies basic search filtering.

    Args:
        fields: Optional list of field names to search. For SQLAlchemy queries the
            names should be attributes on the mapped entity. For iterables those
            are keys (for dicts) or attribute names (for objects).
        mode: One of 'ilike', 'like', or 'exact'. Controls SQLAlchemy filter
            behavior and the matching performed for iterable-based results.
        param_name: Name of the keyword arg that carries the search string.
        model: Optional SQLAlchemy model class to use for query filtering.

    Returns:
        A decorator which wraps endpoint functions (sync or async).
    """

    def decorator(func: Callable) -> Callable:
        is_coroutine = inspect.iscoroutinefunction(func)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            search_value = kwargs.get(param_name)
            result = await func(*args, **kwargs)
            return _apply_search(result, search_value, fields, mode, model)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            search_value = kwargs.get(param_name)
            result = func(*args, **kwargs)
            return _apply_search(result, search_value, fields, mode, model)

        return async_wrapper if is_coroutine else sync_wrapper

    return decorator


def _apply_search(
    result: Any,
    search_value: Optional[str],
    fields: Optional[List[str]],
    mode: str,
    model: Optional[type] = None,
) -> Any:
    """
    Apply search to the given result. If `result` is a SQLAlchemy Query-like
    object, returns a filtered Query. If it's an iterable, returns a filtered
    list. If `search_value` is falsy, returns `result` unchanged.
    """
    if not search_value:
        return result

    # SQLAlchemy Query path
    if _is_sa_query(result):
        try:
            # Try to detect the mapped entity from the query description
            desc = getattr(result, "column_descriptions", None)
            entity = None
            # Prefer explicit model passed to decorator
            if model is not None:
                entity = model
            else:
                if desc and len(desc) > 0:
                    entity = desc[0].get("entity")

            if entity is None:
                # Could not infer entity -> return original query
                return result

            # Determine which fields to search
            if fields:
                search_fields = fields
            else:
                # Try to pick text-like columns from the mapped table
                try:
                    cols = getattr(entity, "__table__").columns
                    # Best-effort: include columns that have string-like SQLAlchemy types
                    def is_text_col(c):
                        try:
                            if String is not None and isinstance(c.type, String):
                                return True
                            if Text is not None and isinstance(c.type, Text):
                                return True
                            # Fallback to python_type check when available
                            return getattr(c.type, "python_type", None) is str
                        except Exception:
                            return False

                    search_fields = [c.name for c in cols if is_text_col(c)]
                except Exception:
                    search_fields = []

            if not search_fields:
                return result

            filters = []
            for f in search_fields:
                col = getattr(entity, f, None)
                if col is None:
                    continue
                if mode == "exact":
                    filters.append(col == search_value)
                elif mode == "like":
                    filters.append(col.like(f"%{search_value}%"))
                else:
                    # default: ilike when supported
                    ilike_fn = getattr(col, "ilike", None)
                    if ilike_fn is not None:
                        filters.append(col.ilike(f"%{search_value}%"))
                    else:
                        filters.append(col.like(f"%{search_value}%"))

            if filters:
                return result.filter(or_(*filters))
            return result
        except Exception:
            # If anything goes wrong with SQLAlchemy reflection, return original
            return result

    # Iterable/list path
    try:
        if isinstance(result, Iterable) and not isinstance(result, (str, bytes)):
            items = list(result)
        else:
            return result
    except Exception:
        return result

    sv_lower = str(search_value).lower()

    if not fields:
        # Fallback: string-containment on the whole item rendering
        def match_any(item: Any) -> bool:
            try:
                return sv_lower in str(item).lower()
            except Exception:
                return False
    else:
        def match_fields(item: Any) -> bool:
            for f in fields:
                try:
                    val = None
                    if isinstance(item, dict):
                        val = item.get(f)
                    else:
                        val = getattr(item, f, None)
                    if val is None:
                        continue
                    if mode == "exact":
                        if str(val) == search_value:
                            return True
                    else:
                        if sv_lower in str(val).lower():
                            return True
                except Exception:
                    continue
            return False

        def match_any(item: Any) -> bool:
            return match_fields(item)

    filtered = [it for it in items if match_any(it)]
    return filtered

"""Helper functions for weather data processing."""

from datetime import datetime
from typing import Any, Optional


# Map variable keys to readable names
VARIABLE_MAP = {
    "tp_mm": "rainfall_mm",
    "t2m_c": "temperature_c",
    "d2m_c": "dewpoint_c",
    "msl_pa": "pressure_pa",
    "u10": "wind_u10",
    "v10": "wind_v10",
    "wind_speed": "wind_speed_ms",
    "wind_direction_deg": "wind_direction_deg",
}


def get_weekday(dt_str: Optional[str]) -> Optional[str]:
    """Convert datetime string to weekday name (Monday, Tuesday, etc.)."""
    if not dt_str:
        return None
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%A")
    except Exception:
        return None


def wind_direction_label(deg: float) -> str:
    """Convert wind direction in degrees to 16-point compass label."""
    dirs = [
        "North", "North-Northeast", "Northeast", "East-Northeast",
        "East", "East-Southeast", "Southeast", "South-Southeast",
        "South", "South-Southwest", "Southwest", "West-Southwest",
        "West", "West-Northwest", "Northwest", "North-Northwest",
    ]
    ix = int((deg + 11.25) % 360 / 22.5)
    return dirs[ix]


def format_value(key: str, value: float) -> str:
    """Format weather variable values for human readability."""
    if key == "rainfall_mm":
        return f"{value:.2f} mm"
    elif key == "temperature_c":
        return f"{value:.1f} °C"
    elif key == "dewpoint_c":
        return f"{value:.1f} °C"
    elif key == "pressure_pa":
        return f"{value:,.0f} Pa"
    elif key == "wind_speed_ms":
        # Convert m/s to km/h
        return f"{value * 3.6:.1f} km/h"
    elif key in ("wind_u10", "wind_v10"):
        return f"{value:.2f}"
    elif key == "wind_direction_deg":
        return f"{value:.0f}°"
    else:
        return str(value)


def classify_weather(variables: dict[str, Any]) -> str:
    """Classify weather condition based on variables."""
    rain = variables.get("tp_mm", 0)
    temp = variables.get("t2m_c", 0)

    if rain >= 1.0:
        return "Rainy"
    elif rain > 0.1:
        return "Showers"
    elif temp < 18:
        return "Cool"
    else:
        return "Clear"


def process_forecast(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Process raw forecast data into human-readable format."""
    processed = []

    for f in data.get("forecasts", []):
        valid_time = f.get("valid_time")
        variables = f.get("variables", {})

        entry: dict[str, Any] = {
            "datetime": valid_time,
            "weekdate": get_weekday(valid_time),
        }

        for k, v in variables.items():
            readable = VARIABLE_MAP.get(k, k)
            if not readable:
                continue

            if readable == "wind_speed_ms":
                entry[readable] = format_value(readable, v)
                entry["wind_speed_kmh"] = f"{v * 3.6:.1f} km/h"
            elif readable == "wind_direction_deg":
                entry[readable] = format_value(readable, v)
                entry["wind_direction"] = wind_direction_label(v)
            else:
                entry[readable] = format_value(readable, v)

        entry["weather"] = classify_weather(variables)
        processed.append(entry)

    return processed

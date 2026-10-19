"""Weather triggers from the free US National Weather Service API (no key needed).

A cold snap or heat wave in a lead's city is the best possible reason to email
an HVAC owner *this week*: their phones are about to blow up and they know it.
"""

import json
import urllib.request

from .models import Lead

NWS_BASE = "https://api.weather.gov"


def _get_json(url: str, user_agent: str, timeout: float = 15.0) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": user_agent, "Accept": "application/geo+json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_periods(lat: float, lon: float, user_agent: str, getter=_get_json) -> list[dict]:
    """The 7-day forecast periods (day and night) for a point."""
    point = getter(f"{NWS_BASE}/points/{lat:.4f},{lon:.4f}", user_agent)
    forecast_url = point["properties"]["forecast"]
    return getter(forecast_url, user_agent)["properties"]["periods"]


def _fahrenheit(period: dict) -> int:
    temp = period["temperature"]
    if isinstance(temp, dict):  # newer NWS payloads: {"unitCode": "wmoUnit:degC", "value": -3}
        value = temp.get("value")
        unit = "C" if "degC" in str(temp.get("unitCode", "")) else "F"
    else:
        value, unit = temp, period.get("temperatureUnit", "F")
    return round(value * 9 / 5 + 32) if unit == "C" else round(value)


def extremes(periods: list[dict]) -> tuple[int | None, str, int | None, str]:
    """(coldest night temp, its name, hottest day temp, its name)."""
    nights = [p for p in periods if not p.get("isDaytime", True) and p.get("temperature") is not None]
    days = [p for p in periods if p.get("isDaytime", False) and p.get("temperature") is not None]
    low = min(nights, key=_fahrenheit) if nights else None
    high = max(days, key=_fahrenheit) if days else None
    return (
        _fahrenheit(low) if low else None,
        low["name"] if low else "",
        _fahrenheit(high) if high else None,
        high["name"] if high else "",
    )


def apply_weather(leads: list[Lead], user_agent: str, getter=_get_json, progress=None) -> tuple[int, int]:
    """Fill forecast fields for every lead with coordinates.

    Leads are grouped to ~10 km cells so a metro with 300 shops costs 2 API calls.
    Returns (leads updated, failed cells).
    """
    cells: dict[tuple[float, float], list[Lead]] = {}
    for lead in leads:
        if lead.lat is not None and lead.lon is not None:
            cells.setdefault((round(lead.lat, 1), round(lead.lon, 1)), []).append(lead)
    updated = failed = 0
    for index, ((lat, lon), group) in enumerate(cells.items(), start=1):
        try:
            low, low_name, high, high_name = extremes(fetch_periods(lat, lon, user_agent, getter))
        except Exception:  # NWS is free and occasionally flaky; skip the cell, keep going
            failed += 1
            continue
        for lead in group:
            lead.forecast_low_f, lead.forecast_low_when = low, low_name
            lead.forecast_high_f, lead.forecast_high_when = high, high_name
            updated += 1
        if progress:
            progress(index, len(cells))
    return updated, failed

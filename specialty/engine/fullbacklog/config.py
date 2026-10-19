"""Engine settings. Copy config.example.toml to config.toml and edit it."""

import copy
import os
import tomllib
from pathlib import Path

DEFAULTS: dict = {
    "sender": {
        "first_name": "Jordan",
        "agency": "FullBacklog",
        "calendar_link": "https://cal.com/your-link/15min",
        "website": "https://getfullbacklog.com",
    },
    "targeting": {
        # Trades we sell to first (keys from fullbacklog/trades.py).
        "trades": ["drywall", "painting", "flooring", "electrical", "concrete", "glazing",
                   "fire_protection", "roofing", "insulation", "masonry"],
        "min_export_score": 35,
        # Permit window used for market stats and hooks.
        "permit_days": 90,
        # Permits with no clear commercial/residential wording count as commercial at or above this value.
        "min_commercial_value": 250000,
        # Optional fixed "today" for permit windows (YYYY-MM-DD); empty means today.
        "as_of": "",
    },
    # Market (metro) -> the cities in it. A lead in Round Rock gets Austin's permit data.
    "markets": {},
    "ai": {
        "model": "claude-opus-5-5",
        "effort": "low",
        "workers": 4,
    },
}


def _merge(base: dict, override: dict) -> dict:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path: str | None = None) -> dict:
    for candidate in (path, os.environ.get("FULLBACKLOG_CONFIG"), "config.toml"):
        if candidate and Path(candidate).is_file():
            with open(candidate, "rb") as handle:
                return _merge(DEFAULTS, tomllib.load(handle))
    return copy.deepcopy(DEFAULTS)

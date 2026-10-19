"""Engine settings. Copy config.example.toml to config.toml and edit it."""

import copy
import os
import tomllib
from pathlib import Path

DEFAULTS: dict = {
    "sender": {
        "first_name": "Jordan",
        "agency": "BookedOut",
        "calendar_link": "https://cal.com/your-link/15min",
        "demo_line": "(555) 010-0199",
        "website": "https://getbookedout.com",
    },
    "targeting": {
        # A forecast at or below this (F) switches a lead to the cold-snap sequence.
        "cold_threshold_f": 25,
        # A forecast at or above this (F) switches a lead to the heat-wave angle.
        "hot_threshold_f": 95,
        # Leads below this score are not exported to email.
        "min_export_score": 35,
    },
    "ai": {
        "model": "claude-opus-5-5",
        "effort": "low",
        "workers": 4,
    },
    "nws": {
        # api.weather.gov asks for a User-Agent with contact info.
        "user_agent": "BookedOut outreach engine (contact: you@example.com)",
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
    candidates = [path, os.environ.get("BOOKEDOUT_CONFIG"), "config.toml"]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            with open(candidate, "rb") as handle:
                return _merge(DEFAULTS, tomllib.load(handle))
    return copy.deepcopy(DEFAULTS)

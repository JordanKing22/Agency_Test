"""Specialty trades, their CSI MasterFormat division, and how to recognize them."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Trade:
    key: str
    label: str      # used in copy: "commercial {label} subs"
    division: str   # CSI MasterFormat division
    pattern: str


# Order matters: more specific trades first ("fire sprinkler" before "plumbing").
TRADES = [
    Trade("fire_protection", "fire protection", "21", r"fire (?:protection|sprinkler)|sprinkler"),
    Trade("electrical", "electrical", "26", r"electric"),
    Trade("drywall", "drywall and framing", "09", r"drywall|gypsum|metal stud|acoustical|ceilings?\b|interior systems|framing"),
    Trade("painting", "painting", "09", r"painting|painters|wallcovering|coatings"),
    Trade("flooring", "flooring", "09", r"flooring|floor covering|carpet|terrazzo|resilient|\btile\b"),
    Trade("glazing", "glass and glazing", "08", r"glazing|glass|curtain ?wall|storefront"),
    Trade("concrete", "concrete", "03", r"concrete|flatwork|tilt-?up|foundations?\b"),
    Trade("masonry", "masonry", "04", r"masonry|brick|\bblock\b|stone"),
    Trade("roofing", "commercial roofing", "07", r"roofing|roofers?\b"),
    Trade("insulation", "insulation", "07", r"insulation|spray foam|firestop"),
    Trade("steel", "structural steel", "05", r"steel|iron ?works|metal fabricat|welding"),
    Trade("mechanical", "mechanical", "23", r"mechanical|hvac|sheet metal"),
    Trade("plumbing", "plumbing", "22", r"plumb"),
    Trade("earthwork", "sitework", "31", r"excavat|earthwork|site ?work|grading|underground utilit"),
]
BY_KEY = {trade.key: trade for trade in TRADES}
UNKNOWN_LABEL = "specialty"


def detect_trade(*texts: str, page: str = "") -> str:
    """Trade key from category/company (first match), else the most-mentioned trade on the page."""
    for text in texts:
        for trade in TRADES:
            if text and re.search(trade.pattern, text, re.I):
                return trade.key
    if page:
        counts = {trade.key: len(re.findall(trade.pattern, page, re.I)) for trade in TRADES}
        best = max(counts, key=counts.get)
        if counts[best] >= 2:
            return best
    return ""


def trade_label(key: str) -> str:
    return BY_KEY[key].label if key in BY_KEY else UNKNOWN_LABEL


def trade_division(key: str) -> str:
    return BY_KEY[key].division if key in BY_KEY else ""

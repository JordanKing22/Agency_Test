"""ICP scoring: who to call first and who gets the email budget.

Ideal client: an owner-operated HVAC shop with 3-30 trucks, a real review
footprint, paying for leads (ads / call tracking), and no system catching
after-hours calls. Franchises with corporate call centers are a poor fit.
"""

import re

from .models import Lead

HVAC_RE = re.compile(r"hvac|heating|cooling|air condition|furnace|heat pump|mechanical|refrigeration|comfort|boiler", re.I)
ADJACENT_RE = re.compile(r"plumb|electric|home services|drain|water heater", re.I)
NATIONAL_BRANDS = (
    "one hour heating", "service experts", "ars rescue rooter", "aire serv", "benjamin franklin plumbing",
    "mr. rooter", "lennox stores", "sears home", "home depot", "trane supply", "carrier enterprise",
)


def score_lead(lead: Lead, cold_threshold_f: int = 25, hot_threshold_f: int = 95) -> tuple[int, list[str]]:
    """Return (0-100 score, reasons) so the call sheet can explain the ranking."""
    points = 0
    reasons: list[str] = []

    def add(value: int, why: str) -> None:
        nonlocal points
        points += value
        reasons.append(f"{value:+d} {why}")

    haystack = f"{lead.category} {lead.company}"
    if any(brand in lead.company.lower() for brand in NATIONAL_BRANDS):
        add(-30, "national franchise / corporate call center")
    if HVAC_RE.search(haystack):
        add(15, "HVAC company")
    elif ADJACENT_RE.search(haystack):
        add(5, "adjacent trade")

    if lead.email:
        add(12, "has email")
    if lead.phone:
        add(5, "has phone")
    if lead.first_name:
        add(4, "named contact")

    reviews = lead.reviews or 0
    if 1000 <= reviews:
        add(10, f"{reviews} reviews (large shop)")
    elif 200 <= reviews:
        add(18, f"{reviews} reviews")
    elif 50 <= reviews:
        add(14, f"{reviews} reviews")
    elif 15 <= reviews:
        add(6, f"{reviews} reviews")
    if (lead.rating or 0) >= 4.5 and reviews >= 15:
        add(4, f"{lead.rating} rating")

    if lead.runs_google_ads:
        add(14, "runs Google Ads (pays per call)")
    if lead.call_tracking:
        add(5, f"uses {lead.call_tracking}")
    if lead.scanned_at and lead.site_ok:
        if not lead.booking_vendor:
            add(6, "no online booking")
        if not lead.chat_vendor:
            add(6, "no chat widget")
    if lead.scanned_at and lead.site_ok == 0:
        add(-5, "website down")
    if lead.has_financing:
        add(3, "offers financing (replacement volume)")
    if lead.has_membership:
        add(3, "sells maintenance plans")

    if lead.audit_result in ("voicemail", "no_answer", "ivr"):
        add(20, f"after-hours audit: {lead.audit_result}")
    elif lead.audit_result == "answering_service":
        add(8, "after-hours audit: answering service")
    elif lead.audit_result == "answered":
        add(-5, "after-hours audit: answered live")
    elif lead.audit_result == "disconnected":
        add(-40, "phone disconnected")

    if lead.forecast_low_f is not None and lead.forecast_low_f <= cold_threshold_f:
        add(10, f"cold snap: {lead.forecast_low_f}F {lead.forecast_low_when}")
    elif lead.forecast_high_f is not None and lead.forecast_high_f >= hot_threshold_f:
        add(10, f"heat wave: {lead.forecast_high_f}F {lead.forecast_high_when}")

    return max(0, min(100, points)), reasons


def tier_for(score: int) -> str:
    if score >= 70:
        return "A"
    if score >= 50:
        return "B"
    return "C"


def apply_scores(leads: list[Lead], cold_threshold_f: int = 25, hot_threshold_f: int = 95) -> None:
    for lead in leads:
        lead.score, _ = score_lead(lead, cold_threshold_f, hot_threshold_f)
        lead.tier = tier_for(lead.score)

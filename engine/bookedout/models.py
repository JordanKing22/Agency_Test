"""The Lead record. One row per HVAC company (we sell to the owner)."""

from dataclasses import dataclass, fields

STATUSES = (
    "new",            # imported, never contacted
    "in_sequence",    # exported to the cold email tool
    "called",         # dialed at least once (see events for history)
    "replied",        # any reply that isn't a hard no
    "interested",     # positive reply / warm on the phone
    "booked",         # sales call on the calendar
    "showed",         # sales call happened
    "proposal",       # offer sent, waiting on payment
    "won",            # paid
    "lost",           # said no after a real conversation
    "not_fit",        # wrong niche, too small, franchise, closed
    "do_not_contact", # asked to be removed - never export again
)

# Statuses that remove a lead from cold outreach (email export and call sheets).
SUPPRESSED = {"replied", "interested", "booked", "showed", "proposal", "won", "lost", "not_fit", "do_not_contact"}

AUDIT_RESULTS = ("answered", "voicemail", "no_answer", "ivr", "answering_service", "disconnected")


@dataclass
class Lead:
    id: str = ""
    company: str = ""
    first_name: str = ""
    last_name: str = ""
    title: str = ""
    email: str = ""
    phone: str = ""
    website: str = ""
    domain: str = ""
    city: str = ""
    state: str = ""
    lat: float | None = None
    lon: float | None = None
    rating: float | None = None
    reviews: int | None = None
    category: str = ""
    linkedin: str = ""
    source: str = ""
    # Website signals (filled by `scan`)
    scanned_at: str = ""
    site_ok: int | None = None
    chat_vendor: str = ""
    booking_vendor: str = ""
    runs_google_ads: int | None = None
    has_fb_pixel: int | None = None
    call_tracking: str = ""
    mentions_24_7: int | None = None
    has_financing: int | None = None
    has_membership: int | None = None
    # After-hours audit (filled by `audit` / `audit-import`)
    audit_result: str = ""
    audit_time: str = ""
    # Weather (filled by `weather`)
    forecast_low_f: int | None = None
    forecast_low_when: str = ""
    forecast_high_f: int | None = None
    forecast_high_when: str = ""
    # Outreach
    score: int | None = None
    tier: str = ""
    sequence: str = ""
    personalization: str = ""
    personalization_source: str = ""
    status: str = "new"
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""


LEAD_FIELDS = [f.name for f in fields(Lead)]
LEAD_TYPES = {f.name: f.type for f in fields(Lead)}


def is_empty(value) -> bool:
    return value is None or (isinstance(value, str) and value.strip() == "")

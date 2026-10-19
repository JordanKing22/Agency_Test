"""Records: a Lead is one subcontractor we sell to; a Permit is one public building permit."""

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
    "not_fit",        # residential-only, wrong trade, too big, closed
    "do_not_contact", # asked to be removed - never export again
)

# Statuses that remove a lead from cold outreach (email export and call sheets).
SUPPRESSED = {"replied", "interested", "booked", "showed", "proposal", "won", "lost", "not_fit", "do_not_contact"}


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
    market: str = ""
    category: str = ""
    trade: str = ""
    employees: int | None = None
    rating: float | None = None
    reviews: int | None = None
    linkedin: str = ""
    source: str = ""
    # Website signals (filled by `scan`)
    scanned_at: str = ""
    site_ok: int | None = None
    commercial_hits: int | None = None
    residential_hits: int | None = None
    certifications: str = ""     # comma-separated, e.g. "WBE, DBE"
    union_shop: int | None = None
    mentions_safety: int | None = None
    mentions_bonding: int | None = None
    hiring: int | None = None
    has_portfolio: int | None = None
    project_types: str = ""      # comma-separated, e.g. "healthcare, education"
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


@dataclass
class Permit:
    id: str = ""
    market: str = ""
    city: str = ""
    permit_no: str = ""
    permit_type: str = ""
    description: str = ""
    contractor: str = ""      # as written on the permit
    contractor_key: str = ""  # normalized for grouping
    valuation: float | None = None
    issued: str = ""          # YYYY-MM-DD
    address: str = ""
    commercial: int | None = None


LEAD_FIELDS = [f.name for f in fields(Lead)]
LEAD_TYPES = {f.name: f.type for f in fields(Lead)}
PERMIT_FIELDS = [f.name for f in fields(Permit)]
PERMIT_TYPES = {f.name: f.type for f in fields(Permit)}


def is_empty(value) -> bool:
    return value is None or (isinstance(value, str) and value.strip() == "")


def split_list(value: str) -> list[str]:
    return [item.strip() for item in (value or "").split(",") if item.strip()]

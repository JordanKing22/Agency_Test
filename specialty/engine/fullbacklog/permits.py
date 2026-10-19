"""Turn public building permits into a GC leaderboard per market.

Who pulled the most commercial permits in a market over the last 90 days is
public record, and it answers the question every sub cares about: which
general contractors have work right now, and am I bidding for them?

Used two ways:
  * selling: "47 commercial permits in Austin last quarter; Halvorsen pulled 9. Are you on their list?"
  * delivering: the ranked GC list is the target list for a client's bid-list sprint.
"""

import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta

from .models import Permit

COMMERCIAL_RE = re.compile(
    r"commercial|non-?residential|tenant (?:improvement|finish|build)|\bt\.?i\.?\b|office|retail|restaurant|"
    r"warehouse|industrial|hospital|medical|clinic|school|universit|college|hotel|church|mixed[- ]use|"
    r"multi-?family|apartment|data cent|laborator|manufactur|shell|assembly|mercantile|storage facility|"
    r"distribution|fire station|library|parking (?:garage|structure)|senior living|dormitor",
    re.I,
)
RESIDENTIAL_RE = re.compile(
    r"single[- ]family|\bsfr\b|\bsfd\b|duplex|townho|residential|dwelling|\badu\b|garage|\bdeck\b|"
    r"swimming pool|\bpool\b|fence|patio|re-?roof|kitchen|bath(?:room)?\b|carport|shed",
    re.I,
)
NON_RESIDENTIAL_RE = re.compile(r"non-?residential", re.I)
# Permit types pulled by trade subs, not GCs; leave them out of the GC leaderboard.
TRADE_PERMIT_RE = re.compile(
    r"^\s*(electric|plumb|mechanic|hvac|fire|sign|demoli|elevator|gas|boiler|sprinkler|low[- ]voltage|solar|irrigation)",
    re.I,
)
NOT_A_CONTRACTOR = {"", "OWNER", "OWNER BUILDER", "HOMEOWNER", "SELF", "NA", "N A", "NONE", "TBD", "UNKNOWN",
                    "NOT APPLICABLE", "PROPERTY OWNER", "OWNER AS CONTRACTOR"}
SUFFIX_RE = re.compile(r"\b(INC|INCORPORATED|LLC|L L C|CO|CORP|CORPORATION|COMPANY|LTD|LP|LLP|PLLC|THE)\b")


def contractor_key(name: str) -> str:
    """Normalize a contractor name so 'Halvorsen Builders, Inc.' and 'HALVORSEN BUILDERS INC' group together."""
    text = re.sub(r"[^A-Z0-9& ]", " ", (name or "").upper())
    text = re.sub(r"\bGENERAL CONTRACT(?:ORS?|ING)\b", "GC", text)
    text = re.sub(r"\bAND\b", "&", text)
    text = SUFFIX_RE.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return "" if text in NOT_A_CONTRACTOR else text


def same_contractor(key: str, other: str) -> bool:
    """'MARROW & PIKE GC' matches 'MARROW & PIKE': equal, or one is the other plus extra words."""
    if not key or not other:
        return False
    return key == other or key.startswith(other + " ") or other.startswith(key + " ")


def display_name(variants: list[str]) -> str:
    """Most common spelling, cleaned up and un-shouted."""
    name = Counter(v.strip() for v in variants if v.strip()).most_common(1)[0][0]
    name = re.sub(r"[,\s]+(llc|l\.l\.c\.|inc\.?|corp\.?|co\.?|ltd\.?|lp)\s*$", "", name, flags=re.I).strip()
    if name.isupper():
        keep = lambda w: not w.isalpha() or (len(w) <= 3 and w not in {"AND", "THE"})  # J&B, ABC, DPR
        name = " ".join(w if keep(w) else w.capitalize() for w in name.split())
    return name


def classify_commercial(permit: Permit, min_value: float = 250_000) -> bool:
    if TRADE_PERMIT_RE.search(permit.permit_type or ""):
        return False
    text = f"{permit.permit_type} {permit.description}"
    commercial = len(COMMERCIAL_RE.findall(text))
    residential = len(RESIDENTIAL_RE.findall(NON_RESIDENTIAL_RE.sub(" ", text)))
    if commercial and commercial >= residential:
        return True
    if residential:
        return False
    return (permit.valuation or 0) >= min_value


@dataclass
class GCRow:
    key: str
    name: str
    permits: int = 0
    value: float = 0.0
    last_issued: str = ""
    largest_value: float = 0.0
    largest_desc: str = ""
    variants: list[str] = field(default_factory=list)


@dataclass
class MarketStats:
    market: str
    days: int
    permits: int
    value: float
    leaders: list[GCRow]

    def top_names(self, n: int = 3) -> list[str]:
        return [row.name for row in self.leaders[:n]]


def leaderboard(permits: list[Permit], as_of: date | None = None, days: int = 90, market: str = "") -> MarketStats:
    """Rank contractors by commercial permit value issued in the window."""
    as_of = as_of or date.today()
    start = (as_of - timedelta(days=days)).isoformat()
    end = as_of.isoformat()
    rows: dict[str, GCRow] = {}
    count = 0
    total = 0.0
    for permit in permits:
        if not permit.commercial or not permit.contractor_key:
            continue
        if permit.issued and not (start <= permit.issued <= end):
            continue
        count += 1
        value = permit.valuation or 0.0
        total += value
        row = rows.setdefault(permit.contractor_key, GCRow(key=permit.contractor_key, name=""))
        row.permits += 1
        row.value += value
        row.variants.append(permit.contractor)
        row.last_issued = max(row.last_issued, permit.issued or "")
        if value >= row.largest_value:
            row.largest_value, row.largest_desc = value, (permit.description or permit.permit_type)[:90]
    for row in rows.values():
        row.name = display_name(row.variants)
    leaders = sorted(rows.values(), key=lambda r: (r.value, r.permits), reverse=True)
    return MarketStats(market=market, days=days, permits=count, value=total, leaders=leaders)


def all_market_stats(store, as_of: date | None = None, days: int = 90) -> dict[str, MarketStats]:
    """{market name (lowercase): stats} for every market with permit data."""
    by_market: dict[str, list[Permit]] = defaultdict(list)
    for permit in store.permits():
        by_market[permit.market].append(permit)
    return {
        market.lower(): leaderboard(permits, as_of, days, market)
        for market, permits in by_market.items()
        if market
    }


def money_short(value: float) -> str:
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"${value / 1_000:.0f}K"
    return f"${value:,.0f}"


def assign_market(city: str, markets: dict[str, list[str]]) -> str:
    """Map a lead's city to a configured market (metro); default to the city itself."""
    lowered = (city or "").strip().lower()
    for market, cities in markets.items():
        if lowered == market.lower() or lowered in {c.lower() for c in cities}:
            return market
    return (city or "").strip()

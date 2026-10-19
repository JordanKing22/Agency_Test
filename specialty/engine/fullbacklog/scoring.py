"""ICP scoring: who to call first and who gets the email budget.

Ideal client: a commercial specialty sub with 10-200 people, in a trade we
target, that lives on GC bid invitations, ideally certified (MBE/WBE/DBE...)
or hiring, in a market where we have permit data to show them.
"""

from .models import Lead, split_list
from .permits import MarketStats

NATIONAL_BRANDS = ("rosendin", "cupertino electric", "comfort systems usa", "emcor",
                   "performance contracting", "baker concrete", "tecta america", "api group")


def score_lead(lead: Lead, target_trades: list[str], stats: MarketStats | None = None) -> tuple[int, list[str]]:
    points = 0
    reasons: list[str] = []

    def add(value: int, why: str) -> None:
        nonlocal points
        points += value
        reasons.append(f"{value:+d} {why}")

    if any(brand in lead.company.lower() for brand in NATIONAL_BRANDS):
        add(-30, "national sub with its own BD team")

    if lead.trade in target_trades:
        add(15, f"target trade ({lead.trade})")
    elif lead.trade:
        add(6, f"other trade ({lead.trade})")

    if lead.scanned_at and lead.site_ok:
        commercial, residential = lead.commercial_hits or 0, lead.residential_hits or 0
        if commercial >= 2 and commercial >= residential:
            add(15, "commercial focus on website")
        elif residential > commercial:
            add(-20, "mostly residential")
    elif lead.scanned_at and lead.site_ok == 0:
        add(-5, "website down")

    if lead.email:
        add(12, "has email")
    if lead.phone:
        add(5, "has phone")
    if lead.first_name:
        add(4, "named contact")

    employees = lead.employees or 0
    if 10 <= employees <= 200:
        add(10, f"{employees} employees")
    elif 200 < employees <= 500:
        add(3, f"{employees} employees (larger)")
    elif employees > 500:
        add(-10, f"{employees} employees (has BD staff)")

    certs = split_list(lead.certifications)
    if certs:
        add(10, "certified: " + ", ".join(certs))
    if lead.hiring:
        add(8, "hiring")
    if lead.has_portfolio:
        add(4, "project portfolio")
    if len(split_list(lead.project_types)) >= 2:
        add(4, "multiple project types")
    if lead.mentions_safety:
        add(2, "talks about safety/EMR")
    if lead.mentions_bonding:
        add(2, "mentions bonding")
    if stats and len(stats.leaders) >= 3:
        add(8, f"permit data for {stats.market}")

    return max(0, min(100, points)), reasons


def tier_for(score: int) -> str:
    if score >= 70:
        return "A"
    if score >= 50:
        return "B"
    return "C"

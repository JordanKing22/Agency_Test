"""Daily call sheet: phones first while the email inboxes warm up."""

import csv
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from .db import LeadStore
from .importer import clean_company
from .models import SUPPRESSED, Lead, split_list
from .permits import MarketStats
from .sequences import choose_sequence
from .trades import trade_label

STATE_TZ = {
    **dict.fromkeys("CT DE FL GA IN KY ME MD MA MI NH NJ NY NC OH PA RI SC VT VA WV DC".split(), "ET"),
    **dict.fromkeys("AL AR IL IA KS LA MN MS MO NE ND OK SD TN TX WI".split(), "CT"),
    **dict.fromkeys("AZ CO ID MT NM UT WY".split(), "MT"),
    **dict.fromkeys("CA NV OR WA".split(), "PT"),
    "AK": "AKT", "HI": "HT",
}
STATE_NAMES = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA", "colorado": "CO",
    "connecticut": "CT", "delaware": "DE", "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
    "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS", "kentucky": "KY", "louisiana": "LA",
    "maine": "ME", "maryland": "MD", "massachusetts": "MA", "michigan": "MI", "minnesota": "MN",
    "mississippi": "MS", "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY", "north carolina": "NC",
    "north dakota": "ND", "ohio": "OH", "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA",
    "rhode island": "RI", "south carolina": "SC", "south dakota": "SD", "tennessee": "TN", "texas": "TX",
    "utah": "UT", "vermont": "VT", "virginia": "VA", "washington": "WA", "west virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY", "district of columbia": "DC",
}
SCRIPT_FOR_SEQUENCE = {
    "certified-sub": "Opener C (certified sub)",
    "permit-pulse": "Opener A (permit pulse: name their top GCs)",
    "hiring": "Opener D (hiring)",
    "bid-chase": "Opener B (after bid day)",
}


def time_zone(state: str) -> str:
    code = state.strip().upper() if len(state.strip()) == 2 else STATE_NAMES.get(state.strip().lower(), "")
    return STATE_TZ.get(code, "?")


def signal_summary(lead: Lead, stats: MarketStats | None) -> str:
    parts = [trade_label(lead.trade)]
    if lead.employees:
        parts.append(f"~{lead.employees} employees")
    if split_list(lead.certifications):
        parts.append("certified: " + lead.certifications)
    if lead.hiring:
        parts.append("hiring")
    if lead.project_types:
        parts.append(lead.project_types)
    if lead.scanned_at and lead.site_ok:
        parts.append(f"site words: {lead.commercial_hits or 0} commercial / {lead.residential_hits or 0} residential")
    if stats and stats.leaders:
        parts.append(f"{stats.market}: {stats.permits} commercial permits, top GCs {', '.join(stats.top_names(3))}")
    return " · ".join(parts)


def _recently_called(store: LeadStore, cooldown_days: int) -> set[str]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=cooldown_days)
    return {e["lead_id"] for e in store.events(kind="call") if datetime.fromisoformat(e["at"]) >= cutoff}


def callsheet_rows(store: LeadStore, stats_by_market: dict[str, MarketStats], n: int = 60, cooldown_days: int = 3) -> list[dict]:
    recent = _recently_called(store, cooldown_days)
    candidates = [l for l in store.all() if l.phone and l.status not in SUPPRESSED and l.id not in recent]
    candidates.sort(key=lambda l: l.score or 0, reverse=True)
    rows = []
    for rank, lead in enumerate(candidates[:n], start=1):
        stats = stats_by_market.get((lead.market or lead.city).lower())
        rows.append({
            "rank": rank,
            "lead_id": lead.id,
            "company": clean_company(lead.company),
            "contact": " ".join(p for p in (lead.first_name, lead.last_name) if p) or "owner / chief estimator",
            "phone": lead.phone,
            "location": ", ".join(p for p in (lead.city, lead.state) if p),
            "tz": time_zone(lead.state),
            "score": lead.score or 0,
            "script": SCRIPT_FOR_SEQUENCE[choose_sequence(lead, stats)],
            "hook": lead.personalization,
            "signals": signal_summary(lead, stats),
        })
    return rows


def callsheet_markdown(rows: list[dict], day: date | None = None) -> str:
    day = day or date.today()
    lines = [
        f"# Call sheet: {day.isoformat()}",
        "",
        "Best windows (their local time): 6:30-7:30am before they leave for jobsites, 3:30-5:00pm when they're back.",
        "Estimators are at their desks mid-morning; avoid bid days (Tue-Thu afternoons are common).",
        "Scripts: `sales/cold-call.md`. Log every dial: `fullbacklog call <lead_id> --outcome <outcome>`.",
        "",
    ]
    for row in rows:
        lines += [
            f"## {row['rank']}. {row['company']} ({row['score']})",
            f"- **Call:** {row['contact']} · {row['phone']} · {row['location']} ({row['tz']})",
            f"- **Use:** {row['script']}",
            f"- **Hook:** {row['hook']}",
            f"- **Signals:** {row['signals']}",
            f"- **Log:** `fullbacklog call {row['lead_id']} --outcome ...`",
            "",
        ]
    return "\n".join(lines)


def write_callsheet(rows: list[dict], out_dir: str | Path) -> tuple[Path, Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = date.today().isoformat()
    md_path, csv_path = out_dir / f"callsheet-{stamp}.md", out_dir / f"callsheet-{stamp}.csv"
    md_path.write_text(callsheet_markdown(rows), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else ["rank"])
        writer.writeheader()
        writer.writerows(rows)
    return md_path, csv_path

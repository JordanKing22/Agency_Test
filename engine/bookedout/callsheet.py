"""Daily call sheet and after-hours audit list.

Phones beat email in week one: inboxes need ~2 weeks of warmup, a dialer
does not. The call sheet ranks leads by score, skips anyone dialed in the
last few days, and gives each row a hook and the script to use.
"""

import csv
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from .db import LeadStore
from .importer import clean_company
from .models import SUPPRESSED, Lead
from .sequences import choose_sequence

# Rough state -> time zone, for "when to call" hints. Split states use the majority zone.
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
    "after-hours": "Opener A (after-hours audit)",
    "cold-snap": "Opener C (cold snap)",
    "heat-wave": "Opener C (heat wave)",
    "paid-clicks": "Opener D (paid clicks)",
    "estimate-recovery": "Opener B (unsold estimates)",
}


def time_zone(state: str) -> str:
    code = state.strip().upper() if len(state.strip()) == 2 else STATE_NAMES.get(state.strip().lower(), "")
    return STATE_TZ.get(code, "?")


def signal_summary(lead: Lead) -> str:
    parts = []
    if lead.reviews:
        parts.append(f"{lead.reviews} reviews" + (f" @ {lead.rating:.1f}" if lead.rating else ""))
    if lead.scanned_at and lead.site_ok:
        parts.append("Google Ads" if lead.runs_google_ads else "no ads seen")
        parts.append(f"booking: {lead.booking_vendor or 'none'}")
        parts.append(f"chat: {lead.chat_vendor or 'none'}")
        if lead.call_tracking:
            parts.append(lead.call_tracking)
    if lead.audit_result:
        parts.append(f"audit: {lead.audit_result}" + (f" ({lead.audit_time})" if lead.audit_time else ""))
    if lead.forecast_low_f is not None:
        parts.append(f"low {lead.forecast_low_f}F {lead.forecast_low_when}")
    return " · ".join(parts)


def _recently_called(store: LeadStore, cooldown_days: int) -> set[str]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=cooldown_days)
    recent = set()
    for event in store.events(kind="call"):
        if datetime.fromisoformat(event["at"]) >= cutoff:
            recent.add(event["lead_id"])
    return recent


def callsheet_rows(store: LeadStore, config: dict, n: int = 60, cooldown_days: int = 3) -> list[dict]:
    targeting = config["targeting"]
    recent = _recently_called(store, cooldown_days)
    candidates = [
        lead for lead in store.all()
        if lead.phone and lead.status not in SUPPRESSED and lead.id not in recent and lead.audit_result != "disconnected"
    ]
    candidates.sort(key=lambda l: l.score or 0, reverse=True)
    rows = []
    for rank, lead in enumerate(candidates[:n], start=1):
        sequence = choose_sequence(lead, targeting["cold_threshold_f"], targeting["hot_threshold_f"])
        rows.append({
            "rank": rank,
            "lead_id": lead.id,
            "company": clean_company(lead.company),
            "contact": " ".join(p for p in (lead.first_name, lead.last_name) if p) or "owner",
            "phone": lead.phone,
            "location": ", ".join(p for p in (lead.city, lead.state) if p),
            "tz": time_zone(lead.state),
            "score": lead.score or 0,
            "script": SCRIPT_FOR_SEQUENCE[sequence],
            "hook": lead.personalization,
            "signals": signal_summary(lead),
        })
    return rows


def callsheet_markdown(rows: list[dict], day: date | None = None) -> str:
    day = day or date.today()
    lines = [
        f"# Call sheet: {day.isoformat()}",
        "",
        "Best windows (lead's local time): 7:00-8:30am before trucks roll, 4:00-6:00pm as techs come back.",
        "Scripts: `sales/cold-call.md`. Log every dial: `bookedout call <lead_id> --outcome <outcome>`.",
        "",
    ]
    for row in rows:
        lines += [
            f"## {row['rank']}. {row['company']} ({row['score']})",
            f"- **Call:** {row['contact']} · {row['phone']} · {row['location']} ({row['tz']})",
            f"- **Use:** {row['script']}",
            f"- **Hook:** {row['hook']}",
            f"- **Signals:** {row['signals'] or 'none yet (run scan)'}",
            f"- **Log:** `bookedout call {row['lead_id']} --outcome ...`",
            "",
        ]
    return "\n".join(lines)


def write_callsheet(rows: list[dict], out_dir: str | Path) -> tuple[Path, Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = date.today().isoformat()
    md_path = out_dir / f"callsheet-{stamp}.md"
    csv_path = out_dir / f"callsheet-{stamp}.csv"
    md_path.write_text(callsheet_markdown(rows), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else ["rank"])
        writer.writeheader()
        writer.writerows(rows)
    return md_path, csv_path


# --- after-hours audit ------------------------------------------------------

AUDIT_COLUMNS = ["lead_id", "company", "phone", "location", "tz", "result", "called_at"]


def audit_rows(store: LeadStore, n: int = 40) -> list[dict]:
    """Top leads with a phone and no audit yet, for a VA to call after 6pm local time."""
    candidates = [
        lead for lead in store.all()
        if lead.phone and not lead.audit_result and lead.status not in SUPPRESSED
    ]
    candidates.sort(key=lambda l: l.score or 0, reverse=True)
    return [
        {
            "lead_id": lead.id,
            "company": clean_company(lead.company),
            "phone": lead.phone,
            "location": ", ".join(p for p in (lead.city, lead.state) if p),
            "tz": time_zone(lead.state),
            "result": "",
            "called_at": "",
        }
        for lead in candidates[:n]
    ]


def write_audit_list(rows: list[dict], path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=AUDIT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return path

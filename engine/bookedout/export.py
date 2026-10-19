"""Export leads to CSV for Instantly / Smartlead: one file per sequence.

Create one campaign per sequence in your sending tool, paste in the copy from
sales/email-sequences.md, and upload the matching CSV. Every {{variable}} in
the copy is a column here.
"""

import csv
from datetime import date
from pathlib import Path

from .db import LeadStore
from .models import SUPPRESSED, Lead
from .personalize import rule_opener
from .sequences import choose_sequence, lead_variables, load_sequences

BASE_COLUMNS = {
    "instantly": ["email", "first_name", "last_name", "company_name", "website", "phone"],
    "smartlead": ["email", "first_name", "last_name", "company_name", "website", "phone_number"],
}
EXTRA_COLUMNS = ["lead_id", "sequence", "score", "tier"]


def custom_columns() -> list[str]:
    names: set[str] = set()
    for sequence in load_sequences().values():
        names |= sequence.variables()
    names |= {"city", "state", "personalization"}
    return sorted(names)


def is_exportable(lead: Lead, min_score: int, include_contacted: bool = False) -> bool:
    if not lead.email or lead.status in SUPPRESSED:
        return False
    if lead.status == "in_sequence" and not include_contacted:
        return False
    return (lead.score or 0) >= min_score


def export_leads(
    store: LeadStore,
    config: dict,
    out_dir: str | Path,
    fmt: str = "instantly",
    min_score: int | None = None,
    include_contacted: bool = False,
    mark: bool = True,
) -> dict[str, tuple[Path, int]]:
    """Write <out_dir>/<fmt>-<sequence>-<date>.csv files. Returns {sequence: (path, rows)}."""
    targeting = config["targeting"]
    min_score = targeting["min_export_score"] if min_score is None else min_score
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    columns = BASE_COLUMNS[fmt] + [c for c in custom_columns() if c not in BASE_COLUMNS[fmt]] + EXTRA_COLUMNS

    groups: dict[str, list[dict]] = {}
    leads = sorted(store.all(), key=lambda l: l.score or 0, reverse=True)
    for lead in leads:
        if not is_exportable(lead, min_score, include_contacted):
            continue
        if not lead.personalization:
            lead.personalization, lead.personalization_source = rule_opener(
                lead, targeting["cold_threshold_f"], targeting["hot_threshold_f"]
            )
        sequence = choose_sequence(lead, targeting["cold_threshold_f"], targeting["hot_threshold_f"])
        variables = lead_variables(lead, config)
        row = {
            "email": lead.email,
            "first_name": lead.first_name,
            "last_name": lead.last_name,
            "company_name": variables["company"],
            "website": lead.domain,
            "phone": lead.phone,
            "phone_number": lead.phone,
            "lead_id": lead.id,
            "sequence": sequence,
            "score": lead.score or 0,
            "tier": lead.tier,
        }
        for column in columns:
            if column not in row:
                row[column] = variables.get(column, getattr(lead, column, ""))
        groups.setdefault(sequence, []).append(row)
        if mark:
            lead.sequence = sequence
            lead.status = "in_sequence"
            store.save(lead, commit=False)
            store.log(lead.id, "exported", f"{fmt}:{sequence}", commit=False)

    written = {}
    stamp = date.today().isoformat()
    for sequence, rows in groups.items():
        path = out_dir / f"{fmt}-{sequence}-{stamp}.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        written[sequence] = (path, len(rows))
    store.commit()
    return written

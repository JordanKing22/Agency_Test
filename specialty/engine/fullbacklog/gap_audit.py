"""The Bid List Gap Audit: the top GCs building in a market, and which ones a sub is missing.

It is the free lead magnet (send it to a prospect), the centerpiece of the
sales call (share your screen), and the target list for a client's sprint
(the CSV goes to Apollo/GetLeads to find each GC's estimators).
"""

import csv
from datetime import date
from pathlib import Path

from .permits import MarketStats, contractor_key, money_short, same_contractor


def read_known(path: str | Path | None) -> set[str]:
    """GCs the sub already gets invitations from: one name per line (or a CSV's first column)."""
    if not path:
        return set()
    keys = set()
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        name = line.split(",")[0].strip().strip('"')
        if name and name.lower() not in ("name", "gc", "company", "general contractor"):
            keys.add(contractor_key(name))
    return keys


def gap_rows(stats: MarketStats, known: set[str], n: int = 25) -> list[dict]:
    return [
        {
            "rank": rank,
            "general_contractor": row.name,
            "commercial_permits": row.permits,
            "permit_value": round(row.value),
            "largest_project": row.largest_desc,
            "last_permit": row.last_issued,
            "invites_you": ("yes" if any(same_contractor(row.key, k) for k in known) else "no") if known else "",
        }
        for rank, row in enumerate(stats.leaders[:n], start=1)
    ]


def gap_markdown(stats: MarketStats, rows: list[dict], company: str = "", as_of: date | None = None) -> str:
    as_of = as_of or date.today()
    title = f"Bid List Gap Audit: {stats.market}" + (f" for {company}" if company else "")
    lines = [
        f"# {title}",
        "",
        f"Commercial building permits issued in **{stats.market}** in the {stats.days} days before {as_of.isoformat()}: "
        f"**{stats.permits}** permits worth **{money_short(stats.value)}**, pulled by **{len(stats.leaders)}** contractors.",
        "",
        "Source: public building permit records. Valuations are as declared on the permit application.",
        "",
    ]
    known_marked = any(row["invites_you"] for row in rows)
    if known_marked:
        missing = [row for row in rows if row["invites_you"] == "no"]
        lines += [f"**You're not on the bid list of {len(missing)} of the top {len(rows)} GCs.**", ""]
    lines += [
        "| # | General contractor | Permits | Permit value | Largest project | Invites you? |",
        "|---|---|---:|---:|---|---|",
    ]
    for row in rows:
        mark = {"yes": "✅ yes", "no": "❌ no"}.get(row["invites_you"], "☐")
        lines.append(
            f"| {row['rank']} | {row['general_contractor']} | {row['commercial_permits']} | "
            f"{money_short(row['permit_value'])} | {row['largest_project']} | {mark} |"
        )
    lines += [
        "",
        "Next step: we get you onto the bid lists you're missing. At least 10 new GC bid lists in 30 days, or you don't pay.",
    ]
    return "\n".join(lines) + "\n"


def write_gap_audit(stats: MarketStats, rows: list[dict], out_dir: str | Path, company: str = "",
                    as_of: date | None = None) -> tuple[Path, Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = "-".join(part for part in (stats.market, company) if part).lower().replace(" ", "-").replace("/", "-")
    md_path, csv_path = out_dir / f"gap-audit-{slug}.md", out_dir / f"gc-targets-{slug}.csv"
    md_path.write_text(gap_markdown(stats, rows, company, as_of), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else ["rank"])
        writer.writeheader()
        writer.writerows(rows)
    return md_path, csv_path

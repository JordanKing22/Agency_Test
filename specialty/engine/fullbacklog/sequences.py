"""Cold email sequences: loading, choosing one per lead, and rendering.

Templates use {{variable}} placeholders. Every variable is also exported as a
CSV column, so the same copy can be pasted into Instantly or Smartlead and
filled there, or rendered here with `fullbacklog preview` for QA.
"""

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

from .importer import clean_company
from .models import Lead, split_list
from .permits import MarketStats, money_short
from .trades import trade_label

SEQUENCE_DIR = Path(__file__).parent / "sequences"
VAR_RE = re.compile(r"\{\{\s*([a-z0-9_]+)\s*\}\}")


@dataclass
class Step:
    day: int
    subject: str
    body: str


@dataclass
class Sequence:
    name: str
    description: str
    when: str
    steps: list[Step]

    def variables(self) -> set[str]:
        found: set[str] = set()
        for step in self.steps:
            found |= set(VAR_RE.findall(step.subject)) | set(VAR_RE.findall(step.body))
        return found


def load_sequences(directory: Path = SEQUENCE_DIR) -> dict[str, Sequence]:
    sequences = {}
    for path in sorted(directory.glob("*.toml")):
        with path.open("rb") as handle:
            data = tomllib.load(handle)
        steps = [Step(int(s["day"]), s.get("subject", ""), s["body"].strip()) for s in data["steps"]]
        sequences[data["name"]] = Sequence(data["name"], data.get("description", ""), data.get("when", ""), steps)
    return sequences


def has_permit_hook(stats: MarketStats | None) -> bool:
    return bool(stats and stats.permits and len(stats.leaders) >= 3)


def choose_sequence(lead: Lead, stats: MarketStats | None = None) -> str:
    """Strongest available hook wins."""
    if split_list(lead.certifications):
        return "certified-sub"
    if has_permit_hook(stats):
        return "permit-pulse"
    if lead.hiring:
        return "hiring"
    return "bid-chase"


def lead_variables(lead: Lead, config: dict, stats: MarketStats | None = None) -> dict[str, str]:
    sender = config["sender"]
    certs = split_list(lead.certifications)
    top = stats.top_names(3) if stats else []
    top += [""] * (3 - len(top))
    return {
        "greeting_name": lead.first_name or "there",
        "first_name": lead.first_name,
        "company": clean_company(lead.company) or "your company",
        "trade": trade_label(lead.trade),
        "city": lead.city or "your area",
        "state": lead.state,
        "market": lead.market or lead.city or "your area",
        "certification": certs[0] if certs else "",
        "personalization": lead.personalization,
        "permits_90d": str(stats.permits) if stats and stats.permits else "",
        "permit_value_90d": money_short(stats.value) if stats and stats.value else "",
        "top_gc_1": top[0],
        "top_gc_2": top[1],
        "top_gc_3": top[2],
        "sender_first_name": sender["first_name"],
        "agency": sender["agency"],
        "calendar_link": sender["calendar_link"],
    }


def render(text: str, variables: dict[str, str]) -> tuple[str, list[str]]:
    missing: list[str] = []

    def replace(match: re.Match) -> str:
        value = variables.get(match.group(1), "")
        if not value:
            missing.append(match.group(1))
        return value

    return VAR_RE.sub(replace, text), missing


def render_sequence(sequence: Sequence, variables: dict[str, str]) -> tuple[list[tuple[int, str, str]], list[str]]:
    rendered, missing = [], []
    for step in sequence.steps:
        subject, miss_subject = render(step.subject, variables)
        body, miss_body = render(step.body, variables)
        rendered.append((step.day, subject, body))
        missing += miss_subject + miss_body
    return rendered, sorted(set(missing))


def sequences_markdown(sequences: dict[str, Sequence]) -> str:
    """Human-readable copy deck (sales/email-sequences.md is generated from this)."""
    lines = [
        "# Cold email sequences",
        "",
        "_Generated from `engine/fullbacklog/sequences/*.toml` by `fullbacklog sequences-md`. "
        "Edit the TOML files, not this page._",
        "",
        "Paste these into Instantly or Smartlead (one campaign per sequence). Every `{{variable}}` "
        "is a column in the CSVs that `fullbacklog export` writes, so the tool fills them per lead. "
        "Follow-ups have no subject so they thread under step 1.",
        "",
    ]
    for sequence in sequences.values():
        lines += [f"## `{sequence.name}`", "", sequence.description, "", f"**Used when:** {sequence.when}", ""]
        for index, step in enumerate(sequence.steps, start=1):
            subject = step.subject or "_(reply in thread)_"
            lines += [f"### Step {index}: day {step.day}", "", f"**Subject:** {subject}", "", "```text", step.body, "```", ""]
    return "\n".join(lines).rstrip() + "\n"

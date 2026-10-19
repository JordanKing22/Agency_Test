"""Cold email sequences: loading, choosing one per lead, and rendering.

Templates use {{variable}} placeholders. Every variable is also exported as a
CSV column, so the same copy can be pasted into Instantly or Smartlead and
filled there, or rendered here with `bookedout preview` for QA.
"""

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

from .importer import clean_company
from .models import Lead

SEQUENCE_DIR = Path(__file__).parent / "sequences"
VAR_RE = re.compile(r"\{\{\s*([a-z_]+)\s*\}\}")

AUDIT_PHRASES = {
    "voicemail": "it went to voicemail",
    "no_answer": "it rang out with no answer",
    "ivr": "I got a phone menu but never a person",
    "answering_service": "an answering service took a message",
}


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


def choose_sequence(lead: Lead, cold_threshold_f: int = 25, hot_threshold_f: int = 95) -> str:
    """Strongest available hook wins."""
    if lead.audit_result in ("voicemail", "no_answer", "ivr"):
        return "after-hours"
    if lead.city and lead.forecast_low_f is not None and lead.forecast_low_f <= cold_threshold_f:
        return "cold-snap"
    if lead.city and lead.forecast_high_f is not None and lead.forecast_high_f >= hot_threshold_f:
        return "heat-wave"
    if lead.runs_google_ads and lead.domain and not lead.booking_vendor and not lead.chat_vendor:
        return "paid-clicks"
    return "estimate-recovery"


def _period_phrase(name: str) -> str:
    """'Thursday Night' -> 'Thursday night', 'Tonight' -> 'tonight'."""
    if not name:
        return "this week"
    words = name.split()
    if words[0].lower() in ("tonight", "today", "overnight", "this"):
        return name.lower()
    return " ".join([words[0]] + [w.lower() for w in words[1:]])


def _audit_when(audit_time: str) -> str:
    text = audit_time.strip()
    if not text:
        return "after hours"
    if text.lower().split()[0] in ("last", "yesterday", "this", "at", "on", "around", "earlier"):
        return text
    return f"on {text}"


def lead_variables(lead: Lead, config: dict) -> dict[str, str]:
    sender = config["sender"]
    rating = f"{lead.rating:.1f}" if lead.rating else ""
    return {
        "greeting_name": lead.first_name or "there",
        "first_name": lead.first_name,
        "company": clean_company(lead.company) or "your company",
        "city": lead.city,
        "state": lead.state,
        "domain": lead.domain or "your website",
        "personalization": lead.personalization,
        "reviews": str(lead.reviews or ""),
        "rating": rating,
        "audit_when": _audit_when(lead.audit_time),
        "audit_phrase": AUDIT_PHRASES.get(lead.audit_result, "nobody picked up"),
        "forecast_low": "" if lead.forecast_low_f is None else str(lead.forecast_low_f),
        "forecast_low_when": _period_phrase(lead.forecast_low_when),
        "forecast_high": "" if lead.forecast_high_f is None else str(lead.forecast_high_f),
        "forecast_high_when": _period_phrase(lead.forecast_high_when),
        "sender_first_name": sender["first_name"],
        "agency": sender["agency"],
        "demo_line": sender["demo_line"],
        "calendar_link": sender["calendar_link"],
    }


def render(text: str, variables: dict[str, str]) -> tuple[str, list[str]]:
    """Fill placeholders. Returns (text, names that were missing or empty)."""
    missing: list[str] = []

    def replace(match: re.Match) -> str:
        name = match.group(1)
        value = variables.get(name, "")
        if not value:
            missing.append(name)
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
        "_Generated from `engine/bookedout/sequences/*.toml` by `bookedout sequences-md`. "
        "Edit the TOML files, not this page._",
        "",
        "Paste these into Instantly or Smartlead (one campaign per sequence). Every `{{variable}}` "
        "is a column in the CSVs that `bookedout export` writes, so the tool fills them per lead. "
        "Follow-ups have no subject so they thread under step 1.",
        "",
    ]
    for sequence in sequences.values():
        lines += [f"## `{sequence.name}`", "", sequence.description, "", f"**Used when:** {sequence.when}", ""]
        for index, step in enumerate(sequence.steps, start=1):
            subject = step.subject or "_(reply in thread)_"
            lines += [f"### Step {index}: day {step.day}", "", f"**Subject:** {subject}", "", "```text", step.body, "```", ""]
    return "\n".join(lines).rstrip() + "\n"

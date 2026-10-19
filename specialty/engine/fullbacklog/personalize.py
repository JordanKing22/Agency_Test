"""First-line personalization.

Rules produce a fact-based opener for every lead for free. With `--ai`,
Claude rewrites the opener from the same facts so it reads less templated.
Claude only sees facts we collected; anything it returns that fails
validation falls back to the rule-based line.
"""

import json
import re
from concurrent.futures import ThreadPoolExecutor

from .importer import clean_company
from .models import Lead, split_list
from .permits import MarketStats, money_short
from .trades import trade_label


def _join(items: list[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def rule_opener(lead: Lead, stats: MarketStats | None = None) -> tuple[str, str]:
    """Return (opener, which fact it used)."""
    company = clean_company(lead.company) or "your company"
    certs = split_list(lead.certifications)
    if certs:
        return f"Saw {company} is {certs[0]}-certified, which GCs with participation goals actively look for.", "certification"
    if stats and stats.permits and stats.leaders:
        return (
            f"{stats.permits} commercial permits were issued in {stats.market} over the last {stats.days} days, "
            f"and {stats.leaders[0].name} pulled the most.",
            "permits",
        )
    if lead.hiring:
        return f"Saw {company} is hiring, which usually means this year is full and next year is the question.", "hiring"
    types = split_list(lead.project_types)[:2]
    if types:
        where = f" around {lead.city}" if lead.city else ""
        return f"Saw {company} has done {_join(types)} work{where}.", "project_types"
    if lead.city:
        return f"I work with commercial {trade_label(lead.trade)} subs around {lead.city}.", "generic"
    return f"I work with commercial {trade_label(lead.trade)} subs like {company}.", "generic"


# --- Claude ---------------------------------------------------------------

SYSTEM_PROMPT = """You write the opening line of a cold email from a small agency to the owner or chief estimator of a US commercial specialty subcontractor (drywall, electrical, concrete, glazing and similar trades that bid work to general contractors).

The rest of the email (written separately) offers to get them onto more general contractors' bid lists and to follow up on their bids after bid day. Your line comes first and earns the next sentence.

Rules:
- Exactly one sentence, at most 28 words.
- Use only facts in the lead data. Never invent numbers, names, projects, awards, or events.
- Pick the single most relevant fact, in this order of strength: a certification (MBE, WBE, DBE, SDVOSB and similar), commercial permit activity in their market and the general contractor who pulled the most, that they're hiring, the project types they build.
- Write like a plain-spoken person talking to a busy contractor. No flattery words (impressive, amazing, love, great), no "I hope this finds you well", no exclamation marks, no emojis, no questions, no pitch.
- Refer to the company by the short name given.
- Output only the sentence, with no quotes or preamble."""

BANNED_RE = re.compile(r"hope this|impressive|amazing|i love|!|\?|\{\{|\}\}", re.I)


def lead_facts(lead: Lead, stats: MarketStats | None) -> dict:
    facts = {
        "company_short_name": clean_company(lead.company),
        "owner_first_name": lead.first_name or None,
        "trade": trade_label(lead.trade),
        "city": lead.city or None,
        "state": lead.state or None,
        "certifications": split_list(lead.certifications) or None,
        "hiring": bool(lead.hiring),
        "project_types": split_list(lead.project_types) or None,
        "employees": lead.employees,
    }
    if stats and stats.permits and stats.leaders:
        facts["market_permits"] = {
            "market": stats.market,
            "window_days": stats.days,
            "commercial_permits": stats.permits,
            "total_value": money_short(stats.value),
            "top_general_contractors": stats.top_names(3),
        }
    return {key: value for key, value in facts.items() if value not in (None, "", False)}


def validate_opener(text: str) -> str | None:
    line = " ".join(text.strip().strip('"').strip("'").split())
    if not line or len(line) > 240 or len(line.split()) > 32 or BANNED_RE.search(line):
        return None
    return line


def make_client():
    try:
        import anthropic
    except ImportError as exc:
        raise RuntimeError("AI mode needs the Anthropic SDK: pip install -e '.[ai]'") from exc
    return anthropic.Anthropic(max_retries=4)


def ai_opener(client, lead: Lead, stats: MarketStats | None, model: str, effort: str) -> str | None:
    import anthropic

    try:
        response = client.beta.messages.create(
            model=model,
            max_tokens=4000,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            output_config={"effort": effort},
            system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": "Lead data:\n" + json.dumps(lead_facts(lead, stats), indent=2, sort_keys=True)}],
        )
    except (anthropic.AuthenticationError, anthropic.PermissionDeniedError, anthropic.NotFoundError):
        raise  # misconfiguration: stop the run instead of failing every lead
    except (anthropic.RateLimitError, anthropic.APIStatusError, anthropic.APIConnectionError):
        return None  # the SDK already retried; keep the rule-based line
    if response.stop_reason == "refusal":
        return None
    return validate_opener("".join(block.text for block in response.content if block.type == "text"))


def personalize_leads(
    leads: list[Lead],
    stats_by_market: dict[str, MarketStats] | None = None,
    use_ai: bool = False,
    model: str = "claude-opus-5-5",
    effort: str = "low",
    workers: int = 4,
    client=None,
    progress=None,
) -> dict[str, int]:
    """Set lead.personalization for every lead. Returns counts by source."""
    stats_by_market = stats_by_market or {}
    stats_for = lambda lead: stats_by_market.get((lead.market or lead.city).lower())
    for lead in leads:
        lead.personalization, lead.personalization_source = rule_opener(lead, stats_for(lead))
    if use_ai and leads:
        client = client or make_client()

        def work(lead: Lead) -> None:
            line = ai_opener(client, lead, stats_for(lead), model, effort)
            if line:
                lead.personalization = line
                lead.personalization_source = "ai:" + lead.personalization_source

        with ThreadPoolExecutor(max_workers=workers) as pool:
            for done, _ in enumerate(pool.map(work, leads), start=1):
                if progress:
                    progress(done, len(leads))
    counts: dict[str, int] = {}
    for lead in leads:
        counts[lead.personalization_source] = counts.get(lead.personalization_source, 0) + 1
    return counts

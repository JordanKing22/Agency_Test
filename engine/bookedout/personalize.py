"""First-line personalization.

Rules produce a solid, fact-based opener for every lead for free. With
`--ai`, Claude rewrites the opener from the same facts so it reads less
templated. Claude only sees facts we collected, and anything it returns that
fails validation falls back to the rule-based line.
"""

import json
import re
from concurrent.futures import ThreadPoolExecutor

from .importer import clean_company
from .models import Lead
from .sequences import AUDIT_PHRASES, _audit_when, _period_phrase


def rule_opener(lead: Lead, cold_threshold_f: int = 25, hot_threshold_f: int = 95) -> tuple[str, str]:
    """Return (opener, which fact it used)."""
    company = clean_company(lead.company) or "your shop"
    if lead.audit_result in ("voicemail", "no_answer", "ivr"):
        return f"I called {company} {_audit_when(lead.audit_time)} and {AUDIT_PHRASES[lead.audit_result]}.", "audit"
    if lead.city and lead.forecast_low_f is not None and lead.forecast_low_f <= cold_threshold_f:
        return (
            f"Looks like {lead.city} drops to {lead.forecast_low_f}°F {_period_phrase(lead.forecast_low_when)}, "
            "so your phones are about to get busy.",
            "cold_snap",
        )
    if lead.city and lead.forecast_high_f is not None and lead.forecast_high_f >= hot_threshold_f:
        return (
            f"Looks like {lead.city} hits {lead.forecast_high_f}°F {_period_phrase(lead.forecast_high_when)}, "
            "so your phones are about to get busy.",
            "heat_wave",
        )
    if lead.runs_google_ads and lead.domain and not lead.booking_vendor and not lead.chat_vendor:
        return f"Noticed {company} runs Google Ads, but {lead.domain} has no way to book or chat after hours.", "ads_no_booking"
    if (lead.reviews or 0) >= 50 and (lead.rating or 0) >= 4.5:
        return (
            f"{lead.reviews} Google reviews at {lead.rating:.1f} stars says {company} takes care of people "
            "once they get you on the phone.",
            "reviews",
        )
    if lead.has_membership:
        return f"Saw {company} sells maintenance plans, which usually means a big list of past customers.", "membership"
    if lead.city:
        return f"I work with HVAC companies around {lead.city}, so {company} came up.", "generic"
    return f"I work with HVAC companies like {company}.", "generic"


# --- Claude ---------------------------------------------------------------

SYSTEM_PROMPT = """You write the opening line of a cold email from a small agency to the owner of a US HVAC company.

The rest of the email (written separately) asks how many unsold replacement quotes they have and offers to book appointments from them, or offers a 24/7 AI phone dispatcher. Your line comes first and earns the next sentence.

Rules:
- Exactly one sentence, at most 25 words.
- Use only facts in the lead data. Never invent numbers, names, awards, history, or events.
- Pick the single most relevant fact, in this order of strength: an after-hours call that went unanswered, a cold snap or heat wave in their city, Google Ads without online booking or chat, their review count and rating, maintenance plans.
- Write like a plain-spoken person talking to a busy tradesman. No flattery words (impressive, amazing, love, great), no "I hope this finds you well", no exclamation marks, no emojis, no questions, no pitch.
- Refer to the company by the short name given.
- Output only the sentence, with no quotes or preamble."""

BANNED_RE = re.compile(r"hope this|impressive|amazing|i love|!|\?|\{\{|\}\}", re.I)


def lead_facts(lead: Lead, cold_threshold_f: int, hot_threshold_f: int) -> dict:
    facts = {
        "company_short_name": clean_company(lead.company),
        "owner_first_name": lead.first_name or None,
        "city": lead.city or None,
        "state": lead.state or None,
        "website": lead.domain or None,
        "google_reviews": lead.reviews,
        "google_rating": lead.rating,
        "runs_google_ads": bool(lead.runs_google_ads),
        "has_online_booking": bool(lead.booking_vendor),
        "has_website_chat": bool(lead.chat_vendor),
        "advertises_24_7_service": bool(lead.mentions_24_7),
        "sells_maintenance_plans": bool(lead.has_membership),
    }
    if lead.audit_result:
        facts["after_hours_test_call"] = {
            "when": lead.audit_time or "after business hours",
            "result": AUDIT_PHRASES.get(lead.audit_result, lead.audit_result),
        }
    if lead.forecast_low_f is not None and lead.forecast_low_f <= cold_threshold_f:
        facts["forecast_cold_snap"] = f"{lead.forecast_low_f}F {_period_phrase(lead.forecast_low_when)}"
    if lead.forecast_high_f is not None and lead.forecast_high_f >= hot_threshold_f:
        facts["forecast_heat_wave"] = f"{lead.forecast_high_f}F {_period_phrase(lead.forecast_high_when)}"
    return {key: value for key, value in facts.items() if value not in (None, "", False)}


def validate_opener(text: str) -> str | None:
    line = " ".join(text.strip().strip('"').strip("'").split())
    if not line or len(line) > 220 or len(line.split()) > 30 or BANNED_RE.search(line):
        return None
    return line


def make_client():
    """Build the Anthropic client, or explain how to enable AI mode."""
    try:
        import anthropic
    except ImportError as exc:
        raise RuntimeError("AI mode needs the Anthropic SDK: pip install -e '.[ai]'") from exc
    return anthropic.Anthropic(max_retries=4)


def ai_opener(client, lead: Lead, model: str, effort: str, cold_threshold_f: int, hot_threshold_f: int) -> str | None:
    import anthropic

    facts = lead_facts(lead, cold_threshold_f, hot_threshold_f)
    try:
        response = client.beta.messages.create(
            model=model,
            max_tokens=4000,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            output_config={"effort": effort},
            system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": "Lead data:\n" + json.dumps(facts, indent=2, sort_keys=True)}],
        )
    except (anthropic.AuthenticationError, anthropic.PermissionDeniedError, anthropic.NotFoundError):
        raise  # misconfiguration: stop the run instead of failing every lead
    except (anthropic.RateLimitError, anthropic.APIStatusError, anthropic.APIConnectionError):
        return None  # the SDK already retried; fall back to the rule-based line
    if response.stop_reason == "refusal":
        return None
    text = "".join(block.text for block in response.content if block.type == "text")
    return validate_opener(text)


def personalize_leads(
    leads: list[Lead],
    use_ai: bool = False,
    model: str = "claude-opus-5-5",
    effort: str = "low",
    workers: int = 4,
    cold_threshold_f: int = 25,
    hot_threshold_f: int = 95,
    client=None,
    progress=None,
) -> dict[str, int]:
    """Set lead.personalization for every lead. Returns counts by source."""
    counts: dict[str, int] = {}
    for lead in leads:
        lead.personalization, lead.personalization_source = rule_opener(lead, cold_threshold_f, hot_threshold_f)
    if use_ai and leads:
        client = client or make_client()

        def work(lead: Lead) -> None:
            line = ai_opener(client, lead, model, effort, cold_threshold_f, hot_threshold_f)
            if line:
                lead.personalization = line
                lead.personalization_source = "ai:" + lead.personalization_source

        with ThreadPoolExecutor(max_workers=workers) as pool:
            for done, _ in enumerate(pool.map(work, leads), start=1):
                if progress:
                    progress(done, len(leads))
    for lead in leads:
        counts[lead.personalization_source] = counts.get(lead.personalization_source, 0) + 1
    return counts

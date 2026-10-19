"""Scan each subcontractor's website for fit and hooks.

  * commercial vs residential language -> do they actually bid GC work?
  * certifications (MBE/WBE/DBE/SDVOSB...) -> GCs need them for participation goals
  * hiring -> busy now, worried about next year's backlog
  * project types, portfolio, safety, bonding, union -> how mature the shop is
"""

import re
import ssl
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from .db import now_iso
from .models import Lead
from .trades import detect_trade

USER_AGENT = "Mozilla/5.0 (compatible; FullBacklogScanner/0.1; +https://example.com/bot)"
MAX_BYTES = 1_500_000
FETCH_ERRORS = (urllib.error.URLError, TimeoutError, ConnectionError, ssl.SSLError, ValueError, OSError)

COMMERCIAL_RE = re.compile(
    r"commercial|general contractors?|tenant improvement|ground[- ]up|institutional|industrial|"
    r"design[- ]build|subcontract|\bbids?\b|preconstruction|project managers?|healthcare|data center|multifamily"
)
RESIDENTIAL_RE = re.compile(r"homeowners?|residential|free (?:in-home )?estimate|your home|kitchen|bathroom|remodel")
CERTIFICATIONS = [
    ("SDVOSB", r"\bsdvosb\b|service[- ]disabled veteran"),
    ("VOSB", r"\bvosb\b|veteran[- ]owned"),
    ("HUBZone", r"hubzone"),
    ("8(a)", r"\b8\(a\)"),
    ("DBE", r"\bdbe\b|disadvantaged business"),
    ("MBE", r"\bmbe\b|minority[- ]owned"),
    ("WBE", r"\bwbe\b|wosb|wom[ae]n[- ]owned"),
    ("SBE", r"\bsbe\b|small business enterprise"),
    ("HUB", r"\bhub\b certified|historically underutilized"),
]
PROJECT_TYPES = [
    ("healthcare", r"healthcare|hospital|medical"),
    ("education", r"education|school|universit|college|k-12"),
    ("data centers", r"data cent"),
    ("industrial", r"industrial|warehouse|distribution|manufactur"),
    ("multifamily", r"multifamily|multi-family|apartment"),
    ("hospitality", r"hospitality|hotel"),
    ("retail", r"retail|restaurant"),
    ("office", r"\boffice"),
    ("government", r"government|municipal|federal|military"),
]
UNION_RE = re.compile(r"union (?:contractor|signatory|shop)|signatory|\bibew\b|\biupat\b|local union|\blocal \d{2,4}\b")
SAFETY_RE = re.compile(r"\bemr\b|experience modification|\bosha\b|safety (?:record|program|first)")
BONDING_RE = re.compile(r"bonding capacity|bonded|bondable|surety")
HIRING_RE = re.compile(r"now hiring|we['’]re hiring|we are hiring|open positions|apply now|join our team")
PORTFOLIO_RE = re.compile(r"href=[\"'][^\"']*(projects|portfolio|our-work|experience|case-stud)")
EMAIL_RE = re.compile(r"(?:mailto:)?([a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,})")
JUNK_EMAIL_RE = re.compile(r"\.(png|jpe?g|gif|svg|webp)$|sentry|wixpress|example\.|domain\.com|email\.com|yourname|godaddy")


@dataclass
class Signals:
    trade: str = ""
    commercial_hits: int = 0
    residential_hits: int = 0
    certifications: tuple[str, ...] = ()
    union: bool = False
    mentions_safety: bool = False
    mentions_bonding: bool = False
    hiring: bool = False
    has_portfolio: bool = False
    project_types: tuple[str, ...] = ()
    emails: tuple[str, ...] = ()


def extract_emails(html: str, domain: str = "") -> list[str]:
    found: list[str] = []
    for match in EMAIL_RE.finditer(html.lower()):
        email = match.group(1).strip(".")
        if JUNK_EMAIL_RE.search(email) or email in found:
            continue
        found.append(email)
    if domain:
        found.sort(key=lambda e: 0 if e.endswith("@" + domain) else 1)
    return found


def visible_text(html: str) -> str:
    text = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", html)
    return re.sub(r"\s+", " ", re.sub(r"(?s)<[^>]+>", " ", text)).lower()


def detect_signals(html: str, domain: str = "") -> Signals:
    page = html.lower()
    text = visible_text(html)
    return Signals(
        trade=detect_trade(page=text),
        commercial_hits=len(COMMERCIAL_RE.findall(text)),
        residential_hits=len(RESIDENTIAL_RE.findall(text)),
        certifications=tuple(name for name, pattern in CERTIFICATIONS if re.search(pattern, text)),
        union=bool(UNION_RE.search(text)),
        mentions_safety=bool(SAFETY_RE.search(text)),
        mentions_bonding=bool(BONDING_RE.search(text)),
        hiring=bool(HIRING_RE.search(text)),
        has_portfolio=bool(PORTFOLIO_RE.search(page)),
        project_types=tuple(name for name, pattern in PROJECT_TYPES if re.search(pattern, text)),
        emails=tuple(extract_emails(page, domain)),
    )


def fetch(url: str, timeout: float = 10.0) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*"})
    with urllib.request.urlopen(request, timeout=timeout, context=ssl.create_default_context()) as response:
        raw = response.read(MAX_BYTES)
        charset = response.headers.get_content_charset() or "utf-8"
    return raw.decode(charset, errors="replace")


def apply_signals(lead: Lead, signals: Signals) -> Lead:
    lead.trade = lead.trade or signals.trade
    lead.commercial_hits = signals.commercial_hits
    lead.residential_hits = signals.residential_hits
    certs = [c.strip() for c in lead.certifications.split(",") if c.strip()]
    certs += [c for c in signals.certifications if c not in certs]
    lead.certifications = ", ".join(certs)
    lead.union_shop = int(signals.union)
    lead.mentions_safety = int(signals.mentions_safety)
    lead.mentions_bonding = int(signals.mentions_bonding)
    lead.hiring = int(signals.hiring)
    lead.has_portfolio = int(signals.has_portfolio)
    lead.project_types = ", ".join(signals.project_types)
    if not lead.email and signals.emails:
        lead.email = signals.emails[0]
    return lead


def scan_lead(lead: Lead, fetcher=fetch) -> Lead:
    """Homepage (https, then http), plus the contact page when no email was found."""
    lead.scanned_at = now_iso()
    if not lead.domain:
        lead.site_ok = 0
        return lead
    html = ""
    for scheme in ("https", "http"):
        try:
            html = fetcher(f"{scheme}://{lead.domain}/")
            break
        except FETCH_ERRORS:
            continue
    lead.site_ok = int(bool(html))
    if not html:
        return lead
    signals = detect_signals(html, lead.domain)
    if not signals.emails and not lead.email:
        for path in ("contact", "contact-us"):
            try:
                extra = extract_emails(fetcher(f"https://{lead.domain}/{path}/"), lead.domain)
            except FETCH_ERRORS:
                continue
            if extra:
                signals.emails = tuple(extra)
                break
    return apply_signals(lead, signals)


def scan_many(leads: list[Lead], workers: int = 16, fetcher=fetch, progress=None) -> list[Lead]:
    done = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for lead in pool.map(lambda item: scan_lead(item, fetcher), leads):
            done.append(lead)
            if progress:
                progress(len(done), len(leads), lead)
    return done

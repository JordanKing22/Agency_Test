"""Scan each lead's website for buying signals.

The signals drive both scoring and personalization:
  * running Google Ads  -> they pay for every call, so a missed call costs real money
  * no chat / no online booking -> nothing catches after-hours web visitors
  * call tracking -> they measure calls and will understand the pitch instantly
  * financing / membership plan -> a mature shop with replacement volume
"""

import re
import ssl
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from .db import now_iso
from .models import Lead

USER_AGENT = "Mozilla/5.0 (compatible; BookedOutScanner/0.1; +https://example.com/bot)"
MAX_BYTES = 1_500_000

CHAT_VENDORS = [
    ("Podium", r"podium\.com|podium-webchat"),
    ("Birdeye", r"birdeye\.com"),
    ("LeadConnector", r"leadconnectorhq\.com|msgsndr\.com"),
    ("Intercom", r"widget\.intercom\.io|intercomcdn\.com"),
    ("Drift", r"js\.driftt\.com|drift\.com/"),
    ("Tidio", r"code\.tidio\.co"),
    ("LiveChat", r"livechatinc\.com"),
    ("Tawk.to", r"embed\.tawk\.to"),
    ("HubSpot Chat", r"usemessages\.com"),
    ("Zendesk", r"static\.zdassets\.com"),
    ("Smith.ai", r"smith\.ai"),
    ("Olark", r"static\.olark\.com"),
    ("Crisp", r"client\.crisp\.chat"),
    ("Broadly", r"broadly\.com"),
    ("Hatch", r"usehatchapp\.com"),
    ("Signpost", r"signpost\.com"),
]

BOOKING_VENDORS = [
    ("ServiceTitan", r"scheduler\.servicetitan\.com|st-scheduler|servicetitan.{0,80}schedul"),
    ("Housecall Pro", r"housecallpro\.com"),
    ("Jobber", r"getjobber\.com"),
    ("Schedule Engine", r"scheduleengine"),
    ("FieldEdge", r"fieldedge"),
    ("Service Fusion", r"servicefusion"),
    ("Calendly", r"calendly\.com"),
    ("LeadConnector Booking", r"(leadconnectorhq|msgsndr)\.com/widget/booking"),
    ("Online booking", r"book (?:service |an appointment )?online|schedule (?:service |an appointment )?online|online booking|online scheduling"),
]

CALL_TRACKING = [
    ("CallRail", r"callrail"),
    ("CallTrackingMetrics", r"tctm\.co|calltrackingmetrics"),
    ("Invoca", r"invoca"),
    ("WhatConverts", r"whatconverts"),
]

GOOGLE_ADS_RE = re.compile(r"googleadservices\.com|['\"/=]aw-\d{6,}")
FB_PIXEL_RE = re.compile(r"connect\.facebook\.net/[^\"']*fbevents|fbq\(")
TWENTY_FOUR_SEVEN_RE = re.compile(r"24\s*/\s*7|24 hours|24-hour|24hr|around the clock")
FINANCING_RE = re.compile(r"financing|synchrony|greensky|goodleap|0% apr")
MEMBERSHIP_RE = re.compile(r"maintenance (?:plan|agreement|club|membership)|comfort club|service club|vip club|membership")
EMAIL_RE = re.compile(r"(?:mailto:)?([a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,})")
JUNK_EMAIL_RE = re.compile(r"\.(png|jpe?g|gif|svg|webp)$|sentry|wixpress|example\.|domain\.com|email\.com|yourname|godaddy")


@dataclass
class Signals:
    chat_vendor: str = ""
    booking_vendor: str = ""
    runs_google_ads: bool = False
    has_fb_pixel: bool = False
    call_tracking: str = ""
    mentions_24_7: bool = False
    has_financing: bool = False
    has_membership: bool = False
    emails: tuple[str, ...] = ()


def _first_match(html: str, vendors: list[tuple[str, str]]) -> str:
    for name, pattern in vendors:
        if re.search(pattern, html):
            return name
    return ""


def extract_emails(html: str, domain: str = "") -> list[str]:
    """Emails on the page, the company's own domain first."""
    found: list[str] = []
    for match in EMAIL_RE.finditer(html.lower()):
        email = match.group(1).strip(".")
        if JUNK_EMAIL_RE.search(email) or email in found:
            continue
        found.append(email)
    if domain:
        found.sort(key=lambda e: 0 if e.endswith("@" + domain) else 1)
    return found


def detect_signals(html: str, domain: str = "") -> Signals:
    page = html.lower()
    return Signals(
        chat_vendor=_first_match(page, CHAT_VENDORS),
        booking_vendor=_first_match(page, BOOKING_VENDORS),
        runs_google_ads=bool(GOOGLE_ADS_RE.search(page)),
        has_fb_pixel=bool(FB_PIXEL_RE.search(page)),
        call_tracking=_first_match(page, CALL_TRACKING),
        mentions_24_7=bool(TWENTY_FOUR_SEVEN_RE.search(page)),
        has_financing=bool(FINANCING_RE.search(page)),
        has_membership=bool(MEMBERSHIP_RE.search(page)),
        emails=tuple(extract_emails(page, domain)),
    )


def fetch(url: str, timeout: float = 10.0) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*"})
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
        raw = response.read(MAX_BYTES)
        charset = response.headers.get_content_charset() or "utf-8"
    return raw.decode(charset, errors="replace")


def apply_signals(lead: Lead, signals: Signals) -> Lead:
    lead.chat_vendor = signals.chat_vendor
    lead.booking_vendor = signals.booking_vendor
    lead.runs_google_ads = int(signals.runs_google_ads)
    lead.has_fb_pixel = int(signals.has_fb_pixel)
    lead.call_tracking = signals.call_tracking
    lead.mentions_24_7 = int(signals.mentions_24_7)
    lead.has_financing = int(signals.has_financing)
    lead.has_membership = int(signals.has_membership)
    if not lead.email and signals.emails:
        lead.email = signals.emails[0]
    return lead


def scan_lead(lead: Lead, fetcher=fetch) -> Lead:
    """Fetch the homepage (https, then http) and, if no email yet, the contact page."""
    lead.scanned_at = now_iso()
    if not lead.domain:
        lead.site_ok = 0
        return lead
    html = ""
    for scheme in ("https", "http"):
        try:
            html = fetcher(f"{scheme}://{lead.domain}/")
            break
        except (urllib.error.URLError, TimeoutError, ConnectionError, ssl.SSLError, ValueError, OSError):
            continue
    lead.site_ok = int(bool(html))
    if not html:
        return lead
    signals = detect_signals(html, lead.domain)
    if not signals.emails and not lead.email:
        for path in ("contact", "contact-us"):
            try:
                extra = extract_emails(fetcher(f"https://{lead.domain}/{path}/"), lead.domain)
            except (urllib.error.URLError, TimeoutError, ConnectionError, ssl.SSLError, ValueError, OSError):
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

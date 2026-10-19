"""Read lead CSVs from Google Maps scrapers (Outscraper, Apify), Apollo, GetLeads
or anything else with sensible headers, and normalize them into Leads."""

import csv
import hashlib
import re
from pathlib import Path

from .models import Lead

# Domains that are listings or social profiles, not the company's own website.
NOT_A_WEBSITE = {
    "facebook.com", "m.facebook.com", "instagram.com", "yelp.com", "google.com", "sites.google.com",
    "business.site", "linktr.ee", "angi.com", "homeadvisor.com", "nextdoor.com", "bbb.org",
    "thumbtack.com", "houzz.com", "linkedin.com", "x.com", "twitter.com", "youtube.com",
}

# Canonical field -> normalized header aliases, in priority order.
ALIASES: dict[str, list[str]] = {
    "company": ["company", "companyname", "businessname", "organizationname", "accountname", "name", "business"],
    "first_name": ["firstname", "first", "contactfirstname"],
    "last_name": ["lastname", "last", "contactlastname"],
    "full_name": ["fullname", "contactname", "ownername", "personname"],
    "title": ["title", "jobtitle", "position"],
    "email": ["email", "workemail", "emailaddress", "email1", "contactemail", "emails", "companyemail"],
    "phone": ["phone", "companyphone", "corporatephone", "phonenumber", "phone1", "workdirectphone",
              "mobilephone", "telephone", "phonenumbers"],
    "website": ["website", "site", "companywebsite", "websiteurl", "url", "domain", "companydomain"],
    "city": ["companycity", "city", "locality"],
    "state": ["companystate", "usstate", "state", "region", "statecode"],
    "lat": ["latitude", "lat", "locationlat"],
    "lon": ["longitude", "lng", "lon", "locationlng"],
    "rating": ["rating", "totalscore", "googlerating", "stars", "averagerating"],
    "reviews": ["reviews", "reviewscount", "reviewcount", "userratingstotal", "numberofreviews"],
    "category": ["category", "categoryname", "maincategory", "type", "industry", "subtypes"],
    "linkedin": ["personlinkedinurl", "linkedinurl", "linkedin"],
}

EMAIL_RE = re.compile(r"[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}", re.I)
LEGAL_SUFFIX_RE = re.compile(r"[,\s]+(llc|l\.l\.c\.|inc\.?|incorporated|corp\.?|corporation|co\.|ltd\.?|pllc)\s*$", re.I)


def norm_header(header: str) -> str:
    return re.sub(r"[^a-z0-9]", "", header.lower())


def detect_format(headers: list[str]) -> str:
    normed = {norm_header(h) for h in headers}
    if normed & {"totalscore", "reviewscount", "categoryname"} and "title" in normed:
        return "apify_google_maps"
    if "fulladdress" in normed or ("site" in normed and "name" in normed):
        return "outscraper"
    if "firstname" in normed and normed & {"company", "companyname"}:
        return "contact_list"
    return "generic"


def build_mapping(headers: list[str]) -> dict[str, str]:
    """Map canonical field -> the CSV header that holds it."""
    by_norm: dict[str, str] = {}
    for header in headers:
        by_norm.setdefault(norm_header(header), header)
    fmt = detect_format(headers)
    mapping: dict[str, str] = {}
    for field, aliases in ALIASES.items():
        for alias in aliases:
            if alias in by_norm:
                mapping[field] = by_norm[alias]
                break
    if fmt == "apify_google_maps":
        # Apify calls the business name "title"; there is no job title.
        mapping["company"] = by_norm["title"]
        mapping.pop("title", None)
    return mapping


def normalize_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) == 10:
        return "+1" + digits
    return ("+" + digits) if digits else ""


def normalize_domain(raw: str) -> str:
    value = (raw or "").strip().lower()
    if not value:
        return ""
    value = re.sub(r"^[a-z]+://", "", value)
    value = value.split("/")[0].split("?")[0].split("#")[0]
    value = value.removeprefix("www.")
    if "." not in value:
        return ""
    for listing in NOT_A_WEBSITE:
        if value == listing or value.endswith("." + listing):
            return ""
    return value


def first_email(raw: str) -> str:
    match = EMAIL_RE.search(raw or "")
    return match.group(0).lower() if match else ""


def clean_company(name: str) -> str:
    """'Smith Heating & Air, LLC | Furnace Repair' -> 'Smith Heating & Air'."""
    name = re.split(r"\s+[|\-–—]\s+", (name or "").strip())[0]
    previous = None
    while previous != name:
        previous = name
        name = LEGAL_SUFFIX_RE.sub("", name).strip()
    return name


def _to_float(raw: str) -> float | None:
    try:
        return float(str(raw).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def _to_int(raw: str) -> int | None:
    value = _to_float(raw)
    return int(value) if value is not None else None


def make_id(lead: Lead) -> str:
    basis = lead.domain or lead.phone or f"{lead.company}|{lead.city}|{lead.state}".lower()
    return hashlib.sha1(basis.encode()).hexdigest()[:10]


def row_to_lead(row: dict[str, str], mapping: dict[str, str], source: str) -> Lead | None:
    def get(field: str) -> str:
        header = mapping.get(field)
        return (row.get(header) or "").strip() if header else ""

    lead = Lead(source=source)
    lead.company = clean_company(get("company"))
    lead.first_name = get("first_name").title() if get("first_name").isupper() else get("first_name")
    lead.last_name = get("last_name")
    if not lead.first_name and get("full_name"):
        parts = get("full_name").split()
        lead.first_name = parts[0]
        lead.last_name = " ".join(parts[1:])
    lead.title = get("title")
    lead.email = first_email(get("email"))
    lead.phone = normalize_phone(get("phone"))
    lead.website = get("website")
    lead.domain = normalize_domain(lead.website)
    if not lead.domain and lead.email and not lead.email.split("@")[1] in {"gmail.com", "yahoo.com", "hotmail.com", "aol.com", "outlook.com", "icloud.com", "comcast.net"}:
        lead.domain = lead.email.split("@")[1]
    lead.city = get("city")
    lead.state = get("state")
    lead.lat = _to_float(get("lat"))
    lead.lon = _to_float(get("lon"))
    lead.rating = _to_float(get("rating"))
    lead.reviews = _to_int(get("reviews"))
    lead.category = get("category")
    lead.linkedin = get("linkedin")
    if not (lead.company or lead.domain or lead.phone):
        return None
    lead.id = make_id(lead)
    return lead


def read_leads(path: str | Path, source: str | None = None) -> tuple[list[Lead], dict[str, str], str]:
    """Return (leads, header mapping used, detected format)."""
    path = Path(path)
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        mapping = build_mapping(headers)
        fmt = detect_format(headers)
        leads = []
        for row in reader:
            lead = row_to_lead(row, mapping, source or fmt)
            if lead:
                leads.append(lead)
    return leads, mapping, fmt

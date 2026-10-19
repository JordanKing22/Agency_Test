"""Read CSVs and normalize them.

Two kinds of input:
  * Lead lists (subcontractors to sell to) from Google Maps scrapers, Apollo, GetLeads,
    association or DBE directories, or anything with sensible headers.
  * Building permit exports from a city or county open-data portal.
"""

import csv
import hashlib
import re
from datetime import datetime
from pathlib import Path

from .models import Lead, Permit
from .trades import detect_trade

NOT_A_WEBSITE = {
    "facebook.com", "m.facebook.com", "instagram.com", "yelp.com", "google.com", "sites.google.com",
    "business.site", "linktr.ee", "angi.com", "homeadvisor.com", "nextdoor.com", "bbb.org",
    "thumbtack.com", "houzz.com", "linkedin.com", "x.com", "twitter.com", "youtube.com", "buildzoom.com",
}
FREE_MAIL = {"gmail.com", "yahoo.com", "hotmail.com", "aol.com", "outlook.com", "icloud.com", "comcast.net", "att.net"}

LEAD_ALIASES: dict[str, list[str]] = {
    "company": ["company", "companyname", "businessname", "organizationname", "accountname", "firmname", "name", "business"],
    "first_name": ["firstname", "first", "contactfirstname"],
    "last_name": ["lastname", "last", "contactlastname"],
    "full_name": ["fullname", "contactname", "ownername", "personname", "contactperson"],
    "title": ["title", "jobtitle", "position"],
    "email": ["email", "workemail", "emailaddress", "email1", "contactemail", "emails", "companyemail"],
    "phone": ["phone", "companyphone", "corporatephone", "phonenumber", "phone1", "workdirectphone",
              "mobilephone", "telephone", "phonenumbers"],
    "website": ["website", "site", "companywebsite", "websiteurl", "url", "domain", "companydomain"],
    "city": ["companycity", "city", "locality"],
    "state": ["companystate", "usstate", "state", "region", "statecode"],
    "rating": ["rating", "totalscore", "googlerating", "stars", "averagerating"],
    "reviews": ["reviews", "reviewscount", "reviewcount", "userratingstotal", "numberofreviews"],
    "category": ["category", "categoryname", "maincategory", "type", "industry", "subtypes", "workcodes", "naicsdescription"],
    "employees": ["employees", "numberofemployees", "employeecount", "estimatednumemployees", "companysize", "headcount", "employeesrange"],
    "linkedin": ["personlinkedinurl", "linkedinurl", "linkedin"],
    "certifications": ["certifications", "certification", "certificationtype", "certtype"],
}

PERMIT_ALIASES: dict[str, list[str]] = {
    "contractor": ["contractorcompanyname", "contractorname", "contractorbusinessname", "permitteesbusinessname",
                   "generalcontractor", "gcname", "contractor", "contractorcompany", "applicantbusinessname",
                   "contact1name", "applicantname", "applicant"],
    "valuation": ["valuation", "totalvaluation", "estimatedcost", "estprojectcost", "reportedcost", "jobvalue",
                  "projectvalue", "declaredvaluation", "totaljobvaluation", "estimatedjobcost", "value", "cost"],
    "description": ["description", "workdescription", "projectdescription", "jobdescription", "descriptionofwork",
                    "permitdescription", "worktypedescription", "scopeofwork"],
    "permit_type": ["permittype", "permittypedesc", "permittypemapped", "permitclass", "permitclassmapped",
                    "worktype", "typeofwork", "workclass", "permitsubtype", "type"],
    "issued": ["issuedate", "issueddate", "dateissued", "issued", "permitissuedate", "finalizeddate",
               "applieddate", "applicationdate", "filingdate"],
    "permit_no": ["permitnumber", "permitnum", "permitno", "permit", "permitid", "jobnumber", "applicationnumber", "id"],
    "city": ["city", "originalcity", "jurisdiction", "municipality"],
    "address": ["address", "originaladdress1", "streetaddress", "siteaddress", "permitlocation", "location", "fulladdress"],
}

EMAIL_RE = re.compile(r"[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}", re.I)
LEGAL_SUFFIX_RE = re.compile(r"[,\s]+(llc|l\.l\.c\.|inc\.?|incorporated|corp\.?|corporation|co\.|ltd\.?|pllc|lp|llp)\s*$", re.I)


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


def build_mapping(headers: list[str], aliases: dict[str, list[str]]) -> dict[str, str]:
    by_norm: dict[str, str] = {}
    for header in headers:
        by_norm.setdefault(norm_header(header), header)
    mapping: dict[str, str] = {}
    for field, names in aliases.items():
        for alias in names:
            if alias in by_norm:
                mapping[field] = by_norm[alias]
                break
    if aliases is LEAD_ALIASES and detect_format(headers) == "apify_google_maps":
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
    value = re.sub(r"^[a-z]+://", "", (raw or "").strip().lower())
    value = value.split("/")[0].split("?")[0].split("#")[0].removeprefix("www.")
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
    """'Acme Interiors, LLC | Commercial Drywall' -> 'Acme Interiors'."""
    name = re.split(r"\s+[|\-–—]\s+", (name or "").strip())[0]
    previous = None
    while previous != name:
        previous = name
        name = LEGAL_SUFFIX_RE.sub("", name).strip()
    return name


def to_float(raw) -> float | None:
    try:
        return float(re.sub(r"[,$\s]", "", str(raw)))
    except (TypeError, ValueError):
        return None


def parse_employees(raw: str) -> int | None:
    """'45' -> 45, '11-50' -> 30, '51 to 200' -> 125, '1,001-5,000' -> 3000."""
    numbers = [int(n.replace(",", "")) for n in re.findall(r"\d[\d,]*", raw or "")]
    if not numbers:
        return None
    if len(numbers) == 1:
        return numbers[0]
    return (numbers[0] + numbers[1]) // 2


def parse_date(raw: str) -> str:
    text = (raw or "").strip()
    if not text:
        return ""
    if re.match(r"\d{4}-\d{2}-\d{2}", text):
        return text[:10]
    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%m-%d-%Y", "%Y/%m/%d", "%b %d, %Y", "%d-%b-%Y"):
        try:
            return datetime.strptime(text.split(" ")[0] if "/" in text else text, fmt).date().isoformat()
        except ValueError:
            continue
    return ""


def make_id(*parts: str) -> str:
    return hashlib.sha1("|".join(parts).lower().encode()).hexdigest()[:10]


# --- leads -------------------------------------------------------------------

def row_to_lead(row: dict[str, str], mapping: dict[str, str], source: str) -> Lead | None:
    def get(field: str) -> str:
        header = mapping.get(field)
        return (row.get(header) or "").strip() if header else ""

    lead = Lead(source=source)
    lead.company = clean_company(get("company"))
    first = get("first_name")
    lead.first_name = first.title() if first.isupper() else first
    lead.last_name = get("last_name")
    if not lead.first_name and get("full_name"):
        parts = get("full_name").split()
        lead.first_name, lead.last_name = parts[0], " ".join(parts[1:])
    lead.title = get("title")
    lead.email = first_email(get("email"))
    lead.phone = normalize_phone(get("phone"))
    lead.website = get("website")
    lead.domain = normalize_domain(lead.website)
    if not lead.domain and lead.email and lead.email.split("@")[1] not in FREE_MAIL:
        lead.domain = lead.email.split("@")[1]
    lead.city = get("city")
    lead.state = get("state")
    lead.category = get("category")
    lead.employees = parse_employees(get("employees"))
    lead.rating = to_float(get("rating"))
    reviews = to_float(get("reviews"))
    lead.reviews = int(reviews) if reviews is not None else None
    lead.linkedin = get("linkedin")
    lead.certifications = get("certifications")
    lead.trade = detect_trade(lead.category, lead.company)
    if not (lead.company or lead.domain or lead.phone):
        return None
    lead.id = make_id(lead.domain or lead.phone or f"{lead.company}|{lead.city}|{lead.state}")
    return lead


def read_leads(path: str | Path, source: str | None = None) -> tuple[list[Lead], dict[str, str], str]:
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        mapping = build_mapping(headers, LEAD_ALIASES)
        fmt = detect_format(headers)
        leads = [lead for row in reader if (lead := row_to_lead(row, mapping, source or fmt))]
    return leads, mapping, fmt


# --- permits -----------------------------------------------------------------

def read_permits(path: str | Path, market: str = "", city: str = "",
                 min_commercial_value: float = 250_000) -> tuple[list[Permit], dict[str, str]]:
    """Read a permit export. Classification and contractor grouping happen in permits.py."""
    from .permits import classify_commercial, contractor_key  # avoid an import cycle

    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        mapping = build_mapping(reader.fieldnames or [], PERMIT_ALIASES)
        permits = []
        for row in reader:
            def get(field: str) -> str:
                header = mapping.get(field)
                return (row.get(header) or "").strip() if header else ""

            permit = Permit(
                city=get("city") or city,
                permit_no=get("permit_no"),
                permit_type=get("permit_type"),
                description=get("description"),
                contractor=get("contractor"),
                valuation=to_float(get("valuation")),
                issued=parse_date(get("issued")),
                address=get("address"),
            )
            permit.market = market or permit.city
            permit.contractor_key = contractor_key(permit.contractor)
            permit.commercial = int(classify_commercial(permit, min_commercial_value))
            permit.id = make_id(permit.market, permit.permit_no or f"{permit.address}|{permit.issued}|{permit.description}")
            permits.append(permit)
    return permits, mapping

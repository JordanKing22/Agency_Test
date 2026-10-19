# 4. Tech stack and startup budget

Prices move; check each vendor's pricing page before you buy. Ranges are planning numbers.

## Sell (outreach)

| Need | Pick | Alternative | Rough cost |
|---|---|---|---|
| Permit data | City / county open-data portals (CSV export) | County building department records requests | $0 |
| Sub lead lists | Outscraper or Apify Google Maps scraper | GetLeads (connected here), Apollo | $0-$50 to start |
| Certified sub lists | State DOT DBE directories, city/county MBE/WBE directories, SBA certification search | | $0 |
| Owner / estimator contacts | Apollo or GetLeads | LinkedIn Sales Navigator | $0-$99/mo |
| Email verification | Sending tool's verifier | MillionVerifier, NeverBounce | ~$5-$20 per 1-2k |
| Sending + warmup | Instantly | Smartlead | ~$40-$100/mo |
| Sending domains + inboxes | 3 lookalike domains, 2-3 Google Workspace or Microsoft 365 inboxes each | Pre-warmed inbox providers | ~$10-$15/yr per domain, ~$7-$14/inbox/mo |
| LinkedIn | Your profile, rewritten for subs ("I help commercial subs get on more GC bid lists") | Sales Navigator | $0-$100/mo |
| Engine | `engine/` (this repo) + optional Claude API for openers | | pennies per lead |
| Booking / payments / website | Cal.com, Stripe, Cloudflare Pages or Netlify | Calendly | ~$0-$15/mo + Stripe fees |

## Deliver (fulfillment)

| Need | Pick | Notes |
|---|---|---|
| Outreach to GCs for a client | A mailbox on the **client's** domain (e.g. `bids@acmeinteriors.com` or a named BD mailbox), sent manually or through your sending tool at low volume | Relevant B2B email from a real company domain to GCs who want more subs. Keep it under ~40/day per mailbox |
| GC contacts | Apollo / GetLeads people search by GC domain: Chief Estimator, Estimator, Preconstruction Manager/Director, Procurement/Buyout Manager, Project Manager | Start from `gc-targets-*.csv` from `fullbacklog gap-audit` |
| Bid platforms | BuildingConnected, PlanHub, ConstructConnect, iSqFt, Procore (client's free sub profiles) | You manage profiles with the client's login and permission; the client keeps ownership |
| Prequal platforms GCs use | TradeTapp, Highwire, Compass and GC-specific forms | Client approves every submission; never guess at financials or safety data |
| Bid tracking | Airtable or a Google Sheet per client (template in `delivery/bid-desk.md`) | Bid, GC, due date, number, follow-up dates, result, buyout contact |
| Document vault | Shared Google Drive / OneDrive folder owned by the client | COI, W-9, EMR letter, bonding letter, licenses, certifications, financials |
| Coordinator | Part-time VA (US or offshore) for triage, follow-ups and paperwork | Hire before your 4th Bid Desk client |

## Month-one budget

| Item | Low | High |
|---|---|---|
| Domains (main + 3 sending) | $40 | $60 |
| Inboxes (8-10) | $60 | $140 |
| Sending tool | $40 | $100 |
| Lead and contact data | $0 | $150 |
| Claude API (openers for a few thousand leads) | $5 | $30 |
| Association membership or event ticket (optional) | $0 | $300 |
| **Total** | **~$145** | **~$780** |

One founding sprint covers it.

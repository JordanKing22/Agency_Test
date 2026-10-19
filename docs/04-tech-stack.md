# 4. Tech stack and startup budget

Prices move; check each vendor's pricing page before you buy. Ranges below are planning numbers.

## Sell (outreach)

| Need | Pick | Alternative | Rough cost |
|---|---|---|---|
| Lead lists | Outscraper or Apify Google Maps scraper | GetLeads (connected here), Apollo | $0-$50 to start |
| Owner emails | Apollo or GetLeads contact export | Outscraper email enrichment | $0-$99/mo |
| Email verification | Your sending tool's built-in verifier | MillionVerifier, NeverBounce | ~$5-$20 per 1-2k |
| Sending + warmup | Instantly | Smartlead | ~$40-$100/mo |
| Sending domains | 3 lookalikes (e.g. `trybookedout.com`) | | ~$10-$15/yr each |
| Inboxes | Google Workspace or Microsoft 365, 2-3 per domain | Pre-warmed inbox providers | ~$7-$14/inbox/mo |
| Cold calling | Your phone or Google Voice, manual dial | A power dialer with *manual* dialing | $0-$50/mo |
| Engine | `engine/` (this repo) + optional Claude API for openers | | pennies per lead |
| Booking | Cal.com | Calendly | $0-$15/mo |
| Payments | Stripe payment links + subscriptions | | 2.9% + 30¢ |
| Website | `website/` on Cloudflare Pages or Netlify | | $0 |

**Email setup rules:** never send cold email from your main domain; SPF, DKIM and DMARC on every sending domain;
plain text, no images, at most one link (none in step 1); 30-40 sends per inbox per day after warmup; keep
warmup running forever.

## Deliver (fulfillment)

| Need | Pick | Alternative | Notes |
|---|---|---|---|
| CRM, SMS, automations, client sub-accounts | GoHighLevel (agency plan) | HubSpot + Twilio, or build on the client's FSM | One sub-account per client; snapshot your build so setup takes hours, not days |
| AI voice agent | Retell AI | Vapi, Synthflow | Roughly $0.10-$0.30/min all-in depending on model, voice and telephony |
| Phone numbers / SMS | Twilio (or GHL's LC Phone) | Telnyx | Register A2P 10DLC per client brand before any texting |
| Field service software | Client's: ServiceTitan, Housecall Pro, Jobber, FieldEdge | | Book via API/integration where available; otherwise a synced calendar + notification to the CSR |
| Reporting | GHL dashboards or a Google Sheet | | Weekly report template in `delivery/weekly-report-template.md` |
| Call recordings / QA | Built into Retell/Vapi | | Review 10 calls a week per client |

## Month-one budget

| Item | Low | High |
|---|---|---|
| Domains (main + 3 sending) | $40 | $60 |
| Inboxes (8-10) | $60 | $140 |
| Sending tool | $40 | $100 |
| Lead data | $0 | $100 |
| GoHighLevel | $97 | $297 |
| Voice AI demo line + phone number | $20 | $50 |
| Claude API (openers for a few thousand leads) | $5 | $30 |
| **Total** | **~$260** | **~$780** |

Your first founding sprint pays for all of it.

# Agency playbooks

This repo holds two complete, independent agencies. Each has its own niche, offer, outreach engine, website,
sales scripts and delivery playbooks.

| Agency | Sells to | Offer | Where |
|---|---|---|---|
| **BookedOut** | Owner-operated HVAC companies | Estimate Recovery Sprint ($1,500) → AI Dispatcher ($997/mo) | this page and the root folders (`docs/`, `engine/`, `sales/`, `website/`, `delivery/`) |
| **FullBacklog** | Commercial specialty subcontractors (drywall, electrical, glazing, concrete, fire protection...) | Bid List Sprint ($2,500) → Bid Desk ($2,500/mo). No AI receptionist | [`specialty/`](specialty/README.md) |

---

# BookedOut: an AI dispatch and estimate-recovery agency for HVAC companies

Everything you need to launch and sell: the niche, the offer, the outreach engine, the website, the sales scripts
and the delivery playbooks.

## The business in one paragraph

We sell to **owner-operated HVAC companies** (3-30 trucks) in cold-winter US metros. Instead of selling them more
leads, we sell **recovered revenue**: (1) a 14-day **Estimate Recovery Sprint** that turns their old, unsold
replacement quotes into booked appointments, $1,500 with a "5 appointments or you pay nothing" guarantee; and
(2) an **AI Dispatcher** that answers every call 24/7, triages emergencies and books jobs into their schedule,
$997/month + $1,500 setup. The sprint gets the first yes in days; its fee is credited toward the dispatcher, which
makes the second yes easy. It's late October, so heating season is about to fill their phones.

Why this niche and offer: [`docs/01-niche.md`](docs/01-niche.md). Pricing, guarantees, unit economics and a
6-month revenue model (~$80k collected, ~$12k MRR at conservative rates): [`docs/02-offer.md`](docs/02-offer.md).

## What's in here

| Folder | What it is | Start with |
|---|---|---|
| [`docs/`](docs) | Strategy: niche, offer, 30-day launch plan, tech stack, compliance | [`03-launch-plan.md`](docs/03-launch-plan.md) |
| [`engine/`](engine) | Python CLI: import lead lists, scan websites for buying signals, pull cold-snap forecasts, score, write openers (optionally with Claude), export to Instantly/Smartlead, build daily call sheets, track the pipeline | [`engine/README.md`](engine/README.md) |
| [`sales/`](sales) | Cold call openers, voicemail, gatekeeper, the 30-minute close, objections, social DMs, follow-ups, and 5 email sequences | [`cold-call.md`](sales/cold-call.md) |
| [`website/`](website) | Landing page with a missed-revenue calculator and audit form, plus A2P-ready privacy and SMS terms pages | `website/index.html` |
| [`delivery/`](delivery) | The AI dispatcher prompt + functions + 20-call test script, the sprint playbook with customer templates, onboarding, proposal and weekly report | [`ai-dispatcher-prompt.md`](delivery/ai-dispatcher-prompt.md) |

## Your first 72 hours

1. **Rename or keep the brand.** "BookedOut" is a placeholder: find-and-replace it, and check domain
   availability before you buy (`getbookedout.com`, `trybookedout.com`, ...).
2. **Set up sending** (it needs 14 days of warmup, so do it first): 3 lookalike domains, 2-3 inboxes each,
   SPF/DKIM/DMARC, warmup on in Instantly or Smartlead. → `docs/04-tech-stack.md`
3. **Build your demo dispatcher** on Retell or Vapi from `delivery/ai-dispatcher-prompt.md` and get a phone
   number for it. This is your best sales tool: prospects call it during the pitch.
4. **Publish the website.** Edit the `CONFIG` block at the bottom of `website/index.html` (demo line, calendar
   link, form endpoint, email, address), fill the `[bracketed]` values in `privacy.html` and `terms.html`, then
   drag the `website/` folder onto Cloudflare Pages or Netlify.
5. **Stripe payment links:** $997 founding sprint, $1,500 sprint, $1,500 setup, $997/month subscription.
6. **Build your first list and start calling:**
   ```bash
   cd engine && pip install -e . && cp config.example.toml config.toml   # edit config.toml
   bookedout import ~/Downloads/hvac-minneapolis.csv
   bookedout daily
   open out/callsheet-*.md
   ```
7. **Tonight, 6-8pm:** after-hours audits on your top 20 leads (`bookedout audit-list`). Every unanswered line
   becomes your strongest opener tomorrow morning.

Then follow the day-by-day plan in [`docs/03-launch-plan.md`](docs/03-launch-plan.md).

## Before you contact anyone

Read [`docs/05-compliance.md`](docs/05-compliance.md). Short version: cold email with an opt-out and a postal
address; dial manually; never cold text; never use AI voice for outbound calls; only text a client's customers who
opted in, from an A2P-registered number. Have an attorney review your client agreement and texting templates.

## What's real and what's a placeholder

- **Real and tested:** the engine (20 unit tests, `python3 -m unittest discover -s engine/tests`), the calculator
  math, the scripts, sequences and playbooks.
- **Placeholders you must replace:** brand name, demo phone number, calendar link, form endpoint, address, legal
  name, and the `[bracketed]` values in the legal pages. The sample lead files in `engine/sample_data/` are
  fictional (`.example` domains, 555 numbers).
- **Planning assumptions, not promises:** the reply rates, close rates and revenue model in `docs/02-offer.md`.
  Replace them with your own numbers by week 3. Guarantee thresholds should be revisited after your first three
  sprints.

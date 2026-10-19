# FullBacklog: a bid-pipeline agency for commercial specialty subcontractors

Everything you need to launch and sell: the niche, the offer, the outreach engine, the website, the sales scripts
and the delivery playbooks. No AI receptionist anywhere in it.

## The business in one paragraph

We sell to **commercial specialty subcontractors** (drywall, electrical, glazing, concrete, fire protection,
painting, flooring and similar trades; 10-200 employees) whose work comes from general contractors' invitations to
bid. We sell **more invitations to bid and follow-up on every bid**: (1) a 30-day **Bid List Sprint** that gets
them onto at least 10 new GC bid lists or they don't pay, $2,500; and (2) the **Bid Desk**, $2,500/month, which
triages their invitations, chases every bid after bid day, and keeps adding GCs. One sub per trade per metro. The
hook that makes it all work is public data: city permit records show which GCs are building the most right now,
and the **Bid List Gap Audit** shows a sub exactly which of them never invite them.

Why this niche and offer: [`docs/01-niche.md`](docs/01-niche.md). Pricing, guarantees, unit economics and a 6-month
model (~$110k collected, ~$20k MRR at conservative rates): [`docs/02-offer.md`](docs/02-offer.md).

## What's in here

| Folder | What it is | Start with |
|---|---|---|
| [`docs/`](docs) | Niche, offer, 30-day launch plan, tech stack, compliance | [`03-launch-plan.md`](docs/03-launch-plan.md) |
| [`engine/`](engine) | Python CLI: imports permit data and ranks GCs per market, imports and scans sub leads (trade, commercial focus, certifications, hiring), scores, writes openers (optionally with Claude), exports to Instantly/Smartlead, builds call sheets and Gap Audits, tracks the pipeline | [`engine/README.md`](engine/README.md) |
| [`sales/`](sales) | Cold call openers, the 30-minute close with a live Gap Audit, objections, LinkedIn and association playbook, follow-ups, 4 email sequences | [`cold-call.md`](sales/cold-call.md) |
| [`website/`](website) | Landing page with an example Gap Audit, backlog calculator, scope-of-work pricing and audit request form; privacy and terms templates | `website/index.html` |
| [`delivery/`](delivery) | Sprint playbook, GC outreach templates, Bid Desk operating manual (bid/no-bid scorecard, follow-up cadence, GC scorecard), onboarding, proposal, monthly report | [`bid-list-sprint.md`](delivery/bid-list-sprint.md) |

## Your first 72 hours

1. **Rename or keep the brand.** "FullBacklog" is a placeholder; check domains before you buy.
2. **Start email warmup today** (14 days): 3 lookalike domains, 2-3 inboxes each, SPF/DKIM/DMARC. → `docs/04-tech-stack.md`
3. **Get permit data for your first metro** from its open-data portal (CSV with contractor name, valuation, issue date):
   ```bash
   cd specialty/engine && pip install -e . && cp config.example.toml config.toml   # set [markets]
   fullbacklog permits ~/Downloads/austin-permits.csv --market Austin
   fullbacklog gap-audit --market Austin            # learn the top 10 GC names
   ```
4. **Build your first lead list** (Google Maps per trade + Apollo/GetLeads owners + your state's DBE directory):
   ```bash
   fullbacklog import leads/*.csv
   fullbacklog daily
   open out/callsheet-*.md
   ```
5. **Publish the website**: edit the `CONFIG` block at the bottom of `website/index.html`, fill the bracketed values
   in `privacy.html` / `terms.html`, deploy the folder to Cloudflare Pages or Netlify.
6. **Stripe payment links**: $1,500 founding sprint, $2,500 sprint, $1,500 onboarding, $2,500/month.
7. **Tomorrow, 6:30am**: start dialing. Offer every owner the free Gap Audit for their market.

## Before you contact anyone

Read [`docs/05-compliance.md`](docs/05-compliance.md). Short version: cold email with an opt-out and postal address;
dial manually; no texting; represent clients honestly to GCs and only with facts from their own documents; never
share one client's bid information with anyone; one client per trade per metro.

## What's real and what's a placeholder

- **Real and tested:** the engine (21 unit tests: `python3 -m unittest discover -s specialty/engine/tests`), the
  calculator math, the scripts, sequences and playbooks.
- **Placeholders:** brand, calendar link, form endpoint, address, legal name, `[bracketed]` legal values. All sample
  data (`engine/sample_data/`, the website's example audit) is fictional: `.example` domains, 555 numbers, made-up GCs.
- **Planning assumptions, not promises:** reply rates, close rates and the revenue model in `docs/02-offer.md`.
  Revisit guarantee thresholds after your first three sprints.

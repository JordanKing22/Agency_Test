# Bid List Sprint: 30-day playbook

**Promise:** at least 10 new GCs add the client to their bid list, accept their prequal, or send them an
invitation to bid within 30 days of receiving their documents. Otherwise a full refund. Read
`docs/05-compliance.md` first: everything you say about the client must come from their own documents.

## Day 0: kickoff (30 minutes)

1. Confirm the target: trade(s), CSI divisions, project types, sweet-spot package size, max size (bonding), service
   area, union/open shop, certifications.
2. Their current GC list: who invites them, who awards them, who they refuse to work for (and why).
3. Collect documents into the client-owned shared folder (checklist below).
4. Approve the outreach templates (`gc-outreach-templates.md`) and the signature: "{Your name}, Business
   Development, {Client}" from a mailbox on their domain.
5. Logins (or delegate access) for BuildingConnected, PlanHub, ConstructConnect and any GC portals they use.
6. Agree who answers GC questions about scope and pricing (always the client) and how fast.

**Document checklist**
- [ ] Certificate of insurance (GL, auto, umbrella, workers' comp limits)
- [ ] W-9
- [ ] EMR letter from their insurer (last 3 years) and OSHA 300A summaries
- [ ] Bonding letter from their surety (single and aggregate capacity), if they bond
- [ ] Contractor licenses (state / city)
- [ ] Certifications (MBE, WBE, DBE, SBE, SDVOSB, HUBZone, 8(a)) with certifying agency and expiry
- [ ] Project list: 10-20 recent projects with GC, owner, type, size, scope, contract value, completion year, GC
      reference contact
- [ ] Safety program summary; union affiliation or open shop
- [ ] Financial statements (only if they're willing; many GC prequals ask; never send without explicit approval)

## Week 1: package and targets

**Capabilities statement (1 page, PDF)**
- Company name, trade, CSI divisions, years in business, crew size, service area
- Project types and package size range (e.g. "$50k-$2.5M interior packages")
- Safety (EMR), bonding capacity, insurance limits, licenses, certifications, union/open shop
- 5-6 representative projects with GC names (with permission)
- Contact for ITBs: the client's estimating email

**Bid platform profiles**
- BuildingConnected / PlanHub / ConstructConnect / iSqFt: correct trades (CSI codes), regions (exact counties), project
  size range, labor type, certifications, capabilities PDF, current contact emails. Junk ITBs usually come from
  over-broad profiles.

**Target list (60-100 GCs)**
1. `fullbacklog gap-audit --market {market} --company "{client}" --known client-gcs.txt --n 100`
2. Remove GCs the client already works with or refuses; add GCs from association directories, bid board plan-holder
   lists and the client's own wish list.
3. Prioritize: GCs building the client's project types, at the client's package size, who use their labor type.
4. Enrich the `gc-targets-*.csv` in Apollo/GetLeads: Chief Estimator, Estimator, Preconstruction Manager/Director,
   Procurement/Buyout Manager, Project Manager. Two or three contacts per GC.
5. Have the client approve the final list. Never pitch them to a GC they didn't approve.

## Weeks 2-4: outreach and prequals

| Day | Action |
|---|---|
| 8 | Email 1 to every target contact (`gc-outreach-templates.md`); connect on LinkedIn |
| 9-11 | Call the estimating line of the top 30 GCs: "who handles sub prequal / bid list for {trade}?" |
| 11 | Email 2 (in thread) |
| 12-20 | Submit prequals as GCs request them (client approves each one first); log every "added" confirmation |
| 15 | Email 3 to non-responders |
| 16-25 | Second round of calls; ask for a 15-minute intro meeting with the client for the 5 warmest GCs |
| 22 | Breakup email to non-responders; move to the Bid Desk list for later |

**What counts toward the guarantee (log proof for each):** written confirmation the client was added to the bid list
or sub database; prequal accepted; or an ITB received from a GC that hadn't invited them in the prior 12 months.

**Tracking sheet columns:** GC · contact · title · email · phone · first touch · replies · prequal required (Y/N) ·
prequal submitted · prequal accepted · added confirmation · first ITB date · notes.

## Weekly update (Friday, to the client)

> {Week n}: {x} GCs contacted, {y} replies, {z} added you / accepted prequal ({names}), {w} ITBs so far ({names, bid
> dates}). Prequals waiting on your approval: {list}. Next week: {plan}.

## Day 30: results call → Bid Desk

Report: GCs contacted, replies, prequals submitted/accepted, GCs that added them (with proof), ITBs received (GC,
project, bid date, size), intro meetings held, and what's still pending.

> "So in 30 days you're on {14} new lists and you've had {31} invitations, {12} of them in your sweet spot. The next
> part is what wins work: triaging those ITBs so your estimators only price the good ones, chasing every bid after bid
> day, and adding GCs every month. That's the Bid Desk, $2,500 a month, and the onboarding fee is waived if we start
> within two weeks. Want to keep going?"

If the guarantee wasn't met: refund promptly, without argument, and offer to keep working the list for free for two
more weeks. The construction world is small; reputation matters more than one fee.

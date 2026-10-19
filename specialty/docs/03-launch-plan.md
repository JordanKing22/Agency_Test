# 3. Launch plan: first sprint sold in 7-14 days, first $10k month in ~60

Email inboxes need about two weeks of warmup, so **start them on day 1 and sell by phone while they warm.** Your
unfair advantage is the Gap Audit: build it for your first market on day 2 and every conversation gets easier.

## Days 1-2: set up (about 8 hours)

| Task | Why | Where |
|---|---|---|
| Buy your main domain + 3 lookalike sending domains | Never cold email from your main domain | `docs/04-tech-stack.md` |
| 2-3 inboxes per sending domain, SPF/DKIM/DMARC, warmup on | 14 days to safe volume | Instantly / Smartlead |
| Publish the website (`website/` onto Netlify or Cloudflare Pages) | Prospects check you out | `website/` |
| Pick your first 2 metros and download their permit data | Powers your hooks and the Gap Audit | city open-data portals |
| Stripe: payment links for $1,500 founding sprint, $2,500 sprint, $1,500 onboarding, $2,500/mo subscription | Collect on the call | Stripe |
| Calendar page: "15-minute Bid List Gap review" | CTA everywhere | Cal.com / Calendly |
| Template your capabilities statement and prequal checklist | You'll build one per client | `delivery/bid-list-sprint.md` |

## Days 2-3: data and first list

```bash
fullbacklog permits data/austin-permits.csv --market Austin
fullbacklog markets                               # sanity-check the top GCs look right
fullbacklog import leads/austin-subs.csv leads/apollo-austin.csv
fullbacklog daily
```

- Scrape Google Maps per trade per metro ("commercial drywall contractor Austin", "glazing contractor Austin", ...).
  Aim for 300-600 subs per metro across your target trades.
- Pull owners / presidents / chief estimators from Apollo or GetLeads.
- Download your state DOT's DBE directory and any city MBE/WBE directory for certified subs.
- Run `fullbacklog gap-audit --market Austin` and read it. Learn the top 10 GC names; you'll say them on every call.

## Days 3-14: phone-first

**Daily schedule (prospect's local time):**

| Time | Activity | Target |
|---|---|---|
| 6:30-7:30am | Cold calls from the call sheet: owners before they leave for jobsites | 25 dials |
| 8:00-10:00 | LinkedIn: connect with owners / chief estimators, comment, DM (`sales/dms.md`) | 25 touches |
| 10:00-3:00 | Sales calls, Gap Audits for booked prospects, client delivery | |
| 3:30-5:00pm | Cold calls round two | 25 dials |
| Evening | `fullbacklog stats`, tomorrow's call sheet, send promised Gap Audits | |

Goal by day 5: first sales call booked. Goal by day 7-14: first founding sprint paid.

Also this month: go to one local association event (ASA, ABC or AGC chapter, or a trade association meeting).
Subs and GCs are in the same room, and you'll meet both your buyers and the GCs you'll pitch for them.

## Days 15-30: email on, phone stays on

- Day 15: start campaigns at 15 sends/inbox/day; day 18: 25; day 21: 30-40.
- Upload `out/instantly-*.csv` into matching campaigns (copy in `sales/email-sequences.md`).
- Reply to positive replies within 15 minutes; send the Gap Audit the same day you're asked for it.
- Run your first sprints (`delivery/bid-list-sprint.md`). The day-30 report becomes your first case study.

## Days 31-60: convert and compound

- Day 30 of each sprint: results call → Bid Desk (onboarding waived within 14 days).
- Turn results into one-page case studies: "Added to 14 new GC bid lists, 31 ITBs in 30 days, first award in week 7."
- Add a third metro. Hire a part-time coordinator before your 4th Bid Desk client.
- Raise the sprint to $2,500 (founding spots gone); after 3 documented wins, test $3,500.

## Scoreboard

| Metric | Daily target | Healthy rate |
|---|---|---|
| Dials | 50 | |
| Owner / chief estimator conversations | 5 | ~10% of dials |
| LinkedIn touches | 25 | |
| Emails sent (from day 21) | 300 | |
| Positive replies | 2-3 | 0.5-1% of sends |
| Gap Audits sent | 1-2 | |
| Sales calls booked | 1 | |
| Show rate | | 70%+ (confirm the day before and 2 hours before) |
| Close rate (held calls) | | 15-25% |

## Kill / fix rules

| Symptom | Fix |
|---|---|
| < 1 positive reply per 500 emails after 2,000 sends | Lead with the Gap Audit offer in step 1; tighten trade targeting; seed-test inbox placement |
| Many "sure, send the list" replies but no calls | Send the audit with 3 GCs blank and offer to fill the rest on a 15-minute call |
| Calls held, no closes | Show the audit live, ask "which of these invite you?", then offer the sprint and its guarantee in the same breath |
| Sprints hit < 10 new bid lists | More GCs in the target list, faster prequal turnaround, add phone calls to GC estimators |
| Bid Desk clients churn at month 3 | Win/loss scorecard isn't visible enough; show awards and pipeline in every monthly review |

## Weekly review (Friday, 30 minutes)

1. `fullbacklog stats`: where does the funnel leak?
2. Which sequence and which trade reply best? Shift volume.
3. Add the week's most common objection and best answer to `sales/objections.md`.
4. Refresh permit data monthly; the top-GC list changes.

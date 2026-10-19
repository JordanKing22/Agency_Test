# 2. The offer

Brand: **BookedOut** ("Every call answered. Every estimate followed up. Every truck booked out.")
Rename it with one find-and-replace if you prefer something else; check domain availability first
(`getbookedout.com`, `bookedouthq.com`, `trybookedout.com` are the patterns to try).

## The ladder

```
  FRONT END (cash in week 1)            CORE (recurring)                 TOP (expansion)
  Estimate Recovery Sprint     ──►      AI Dispatcher            ──►     BookedOut Complete
  $1,500 one-time, 14 days              $997/mo + $1,500 setup           $1,997/mo
  5 booked appts or full refund         pays for itself in 60 days       everything + monthly campaigns
                                        or setup fee back
         └── sprint fee is credited 100% toward Dispatcher setup if they upgrade within 14 days ──┘
```

The sprint exists to make the first yes easy. The credit makes the second yes automatic.

---

## Offer 1: Estimate Recovery Sprint (front end)

**Promise:** "In 14 days we'll turn your old, unsold replacement quotes into booked appointments on your
calendar. If we don't book at least 5, you pay nothing."

**Price:** $1,500 flat. **Founding rate: $997 for the first 5 clients** in exchange for a written review, a
short video testimonial if results are good, and permission to share anonymized numbers.

**What's included**
1. Kickoff call (30 min) + export walkthrough for ServiceTitan / Housecall Pro / Jobber / FieldEdge
2. List cleaning: dedupe, remove customers who bought, opted out or are on DNC lists; segment into hot (0-90
   days), warm (3-12 months) and cold (12-24 months)
3. A reason to act now, built with the owner (winter install slots, extended labor warranty, financing promo,
   price-hold on their original quote)
4. Campaign: 3 emails to the whole list + 2 texts to customers with SMS consent + phone follow-up on the hot
   segment and every responder
5. Appointments booked directly onto their calendar with notes (system, quote amount, objection)
6. Daily text update to the owner; end-of-sprint report with pipeline value
7. Sprint fee credited toward AI Dispatcher setup if they upgrade within 14 days

**Qualification (protects your guarantee)**
- At least 250 unsold estimates from the last 24 months, or 1,000+ past customers
- They can export the list within 48 hours of paying
- Someone on their team runs the appointments within 72 hours of booking
- They confirm which contacts gave SMS consent (no consent → email and phone only)

**Guarantee:** at least 5 booked appointments (homeowner confirmed a date and time for a replacement
consultation) within 14 days of receiving the list, or a full refund. Refund requests within 7 days of the
sprint end. Adjust the number after your first 3 sprints once you know your real booking rates.

---

## Offer 2: AI Dispatcher (core, recurring)

**Promise:** "Every call to {company} gets answered on the first ring, 24/7, by a dispatcher that triages
emergencies, books jobs into your schedule and never calls in sick."

**Price:** $1,500 setup + $997/month. 90-day initial term, then month-to-month.
Annual prepay option once it has proved itself: 10 months' price for 12 ($9,970 upfront).

**What's included**
- 24/7 AI voice answering on after-hours + overflow (or every call, their choice). Tells callers up front
  it's a virtual assistant; transfers to a human any time the caller asks
- Emergency triage (gas smell, CO alarm, no heat with freezing temps or vulnerable occupants) with warm
  transfer or instant page to the on-call tech
- Booking into their FSM calendar or a synced calendar using their rules (zones, job types, slots)
- Missed-call text-back within seconds when a call drops
- Instant response to website form leads (text + call within 60 seconds)
- New-estimate follow-up automation (every quote gets a 5-touch, 21-day follow-up)
- Post-job review requests to Google
- Weekly report: calls answered, after-hours calls, bookings, emergencies, transfers, estimated revenue
- 1,000 AI voice minutes / month included (enough for most shops under ~15 trucks)

**Guarantee:** if, after 60 days, revenue from jobs the dispatcher booked (job count × their average ticket from
their own FSM) is less than 2× what they've paid us, we refund the setup fee and they can cancel.

**The anchor to use on calls:** a full-time CSR costs roughly $3,500-$4,500 a month loaded, covers 40 of the 168
hours in a week, takes vacations and quits. The dispatcher is $997 and covers all 168.

---

## Offer 3: BookedOut Complete (top)

$1,997/month (setup waived on a 6-month term). Everything in AI Dispatcher plus:
- A reactivation campaign every month: unsold estimates, fall/spring tune-up drives, maintenance-plan
  renewals, "system is 12+ years old" replacement campaigns
- Review engine and Google Business Profile posting
- 2,500 AI minutes / month, priority changes within 24 hours
- Quarterly numbers review with the owner

Pitch this at the 60-day review to clients who loved the sprint.

---

## Unit economics (per AI Dispatcher client)

| Item | Monthly cost |
|---|---|
| Voice AI minutes (~800 min at $0.10-$0.30/min all-in, depending on stack) | $80-$240 |
| Phone number + SMS (A2P 10DLC registered) | $15-$40 |
| CRM / automation sub-account (e.g. GoHighLevel unlimited plan spread across clients) | $0-$50 |
| **Total delivery cost** | **~$100-$330** |
| **Gross margin at $997** | **~67-90%** |

Setup takes 4-6 hours once you've built your template (see `delivery/`).

## Revenue model (planning assumptions, not a promise)

Assumptions to replace with your own numbers by week 3:
- Email live from day 15: 10 inboxes × 30 sends/day ≈ 6,000 sends/month → 3 booked sales calls per 1,000 sends
- Phone: 60 dials/day → ~10% reach an owner → ~10% of conversations book a call
- 70% of booked sales calls show; 25% of held calls buy (almost always the sprint first)
- 50% of sprints upgrade to the Dispatcher; ~1 Dispatcher cancellation by month 6

| Month | Sprints sold | Sprint cash | Dispatcher clients | Dispatcher MRR | **Cash collected** |
|---|---|---|---|---|---|
| 1 | 3 (founding, $997) | $2,991 | 0 | $0 | **$2,991** |
| 2 | 5 (2 founding + 3 × $1,500) | $6,494 | 2 | $1,994 | **$8,488** |
| 3 | 6 | $9,000 | 4 | $3,988 | **$12,988** |
| 4 | 6 | $9,000 | 7 | $6,979 | **$15,979** |
| 5 | 6 | $9,000 | 10 | $9,970 | **$18,970** |
| 6 | 6 | $9,000 | 12 | $11,964 | **$20,964** |

About **$80k collected in 6 months and ~$12k MRR**, solo, at modest conversion rates. Upgrades are counted with
setup fully credited (no setup cash), so direct Dispatcher sales are pure upside.

## Levers that make the money come faster

1. **Take payment on the call.** Stripe payment link in the chat while you're still talking. Every day between
   "yes" and "paid" loses deals.
2. **Phone first.** Email needs ~2 weeks of inbox warmup. Phones don't. Book your first calls in week 1.
3. **Founding scarcity is real:** "5 founding spots at $997, 2 are left." Only say it while it's true.
4. **Annual prepay** at day 60: one client paying $9,970 upfront beats eight months of waiting.
5. **Raise the sprint to $2,500** after 3 documented results. The guarantee makes the price easy to accept.
6. **Referrals:** HVAC owners know each other through supply houses and buying groups. Pay $500 (or one
   free Dispatcher month) per referred client who signs.
7. **Hire a setter** (commission per show) once you're booking more calls than you can run.

# 3. Launch plan: first dollar in 7-10 days, first $10k month in ~60

The constraint is time, so everything is ordered by what unblocks revenue soonest. Email inboxes need about
two weeks of warmup, so **you start them on day 1 and sell by phone while they warm.**

## Days 1-2: set up (about 8 hours total)

| Task | Why | Where |
|---|---|---|
| Buy your main domain + 3 lookalike sending domains | Never cold email from your main domain | `docs/04-tech-stack.md` |
| Create 2-3 inboxes per sending domain, set SPF/DKIM/DMARC, start warmup | 14 days to safe volume | Instantly / Smartlead |
| Publish the website (drag `website/` onto Netlify/Cloudflare Pages) | Prospects check you out; A2P registration needs a privacy page | `website/` |
| Build the demo AI dispatcher on a demo phone number | **Your #1 sales asset.** Prospects call it during the pitch | `delivery/ai-dispatcher-prompt.md` |
| Record a 3-minute Loom: you calling the demo line with a no-heat emergency | Sent after every call and to warm replies | |
| Stripe: payment links for $997 founding sprint, $1,500 sprint, $1,500 setup, $997/mo subscription | Collect on the call | Stripe dashboard |
| Calendar booking page (15 min "Missed-revenue review") | CTA everywhere | Cal.com / Calendly |
| Google Voice or a dialer number with local area code for cold calls | Manual dialing only | |

## Days 2-3: build the first list

1. Pick 3 metros from `docs/01-niche.md` with a cold front coming.
2. Scrape `HVAC contractor` + `heating contractor` + `air conditioning contractor` per metro on Google Maps
   (Outscraper or Apify). Aim for 1,500-2,500 companies.
3. Pull owner names/emails with Apollo or GetLeads (titles: Owner, President, CEO, General Manager).
4. Run the engine:
   ```bash
   bookedout import leads/*.csv
   bookedout daily
   bookedout audit-list --n 60
   ```

## Days 3-14: phone-first sprint (this is where the first clients come from)

**Daily schedule (prospect's local time):**

| Time | Activity | Target |
|---|---|---|
| 7:00-8:30am | Cold calls from the call sheet (owners are in the office before trucks roll) | 30 dials |
| 9:00-11:00 | Facebook groups + LinkedIn: comment, post, DM (`sales/dms.md`) | 20 touches |
| 11:00-3:00 | Sales calls, follow-ups, building sprint campaigns for clients | |
| 4:00-6:00pm | Cold calls round two (techs back, owner doing paperwork) | 30 dials |
| 6:00-8:00pm | After-hours audits: call 20 main lines, log results | 20 audits |
| 8:00pm | `bookedout audit-import`, `bookedout stats`, tomorrow's call sheet | |

Day 3 goal: first sales call booked. Day 7-10 goal: first founding sprint paid.

## Days 15-30: turn on email, keep the phone going

- Day 15: start campaigns at 15 sends/inbox/day; day 18: 25; day 21: 30-40.
- Upload the `out/instantly-*.csv` files to matching campaigns (copy in `sales/email-sequences.md`).
- Reply to every positive reply within 15 minutes during business hours. Speed is the whole pitch, so live it.
- Every reply that isn't "remove me" gets a phone call the same day.
- Run your first sprints (`delivery/estimate-recovery-sprint.md`). Results become your case study by day 30.

## Days 31-60: convert and compound

- Day 14 of each sprint: results call + Dispatcher upgrade pitch (sprint fee credited).
- Turn the first 2-3 results into one-page case studies and a 60-second video; add them to the website,
  email step 2, and your Facebook posts.
- Raise the sprint price to $1,500 (founding spots gone). After 3 documented wins, test $2,500.
- Add a 5th and 6th metro; rotate by weather.

## Scoreboard (track daily; `bookedout stats` does most of it)

| Metric | Daily target | Healthy rate |
|---|---|---|
| Dials | 60 | |
| Owner conversations | 6 | ~10% of dials |
| After-hours audits | 20 | Every unanswered line becomes your strongest email and call opener |
| Emails sent (from day 21) | 300 | |
| Positive replies | 2-4 | 0.5-1% of sends |
| Sales calls booked | 1-2 | |
| Show rate | | 70%+ (send a text reminder 2h before) |
| Close rate (held calls) | | 20-30% |

## Kill / fix rules (decide with data, not feelings)

| Symptom (after enough volume) | Fix |
|---|---|
| < 1 positive reply per 500 emails after 2,000 sends | Rewrite step 1 subject + first line; check inbox placement with a seed test |
| Bounce rate > 3% | Verify emails before upload; drop catch-all domains |
| Many conversations, few bookings | Shorter ask: "can I show you the demo line, 10 minutes?" Lead with the after-hours audit |
| Show rate < 60% | Confirmation text + call 2h before; book within 48h, not next week |
| Calls held, no closes | Do the live demo earlier in the call; lead with the sprint and its guarantee; take payment on the call |
| Sprints don't hit 5 appointments | Better reason to act now (price-hold, warranty upgrade), more phone follow-up on hot segment, bigger lists |

## Weekly review (Friday, 30 min)

1. `bookedout stats`: where does the funnel leak most?
2. Read 10 replies and 3 call recordings. What objection keeps coming up? Add the answer to `sales/objections.md`.
3. Which sequence has the best reply rate? Shift volume to it.
4. Pick the next 2 metros by weather.

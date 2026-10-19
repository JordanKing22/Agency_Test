# Bid Desk: operating manual (recurring)

The Bid Desk is three jobs done every week: **triage** what comes in, **chase** what went out, and **grow** the GC
list. The client's estimators do takeoffs and pricing. We do everything around them.

## Weekly rhythm

| Day | Work |
|---|---|
| Monday | Triage every ITB from the last 7 days → bid/no-bid shortlist to the chief estimator by 10am |
| Tue-Thu | Bid-day follow-ups; leveling-feedback and award-status calls; new GC outreach (5+ GCs/week) |
| Friday | Update the bid log and GC scorecard; send the weekly note |
| Monthly | Report + 30-minute review; refresh permit data and the GC target list; prequal renewals |

## 1. Triage: the bid/no-bid scorecard

Score every ITB 0-10. Default rule: **7+ bid, 4-6 the chief estimator decides, 0-3 decline politely** (declining keeps
the GC relationship; silence hurts it). Tune weights per client in month one.

| Factor | 2 points | 1 point | 0 points |
|---|---|---|---|
| Fit: trade and scope | Core scope | Partial or unusual scope | Not our work |
| Size | In the sweet spot | Within capacity, off sweet spot | Above bonding or too small to bother |
| GC history | GC has awarded us before | New GC, good reputation | GC shops numbers and never awards / slow pay |
| Project type & location | Our type, our area | One of the two | Neither |
| Timing | Fits the schedule and estimating capacity | Tight | Bid due in < 3 days or conflicts with a bigger bid |

Shortlist format (Monday email):
> **Bid:** {project} · {GC} · due {date} · ~{size} · score {9} · why: {awards us, healthcare, sweet spot}
> **Decide:** {project} · {GC} · score {5} · question: {large, new GC}
> **Decline:** {n} ITBs (list attached); I'll send polite declines unless you say otherwise.

Polite decline (sent on the client's behalf):
> Thanks for including {client} on {project}. We're not able to price this one; please keep us on your list for
> {trade} on {project types}.

## 2. Bid chasing: follow-up cadence

| When | Ask | Channel |
|---|---|---|
| Bid day +1 | "Confirming you received our {trade} number for {project}. Any scope questions or clarifications?" | Email |
| +7 days | "Any feedback on where we landed? Anything in our scope or qualifications you'd like adjusted?" | Phone, then email |
| +14 to +30 days | "Did {GC} get the project? Who's running buyout for {trade}?" | Phone |
| GC won the job | "We'd like to be part of buyout. Can {client owner} meet with the PM this week?" | Phone + email to PM |
| GC lost the job | "Thanks for the look. Who was the GC that got it?" → add that GC to outreach for buyout | Phone |
| We lost | "Thanks. Was it price, scope or something else?" (never ask for competitors' numbers) | Phone |

Bid log columns: project · GC · bid date · our number · score · follow-up dates · GC won project? · buyout contact ·
result (won / lost / no decision / project dead) · reason · notes.

## 3. Grow: new GCs every month

- Refresh permit data monthly; run `fullbacklog gap-audit --market {market} --company "{client}" --known client-gcs.txt`
  and work new names from the top 50.
- When a GC wins a project the client bid through another GC, pitch the client to the winner for buyout.
- Keep prequals current: insurance renewals, new EMR letters, updated financials (with approval).
- Quarterly: send each top GC a short project update (completed jobs, photos, references).

## 4. The GC scorecard (the retention engine)

Per GC, rolling 12 months: ITBs received · bids submitted · win rate · average days to award · slow-pay flag ·
notes. Every monthly review starts with it: "These 3 GCs award you 60% of your work; these 4 never have." That's the
insight clients can't get anywhere else, and it's why they stay.

## Escalation rules

- Anything about price or scope → the client's estimator, same day.
- A GC asks for a meeting → offer two times within the week; the owner or chief estimator attends.
- Prequal asks for financials → client approval first, every time.
- Bad experience with a GC (slow pay, backcharges) → record it and lower their score.

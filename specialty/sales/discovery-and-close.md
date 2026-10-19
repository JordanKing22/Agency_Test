# The sales call: discovery, the live Gap Audit, close (30 minutes)

**Goal: payment collected before you hang up.** The Gap Audit does the selling. Your job is to ask good questions
first, so the gaps in the audit mean something to them.

Before the call: run `fullbacklog gap-audit --market {market} --company "{company}" --n 40`, open the markdown, have
the Stripe links and onboarding form ready, and read `fullbacklog show <lead>`.

---

## 1. Frame (2 minutes)

> "Thanks for the time. Here's the plan: I'll ask a few questions about how you get invited to bid today, then I'll
> share the GC list for {market} and we'll see where the gaps are. If it makes sense, I'll show you how we'd close
> them. If not, you keep the list. Fair?"

## 2. Discovery (10 minutes)

**Volume and mix**
1. "Roughly how many bids does {company} put out in a month? How many estimators?"
2. "What's a typical package for you, dollar-wise? Your sweet spot?"
3. "What kind of work: TI, ground-up, healthcare, schools, multifamily?"

**Where bids come from**
4. "How many GCs invite you regularly? Who are your top three?"
5. "What share of your revenue comes from those top three?" *(Concentration risk is the pain.)*
6. "When did you last get on a new GC's list? How did that happen?"

**Hit rate and follow-up**
7. "Out of 10 bids, how many do you win? Does it change by GC?"
8. "After bid day, what happens? Does anyone call to find out where you landed or who won the job?"
9. "How often do you bid a job and never hear anything again?"

**Stakes**
10. "What does the backlog look like for Q2 and Q3 next year?"
11. "If you added 3 more GCs that award you work, what would that do for next year?"

**Do the math with their numbers** (or share the calculator on your website):
> "You said about {20} bids a month at about {12%}, average job around {$120k}. If new GC lists added even {4} bids a
> month you'd actually want, that's about {48} more bids a year, and at your hit rate roughly {6} more jobs, about
> {$690k}. And if chasing every bid moved your hit rate by just one point, that's another {2-3} jobs. Sound right?"

## 3. The live Gap Audit (8 minutes): the moment that sells it

Share your screen with the audit.

> "This is every commercial permit pulled in {market} in the last 90 days, ranked by the GC who pulled it. {N}
> permits, about {$value}. Go down the list with me. Does {GC 1} invite you to bid?"

Mark yes/no as they answer. Let them notice the pattern themselves. Then:
> "So of the top {15}, you're getting invitations from {4}. {GC 2} pulled {$27M} in permits this quarter and you've
> never priced a job for them. What would it take to get on their list?"

They'll usually say "someone needs to call them / do the prequal / we don't have time." That's the sale.

## 4. The recommendation (4 minutes)

Recommend one thing:

> "Here's what I'd do. Start with the Bid List Sprint. In 30 days we put together your prequal package and
> capabilities sheet, reach the estimators and precon managers at the GCs on this list you're missing, do the prequal
> paperwork, and track every invitation. If we don't get you on at least 10 new GC bid lists, you pay nothing. It's
> {$2,500} ({$1,500} while founding spots last), and we only take one {trade} sub in {market}, so it's yours if you
> want it."

If they asked a lot about follow-up and hit rate, add:
> "After the sprint, most clients keep us on as their Bid Desk: we triage every ITB, chase every bid after bid day,
> and keep adding GCs. That's $2,500 a month, and the onboarding fee is waived if you start within two weeks of the
> sprint report."

## 5. The close

> "Want to grab the {trade} spot for {market}?"

When they say yes:
> "Great. I'm sending the payment link now, then a short onboarding form with the document list: COI, W-9, EMR
> letter, bonding letter, project list. Let me know when the link comes through."

Stay on until payment clears. Book the kickoff before you hang up.

When they hesitate:
> "Totally fair. Usually it's one of three things: the money, whether it'll work for {trade}, or timing. Which one is it?"

Answer that one (`objections.md`), then ask again.

## 6. After the call

- Paid: `fullbacklog mark <lead> --status won`, welcome email (`follow-up.md`), start `delivery/bid-list-sprint.md`.
- Not yet: `--status proposal`, send the audit and recap within the hour, book the next call before you hang up.
- No: `--status lost --note "<why>"`, still send them the audit. Ask who else they'd recommend (other trades on the
  same jobs are perfect referrals).

---

## 10-minute version (when a cold call turns into a conversation)

1. "How many GCs invite you to bid regularly? Who follows up after bid day?"
2. "Let me read you the top 5 GCs in {market} by permits this quarter. Which invite you?"
3. "We get you on at least 10 new GC bid lists in 30 days or you don't pay. Want the {trade} spot?"
4. Send the payment link, or book the full call within 48 hours.

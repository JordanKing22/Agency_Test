# Cold call scripts

**Goal of a cold call: book a 15-minute "Bid List Gap review" in the next 48 hours.** Don't sell the sprint on a
cold call. Offer the audit.

Who to ask for: the owner/president, or the chief estimator (often the real decision-maker on where the company
bids). In bigger shops, a VP of preconstruction or business development.

Rules:
- Call 6:30-7:30am and 3:30-5:00pm their time. Avoid bid-day afternoons (often Tuesday-Thursday).
- Know the top 5 GCs in their market by name before you dial (`fullbacklog markets`). Saying them out loud is
  your credibility.
- Every opener ends in a question. Then stop talking.
- Log every dial: `fullbacklog call <lead_id> --outcome ...`. The call sheet says which opener to use.

---

## The permission opener (every time)

> "Hey {first name}, it's {your name}. I know you're about to head out, so I'll be quick. Can I tell you why I called,
> and you tell me if it's worth 30 seconds?"

## Opener A: permit pulse (when the call sheet has market data)

> "I pull the public permit data for {market}. Over the last 90 days, {top GC 1}, {top GC 2} and {top GC 3} pulled
> more commercial permits than anyone else. Quick question: are you getting invitations to bid from all three?"

They'll say something like "we bid {GC 2} sometimes." Then:
> "That's what I hear from most {trade} subs. I've got the full top-25 list for {market}. Want me to walk you through
> it? Takes 15 minutes, and you'll see exactly which GCs building right now don't have you on their list."

## Opener B: after bid day (default)

> "I work with commercial {trade} subs on the part of bidding nobody has time for. When you submit a bid, who follows
> up after bid day, to find out if the GC won the job, where your number landed, and who's running buyout?"

Most will laugh or say "nobody." Then:
> "That's normal. We run that follow-up, and we get you on more GC bid lists so there's more worth bidding. The first
> step is a free audit of the GCs building in {market} that you're not bidding for. Got 15 minutes Thursday?"

## Opener C: certified sub

> "I saw {company} is {WBE/DBE/MBE}-certified. GCs bidding public and institutional work around {market} have
> participation goals, and a lot of them are short on certified {trade} subs. How many GCs invite you to bid today
> because of the certification?"

## Opener D: hiring

> "Saw you're hiring. Usually that means this year's full. What does the backlog look like for next spring once
> you've added the people?"

Then: "We help subs fill that: more GC bid lists, follow-up on every bid. Want to see which GCs building in {market}
aren't inviting you yet?"

---

## Asking for the meeting

> "Here's what I'd suggest. 15 minutes {tomorrow at 7:00 or Thursday at 3:45}. I'll share my screen with the top GCs
> in {market} by permits, you tell me which ones invite you, and we'll see how big the gap is. If there's no gap, I'll
> tell you. Which works better?"

Two specific times within 48 hours. Send the invite while they're on the phone.

## Quick "no" responses (full list in `objections.md`)

| They say | You say |
|---|---|
| "We have plenty of work." | "Great problem to have. How does next spring look? Most subs I talk to are full through Q1 and thin after that." |
| "We already get invited to everything." | "Then the audit will take you 5 minutes and confirm it. If you're on all of the top 10 lists, I'll leave you alone." |
| "Send me something." | "Sure. I'll send the top-25 GC list for {market}. Can I call Thursday at 7 to go through it with you? It's more useful with your notes on it." |
| "We only bid our regular GCs." | "Makes sense, they award you. What happens to your volume if one of them has a slow year?" |
| "We don't use agencies." | "Fair. We're not marketing: no ads, no leads. We get you on GC bid lists and chase your bids. That's it." |

## Gatekeeper

> "Hey, it's {your name}. Is {first name} around? ... It's about which GCs are inviting {company} to bid in {market}.
> Is {first name} the right person for that, or is that your chief estimator?"

If blocked: "When's the best time to catch them, early morning?" Log `gatekeeper` and call back then.

## Voicemail (20 seconds, 1st and 3rd attempt only)

> "Hey {first name}, {your name}. I pulled the commercial permits for {market}. {top GC 1} and {top GC 2} have pulled
> more than anyone this quarter, and I wanted to see if you're on their bid lists. My number is {number}, again
> {number}. I'll send you a quick email too."

## After every conversation

- Booked: `fullbacklog call <id> --outcome booked --note "Thu 7:00, bids ~20/mo, mostly 4 GCs"`, then run
  `fullbacklog gap-audit --market {market} --company "{company}"` so it's ready.
- Wants the list: send the audit with your follow-up (`follow-up.md`) and ask for 15 minutes to go through it.
- Hard no: `--outcome not_interested`. Hostile or "don't call": `--outcome do_not_call`.

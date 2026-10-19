# Estimate Recovery Sprint: 14-day playbook

**Promise:** at least 5 booked replacement appointments from the client's unsold quotes in 14 days, or a
full refund. Read `docs/05-compliance.md` before you send anything to a client's customers.

## Day 0: kickoff (30-minute call)

Agenda:
1. Walk the owner or office manager through the export (screen share). What to pull:
   - **ServiceTitan:** Reports → estimates that are open/dismissed, last 24 months, with customer name, phone,
     email, address, estimate date, total, summary, technician/sold-by
   - **Housecall Pro:** Estimates list filtered to unapproved/expired, export CSV
   - **Jobber:** Quotes filtered to not converted, export CSV
   - **Anything else:** a spreadsheet with the same columns is fine
2. Also ask for: customers who bought since (to exclude), the do-not-contact list, and how texting consent was
   collected.
3. Agree the **reason to act now** (pick one, the owner must be able to honor it):
   - Price-hold: "We'll honor your original quote price through {date}"
   - Upgrade: free 10-year labor warranty or free smart thermostat with installs booked by {date}
   - Priority: "{n} install slots left before {holiday}"
   - Financing: special financing promo if the manufacturer/lender is running one
4. Booking rules: who runs the appointments, which calendar, what slots, how the comfort advisor wants notes.
5. Who calls back hot replies: our caller or their CSR (agree response time: 15 minutes in business hours).
6. Daily update channel: text thread with the owner.

## Day 1: build

- Clean the list: dedupe by phone/email, remove customers who bought, opted out, are on the DNC list without
  consent, or have bad numbers. Note anyone who bought elsewhere if the client knows.
- Segment: **hot** 0-90 days · **warm** 3-12 months · **cold** 12-24 months.
- Mark SMS-eligible contacts (documented consent only).
- Load into the client's sub-account; set up the campaign, opt-out handling, and the booking calendar.
- If texting is in scope and the client's number isn't A2P-registered, start registration now and run email +
  calls first.

## The campaign

| Day | Hot (0-90 days) | Warm + cold |
|---|---|---|
| 2 | Email 1 + SMS 1 (consented) | Email 1 |
| 3-4 | Calls to every hot contact (2 attempts) | |
| 5 | | Email 2 + SMS 1 (consented) |
| 6-9 | Calls to non-responders; callbacks on every reply within 15 min | Calls to every responder |
| 10 | Email 3 + SMS 2 (consented) | Email 3 |
| 11-13 | Final calls to warm leads who opened or clicked | |
| 14 | Results report + upgrade call | |

Send texts 9am-8pm local. Start emails on Tuesday-Thursday mornings, then test other slots once you have
data.

## Templates (client's voice; replace braces)

**Email 1: "Still thinking about it?"**
> Subject: Your {system type} quote from {company}
>
> Hi {first name},
>
> {Advisor name} here from {company}. Back in {month} we put together a quote for a new {system type} at your home on
> {street}. I wanted to check in: is that still something you're thinking about?
>
> {Reason to act now, one sentence.}
>
> If you'd like to go over options again, or just ask questions, reply to this email or book a time here:
> {booking link}. No pressure either way.
>
> {Advisor name}
> {company} · {phone}
> {address} · Unsubscribe

**SMS 1 (consented contacts only)**
> Hi {first name}, it's {advisor name} with {company}. You got a quote from us for a new {system type} in {month}.
> Is that still on your list? {Short reason to act now}. Reply YES and I'll call you. Reply STOP to opt out.

**Email 2: "What changed"** (day 5)
> Subject: A few options on your {system type}
>
> Hi {first name},
>
> A lot of homeowners we quote hold off for one of three reasons: the price, not being sure the old system is really
> done, or just bad timing. All three are fair.
>
> If it's price, we have financing options and can look at a different equipment tier. If you're not sure about the
> old system, we can do a quick check. And if it's timing, {reason to act now}.
>
> Want me to have {advisor name} give you a call? Just reply with a good time.
>
> {Advisor name}

**Email 3: "Closing out your quote"** (day 10)
> Subject: Closing out your quote
>
> Hi {first name},
>
> I'm closing out open quotes this week. If you'd still like options for your {system type}, reply "yes" or book
> here: {booking link}, and I'll make sure you get {reason to act now} before {date}.
>
> If you've already taken care of it, no problem at all, and thanks for considering us.
>
> {Advisor name}

**SMS 2 (consented contacts only)** (day 10)
> {First name}, {advisor name} at {company} again. Last call on {reason to act now} for your {system type} quote,
> good through {date}. Want me to hold a time for you? Reply STOP to opt out.

## Caller script (manual calls, our caller or the client's CSR)

> "Hi, is this {first name}? This is {name} calling from {company}. You had {advisor name} out in {month} to quote a
> new {system type}. I'm just following up. Is that still something you're considering?"

- **Yes / maybe** → "Great. {Reason to act now}. {Advisor name} can come back out and go over options. I have
  {two slots}. Which works?" Book it with notes: original quote, what held them back, what they want.
- **Price was the issue** → "Totally understand. There are financing options now and a couple of equipment tiers
  we can look at. Would it help to have {advisor} walk you through those?" → book.
- **Went with someone else** → "Thanks for letting me know. How's it working out?" Note it and mark as bought
  elsewhere.
- **Not now** → "When would be a better time to check back?" Note the date.
- **Don't call** → "Understood, I'll take you off our list." Suppress immediately.

Voicemail (once): "Hi {first name}, {name} from {company}, following up on the {system type} quote from {month}.
{Reason to act now}. Call or text {number} if you'd like to go over it. Thanks!"

## Booked appointment note (what the advisor sees)

```
Recovered quote | {original date} | ${original total} | {equipment}
Why they waited: {price / timing / unsure / spouse}
What they want now: {e.g. financing options, 2-stage vs single-stage}
Reason to act: {offer} (expires {date})
```

## Daily owner update (text)

> Day {n}: {sent} emails, {texts} texts, {calls} calls. {replies} replies, {booked} booked so far ({names/days}).
> Tomorrow: {plan}.

## Day 14: results call → upgrade

Report: list size, contacts reached, replies, appointments booked (with names and dates), appointments run,
replacements sold so far, revenue sold, pipeline still open. Then:

> "So from quotes you'd written off, you've got {booked} appointments and {$sold} sold so far. The reason those quotes
> went cold in the first place is that nobody had time to follow up, and the same thing is happening with calls after
> hours. The dispatcher fixes both: it answers every call 24/7 and follows up every new quote automatically. Your
> sprint fee gets credited to the setup, so it's just $997 a month. Want me to get it started?"

If the guarantee wasn't met: refund promptly and without argument, ask what they'd have needed to see, and offer to
keep going free for 7 more days if the list still has life in it. Your reputation in a tight-knit trade is worth more
than one fee.

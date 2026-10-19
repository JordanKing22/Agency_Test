# The sales call: discovery, live demo, close (30 minutes)

**Goal: payment collected before you hang up.** Most deals that "think about it" die. Structure the call so
that by minute 25 the owner has done the math themselves and heard the dispatcher work.

Have open before the call: the ROI calculator on your website, the demo line, Stripe payment links, the
onboarding form link, and `bookedout show <lead>` for what you already know.

---

## 1. Frame (2 minutes)

> "Thanks for making time. Here's what I was thinking: I'll ask a few questions about how calls and quotes work
> at {company} today, then I'll show you the dispatcher and what a recovery sprint would look like for you. If
> it's not a fit I'll tell you, and if it is we can talk about next steps. Sound good?"

## 2. Discovery (10 minutes): find the leak and get them to put a number on it

Ask, then shut up. Write their numbers down. You'll use them in the close.

**Calls**
1. "Walk me through what happens when someone calls at 8pm on a weeknight."
2. "And at 10am on the first cold Monday, when every line is ringing?"
3. "Roughly how many calls a week come in after hours, or ring out during the day?" *(If they don't know: "Can
   you pull up last week's missed calls in your phone system? Most shops are surprised.")*
4. "Of the people who call about no heat, how many book if someone picks up?"
5. "What's a typical repair ticket? And a replacement?"

**Quotes**
6. "When a tech or comfort advisor quotes a replacement and the homeowner doesn't sign, what happens next?"
7. "How many quotes do you think went out last year that never closed? What's the average quote?"
8. "What software are they in? ServiceTitan, Housecall, Jobber?"

**Stakes**
9. "If you booked 10 more replacements this winter, what would that mean for the business?"
10. "What have you tried before to fix this? Answering service, more CSRs, an agency?"

**Do the math out loud with their numbers** (share the website calculator):
> "So you said about {8} missed calls a week, about {1 in 3} would book, at a {$350} repair. That's {$48,000} a year
> before a single replacement. And {300} unsold quotes at {$11,000}: if we bring back even {3%}, that's
> {$99,000}. Does that sound about right to you?"

Let them agree with their own numbers. Don't argue if they shrink them; even half is a big number.

## 3. The live demo (5 minutes): the moment that sells it

> "Rather than me describing it, call it. Put it on speaker, pretend you're a homeowner whose furnace quit
> tonight, and try to trip it up."

Text them the demo number. Stay quiet while they call. After:
> "What did you think? ... What would your customers think?"

If something went wrong, own it: "Good catch, that's exactly what we tune in the first week. We test 20 scenarios
before it ever answers one of your calls."

## 4. The recommendation (5 minutes)

Recommend one thing. Don't present a menu.

**For most first calls, the sprint:**
> "Here's what I'd do if I were you. Start with the Estimate Recovery Sprint. 14 days, we go back through those
> {300} quotes and book appointments onto your calendar. It's {$1,500} ({$997} if a founding spot is open), and if
> we don't book at least 5 appointments you pay nothing. If you like what you see, the whole fee gets credited
> toward the dispatcher setup. Fair?"

**When calls are the bigger pain and they're bought in after the demo:**
> "Honestly, the quotes can wait. Your bigger leak is the phones, and you're about to hit the busiest weeks of the
> year. Let's get the dispatcher live on your after-hours and overflow line. Setup is $1,500, it's $997 a month,
> and if it hasn't booked at least twice what you've paid us after 60 days, you get the setup fee back. We can be
> live in 5 business days."

## 5. The close

Ask, then stop talking:
> "Want to get started?"

When they say yes:
> "Great. I'm texting you the payment link now, and right after that a 10-minute onboarding form. Once that's
> done I'll book our kickoff for {tomorrow}. Go ahead and open it. Let me know when it comes through."

Stay on the line until payment goes through. Then book the kickoff before you hang up.

When they hesitate, find the real objection (`objections.md`):
> "Totally fair to think it over. Usually when someone says that, it's one of three things: the money, whether
> it'll actually work, or the timing. Which one is it for you?"

## 6. After the call

- Paid: `bookedout mark <lead> --status won`, send the welcome email (`follow-up.md`), start `delivery/onboarding.md`.
- Not yet: `--status proposal`, send the recap within 1 hour, book the next call before you hang up.
- No: `--status lost --note "<why>"`. Ask: "Who else do you know in the trade who's drowning in calls this
  time of year?"

---

## 10-minute version (when a cold call turns into a conversation)

1. "What happens to your calls after 5?" / "How many quotes didn't close last year?"
2. "Want to hear it? Call this number on speaker." (demo)
3. "We do a 14-day sprint on your old quotes. 5 booked appointments or you don't pay. Want to try it?"
4. Send the payment link. If they're not ready: book the full call within 48 hours.

# Follow-up templates

Speed wins. Every positive reply gets an answer within 15 minutes during business hours, and a phone call the
same day.

## Replies to cold email

**Positive ("tell me more", "how does it work", "what does it cost")**
> {First name}, easiest way to see it is to call the demo line: {demo line}. Pretend your furnace quit.
>
> Then let's do 15 minutes so I can show you what it'd look like for {company}. Does tomorrow at 7:30am or 4:30pm
> work? Or grab any time here: {calendar link}

**Price question before a call**
> Fair question. The recovery sprint is a flat $1,500 (founding rate $997 while spots last) and it's guaranteed:
> at least 5 booked appointments or you pay nothing. The AI dispatcher is $997/month. 15 minutes is enough to see
> whether either makes sense for {company}. {Two times}?

**"Not now" / "maybe later"**
> No problem. When would be a better time to circle back, after the first cold snap or in the spring?
*(Log it: `bookedout call <id> --outcome callback --note "..."`.)*

**"Remove me" / "not interested"**
> Understood, I won't reach out again. Thanks for letting me know.
*(Then `bookedout mark <email> --status do_not_contact`.)*

## Booked a sales call

**Confirmation (send immediately)**
> Subject: {Day} at {time}: {company} + {agency}
>
> {First name}, confirmed for {day} at {time} ({their time zone}). I'll call you at {phone}.
>
> Before we talk, try the demo dispatcher: {demo line}. If you can, have a rough idea of how many replacement
> quotes didn't close in the last year and what a typical one is worth.
>
> {Your name}

**Reminder text (2 hours before)**
> Hi {first name}, it's {your name}. Still good for {time} today? I'll call you at this number.

**No-show (5 minutes after the start)**
> Text: Hey {first name}, tried you at {time}. Looks like the day got away from you. Want to grab {two times}
> instead?
> Then call once more at +15 minutes. If no answer, email the same thing that afternoon.

## After the sales call

**Recap for "need to think about it" (within 1 hour)**
> Subject: {company}: the numbers we talked about
>
> {First name}, thanks for the time today. Quick recap in your numbers:
> - ~{8} missed or after-hours calls a week, ~{1 in 3} would book, ~{$350} per repair → about {$48k}/year
> - ~{300} unsold quotes at ~{$11k} → even {3%} recovered is about {$99k}
>
> What I'd recommend: the 14-day Estimate Recovery Sprint. {Price}, at least 5 booked appointments or you pay
> nothing, and the full fee is credited toward the dispatcher if you want it after.
>
> Here's the link to start: {Stripe link}. Once that's done, I'll send the 10-minute onboarding form and we can
> kick off {day}.
>
> We're scheduled to talk again {day/time}.
>
> {Your name}

**Proposal follow-up cadence:** day 1 recap → day 2 text ("any questions I can answer?") → day 4 call → day 7
email with one new piece of proof (a call recording or result) → day 14 breakup ("should I close this out?").

## Won

**Welcome email (right after payment)**
> Subject: Welcome aboard, next steps for {company}
>
> {First name}, welcome! Here's what happens next:
> 1. Onboarding form (10 minutes): {form link}
> 2. Kickoff call: {day/time}, 30 minutes. We'll walk through the estimate export together.
> 3. You'll get a text update from me every day of the sprint.
>
> Anything urgent, text me at {your cell}.

## Referrals and testimonials

**Asking for a review (after a good result)**
> {First name}, glad the sprint booked {n} appointments. Would you be up for 2 sentences I can share with other
> owners? Something like what you were skeptical about and what happened. A 30-second phone video is even better.

**Asking for referrals (after the first win)**
> Who else do you know who runs a shop and is drowning in calls this time of year? If they sign up, we'll send you
> $500, or give you a free month if you're on the dispatcher.

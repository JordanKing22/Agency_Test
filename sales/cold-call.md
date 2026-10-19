# Cold call scripts

**Goal of a cold call: book a 15-minute "missed-revenue review" in the next 48 hours.** Don't sell the
sprint on a cold call. Sell the next meeting.

Rules that matter more than the words:
- Call 7:00-8:30am and 4:00-6:00pm their time. Owners are in the office then.
- Stand up, smile, talk slower than feels natural. HVAC owners hate slick.
- Every opener ends in a question. Then stop talking.
- Ask for the meeting twice before you accept "no".
- Log every dial: `bookedout call <lead_id> --outcome ...`. The call sheet tells you which opener to use.

---

## The permission opener (use it every time)

> "Hey {first name}, it's {your name}. I'll be quick, I know you're probably about to head out.
> Can I tell you why I called, and you tell me if it's worth 30 seconds?"

Almost everyone says "go ahead." Then pick the opener from the call sheet.

## Opener A: after-hours audit (use when the call sheet says so)

> "I called your main line {Tuesday around 7:40} at night and it went to voicemail. Not a knock, most shops your
> size do the same. But a homeowner with no heat at night doesn't leave a voicemail, they call the next name on
> Google.
>
> We set up AI dispatchers for HVAC companies. It answers every call 24/7, sends real emergencies to your
> on-call tech, and books the rest right into your schedule. Sounds like a real CSR.
>
> **What happens to your calls after 5 right now?**"

Then: listen, and ask "How many of those do you think you miss in a week when it gets cold?"

## Opener B: unsold estimates (default)

> "Every HVAC owner I talk to has a pile of replacement quotes that never closed, usually a few hundred sitting
> in ServiceTitan or Housecall. We run a 14-day campaign that goes back through those and puts appointments
> on your calendar. If we don't book at least five, you don't pay.
>
> **Roughly how many quotes do you think you sent last year that didn't close?**"

Then: "And what happens to a quote today if they don't sign on the spot?"

## Opener C: cold snap / heat wave

> "Looks like {city} is dropping to {18} degrees {Thursday night}. That's usually the night your phones go nuts
> and the on-call tech can't get to all of them. We give HVAC shops an AI dispatcher that picks up every call,
> triages the real no-heats, and books the rest into your first open slots. We can have it on your overflow line
> before the next front.
>
> **When it gets slammed like that, who's answering the phones?**"

## Opener D: paid clicks

> "I was on your site and saw you're running Google Ads, but there's no way to book or chat after hours. So
> every click you pay for at 8pm has one option: call and hope someone picks up. We plug an AI dispatcher into
> your existing number so those calls turn into booked jobs.
>
> **Do you know what you're paying per call from Google right now?**"

---

## Asking for the meeting

> "Here's what I'd suggest. Give me 15 minutes {tomorrow at 7:30 or Thursday at 4:30}. I'll show you exactly
> where calls and quotes are leaking, and you can call our demo dispatcher yourself and try to trip it up. If
> it's not for you, no hard feelings. Which works better?"

Always offer two specific times within 48 hours. Then send the calendar invite while you're still on the phone:
"I just sent it to {email}. Can you see it?"

## When they want to talk now

Great. Run the short version of `discovery-and-close.md`: 3 questions, have them call the demo line on
speaker, offer the sprint, send the payment link.

## The quick "no" responses (full list in `objections.md`)

| They say | You say |
|---|---|
| "Not interested." | "Totally fair. Is it the AI phone piece or the old-quotes piece that's not a fit? ... Got it. Just so I don't bug you again: who answers after 5 right now?" |
| "Send me an email." | "Happy to. So I send something useful: is the bigger leak missed calls or quotes that don't close? ... I'll send the demo number. Can I call Thursday at 7:30 to see what you thought?" |
| "We already have an answering service." | "Makes sense. Does it book the job into your schedule, or take a message someone calls back in the morning? ... That callback gap is exactly where people book someone else." |
| "I answer my own phone." | "Respect. When you're in an attic at 2pm on a cold Monday, who picks up?" |
| "We're too busy." | "That's actually when this pays off the most. Busy is when calls get missed. 15 minutes Thursday?" |

## Gatekeeper (office manager / CSR)

> "Hey, it's {your name}. Is {owner first name} around?"

If asked what it's about:
> "It's about calls going to voicemail after hours. I called the main line the other night. Is {owner} the right
> person for that, or is that you?"

Office managers often own the phones. If it's them, pitch them. If you're blocked, ask: "What's the best time to
catch {owner} in the office? Early morning?" Log `gatekeeper` and call back then.

## Voicemail (20 seconds, leave one on the 1st and 3rd attempt only)

> "Hey {first name}, {your name}. I called your main line {last night} and it went to voicemail. I've got an idea
> on how to catch those calls without hiring anyone. My number is {number}, again {number}. I'll also shoot you
> a quick email."

## After every conversation

- Booked: `bookedout call <id> --outcome booked --note "Thu 7:30, ~300 unsold quotes, uses ServiceTitan"`, then
  send the confirmation (template in `follow-up.md`).
- Interested but no time: `--outcome callback` and put the callback in your calendar.
- Hard no: `--outcome not_interested`. Hostile or "don't call": `--outcome do_not_call` (never contacted again).

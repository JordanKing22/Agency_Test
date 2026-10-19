# Cold email sequences

_Generated from `engine/bookedout/sequences/*.toml` by `bookedout sequences-md`. Edit the TOML files, not this page._

Paste these into Instantly or Smartlead (one campaign per sequence). Every `{{variable}}` is a column in the CSVs that `bookedout export` writes, so the tool fills them per lead. Follow-ups have no subject so they thread under step 1.

## `after-hours`

Lead's main line went to voicemail / rang out when we called after hours. Strongest hook we have.

**Used when:** audit_result is voicemail, no_answer or ivr

### Step 1: day 0

**Subject:** {{company}} after hours

```text
Hi {{greeting_name}},

I called {{company}} {{audit_when}} and {{audit_phrase}}.

Not a knock. Most shops your size do the same. But a homeowner with no heat at 9pm rarely leaves a voicemail. They call the next company on Google.

We set up an AI dispatcher for HVAC companies. It answers every call 24/7, sends the true emergencies to your on-call tech, and books everything else straight into your schedule.

You can call the demo line and try it yourself: {{demo_line}}

Worth 15 minutes before the first real cold snap?

{{sender_first_name}}
```

### Step 2: day 3

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, quick math on the after-hours calls.

Say {{company}} misses 5 calls a week after 5pm, and 1 in 4 would have booked a $350 repair. That's about $22,000 a year going to competitors, before you count a single replacement.

The AI dispatcher costs a fraction of that, and it has to pay for itself in 60 days or you get your setup fee back.

Want me to send a 2-minute video of it handling a no-heat call?

{{sender_first_name}}
```

### Step 3: day 7

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, different idea.

Most HVAC shops have a few hundred replacement quotes from the last year that never closed. Those homeowners already told you they need a system.

We run a 14-day campaign that works back through those quotes and books appointments on your calendar. If we don't book at least 5, you don't pay.

Is that worth a look for {{company}}?

{{sender_first_name}}
```

### Step 4: day 12

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, I'll close the loop here.

If after-hours calls aren't a priority right now, no problem. If they become one when the first cold week hits, the demo line stays open: {{demo_line}}

Or grab 15 minutes here: {{calendar_link}}

{{sender_first_name}}
```

## `cold-snap`

NWS forecast shows a hard freeze in the lead's city this week. Send fast; the window is days, not weeks.

**Used when:** forecast_low_f <= targeting.cold_threshold_f

### Step 1: day 0

**Subject:** {{city}}, {{forecast_low}}°

```text
Hi {{greeting_name}},

Looks like {{city}} drops to {{forecast_low}}°F {{forecast_low_when}}. That's usually the night the phones light up and your on-call tech can't get to all of them.

We give HVAC shops an AI dispatcher that picks up every call, 2am included. It sorts real no-heat emergencies from "can you come Tuesday", sends the emergencies to your on-call tech, and books the rest into your first open slots.

We can have it live on your overflow line within 72 hours. Want to try the demo line first? {{demo_line}}

{{sender_first_name}}
```

### Step 2: day 2

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, the obvious question is whether homeowners hate talking to AI.

Call {{demo_line}} and pretend your furnace just quit. It tells callers up front that it's a virtual assistant, hands off to a person whenever they ask, and never quotes a price you haven't approved.

If it would embarrass {{company}}, you'll know in 60 seconds.

{{sender_first_name}}
```

### Step 3: day 5

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, different idea for the slow days between cold fronts.

Most HVAC shops have a few hundred replacement quotes from the last year that never closed. We run a 14-day campaign that works back through them and books appointments on your calendar. If we don't book at least 5, you don't pay.

Worth a look for {{company}}?

{{sender_first_name}}
```

### Step 4: day 10

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, I'll leave it here.

If the next cold front buries your phones, the demo line is still open: {{demo_line}}

Or grab 15 minutes here: {{calendar_link}}

{{sender_first_name}}
```

## `estimate-recovery`

Default sequence. Leads with the low-risk front-end offer: book 5 appointments from old quotes or don't pay.

**Used when:** no stronger signal

### Step 1: day 0

**Subject:** {{company}}'s unsold quotes

```text
Hi {{greeting_name}},

{{personalization}}

Quick question: how many replacement quotes did {{company}} send in the last 12 months that never closed?

For most shops it's a few hundred. Even 100 quotes at $10k is $1M of work that homeowners already told you they need.

We run a 14-day campaign that works back through those quotes and books appointments on your calendar. If we don't book at least 5, you don't pay.

Worth a 15-minute call?

{{sender_first_name}}
```

### Step 2: day 3

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, here's how the 14 days work:

1. You export unsold estimates from ServiceTitan, Housecall Pro or Jobber. It takes 5 minutes and we'll walk you through it.
2. We build the offer with you and run the email, text (to customers who opted in) and phone follow-up.
3. Booked appointments land on your calendar with notes. Your team shows up and sells.

Flat fee, at least 5 booked appointments or you pay nothing. Open to it?

{{sender_first_name}}
```

### Step 3: day 7

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, one more idea, then I'll leave you alone.

When {{company}} misses a call after hours, where does it go? For most shops it's voicemail, and most homeowners won't leave one.

We set up an AI dispatcher that answers 24/7 and books jobs into your schedule. Call it yourself and see what you think: {{demo_line}}

{{sender_first_name}}
```

### Step 4: day 12

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, I'll close the loop here.

If old quotes or after-hours calls become a priority this winter, I'm easy to find. Grab 15 minutes here: {{calendar_link}}

{{sender_first_name}}
```

## `heat-wave`

NWS forecast shows extreme heat in the lead's city this week. The summer twin of cold-snap.

**Used when:** forecast_high_f >= targeting.hot_threshold_f

### Step 1: day 0

**Subject:** {{city}}, {{forecast_high}}°

```text
Hi {{greeting_name}},

Looks like {{city}} hits {{forecast_high}}°F {{forecast_high_when}}. When the AC calls stack up, the ones that go to voicemail usually book with whoever answers first.

We give HVAC shops an AI dispatcher that answers every call 24/7, sends the no-cool emergencies to your on-call tech, and books the rest straight into your schedule.

Live on your overflow line within 72 hours. Try the demo line yourself: {{demo_line}}

{{sender_first_name}}
```

### Step 2: day 2

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, the obvious question is whether homeowners hate talking to AI.

Call {{demo_line}} and pretend your AC just died. It tells callers up front that it's a virtual assistant, hands off to a person whenever they ask, and never quotes a price you haven't approved.

If it would embarrass {{company}}, you'll know in 60 seconds.

{{sender_first_name}}
```

### Step 3: day 5

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, different idea.

Most HVAC shops have a few hundred replacement quotes from the last year that never closed. We run a 14-day campaign that works back through them and books appointments on your calendar. If we don't book at least 5, you don't pay.

Worth a look for {{company}}?

{{sender_first_name}}
```

### Step 4: day 10

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, I'll leave it here.

If the next heat wave buries your phones, the demo line is still open: {{demo_line}}

Or grab 15 minutes here: {{calendar_link}}

{{sender_first_name}}
```

## `paid-clicks`

Website runs Google Ads but has no online booking and no chat: they pay for clicks that can only become calls.

**Used when:** runs_google_ads and no booking_vendor and no chat_vendor

### Step 1: day 0

**Subject:** {{company}}'s Google Ads after 5pm

```text
Hi {{greeting_name}},

Noticed {{company}} runs Google Ads, but {{domain}} doesn't have online booking or chat. So after 5pm, every click you pay for has one option: call and hope someone picks up.

We plug an AI dispatcher into your existing number. It answers 24/7, sends emergencies to your on-call tech, and books jobs into your schedule, so the clicks you pay for at 8pm turn into jobs instead of voicemails.

Want to hear it? Call the demo line: {{demo_line}}

{{sender_first_name}}
```

### Step 2: day 3

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, one more thought on the ads.

Whatever you pay Google per call, a call that hits voicemail costs exactly the same and returns nothing. Fixing that is usually the cheapest way to lower your cost per booked job, with no change to your ad budget.

The dispatcher has to pay for itself in 60 days or you get your setup fee back. Open to a 15-minute look?

{{sender_first_name}}
```

### Step 3: day 7

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, different idea.

Most HVAC shops have a few hundred replacement quotes from the last year that never closed. We run a 14-day campaign that works back through them and books appointments on your calendar. If we don't book at least 5, you don't pay.

Worth a look for {{company}}?

{{sender_first_name}}
```

### Step 4: day 12

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, I'll close the loop here.

If you ever want to see what happens to your after-hours ad clicks, the demo line stays open: {{demo_line}}

Or grab 15 minutes here: {{calendar_link}}

{{sender_first_name}}
```

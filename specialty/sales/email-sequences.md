# Cold email sequences

_Generated from `engine/fullbacklog/sequences/*.toml` by `fullbacklog sequences-md`. Edit the TOML files, not this page._

Paste these into Instantly or Smartlead (one campaign per sequence). Every `{{variable}}` is a column in the CSVs that `fullbacklog export` writes, so the tool fills them per lead. Follow-ups have no subject so they thread under step 1.

## `bid-chase`

Default. Opens on the follow-up gap after bid day, then offers the guaranteed bid-list sprint.

**Used when:** no stronger signal

### Step 1: day 0

**Subject:** after bid day

```text
Hi {{greeting_name}},

{{personalization}}

Quick question: when {{company}} submits a bid, who follows up after bid day?

For most subs the honest answer is nobody. The estimator is already on the next takeoff, so you never hear whether the GC won the job, where your number landed, or who's running buyout.

We run that for commercial {{trade}} subs, and we get you on new GC bid lists so there's more worth bidding. Start with a 30-day sprint: at least 10 new GC bid lists, or you don't pay.

Worth a 15-minute call?

{{sender_first_name}}
```

### Step 2: day 3

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, here's how the 30-day sprint works:

1. We build a capabilities sheet and prequal package from what you already have (COI, EMR letter, bonding letter, project list).
2. We pick the GCs actually building in your area from public permit data and reach their estimators and precon managers as your business development rep.
3. We fill out the prequal forms and track who adds you and who sends invitations.

At least 10 new GC bid lists or you pay nothing. We only take one {{trade}} sub per market.

Open to it?

{{sender_first_name}}
```

### Step 3: day 7

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, one more thought.

Winter is when a lot of GCs price spring work. The subs they invite are the ones already sitting in their BuildingConnected or PlanHub lists, which is why the same few names keep winning.

If {{company}} wants to be on more of those lists by spring, that's exactly what we do. Quick call?

{{sender_first_name}}
```

### Step 4: day 12

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, I'll close the loop here.

If more invitations to bid would help next year, grab 15 minutes here: {{calendar_link}}

{{sender_first_name}}
```

## `certified-sub`

Sub holds a certification (MBE, WBE, DBE, SBE, SDVOSB, HUBZone...). GCs chasing participation goals need them.

**Used when:** certifications found on the website or in the lead list

### Step 1: day 0

**Subject:** {{company}}'s {{certification}} certification

```text
Hi {{greeting_name}},

Saw {{company}} is {{certification}}-certified.

GCs bidding public and institutional work have participation goals to hit, and on a lot of those jobs they have to document their outreach to certified subs. Plenty of them still don't have a certified {{trade}} sub they trust in {{market}}.

We get certified subs onto new GC bid lists: we build your prequal package, reach the estimators and precon managers, and track every invitation that comes back. If we don't get you on at least 10 new GC bid lists in 30 days, you don't pay.

Worth 15 minutes?

{{sender_first_name}}
```

### Step 2: day 3

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, here's how the 30 days work:

1. We build a one-page capabilities sheet and a prequal package from what you already have (COI, EMR letter, bonding letter, project list).
2. We pick the GCs actually building in {{market}} from public permit data and reach their estimators and precon managers as your business development rep.
3. We fill out the prequal forms and track who adds you and who sends invitations.

At least 10 new GC bid lists or you pay nothing. We only take one {{trade}} sub per market, so it would be just you.

Open to it?

{{sender_first_name}}
```

### Step 3: day 7

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, different question.

When {{company}} submits a bid, who follows up after bid day? Finding out whether the GC won the job, where your number landed, and who's running buyout is where a lot of awards are decided.

We run that follow-up for subs too. Worth a quick call?

{{sender_first_name}}
```

### Step 4: day 12

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, I'll close the loop here.

If more invitations to bid from GCs who need certified {{trade}} subs would help next year, grab 15 minutes here: {{calendar_link}}

{{sender_first_name}}
```

## `hiring`

Sub's website says they're hiring: busy now, so next year's backlog is the worry.

**Used when:** hiring language on the website

### Step 1: day 0

**Subject:** hiring at {{company}}

```text
Hi {{greeting_name}},

Saw {{company}} is hiring. Usually that means this year is busy and the real question is what the backlog looks like next spring, once you've added the people.

We build bid pipelines for commercial {{trade}} subs: new GC bid lists, prequals done for you, and follow-up on every bid so more of them turn into awarded work.

If we don't get you on at least 10 new GC bid lists in 30 days, you don't pay. Worth a look before 2027 budgets are set?

{{sender_first_name}}
```

### Step 2: day 3

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, here's how the 30 days work:

1. We build a capabilities sheet and prequal package from what you already have.
2. We pick the GCs actually building in your area and reach their estimators and precon managers as your business development rep.
3. We fill out the prequal forms and track who adds you and who sends invitations.

At least 10 new GC bid lists or you pay nothing. We only take one {{trade}} sub per market.

Open to it?

{{sender_first_name}}
```

### Step 3: day 7

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, different question.

When {{company}} submits a bid, who follows up after bid day? With the team growing, that's usually the first thing that slips, and it's where a lot of awards are decided.

We run that follow-up for subs. Worth a quick call?

{{sender_first_name}}
```

### Step 4: day 12

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, I'll close the loop here.

If filling next year's schedule becomes a priority, grab 15 minutes here: {{calendar_link}}

{{sender_first_name}}
```

## `permit-pulse`

We have permit data for the lead's market, so we can name the GCs pulling the most commercial permits.

**Used when:** lead's market has 3+ GCs in the permit leaderboard

### Step 1: day 0

**Subject:** {{top_gc_1}} in {{market}}

```text
Hi {{greeting_name}},

{{permits_90d}} commercial building permits were issued in {{market}} over the last 90 days, about {{permit_value_90d}} of work. {{top_gc_1}}, {{top_gc_2}} and {{top_gc_3}} pulled more of it than anyone else.

Is {{company}} getting invitations to bid from all three?

We get commercial {{trade}} subs onto new GC bid lists: prequal package, outreach to the estimators and precon managers, and tracking every invitation that comes back. If we don't get you on at least 10 new GC bid lists in 30 days, you don't pay.

Worth 15 minutes?

{{sender_first_name}}
```

### Step 2: day 3

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, I put together the full list: the top 25 GCs by commercial permits in {{market}} over the last 90 days, with their largest projects.

Happy to send it over. Takes you 2 minutes to mark which ones invite you to bid, and the gaps are usually obvious.

Want it?

{{sender_first_name}}
```

### Step 3: day 7

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, one more idea.

When {{company}} submits a bid, who follows up after bid day? Finding out whether the GC won the job, where your number landed, and who's running buyout is where a lot of awards are decided, and most estimators are already on the next takeoff.

We run that follow-up for subs, alongside getting you on new bid lists. Worth a quick call?

{{sender_first_name}}
```

### Step 4: day 12

**Subject:** _(reply in thread)_

```text
{{greeting_name}}, I'll leave it here.

If you want the {{market}} GC list or a look at your 2027 bid pipeline, grab 15 minutes: {{calendar_link}}

{{sender_first_name}}
```

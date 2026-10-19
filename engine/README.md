# BookedOut outreach engine

A small command-line tool that turns a raw list of HVAC companies into a ranked, personalized
outreach machine: **who to call today, what to say, and CSVs ready for your cold email tool.**

No dependencies beyond Python 3.11+. Claude-written openers are optional.

```
Google Maps / Apollo / GetLeads CSV
        │  bookedout import
        ▼
   leads (SQLite) ──► scan ──► weather ──► score ──► personalize ──► export ──► Instantly / Smartlead
                     website    NWS 7-day   0-100     first line      1 CSV per sequence
                     signals    forecast    A/B/C     rules or Claude
                         ▲                                  │
          after-hours audit (audit-list / audit-import)     └──► callsheet ──► you, on the phone
```

## Install

```bash
cd engine
python3 -m venv .venv && source .venv/bin/activate
pip install -e .            # core (stdlib only)
pip install -e '.[ai]'      # optional: Claude-written openers
cp config.example.toml config.toml   # then edit your name, demo line, calendar link
```

## Where leads come from

Any CSV works; headers are auto-detected. Tested shapes:

| Source | How to get it | What you get |
|---|---|---|
| **Outscraper** Google Maps | Search `HVAC contractor, <city>, <state>`, enable email enrichment | company, site, phone, rating, reviews, lat/lon, emails |
| **Apify** Google Maps Scraper | Same search terms | company (`title`), site, phone, `totalScore`, `reviewsCount`, location |
| **Apollo / GetLeads** contacts | Title: Owner, President, CEO, GM · Industry/keywords: HVAC | owner name + email, merged onto the company row |

Import the Maps list first, then the contact export: rows merge by domain/phone and only fill blanks.

## Daily routine

```bash
bookedout import leads/twin-cities.csv leads/apollo-owners.csv
bookedout daily            # scan new sites -> weather -> score -> personalize -> export -> call sheet
bookedout daily --ai       # same, with Claude writing openers for up to 300 top leads
```

Then:

1. Upload each `out/instantly-<sequence>-<date>.csv` into the matching campaign (copy: `../sales/email-sequences.md`).
2. Open `out/callsheet-<date>.md` and dial. Log each dial:
   `bookedout call <lead_id> --outcome no_answer|voicemail|gatekeeper|conversation|callback|booked|not_interested|bad_number|do_not_call`
3. When a reply comes in: `bookedout mark <domain-or-email> --status replied|interested|booked|...`
4. Weekly: `bookedout stats`.

## The after-hours audit (your best hook)

```bash
bookedout audit-list --n 40            # writes out/audit-list.csv
# a VA (or you) calls each main line after 6pm local time and fills `result` + `called_at`
bookedout audit-import out/audit-list.csv
```

Results: `answered`, `voicemail`, `no_answer`, `ivr`, `answering_service`, `disconnected`. A voicemail or no
answer moves the lead to the `after-hours` sequence and adds +20 to its score. You don't pretend to be anyone:
you just call the number the company advertises and note what happens.

## Commands

| Command | What it does |
|---|---|
| `import FILE...` | Normalize, dedupe and merge CSVs |
| `scan` | Fetch each homepage: Google Ads tag, Facebook pixel, chat vendor, online booking vendor, call tracking, 24/7, financing, maintenance plans, emails (also checks /contact) |
| `weather` | 7-day NWS forecast per ~10 km cell; flags cold snaps / heat waves (US only, free, no key) |
| `score` | 0-100 ICP score + tier A/B/C (`show <lead>` explains it) |
| `personalize [--ai]` | First-line openers from the strongest fact; `--ai` has Claude rewrite them, validated, with rule fallback |
| `export [--format smartlead]` | One CSV per sequence; marks leads `in_sequence` so they're never double-sent |
| `callsheet` | Ranked phone list with hook, signals, time zone and which opener to use |
| `audit-list` / `audit-import` / `audit` | After-hours test calls |
| `call` / `mark` / `show` / `stats` | Pipeline tracking |
| `preview <lead>` | Render the exact emails a lead will get (QA before you upload) |
| `sequences-md --out ../sales/email-sequences.md` | Regenerate the copy deck after editing `bookedout/sequences/*.toml` |

## Sequences and how a lead gets one

Strongest hook wins, in this order:

1. `after-hours`: audit result was voicemail / no answer / phone menu
2. `cold-snap`: forecast low ≤ `cold_threshold_f` (default 25°F) in their city this week
3. `heat-wave`: forecast high ≥ `hot_threshold_f` (default 95°F)
4. `paid-clicks`: site runs Google Ads but has no online booking and no chat
5. `estimate-recovery`: everyone else (leads with the guaranteed front-end offer)

## Claude openers (optional)

`bookedout personalize --ai` sends each lead's collected facts (never anything else) to Claude
(`claude-opus-5-5` at low effort, set in `config.toml`) and asks for one plain sentence. Output that is too long,
asks a question, flatters, or uses `!` is thrown out and the rule-based line is kept. Credentials come from
`ANTHROPIC_API_KEY` (or an `ant auth login` profile). The request opts into server-side refusal fallbacks.

## Tests

```bash
python3 -m unittest discover -s tests
```

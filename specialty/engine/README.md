# FullBacklog outreach engine

A command-line tool for selling to **commercial specialty subcontractors** and delivering for them. It turns
public building permits into a ranked list of the general contractors building in a market, then uses that
list to:

- **sell:** name the top GCs in a prospect's market in the first line of your email ("14 commercial permits in
  Austin last quarter; Northgate pulled the most. Are you on their bid list?")
- **close:** run a Bid List Gap Audit live on the sales call
- **deliver:** export the GC target list for a client's 30-day bid-list sprint

No dependencies beyond Python 3.11+. Claude-written openers are optional.

```
permit CSV (city open data) ──► permits ──► GC leaderboard per market ──┬──► gap-audit (lead magnet / sales call / client target list)
                                                                        │
sub lead CSV (Maps/Apollo/GetLeads/DBE directory) ──► import ──► scan ──► score ──► personalize ──► export ──► Instantly / Smartlead
                                                                                                   └──► callsheet ──► you, on the phone
```

## Install

```bash
cd specialty/engine
python3 -m venv .venv && source .venv/bin/activate
pip install -e .            # core (stdlib only)
pip install -e '.[ai]'      # optional: Claude-written openers
cp config.example.toml config.toml   # edit your name, calendar link, and [markets]
```

## 1. Permits: who's building in each market

Most large US cities publish issued building permits on an open-data portal (look for "issued construction
permits" or "building permits"; export CSV). Filter the export to the last 6 months to keep it small.

```bash
fullbacklog permits data/austin-permits.csv --market Austin
fullbacklog markets
```

Columns are auto-detected. It needs a **contractor name**, a **valuation**, and an **issue date**; it also uses
permit type, description, address and city when present (aliases in `fullbacklog/importer.py`; add one if your
city names a column differently). Then it:

- keeps commercial work (office, retail, medical, school, multifamily, industrial, tenant improvement...) and drops
  single-family/residential work, owner-builders, and trade permits (electrical, plumbing, mechanical, fire...)
- groups spelling variants (`HALVORSEN BUILDERS INC` = `Halvorsen Builders, Inc.`)
- ranks contractors by commercial permit value in the last `permit_days` (default 90)

Use `[markets]` in `config.toml` to put suburbs under their metro, so a sub in Round Rock gets Austin's data.

## 2. Leads: the subs you sell to

```bash
fullbacklog import leads/austin-subs.csv leads/apollo-owners.csv
fullbacklog daily            # scan new sites -> score -> personalize -> export -> call sheet
fullbacklog daily --ai       # same, with Claude writing openers for up to 300 top leads
```

| Source | How | Gets you |
|---|---|---|
| Google Maps (Outscraper / Apify) | Search `commercial drywall contractor`, `glazing contractor`, `fire sprinkler contractor`, `concrete contractor`... per metro | company, site, phone, city |
| Apollo / GetLeads | Industry: Construction / Specialty Trade Contractors; titles Owner, President, VP, Chief Estimator, Estimator; 10-200 employees | named contacts + employee counts (merged onto the company) |
| State DOT DBE directories, city/county MBE-WBE directories, SBA certification search | Download/export the directory for your state | certified subs (add a `certifications` column if the file doesn't have one) |
| Association member directories (ASA, ABC, AGC, trade associations) | Public member lists | active commercial subs |

`scan` reads each homepage and flags: trade, commercial vs residential language, certifications (MBE, WBE, DBE,
SBE, SDVOSB, VOSB, HUBZone, 8(a), HUB), hiring, project types, portfolio page, safety/EMR, bonding, union language,
and emails (also checks /contact).

## 3. Selling

Each lead gets the strongest sequence it qualifies for:

1. `certified-sub`: certification found → GCs with participation goals need them
2. `permit-pulse`: its market has permit data → names the top 3 GCs and offers the full list
3. `hiring`: hiring → "busy now; what does next spring look like?"
4. `bid-chase`: everyone else → the follow-up gap after bid day

Upload each `out/instantly-<sequence>-<date>.csv` to the matching campaign (copy: `../sales/email-sequences.md`),
then work `out/callsheet-<date>.md`. Log every dial:
`fullbacklog call <lead_id> --outcome no_answer|voicemail|gatekeeper|conversation|callback|booked|not_interested|bad_number|do_not_call`

## 4. The Bid List Gap Audit

```bash
# Before a sales call (no known list):
fullbacklog gap-audit --market Austin --company "Acme Interiors"
# With the GCs they already bid for (one per line, from their BuildingConnected or memory):
fullbacklog gap-audit --market Austin --company "Acme Interiors" --known acme-gcs.txt --n 40
```

Writes `out/gap-audit-<market>-<company>.md` (send it, or share your screen) and `out/gc-targets-<...>.csv` (the
sprint's target list; enrich it with estimator/precon contacts in Apollo or GetLeads).

## Commands

| Command | What it does |
|---|---|
| `permits FILE --market NAME` | Import a permit export; prints the market's top GCs |
| `markets` | Permit totals and top GCs for every market |
| `gap-audit --market NAME` | Ranked GC list, marked against the GCs a sub already bids for |
| `import FILE...` | Normalize, dedupe and merge sub lead CSVs |
| `scan` | Website signals (see above) |
| `score` | 0-100 ICP score + tier A/B/C (`show <lead>` explains it) |
| `personalize [--ai]` | First-line openers from the strongest fact |
| `export [--format smartlead]` | One CSV per sequence; marks leads `in_sequence` |
| `callsheet` | Ranked phone list with hook, signals, time zone and opener |
| `call` / `mark` / `show` / `stats` | Pipeline tracking |
| `preview <lead>` | Render the exact emails a lead will get |
| `sequences-md --out ../sales/email-sequences.md` | Regenerate the copy deck after editing `fullbacklog/sequences/*.toml` |

## Claude openers (optional)

`fullbacklog personalize --ai` sends each lead's collected facts (and its market's permit summary, never anything
else) to Claude (`claude-opus-5-5` at low effort, set in `config.toml`) for one plain sentence. Output that's too
long, asks a question, flatters, or uses `!` is discarded and the rule-based line kept. Credentials come from
`ANTHROPIC_API_KEY` or an `ant auth login` profile. Requests opt into server-side refusal fallbacks.

## Tests

```bash
python3 -m unittest discover -s tests
```

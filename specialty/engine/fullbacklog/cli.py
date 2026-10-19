"""fullbacklog: the command line for the outreach engine.

Typical day:
    fullbacklog permits data/austin-permits.csv --market Austin
    fullbacklog import leads/austin-subs.csv
    fullbacklog daily            # scan new sites, score, personalize, export, call sheet
    fullbacklog gap-audit --market Austin --company "Acme Interiors" --known acme-gcs.txt
    fullbacklog call <id> --outcome conversation --note "bids 25/mo, only 6 GCs, call Thu"
    fullbacklog stats
"""

import argparse
import os
import sys
from collections import Counter
from datetime import date
from pathlib import Path

from . import __version__
from .callsheet import callsheet_rows, write_callsheet
from .config import load_config
from .db import LeadStore
from .export import export_leads
from .gap_audit import gap_rows, read_known, write_gap_audit
from .importer import read_leads, read_permits
from .models import STATUSES, SUPPRESSED
from .permits import all_market_stats, assign_market, leaderboard, money_short
from .personalize import personalize_leads
from .scanner import scan_many
from .scoring import score_lead, tier_for
from .sequences import choose_sequence, lead_variables, load_sequences, render_sequence, sequences_markdown

CALL_OUTCOMES = {
    "no_answer": None,
    "voicemail": None,
    "gatekeeper": None,
    "conversation": None,
    "callback": "interested",
    "booked": "booked",
    "not_interested": "lost",
    "bad_number": "not_fit",
    "do_not_call": "do_not_contact",
}


def _progress(label: str):
    def report(done: int, total: int, *_):
        if done == total or done % 25 == 0:
            print(f"  {label}: {done}/{total}", file=sys.stderr)
    return report


def _as_of(config) -> date:
    value = config["targeting"].get("as_of")
    return date.fromisoformat(value) if value else date.today()


def _stats(store, config):
    return all_market_stats(store, _as_of(config), config["targeting"]["permit_days"])


def _stats_for(lead, stats_by_market):
    return stats_by_market.get((lead.market or lead.city).lower())


def _require(store, key: str):
    lead = store.find(key)
    if not lead:
        sys.exit(f"No lead matches '{key}' (use an id, domain, email or phone).")
    return lead


# --- commands ----------------------------------------------------------------

def cmd_import(args, store, config):
    total_new = total_merged = 0
    for path in args.files:
        leads, mapping, fmt = read_leads(path, args.source)
        new = merged = 0
        for lead in leads:
            lead.market = assign_market(lead.city, config["markets"])
            _, created = store.upsert(lead, commit=False)
            new += created
            merged += not created
        store.commit()
        total_new, total_merged = total_new + new, total_merged + merged
        print(f"{path}: {len(leads)} rows ({fmt}) -> {new} new, {merged} merged into existing leads")
        unmapped = [f for f in ("company", "email", "phone", "website") if f not in mapping]
        if unmapped:
            print(f"  note: no column found for {', '.join(unmapped)}")
    print(f"Total: {total_new} new, {total_merged} merged. Next: fullbacklog scan")


def cmd_permits(args, store, config):
    permits, mapping = read_permits(args.file, market=args.market, city=args.city,
                                    min_commercial_value=config["targeting"]["min_commercial_value"])
    for permit in permits:
        store.save_permit(permit)
    store.commit()
    commercial = sum(p.commercial for p in permits)
    print(f"{args.file}: {len(permits)} permits -> {commercial} commercial, market '{args.market or 'from city column'}'")
    for field in ("contractor", "valuation", "issued"):
        if field not in mapping:
            print(f"  WARNING: no column found for {field}; the leaderboard needs it (see engine/README.md)")
    cmd_markets(args, store, config)


def cmd_markets(args, store, config):
    stats = _stats(store, config)
    if not stats:
        print("No permit data yet. Import a city's permit CSV: fullbacklog permits FILE --market NAME")
        return
    print(f"{'market':20s} {'permits':>8s} {'value':>10s}  top GCs (last {config['targeting']['permit_days']} days)")
    for item in sorted(stats.values(), key=lambda s: s.value, reverse=True):
        print(f"{item.market:20s} {item.permits:8d} {money_short(item.value):>10s}  {', '.join(item.top_names(3))}")


def cmd_gap_audit(args, store, config):
    market_permits = store.permits(args.market)
    if not market_permits:
        sys.exit(f"No permits for market '{args.market}'. Known markets: {', '.join(store.markets()) or 'none'}")
    as_of = _as_of(config)
    stats = leaderboard(market_permits, as_of, args.days or config["targeting"]["permit_days"], market_permits[0].market)
    rows = gap_rows(stats, read_known(args.known), n=args.n)
    md_path, csv_path = write_gap_audit(stats, rows, args.out, args.company, as_of)
    missing = sum(row["invites_you"] == "no" for row in rows)
    print(f"{stats.market}: {stats.permits} commercial permits, {len(stats.leaders)} contractors -> {md_path} and {csv_path.name}")
    if args.known:
        print(f"  {missing} of the top {len(rows)} GCs don't invite {args.company or 'this sub'} yet")


def cmd_scan(args, store, config):
    where = "domain != ''" + ("" if args.rescan else " AND (scanned_at IS NULL OR scanned_at = '')")
    leads = store.all(where)
    if args.limit:
        leads = leads[: args.limit]
    if not leads:
        print("Nothing to scan.")
        return
    print(f"Scanning {len(leads)} websites with {args.workers} workers...")
    for lead in scan_many(leads, workers=args.workers, progress=_progress("scanned")):
        store.save(lead, commit=False)
    store.commit()
    ok = [l for l in leads if l.site_ok]
    commercial = sum((l.commercial_hits or 0) >= 2 and (l.commercial_hits or 0) >= (l.residential_hits or 0) for l in ok)
    print(
        f"Done. {len(ok)} sites up · {commercial} commercial-focused · "
        f"{sum(bool(l.certifications) for l in ok)} certified · {sum(bool(l.hiring) for l in ok)} hiring · "
        f"{sum(bool(l.email) for l in leads)} with an email"
    )


def cmd_score(args, store, config):
    stats = _stats(store, config)
    leads = store.all()
    for lead in leads:
        lead.market = lead.market or assign_market(lead.city, config["markets"])
        lead.score, _ = score_lead(lead, config["targeting"]["trades"], _stats_for(lead, stats))
        lead.tier = tier_for(lead.score)
        store.save(lead, commit=False)
    store.commit()
    tiers = Counter(lead.tier for lead in leads)
    print(f"Scored {len(leads)} leads: A={tiers['A']} B={tiers['B']} C={tiers['C']}")


def cmd_personalize(args, store, config):
    where = "" if args.overwrite else "(personalization IS NULL OR personalization = '' OR personalization_source NOT LIKE 'ai:%')"
    leads = [l for l in store.all(where) if l.status not in SUPPRESSED and (l.score or 0) >= args.min_score]
    if args.limit:
        leads = sorted(leads, key=lambda l: l.score or 0, reverse=True)[: args.limit]
    ai = config["ai"]
    counts = personalize_leads(
        leads, _stats(store, config), use_ai=args.ai, model=args.model or ai["model"], effort=ai["effort"],
        workers=ai["workers"], progress=_progress("personalized") if args.ai else None,
    )
    for lead in leads:
        store.save(lead, commit=False)
    store.commit()
    print(f"Personalized {len(leads)} leads: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))


def cmd_export(args, store, config):
    written = export_leads(store, config, args.out, _stats(store, config), fmt=args.format, min_score=args.min_score,
                           include_contacted=args.include_contacted, mark=not args.dry_run)
    if not written:
        print("No exportable leads (need an email, score >= min, and not already in a sequence).")
        return
    for sequence, (path, count) in sorted(written.items()):
        print(f"{count:5d}  {sequence:15s} -> {path}")
    if args.dry_run:
        print("(dry run: leads were not marked in_sequence)")


def cmd_callsheet(args, store, config):
    rows = callsheet_rows(store, _stats(store, config), n=args.n, cooldown_days=args.cooldown)
    md_path, csv_path = write_callsheet(rows, args.out)
    print(f"{len(rows)} leads -> {md_path} (and {csv_path.name})")


def cmd_call(args, store, config):
    lead = _require(store, args.lead)
    store.log(lead.id, "call", f"{args.outcome}: {args.note}".strip().rstrip(":"), commit=False)
    new_status = CALL_OUTCOMES[args.outcome]
    if new_status:
        lead.status = new_status
    elif lead.status in ("new", "in_sequence"):
        lead.status = "called"
    if args.note:
        lead.notes = (lead.notes + "\n" if lead.notes else "") + args.note
    store.save(lead, commit=False)
    store.commit()
    print(f"{lead.company}: {args.outcome} (status: {lead.status})")


def cmd_mark(args, store, config):
    lead = _require(store, args.lead)
    old, lead.status = lead.status, args.status
    if args.note:
        lead.notes = (lead.notes + "\n" if lead.notes else "") + args.note
    store.save(lead, commit=False)
    store.log(lead.id, "status", f"{old} -> {args.status}" + (f": {args.note}" if args.note else ""), commit=False)
    store.commit()
    print(f"{lead.company}: {old} -> {args.status}")


def cmd_show(args, store, config):
    lead = _require(store, args.lead)
    stats = _stats_for(lead, _stats(store, config))
    _, reasons = score_lead(lead, config["targeting"]["trades"], stats)
    for name, value in vars(lead).items():
        if value not in (None, ""):
            print(f"{name:22s} {value}")
    print("\nscore breakdown:")
    for reason in reasons:
        print(f"  {reason}")
    events = store.events(lead_id=lead.id)
    if events:
        print("\nhistory:")
        for event in events:
            print(f"  {event['at']}  {event['kind']:9s} {event['detail']}")


def cmd_preview(args, store, config):
    lead = _require(store, args.lead)
    stats_by_market = _stats(store, config)
    stats = _stats_for(lead, stats_by_market)
    if not lead.personalization:
        personalize_leads([lead], stats_by_market)
    sequences = load_sequences()
    name = args.sequence or choose_sequence(lead, stats)
    if name not in sequences:
        sys.exit(f"Unknown sequence '{name}'. Options: {', '.join(sequences)}")
    rendered, missing = render_sequence(sequences[name], lead_variables(lead, config, stats))
    print(f"Sequence: {name}  ·  To: {lead.email or '(no email)'}\n")
    for day, subject, body in rendered:
        print(f"--- day {day} · subject: {subject or '(reply in thread)'}\n{body}\n")
    if missing:
        print(f"WARNING: empty variables: {', '.join(missing)}", file=sys.stderr)


def cmd_sequences_md(args, store, config):
    text = sequences_markdown(load_sequences())
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        sys.stdout.write(text)


def cmd_stats(args, store, config):
    leads = store.all()
    statuses = Counter(lead.status for lead in leads)
    tiers = Counter(lead.tier or "-" for lead in leads)
    trades = Counter(lead.trade or "unknown" for lead in leads)
    calls = store.events(kind="call")
    outcomes = Counter(event["detail"].split(":")[0] for event in calls)
    print(f"Leads: {len(leads)}   tiers: " + "  ".join(f"{t}={tiers[t]}" for t in ("A", "B", "C", "-") if tiers[t]))
    print("Trades: " + ", ".join(f"{t}={n}" for t, n in trades.most_common()))
    print(f"With email: {sum(bool(l.email) for l in leads)}   with phone: {sum(bool(l.phone) for l in leads)}   "
          f"certified: {sum(bool(l.certifications) for l in leads)}")
    print("\nPipeline:")
    for status in STATUSES:
        if statuses[status]:
            print(f"  {status:16s} {statuses[status]:6d}")
    if calls:
        conversations = sum(outcomes[o] for o in ("conversation", "callback", "booked", "not_interested"))
        print(f"\nDials: {len(calls)}   conversations: {conversations}   booked from phone: {outcomes['booked']}")
        if conversations:
            print(f"  connect rate: {conversations / len(calls):.0%}   book rate per conversation: {outcomes['booked'] / conversations:.0%}")
    reached = sum(statuses[s] for s in ("booked", "showed", "proposal", "won", "lost"))
    if reached:
        held = sum(statuses[s] for s in ("showed", "proposal", "won", "lost"))
        print(f"\nSales calls booked: {reached}   held: {held}   won: {statuses['won']}"
              + (f"   close rate: {statuses['won'] / held:.0%}" if held else ""))


def cmd_daily(args, store, config):
    print("1/5 scan new websites")
    cmd_scan(argparse.Namespace(rescan=False, limit=args.scan_limit, workers=16), store, config)
    print("2/5 score")
    cmd_score(args, store, config)
    print("3/5 personalize")
    cmd_personalize(argparse.Namespace(overwrite=False, min_score=config["targeting"]["min_export_score"],
                                       limit=args.ai_limit, ai=args.ai, model=None), store, config)
    print("4/5 export")
    cmd_export(argparse.Namespace(out=args.out, format=args.format, min_score=None,
                                  include_contacted=False, dry_run=False), store, config)
    print("5/5 call sheet")
    cmd_callsheet(argparse.Namespace(n=args.calls, cooldown=3, out=args.out), store, config)


# --- parser --------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fullbacklog", description="Outreach engine for commercial specialty subcontractors.")
    parser.add_argument("--db", default=os.environ.get("FULLBACKLOG_DB", "fullbacklog.db"), help="SQLite file")
    parser.add_argument("--config", help="config.toml path (default: ./config.toml)")
    parser.add_argument("--version", action="version", version=f"fullbacklog {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("import", help="import subcontractor lead CSVs (Google Maps, Apollo, GetLeads, directories)")
    p.add_argument("files", nargs="+")
    p.add_argument("--source", help="label stored on each lead (default: detected format)")
    p.set_defaults(func=cmd_import)

    p = sub.add_parser("permits", help="import a city/county building permit CSV")
    p.add_argument("file")
    p.add_argument("--market", default="", help="metro name to file these under (default: the city column)")
    p.add_argument("--city", default="", help="city to use when the file has no city column")
    p.set_defaults(func=cmd_permits)

    p = sub.add_parser("markets", help="permit totals and top GCs per market")
    p.set_defaults(func=cmd_markets)

    p = sub.add_parser("gap-audit", help="top GCs in a market, marked against the GCs a sub already bids for")
    p.add_argument("--market", required=True)
    p.add_argument("--company", default="", help="the sub's name, for the report title")
    p.add_argument("--known", help="text/CSV file of GCs that already invite the sub, one per line")
    p.add_argument("--n", type=int, default=25)
    p.add_argument("--days", type=int, default=0, help="permit window (default: targeting.permit_days)")
    p.add_argument("--out", default="out")
    p.set_defaults(func=cmd_gap_audit)

    p = sub.add_parser("scan", help="scan websites: trade, commercial focus, certifications, hiring, emails")
    p.add_argument("--rescan", action="store_true")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--workers", type=int, default=16)
    p.set_defaults(func=cmd_scan)

    p = sub.add_parser("score", help="score and tier every lead")
    p.set_defaults(func=cmd_score)

    p = sub.add_parser("personalize", help="write first-line openers (rules, or Claude with --ai)")
    p.add_argument("--ai", action="store_true", help="use Claude (needs: pip install -e '.[ai]' and API credentials)")
    p.add_argument("--model", help="override the model from config")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--min-score", type=int, default=0)
    p.add_argument("--overwrite", action="store_true", help="redo leads that already have an AI opener")
    p.set_defaults(func=cmd_personalize)

    p = sub.add_parser("export", help="write CSVs for Instantly/Smartlead, one per sequence")
    p.add_argument("--format", choices=["instantly", "smartlead"], default="instantly")
    p.add_argument("--out", default="out")
    p.add_argument("--min-score", type=int)
    p.add_argument("--include-contacted", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("callsheet", help="today's ranked call list with hooks")
    p.add_argument("--n", type=int, default=60)
    p.add_argument("--cooldown", type=int, default=3)
    p.add_argument("--out", default="out")
    p.set_defaults(func=cmd_callsheet)

    p = sub.add_parser("call", help="log a cold call")
    p.add_argument("lead")
    p.add_argument("--outcome", required=True, choices=list(CALL_OUTCOMES))
    p.add_argument("--note", default="")
    p.set_defaults(func=cmd_call)

    p = sub.add_parser("mark", help="set a lead's pipeline status")
    p.add_argument("lead")
    p.add_argument("--status", required=True, choices=STATUSES)
    p.add_argument("--note", default="")
    p.set_defaults(func=cmd_mark)

    p = sub.add_parser("show", help="everything about one lead, with its score breakdown")
    p.add_argument("lead")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("preview", help="render a lead's email sequence for QA")
    p.add_argument("lead")
    p.add_argument("--sequence")
    p.set_defaults(func=cmd_preview)

    p = sub.add_parser("sequences-md", help="render all sequences as Markdown")
    p.add_argument("--out")
    p.set_defaults(func=cmd_sequences_md)

    p = sub.add_parser("stats", help="pipeline and calling numbers")
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("daily", help="scan -> score -> personalize -> export -> call sheet")
    p.add_argument("--ai", action="store_true")
    p.add_argument("--ai-limit", type=int, default=300)
    p.add_argument("--scan-limit", type=int, default=500)
    p.add_argument("--calls", type=int, default=60)
    p.add_argument("--format", choices=["instantly", "smartlead"], default="instantly")
    p.add_argument("--out", default="out")
    p.set_defaults(func=cmd_daily)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    config = load_config(args.config)
    store = LeadStore(args.db)
    try:
        args.func(args, store, config)
    finally:
        store.close()


if __name__ == "__main__":
    main()

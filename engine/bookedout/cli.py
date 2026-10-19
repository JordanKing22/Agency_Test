"""bookedout: the command line for the outreach engine.

Typical day:
    bookedout import leads/minneapolis.csv
    bookedout daily              # scan new sites, weather, score, personalize, export, call sheet
    bookedout call <id> --outcome conversation --note "has 300 unsold quotes, call Thu"
    bookedout stats
"""

import argparse
import csv
import os
import sys
from collections import Counter
from pathlib import Path

from . import __version__
from .callsheet import audit_rows, callsheet_rows, write_audit_list, write_callsheet
from .config import load_config
from .db import LeadStore
from .export import export_leads
from .importer import read_leads
from .models import AUDIT_RESULTS, STATUSES, SUPPRESSED
from .personalize import personalize_leads
from .scanner import scan_many
from .scoring import apply_scores, score_lead
from .sequences import choose_sequence, lead_variables, load_sequences, render_sequence, sequences_markdown
from .weather import apply_weather

CALL_OUTCOMES = {
    # outcome -> status to set (None keeps the current status, but at least "called")
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


def _require(store: LeadStore, key: str):
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
            _, created = store.upsert(lead, commit=False)
            new += created
            merged += not created
        store.commit()
        total_new += new
        total_merged += merged
        print(f"{path}: {len(leads)} rows ({fmt}) -> {new} new, {merged} merged into existing leads")
        unmapped = [field for field in ("company", "email", "phone", "website") if field not in mapping]
        if unmapped:
            print(f"  note: no column found for {', '.join(unmapped)}")
    print(f"Total: {total_new} new, {total_merged} merged. Next: bookedout scan")


def cmd_scan(args, store, config):
    where = "domain != ''" + ("" if args.rescan else " AND (scanned_at IS NULL OR scanned_at = '')")
    leads = store.all(where)
    leads.sort(key=lambda l: l.reviews or 0, reverse=True)
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
    print(
        f"Done. {len(ok)} sites up · {sum(bool(l.runs_google_ads) for l in ok)} running Google Ads · "
        f"{sum(not l.booking_vendor for l in ok)} without online booking · "
        f"{sum(not l.chat_vendor for l in ok)} without chat · "
        f"{sum(bool(l.email) for l in leads)} with an email"
    )


def cmd_weather(args, store, config):
    leads = store.all("lat IS NOT NULL AND lon IS NOT NULL")
    if not leads:
        print("No leads have coordinates (Google Maps exports usually include latitude/longitude).")
        return
    updated, failed = apply_weather(leads, config["nws"]["user_agent"], progress=_progress("forecast cells"))
    for lead in leads:
        store.save(lead, commit=False)
    store.commit()
    cold = config["targeting"]["cold_threshold_f"]
    hot = config["targeting"]["hot_threshold_f"]
    snaps = sum(1 for l in leads if l.forecast_low_f is not None and l.forecast_low_f <= cold)
    waves = sum(1 for l in leads if l.forecast_high_f is not None and l.forecast_high_f >= hot)
    print(f"Updated {updated} leads ({failed} cells failed). Cold snap (<= {cold}F): {snaps} · heat wave (>= {hot}F): {waves}")
    if failed and not updated:
        print("  Every forecast request failed: check that this machine can reach https://api.weather.gov")


def cmd_score(args, store, config):
    leads = store.all()
    apply_scores(leads, config["targeting"]["cold_threshold_f"], config["targeting"]["hot_threshold_f"])
    for lead in leads:
        store.save(lead, commit=False)
    store.commit()
    tiers = Counter(lead.tier for lead in leads)
    print(f"Scored {len(leads)} leads: A={tiers['A']} B={tiers['B']} C={tiers['C']}")


def cmd_personalize(args, store, config):
    where = "" if args.overwrite else "(personalization IS NULL OR personalization = '' OR personalization_source NOT LIKE 'ai:%')"
    leads = [l for l in store.all(where) if l.status not in SUPPRESSED]
    if args.min_score:
        leads = [l for l in leads if (l.score or 0) >= args.min_score]
    if args.limit:
        leads = sorted(leads, key=lambda l: l.score or 0, reverse=True)[: args.limit]
    ai = config["ai"]
    counts = personalize_leads(
        leads,
        use_ai=args.ai,
        model=args.model or ai["model"],
        effort=ai["effort"],
        workers=ai["workers"],
        cold_threshold_f=config["targeting"]["cold_threshold_f"],
        hot_threshold_f=config["targeting"]["hot_threshold_f"],
        progress=_progress("personalized") if args.ai else None,
    )
    for lead in leads:
        store.save(lead, commit=False)
    store.commit()
    print(f"Personalized {len(leads)} leads: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))


def cmd_export(args, store, config):
    written = export_leads(
        store, config, args.out, fmt=args.format, min_score=args.min_score,
        include_contacted=args.include_contacted, mark=not args.dry_run,
    )
    if not written:
        print("No exportable leads (need an email, score >= min, and not already in a sequence).")
        return
    for sequence, (path, count) in sorted(written.items()):
        print(f"{count:5d}  {sequence:18s} -> {path}")
    if args.dry_run:
        print("(dry run: leads were not marked in_sequence)")


def cmd_callsheet(args, store, config):
    rows = callsheet_rows(store, config, n=args.n, cooldown_days=args.cooldown)
    md_path, csv_path = write_callsheet(rows, args.out)
    print(f"{len(rows)} leads -> {md_path} (and {csv_path.name})")


def cmd_audit_list(args, store, config):
    rows = audit_rows(store, n=args.n)
    path = write_audit_list(rows, args.out)
    print(
        f"{len(rows)} numbers -> {path}\n"
        "Call each main line after 6pm local time. Fill `result` with one of: "
        + ", ".join(AUDIT_RESULTS)
        + "\nand `called_at` like 'Tuesday at 7:42pm'. Then: bookedout audit-import " + str(path)
    )


def _set_audit(store, lead, result: str, when: str, config: dict) -> None:
    targeting = config["targeting"]
    lead.audit_result = result
    lead.audit_time = when
    lead.personalization = lead.personalization_source = ""  # the audit is now the strongest hook
    lead.score, _ = score_lead(lead, targeting["cold_threshold_f"], targeting["hot_threshold_f"])
    store.save(lead, commit=False)
    store.log(lead.id, "audit", f"{result} {when}".strip(), commit=False)


def cmd_audit(args, store, config):
    lead = _require(store, args.lead)
    _set_audit(store, lead, args.result, args.at or "", config)
    store.commit()
    sequence = choose_sequence(lead, config["targeting"]["cold_threshold_f"], config["targeting"]["hot_threshold_f"])
    print(f"{lead.company}: audit={args.result} -> sequence will be {sequence}")


def cmd_audit_import(args, store, config):
    updated = skipped = 0
    with open(args.file, newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            result = (row.get("result") or "").strip().lower().replace(" ", "_").replace("-", "_")
            if result not in AUDIT_RESULTS:
                skipped += 1
                continue
            lead = store.find(row.get("lead_id") or row.get("phone") or "")
            if not lead:
                skipped += 1
                continue
            _set_audit(store, lead, result, (row.get("called_at") or "").strip(), config)
            updated += 1
    store.commit()
    print(f"Recorded {updated} audits ({skipped} rows skipped: blank/unknown result or no matching lead).")


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
    old = lead.status
    lead.status = args.status
    if args.note:
        lead.notes = (lead.notes + "\n" if lead.notes else "") + args.note
    store.save(lead, commit=False)
    store.log(lead.id, "status", f"{old} -> {args.status}" + (f": {args.note}" if args.note else ""), commit=False)
    store.commit()
    print(f"{lead.company}: {old} -> {args.status}")


def cmd_show(args, store, config):
    lead = _require(store, args.lead)
    score, reasons = score_lead(lead, config["targeting"]["cold_threshold_f"], config["targeting"]["hot_threshold_f"])
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
    targeting = config["targeting"]
    if not lead.personalization:
        personalize_leads([lead], cold_threshold_f=targeting["cold_threshold_f"], hot_threshold_f=targeting["hot_threshold_f"])
    sequences = load_sequences()
    name = args.sequence or choose_sequence(lead, targeting["cold_threshold_f"], targeting["hot_threshold_f"])
    if name not in sequences:
        sys.exit(f"Unknown sequence '{name}'. Options: {', '.join(sequences)}")
    rendered, missing = render_sequence(sequences[name], lead_variables(lead, config))
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
        print(text)


def cmd_stats(args, store, config):
    leads = store.all()
    statuses = Counter(lead.status for lead in leads)
    tiers = Counter(lead.tier or "-" for lead in leads)
    calls = store.events(kind="call")
    outcomes = Counter(event["detail"].split(":")[0] for event in calls)
    print(f"Leads: {len(leads)}   tiers: " + "  ".join(f"{t}={tiers[t]}" for t in ("A", "B", "C", "-") if tiers[t]))
    print(f"With email: {sum(bool(l.email) for l in leads)}   with phone: {sum(bool(l.phone) for l in leads)}   "
          f"audited: {sum(bool(l.audit_result) for l in leads)}")
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
    """The whole morning routine in one command."""
    print("1/6 scan new websites")
    cmd_scan(argparse.Namespace(rescan=False, limit=args.scan_limit, workers=16), store, config)
    print("2/6 weather")
    cmd_weather(args, store, config)
    print("3/6 score")
    cmd_score(args, store, config)
    print("4/6 personalize")
    cmd_personalize(argparse.Namespace(overwrite=False, min_score=config["targeting"]["min_export_score"],
                                       limit=args.ai_limit, ai=args.ai, model=None), store, config)
    print("5/6 export")
    cmd_export(argparse.Namespace(out=args.out, format=args.format, min_score=None,
                                  include_contacted=False, dry_run=False), store, config)
    print("6/6 call sheet")
    cmd_callsheet(argparse.Namespace(n=args.calls, cooldown=3, out=args.out), store, config)


# --- parser --------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bookedout", description="Outreach engine for HVAC companies.")
    parser.add_argument("--db", default=os.environ.get("BOOKEDOUT_DB", "bookedout.db"), help="SQLite file (default: bookedout.db)")
    parser.add_argument("--config", help="config.toml path (default: ./config.toml)")
    parser.add_argument("--version", action="version", version=f"bookedout {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("import", help="import lead CSVs (Outscraper, Apify, Apollo, GetLeads, generic)")
    p.add_argument("files", nargs="+")
    p.add_argument("--source", help="label stored on each lead (default: detected format)")
    p.set_defaults(func=cmd_import)

    p = sub.add_parser("scan", help="scan websites for ads, booking, chat, call tracking, emails")
    p.add_argument("--rescan", action="store_true", help="rescan sites already scanned")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--workers", type=int, default=16)
    p.set_defaults(func=cmd_scan)

    p = sub.add_parser("weather", help="pull 7-day NWS forecasts to find cold snaps / heat waves")
    p.set_defaults(func=cmd_weather)

    p = sub.add_parser("score", help="score and tier every lead")
    p.set_defaults(func=cmd_score)

    p = sub.add_parser("personalize", help="write first-line openers (rules, or Claude with --ai)")
    p.add_argument("--ai", action="store_true", help="use Claude (needs: pip install -e '.[ai]' and API credentials)")
    p.add_argument("--model", help="override the model from config")
    p.add_argument("--limit", type=int, default=0, help="only the top N by score")
    p.add_argument("--min-score", type=int, default=0)
    p.add_argument("--overwrite", action="store_true", help="redo leads that already have an AI opener")
    p.set_defaults(func=cmd_personalize)

    p = sub.add_parser("export", help="write CSVs for Instantly/Smartlead, one per sequence")
    p.add_argument("--format", choices=["instantly", "smartlead"], default="instantly")
    p.add_argument("--out", default="out")
    p.add_argument("--min-score", type=int, help="default: targeting.min_export_score")
    p.add_argument("--include-contacted", action="store_true", help="also re-export leads already in a sequence")
    p.add_argument("--dry-run", action="store_true", help="write files without marking leads as in_sequence")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("callsheet", help="today's ranked call list with hooks")
    p.add_argument("--n", type=int, default=60)
    p.add_argument("--cooldown", type=int, default=3, help="skip leads dialed in the last N days")
    p.add_argument("--out", default="out")
    p.set_defaults(func=cmd_callsheet)

    p = sub.add_parser("audit-list", help="CSV of main lines to test after hours")
    p.add_argument("--n", type=int, default=40)
    p.add_argument("--out", default="out/audit-list.csv")
    p.set_defaults(func=cmd_audit_list)

    p = sub.add_parser("audit", help="record one after-hours test call")
    p.add_argument("lead")
    p.add_argument("--result", required=True, choices=AUDIT_RESULTS)
    p.add_argument("--at", help="when you called, e.g. 'Tuesday at 7:42pm'")
    p.set_defaults(func=cmd_audit)

    p = sub.add_parser("audit-import", help="record a filled-in audit-list CSV")
    p.add_argument("file")
    p.set_defaults(func=cmd_audit_import)

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
    p.add_argument("--sequence", help="force a sequence instead of the auto choice")
    p.set_defaults(func=cmd_preview)

    p = sub.add_parser("sequences-md", help="render all sequences as Markdown")
    p.add_argument("--out", help="file to write (default: stdout)")
    p.set_defaults(func=cmd_sequences_md)

    p = sub.add_parser("stats", help="pipeline and calling numbers")
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("daily", help="scan -> weather -> score -> personalize -> export -> call sheet")
    p.add_argument("--ai", action="store_true", help="use Claude for openers")
    p.add_argument("--ai-limit", type=int, default=300, help="max leads to send to Claude per run")
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

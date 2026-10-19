import contextlib
import copy
import csv
import io
import tempfile
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace

from fullbacklog import cli
from fullbacklog.config import load_config
from fullbacklog.db import LeadStore
from fullbacklog.export import custom_columns, export_leads
from fullbacklog.gap_audit import gap_markdown, gap_rows, read_known
from fullbacklog.importer import build_mapping, LEAD_ALIASES, parse_date, parse_employees, read_leads, read_permits
from fullbacklog.models import Lead, Permit
from fullbacklog.permits import assign_market, classify_commercial, contractor_key, display_name, leaderboard, money_short
from fullbacklog.personalize import SYSTEM_PROMPT, ai_opener, personalize_leads, rule_opener, validate_opener
from fullbacklog.scanner import detect_signals, scan_lead
from fullbacklog.scoring import score_lead, tier_for
from fullbacklog.sequences import choose_sequence, lead_variables, load_sequences, render_sequence
from fullbacklog.trades import detect_trade

try:
    import anthropic  # noqa: F401
    HAS_SDK = True
except ImportError:
    HAS_SDK = False

SAMPLES = Path(__file__).resolve().parent.parent / "sample_data"
AS_OF = date(2026, 10, 19)
CONFIG = load_config("/nonexistent")
CONFIG["markets"] = {"Austin": ["Austin", "Round Rock", "Pflugerville"]}
CONFIG["targeting"]["as_of"] = AS_OF.isoformat()
TARGETS = CONFIG["targeting"]["trades"]


def austin_stats():
    permits, _ = read_permits(SAMPLES / "permits_sample.csv", market="Austin")
    return leaderboard(permits, AS_OF, 90, "Austin")


def sub(**overrides) -> Lead:
    lead = Lead(
        id="abc", company="Lone Star Interior Systems, LLC", first_name="Rosa", email="rosa@lonestar.example",
        phone="+15125550141", domain="lonestar.example", city="Austin", state="TX", market="Austin",
        category="Drywall contractor", trade="drywall", employees=85,
        scanned_at="2026-10-19T00:00:00+00:00", site_ok=1, commercial_hits=6, residential_hits=0,
    )
    for key, value in overrides.items():
        setattr(lead, key, value)
    return lead


class ImportTests(unittest.TestCase):
    def test_parsers(self):
        self.assertEqual(parse_employees("11-50"), 30)
        self.assertEqual(parse_employees("51 to 200"), 125)
        self.assertEqual(parse_employees("85"), 85)
        self.assertIsNone(parse_employees(""))
        self.assertEqual(parse_date("09/14/2026"), "2026-09-14")
        self.assertEqual(parse_date("2026-09-14T00:00:00.000"), "2026-09-14")
        self.assertEqual(parse_date("Sep 14, 2026"), "2026-09-14")

    def test_trade_detection(self):
        self.assertEqual(detect_trade("Drywall contractor"), "drywall")
        self.assertEqual(detect_trade("Glass & mirror shop"), "glazing")
        self.assertEqual(detect_trade("Fire protection service"), "fire_protection")
        self.assertEqual(detect_trade("", page="we install fire sprinkler systems. sprinkler design and fire sprinkler inspections"), "fire_protection")
        self.assertEqual(detect_trade("General contractor"), "")

    def test_leads_and_merge(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = LeadStore(str(Path(tmp) / "t.db"))
            for name in ("subs_sample.csv", "apollo_contacts_sample.csv"):
                for lead in read_leads(SAMPLES / name)[0]:
                    store.upsert(lead)
            self.assertEqual(len(store.all()), 7)
            lone_star = store.find("lonestarinteriors.example")
            self.assertEqual(lone_star.company, "Lone Star Interior Systems")
            self.assertEqual((lone_star.first_name, lone_star.employees, lone_star.trade), ("Rosa", 85, "drywall"))
            mesa = store.find("(303) 555-0146")
            self.assertEqual((mesa.first_name, mesa.employees, mesa.trade), ("Wade", 30, "electrical"))
            self.assertEqual(store.find("+15125550147").domain, "")  # Facebook page is not a website
            store.close()

    def test_apify_mapping(self):
        mapping = build_mapping(["title", "totalScore", "reviewsCount", "website", "categoryName"], LEAD_ALIASES)
        self.assertEqual(mapping["company"], "title")
        self.assertNotIn("title", mapping)


class PermitTests(unittest.TestCase):
    def test_contractor_names(self):
        self.assertEqual(contractor_key("Halvorsen Builders, Inc."), contractor_key("HALVORSEN BUILDERS INC"))
        self.assertEqual(contractor_key("Owner Builder"), "")
        self.assertEqual(display_name(["HALVORSEN BUILDERS INC"]), "Halvorsen Builders")
        self.assertEqual(display_name(["J&B CONSTRUCTION LLC"]), "J&B Construction")
        self.assertEqual(money_short(125_930_000), "$125.9M")

    def test_classification(self):
        self.assertTrue(classify_commercial(Permit(permit_type="Building Permit", description="Commercial tenant improvement")))
        self.assertTrue(classify_commercial(Permit(description="New 220-unit multifamily apartment building")))
        self.assertFalse(classify_commercial(Permit(description="Single family residence with attached garage", valuation=900_000)))
        self.assertFalse(classify_commercial(Permit(permit_type="Electrical Permit", description="office building", valuation=1e6)))
        self.assertTrue(classify_commercial(Permit(description="Non-residential alterations")))
        self.assertTrue(classify_commercial(Permit(description="Interior alterations", valuation=650_000)))
        self.assertFalse(classify_commercial(Permit(description="Interior alterations", valuation=90_000)))

    def test_leaderboard(self):
        stats = austin_stats()
        self.assertEqual(stats.permits, 14)
        self.assertEqual(money_short(stats.value), "$125.9M")
        self.assertEqual(stats.top_names(3), ["Northgate Commercial Builders", "Ironline Contractors", "Halvorsen Builders"])
        halvorsen = stats.leaders[2]
        self.assertEqual(halvorsen.permits, 3)  # three spellings grouped
        self.assertNotIn("Old Window Builders", [r.name for r in stats.leaders])  # outside the window
        self.assertNotIn("Sparkline Electric", [r.name for r in stats.leaders])  # trade permit

    def test_assign_market(self):
        markets = {"Austin": ["Austin", "Round Rock"]}
        self.assertEqual(assign_market("Round Rock", markets), "Austin")
        self.assertEqual(assign_market("Denver", markets), "Denver")

    def test_gap_audit(self):
        stats = austin_stats()
        with tempfile.TemporaryDirectory() as tmp:
            known = Path(tmp) / "known.txt"
            known.write_text("NORTHGATE COMMERCIAL BUILDERS, INC.\nCrestline Construction\nMarrow and Pike GC\n")
            rows = gap_rows(stats, read_known(known), n=7)
        self.assertEqual([r["invites_you"] for r in rows], ["yes", "no", "no", "no", "yes", "no", "yes"])
        text = gap_markdown(stats, rows, "Lone Star Interior Systems", AS_OF)
        self.assertIn("You're not on the bid list of 4 of the top 7 GCs.", text)
        self.assertIn("| 2 | Ironline Contractors | 1 | $27.0M |", text)


HOMEPAGE = """
<html><head><title>Lone Star Interior Systems</title><script>var x = "residential";</script></head><body>
<nav><a href="/projects/">Projects</a> <a href="/careers">Careers</a></nav>
<h1>Commercial drywall, metal stud framing and acoustical ceilings</h1>
<p>We partner with general contractors on tenant improvement, healthcare and K-12 school projects.
Certified WBE and HUB vendor. Our EMR is 0.71 and we carry $5M single bonding capacity.</p>
<p>Now hiring: drywall foremen and an estimator. <a href="mailto:bids@lonestar.example">Send us your bids</a></p>
</body></html>
"""


class ScannerTests(unittest.TestCase):
    def test_detect_signals(self):
        signals = detect_signals(HOMEPAGE, "lonestar.example")
        self.assertEqual(signals.trade, "drywall")
        self.assertGreaterEqual(signals.commercial_hits, 3)
        self.assertEqual(signals.residential_hits, 0)  # script text ignored
        self.assertIn("WBE", signals.certifications)
        self.assertTrue(signals.hiring and signals.has_portfolio and signals.mentions_safety and signals.mentions_bonding)
        self.assertEqual(signals.project_types, ("healthcare", "education"))
        self.assertEqual(signals.emails, ("bids@lonestar.example",))

    def test_residential_site(self):
        signals = detect_signals("<p>Residential painting for homeowners. Free estimate on your home's kitchen.</p>")
        self.assertGreater(signals.residential_hits, signals.commercial_hits)

    def test_scan_merges_certifications(self):
        lead = scan_lead(Lead(domain="lonestar.example", certifications="DBE"), lambda url: HOMEPAGE)
        self.assertEqual(lead.certifications, "DBE, WBE")
        self.assertEqual(lead.email, "bids@lonestar.example")


class ScoringAndSequenceTests(unittest.TestCase):
    def test_scoring(self):
        stats = austin_stats()
        strong, reasons = score_lead(sub(certifications="WBE", hiring=1), TARGETS, stats)
        weak, _ = score_lead(sub(commercial_hits=0, residential_hits=5, email="", employees=4), TARGETS, None)
        self.assertEqual(tier_for(strong), "A")
        self.assertLess(weak, 35)
        self.assertTrue(any("permit data" in r for r in reasons))

    def test_choose_sequence(self):
        stats = austin_stats()
        self.assertEqual(choose_sequence(sub(certifications="MBE"), stats), "certified-sub")
        self.assertEqual(choose_sequence(sub(), stats), "permit-pulse")
        self.assertEqual(choose_sequence(sub(hiring=1), None), "hiring")
        self.assertEqual(choose_sequence(sub(), None), "bid-chase")

    def test_variables_cover_every_sequence(self):
        sequences = load_sequences()
        self.assertEqual(set(sequences), {"certified-sub", "permit-pulse", "hiring", "bid-chase"})
        provided = set(lead_variables(sub(), CONFIG, austin_stats()))
        for sequence in sequences.values():
            self.assertLessEqual(sequence.variables(), provided, sequence.name)
            self.assertLessEqual(sequence.variables(), set(custom_columns()) | {"first_name"}, sequence.name)

    def test_render_without_gaps(self):
        stats = austin_stats()
        sequences = load_sequences()
        cases = [(sub(certifications="WBE"), stats), (sub(), stats), (sub(hiring=1, market="Denver", city="Denver"), None),
                 (sub(market="", city=""), None)]
        for lead, lead_stats in cases:
            personalize_leads([lead], {"austin": stats} if lead_stats else {})
            name = choose_sequence(lead, lead_stats)
            rendered, missing = render_sequence(sequences[name], lead_variables(lead, CONFIG, lead_stats))
            self.assertEqual(missing, [], name)
        day0 = render_sequence(sequences["permit-pulse"], lead_variables(sub(), CONFIG, stats))[0][0]
        self.assertEqual(day0[1], "Northgate Commercial Builders in Austin")
        self.assertIn("14 commercial building permits were issued in Austin over the last 90 days, about $125.9M", day0[2])


class FakeClient:
    def __init__(self, text="Saw Lone Star is WBE-certified, which matters on Austin's public work.", stop_reason="end_turn"):
        self.calls = []
        response = SimpleNamespace(stop_reason=stop_reason, content=[SimpleNamespace(type="text", text=text)])
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=lambda **kw: (self.calls.append(kw), response)[1]))


class PersonalizeTests(unittest.TestCase):
    def test_rules(self):
        stats = austin_stats()
        self.assertEqual(rule_opener(sub(certifications="DBE"), stats)[1], "certification")
        line, source = rule_opener(sub(), stats)
        self.assertEqual(source, "permits")
        self.assertIn("Northgate Commercial Builders pulled the most", line)
        self.assertEqual(rule_opener(sub(hiring=1), None)[1], "hiring")
        self.assertEqual(rule_opener(sub(project_types="healthcare, education"), None)[0],
                         "Saw Lone Star Interior Systems has done healthcare and education work around Austin.")

    def test_validate(self):
        self.assertIsNone(validate_opener("Great work!"))
        self.assertIsNone(validate_opener("Are you bidding much?"))

    @unittest.skipUnless(HAS_SDK, "anthropic SDK not installed (pip install -e '.[ai]')")
    def test_ai_request_shape_and_fallback(self):
        client = FakeClient()
        line = ai_opener(client, sub(certifications="WBE"), austin_stats(), "claude-opus-5-5", "low")
        self.assertTrue(line.startswith("Saw Lone Star"))
        request = client.calls[0]
        self.assertEqual((request["model"], request["fallbacks"], request["output_config"]),
                         ("claude-opus-5-5", "default", {"effort": "low"}))
        self.assertEqual(request["betas"], ["server-side-fallback-2026-07-01"])
        self.assertEqual(request["system"][0]["text"], SYSTEM_PROMPT)
        self.assertIn("top_general_contractors", request["messages"][0]["content"])
        lead = sub()
        counts = personalize_leads([lead], {}, use_ai=True, client=FakeClient(stop_reason="refusal"))
        self.assertEqual(counts, {"generic": 1})


class CliTests(unittest.TestCase):
    def run_cli(self, tmp, *argv) -> str:
        config_path = Path(tmp) / "config.toml"
        if not config_path.exists():
            config_path.write_text(
                f'[targeting]\nas_of = "{AS_OF.isoformat()}"\n[markets]\nAustin = ["Austin", "Round Rock", "Pflugerville"]\n'
            )
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            cli.main(["--db", str(Path(tmp) / "t.db"), "--config", str(config_path), *argv])
        return out.getvalue()

    def test_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = str(Path(tmp) / "out")
            text = self.run_cli(tmp, "permits", str(SAMPLES / "permits_sample.csv"), "--market", "Austin")
            self.assertIn("19 permits -> 15 commercial", text)  # one is outside the 90-day window
            self.assertIn("Northgate Commercial Builders, Ironline Contractors, Halvorsen Builders", text)

            text = self.run_cli(tmp, "import", str(SAMPLES / "subs_sample.csv"), str(SAMPLES / "apollo_contacts_sample.csv"))
            self.assertIn("Total: 7 new, 2 merged", text)
            self.run_cli(tmp, "score")
            self.run_cli(tmp, "personalize")

            preview = self.run_cli(tmp, "preview", "capcityglazing.example")  # Round Rock -> Austin market
            self.assertIn("Sequence: permit-pulse", preview)
            self.assertNotIn("{{", preview)
            self.assertIn("Sequence: bid-chase", self.run_cli(tmp, "preview", "mesaelectric.example"))

            self.run_cli(tmp, "export", "--out", out_dir, "--min-score", "0")
            rows = []
            for path in Path(out_dir).glob("instantly-*.csv"):
                with path.open() as handle:
                    rows += list(csv.DictReader(handle))
            self.assertTrue(rows)
            self.assertTrue(all(row["email"] and row["personalization"] for row in rows))
            permit_rows = [r for r in rows if r["sequence"] == "permit-pulse"]
            self.assertTrue(permit_rows and permit_rows[0]["top_gc_1"] == "Northgate Commercial Builders")

            self.assertIn("leads ->", self.run_cli(tmp, "callsheet", "--out", out_dir, "--n", "5"))
            known = Path(tmp) / "known.txt"
            known.write_text("Ironline Contractors\n")
            text = self.run_cli(tmp, "gap-audit", "--market", "austin", "--company", "Lone Star", "--known", str(known),
                                "--out", out_dir, "--n", "5")
            self.assertIn("4 of the top 5 GCs don't invite Lone Star yet", text)
            self.assertTrue((Path(out_dir) / "gc-targets-austin-lone-star.csv").exists())

            self.run_cli(tmp, "call", "lonestarinteriors.example", "--outcome", "booked")
            self.assertIn("Dials: 1", self.run_cli(tmp, "stats"))

    def test_export_skips_suppressed(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = LeadStore(str(Path(tmp) / "t.db"))
            store.save(sub(id="a", score=80))
            store.save(sub(id="b", domain="b.example", phone="+15125550100", score=80, status="do_not_contact"))
            store.save(sub(id="c", domain="c.example", phone="+15125550101", score=10))
            written = export_leads(store, copy.deepcopy(CONFIG), Path(tmp) / "out")
            self.assertEqual(sum(count for _, count in written.values()), 1)
            self.assertEqual(store.get("a").status, "in_sequence")
            store.close()


if __name__ == "__main__":
    unittest.main()

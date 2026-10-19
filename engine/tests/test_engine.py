import contextlib
import csv
import io
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from bookedout import cli
from bookedout.config import load_config
from bookedout.db import LeadStore
from bookedout.export import custom_columns, export_leads
from bookedout.importer import build_mapping, clean_company, normalize_domain, normalize_phone, read_leads
from bookedout.models import Lead
from bookedout.personalize import SYSTEM_PROMPT, ai_opener, personalize_leads, rule_opener, validate_opener
from bookedout.scanner import detect_signals, scan_lead
from bookedout.scoring import score_lead, tier_for
from bookedout.sequences import choose_sequence, lead_variables, load_sequences, render_sequence
from bookedout.weather import apply_weather, extremes

try:
    import anthropic  # noqa: F401
    HAS_SDK = True
except ImportError:
    HAS_SDK = False

SAMPLES = Path(__file__).resolve().parent.parent / "sample_data"
CONFIG = load_config("/nonexistent")  # defaults only


def full_lead(**overrides) -> Lead:
    lead = Lead(
        id="abc", company="Northstar Heating & Air, LLC", first_name="Dana", email="dana@northstar.example",
        phone="+16125550101", website="https://northstar.example", domain="northstar.example",
        city="Minneapolis", state="MN", lat=44.97, lon=-93.26, rating=4.8, reviews=412, category="HVAC contractor",
        scanned_at="2026-10-19T00:00:00+00:00", site_ok=1,
    )
    for key, value in overrides.items():
        setattr(lead, key, value)
    return lead


class ImporterTests(unittest.TestCase):
    def test_normalizers(self):
        self.assertEqual(normalize_phone("(612) 555-0101"), "+16125550101")
        self.assertEqual(normalize_phone("+1 952 555 0103"), "+19525550103")
        self.assertEqual(normalize_domain("https://www.Example.com/contact?x=1"), "example.com")
        self.assertEqual(normalize_domain("https://facebook.com/riverbend"), "")
        self.assertEqual(clean_company("Smith Heating & Air, LLC | Furnace Repair"), "Smith Heating & Air")
        self.assertEqual(clean_company("Lakeside Comfort Systems Inc."), "Lakeside Comfort Systems")

    def test_outscraper_sample(self):
        leads, mapping, fmt = read_leads(SAMPLES / "outscraper_sample.csv")
        self.assertEqual(fmt, "outscraper")
        self.assertEqual(mapping["company"], "name")
        self.assertEqual(mapping["website"], "site")
        northstar = leads[0]
        self.assertEqual(northstar.company, "Northstar Heating & Air")
        self.assertEqual(northstar.domain, "northstarheating.example")
        self.assertEqual(northstar.email, "office@northstarheating.example")
        self.assertEqual(northstar.reviews, 412)
        self.assertAlmostEqual(northstar.lat, 44.9778)
        riverbend = next(l for l in leads if l.company == "Riverbend Plumbing")
        self.assertEqual(riverbend.domain, "")  # Facebook page is not a website

    def test_apify_title_is_company(self):
        mapping = build_mapping(["title", "totalScore", "reviewsCount", "website", "phone", "categoryName"])
        self.assertEqual(mapping["company"], "title")
        self.assertNotIn("title", mapping)
        self.assertEqual(mapping["rating"], "totalScore")

    def test_merge_contacts_onto_companies(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = LeadStore(str(Path(tmp) / "t.db"))
            for path in ("outscraper_sample.csv", "apollo_contacts_sample.csv"):
                for lead in read_leads(SAMPLES / path)[0]:
                    store.upsert(lead)
            leads = store.all()
            self.assertEqual(len(leads), 7)  # Apollo rows merged, not duplicated
            northstar = store.find("northstarheating.example")
            self.assertEqual(northstar.first_name, "Dana")
            self.assertEqual(northstar.email, "office@northstarheating.example")  # existing value kept
            summit = store.find("(303) 555-0107")
            self.assertEqual(summit.first_name, "Marcus")
            self.assertEqual(summit.email, "marcus@summitheatingair.example")  # blank filled
            store.close()


HOMEPAGE = """
<html><head>
<script async src="https://www.googletagmanager.com/gtag/js?id=AW-123456789"></script>
<script src="//cdn.callrail.com/companies/1/abc/12/swap.js"></script>
</head><body>
<h1>24/7 Emergency Furnace Repair</h1>
<p>Ask about our Comfort Club maintenance plan and 0% APR financing.</p>
<a href="mailto:info@northstar.example">Email us</a> <img src="logo@2x.png">
</body></html>
"""


class ScannerTests(unittest.TestCase):
    def test_detect_signals(self):
        signals = detect_signals(HOMEPAGE, "northstar.example")
        self.assertTrue(signals.runs_google_ads)
        self.assertEqual(signals.call_tracking, "CallRail")
        self.assertEqual(signals.chat_vendor, "")
        self.assertEqual(signals.booking_vendor, "")
        self.assertTrue(signals.mentions_24_7)
        self.assertTrue(signals.has_financing)
        self.assertTrue(signals.has_membership)
        self.assertEqual(signals.emails, ("info@northstar.example",))

    def test_vendor_detection(self):
        html = '<script src="https://connect.podium.com/widget.js"></script><a href="https://book.housecallpro.com/x">Book</a>'
        signals = detect_signals(html)
        self.assertEqual(signals.chat_vendor, "Podium")
        self.assertEqual(signals.booking_vendor, "Housecall Pro")
        self.assertFalse(signals.runs_google_ads)

    def test_scan_lead_falls_back_to_contact_page(self):
        pages = {
            "https://shop.example/": "<html>Heating and cooling</html>",
            "https://shop.example/contact/": "<p>owner@shop.example</p>",
        }

        def fetcher(url):
            if url not in pages:
                raise OSError("404")
            return pages[url]

        lead = scan_lead(Lead(domain="shop.example"), fetcher)
        self.assertEqual(lead.site_ok, 1)
        self.assertEqual(lead.email, "owner@shop.example")
        dead = scan_lead(Lead(domain="dead.example"), fetcher)
        self.assertEqual(dead.site_ok, 0)


PERIODS = [
    {"name": "Tonight", "isDaytime": False, "temperature": 30, "temperatureUnit": "F"},
    {"name": "Thursday", "isDaytime": True, "temperature": 41, "temperatureUnit": "F"},
    {"name": "Thursday Night", "isDaytime": False, "temperature": -8, "temperatureUnit": "C"},
    {"name": "Friday", "isDaytime": True, "temperature": 35, "temperatureUnit": "F"},
]


class WeatherTests(unittest.TestCase):
    def test_extremes(self):
        self.assertEqual(extremes(PERIODS), (18, "Thursday Night", 41, "Thursday"))

    def test_apply_weather_groups_cells(self):
        calls = []

        def getter(url, user_agent):
            calls.append(url)
            if "/points/" in url:
                return {"properties": {"forecast": "https://api.weather.gov/gridpoints/MPX/1,1/forecast"}}
            return {"properties": {"periods": PERIODS}}

        leads = [full_lead(id=str(i), lat=44.97 + i * 0.001, lon=-93.26) for i in range(5)] + [Lead(id="nocoords")]
        updated, failed = apply_weather(leads, "test", getter)
        self.assertEqual((updated, failed), (5, 0))
        self.assertEqual(len(calls), 2)  # one cell -> one points call + one forecast call
        self.assertEqual(leads[0].forecast_low_f, 18)
        self.assertIsNone(leads[-1].forecast_low_f)


class ScoringTests(unittest.TestCase):
    def test_audit_and_ads_rank_higher(self):
        base, _ = score_lead(full_lead())
        hot, reasons = score_lead(full_lead(audit_result="voicemail", runs_google_ads=1))
        self.assertGreater(hot, base)
        self.assertTrue(any("audit" in r for r in reasons))
        self.assertEqual(tier_for(hot), "A")

    def test_franchise_penalty(self):
        franchise, _ = score_lead(full_lead(company="One Hour Heating & Air Conditioning of Testville"))
        indie, _ = score_lead(full_lead())
        self.assertLess(franchise, indie - 20)


class SequenceTests(unittest.TestCase):
    def test_every_variable_is_provided(self):
        sequences = load_sequences()
        self.assertEqual(set(sequences), {"after-hours", "cold-snap", "heat-wave", "paid-clicks", "estimate-recovery"})
        provided = set(lead_variables(full_lead(), CONFIG))
        for sequence in sequences.values():
            self.assertLessEqual(sequence.variables(), provided, sequence.name)
            self.assertLessEqual(sequence.variables(), set(custom_columns()) | {"first_name"}, sequence.name)

    def test_choose_sequence_priority(self):
        self.assertEqual(choose_sequence(full_lead(audit_result="voicemail", forecast_low_f=5)), "after-hours")
        self.assertEqual(choose_sequence(full_lead(forecast_low_f=12, forecast_low_when="Thursday Night")), "cold-snap")
        self.assertEqual(choose_sequence(full_lead(forecast_high_f=101)), "heat-wave")
        self.assertEqual(choose_sequence(full_lead(runs_google_ads=1)), "paid-clicks")
        self.assertEqual(choose_sequence(full_lead(runs_google_ads=1, chat_vendor="Podium")), "estimate-recovery")

    def test_render_has_no_gaps_for_chosen_sequence(self):
        sequences = load_sequences()
        cases = [
            full_lead(audit_result="voicemail", audit_time="Tuesday at 7:42pm"),
            full_lead(forecast_low_f=12, forecast_low_when="Thursday Night"),
            full_lead(forecast_high_f=101, forecast_high_when="Saturday"),
            full_lead(runs_google_ads=1),
            full_lead(),
        ]
        for lead in cases:
            personalize_leads([lead])
            name = choose_sequence(lead)
            rendered, missing = render_sequence(sequences[name], lead_variables(lead, CONFIG))
            self.assertEqual(missing, [], name)
            self.assertNotIn("{{", "".join(body for _, _, body in rendered))
        day0 = render_sequence(sequences["after-hours"], lead_variables(cases[0], CONFIG))[0][0]
        self.assertIn("I called Northstar Heating & Air on Tuesday at 7:42pm and it went to voicemail.", day0[2])
        self.assertEqual(day0[1], "Northstar Heating & Air after hours")


class FakeClient:
    def __init__(self, text="Called Northstar on Tuesday at 7:42pm and it went straight to voicemail.", stop_reason="end_turn"):
        self.calls = []
        response = SimpleNamespace(stop_reason=stop_reason, content=[
            SimpleNamespace(type="thinking", thinking=""),
            SimpleNamespace(type="text", text=text),
        ])
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=lambda **kw: (self.calls.append(kw), response)[1]))


class PersonalizeTests(unittest.TestCase):
    def test_rule_openers(self):
        self.assertEqual(rule_opener(full_lead(audit_result="no_answer"))[1], "audit")
        self.assertIn("drops to 12°F Thursday night", rule_opener(full_lead(forecast_low_f=12, forecast_low_when="Thursday Night"))[0])
        self.assertEqual(rule_opener(full_lead())[1], "reviews")
        self.assertEqual(rule_opener(full_lead(reviews=3, city=""))[1], "generic")

    def test_validate_opener(self):
        self.assertIsNone(validate_opener("Great job!"))
        self.assertIsNone(validate_opener("How are you?"))
        self.assertEqual(validate_opener('  "Saw the snow coming to Minneapolis."  '), "Saw the snow coming to Minneapolis.")

    @unittest.skipUnless(HAS_SDK, "anthropic SDK not installed (pip install -e '.[ai]')")
    def test_ai_opener_request_shape(self):
        client = FakeClient()
        line = ai_opener(client, full_lead(audit_result="voicemail"), "claude-opus-5-5", "low", 25, 95)
        self.assertTrue(line.startswith("Called Northstar"))
        request = client.calls[0]
        self.assertEqual(request["model"], "claude-opus-5-5")
        self.assertEqual(request["fallbacks"], "default")
        self.assertEqual(request["betas"], ["server-side-fallback-2026-07-01"])
        self.assertEqual(request["output_config"], {"effort": "low"})
        self.assertEqual(request["system"][0]["text"], SYSTEM_PROMPT)
        self.assertIn('"after_hours_test_call"', request["messages"][0]["content"])

    @unittest.skipUnless(HAS_SDK, "anthropic SDK not installed (pip install -e '.[ai]')")
    def test_ai_falls_back_to_rules(self):
        for client in (FakeClient(stop_reason="refusal"), FakeClient(text="Amazing work, Dana!")):
            lead = full_lead()
            counts = personalize_leads([lead], use_ai=True, client=client)
            self.assertEqual(counts, {"reviews": 1})
            self.assertEqual(lead.personalization_source, "reviews")


class ExportAndCliTests(unittest.TestCase):
    def run_cli(self, db, *argv) -> str:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            cli.main(["--db", db, "--config", "/nonexistent", *argv])
        return out.getvalue()

    def test_end_to_end_without_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "leads.db")
            out_dir = str(Path(tmp) / "out")
            text = self.run_cli(db, "import", str(SAMPLES / "outscraper_sample.csv"), str(SAMPLES / "apollo_contacts_sample.csv"))
            self.assertIn("Total: 7 new, 2 merged", text)

            self.run_cli(db, "audit", "lakesidecomfort.example", "--result", "voicemail", "--at", "Tuesday at 7:42pm")
            self.assertIn("Scored 7 leads", self.run_cli(db, "score"))
            self.run_cli(db, "personalize")

            preview = self.run_cli(db, "preview", "lakesidecomfort.example")
            self.assertIn("Sequence: after-hours", preview)
            self.assertNotIn("{{", preview)

            text = self.run_cli(db, "export", "--out", out_dir, "--min-score", "0")
            files = sorted(Path(out_dir).glob("instantly-*.csv"))
            self.assertTrue(files, text)
            exported_emails = set()
            for path in files:
                with path.open() as handle:
                    rows = list(csv.DictReader(handle))
                for row in rows:
                    exported_emails.add(row["email"])
                    self.assertTrue(row["personalization"])
                    self.assertTrue(row["sender_first_name"])
            # Leads without an email are never exported.
            self.assertNotIn("", exported_emails)
            self.assertIn("No exportable leads", self.run_cli(db, "export", "--out", out_dir, "--min-score", "0"))

            sheet = self.run_cli(db, "callsheet", "--out", out_dir, "--n", "5")
            self.assertIn("5 leads", sheet)
            md = next(Path(out_dir).glob("callsheet-*.md")).read_text()
            self.assertIn("Opener A (after-hours audit)", md)

            self.run_cli(db, "call", "badgermech.example", "--outcome", "booked", "--note", "Thu 8am demo")
            self.run_cli(db, "call", "summitheatingair.example", "--outcome", "conversation")
            stats = self.run_cli(db, "stats")
            self.assertIn("booked", stats)
            self.assertIn("Dials: 2", stats)

            audit_csv = Path(tmp) / "audit.csv"
            self.run_cli(db, "audit-list", "--out", str(audit_csv), "--n", "3")
            with audit_csv.open() as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 3)
            rows[0]["result"], rows[0]["called_at"] = "no answer", "Wednesday at 8:05pm"
            with audit_csv.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            self.assertIn("Recorded 1 audits", self.run_cli(db, "audit-import", str(audit_csv)))

    def test_export_skips_suppressed(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = LeadStore(str(Path(tmp) / "t.db"))
            store.save(full_lead(id="a", email="a@x.example", score=80))
            store.save(full_lead(id="b", email="b@x.example", domain="b.example", phone="+16125550199", score=80, status="do_not_contact"))
            store.save(full_lead(id="c", email="c@x.example", domain="c.example", phone="+16125550198", score=10))
            written = export_leads(store, CONFIG, Path(tmp) / "out")
            self.assertEqual(sum(count for _, count in written.values()), 1)
            self.assertEqual(store.get("a").status, "in_sequence")
            store.close()


if __name__ == "__main__":
    unittest.main()

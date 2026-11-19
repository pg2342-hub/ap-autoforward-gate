import subprocess
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import gate  # noqa: E402


def run(data, **kw):
    jobs, vendors, lines, pilot, invoices = gate.load(data)
    gate.tag_invoices(invoices, jobs, vendors, lines, date.fromisoformat(pilot["pilot_start"]))
    end = date.fromisoformat(pilot["gate_window_end"])
    g = gate.job_gate(invoices, jobs, end, kw.get("min_invoices", 20), kw.get("threshold", 0.90))
    return g, gate.route(invoices, g, end)


class SampleTests(unittest.TestCase):
    def test_five_of_eight_jobs_ready(self):
        g, _ = run(ROOT / "data")
        ready = sorted(j for j, v in g.items() if v["decision"] == "AUTO-FORWARD")
        self.assertEqual(ready, ["J101", "J102", "J103", "J105", "J107"])

    def test_planted_exceptions_stay_with_ap(self):
        _, routed = run(ROOT / "data")
        dest = {inv.invoice_id: d for inv, d in routed}
        for iid in ("INV-9001", "INV-9002", "INV-9003", "INV-9004", "INV-9005", "INV-9006", "INV-9007"):
            self.assertEqual(dest[iid], "AP REVIEW", iid)

    def test_unknown_tax_status_job_never_auto_forwards(self):
        _, routed = run(ROOT / "data")
        self.assertTrue(all(d == "AP REVIEW" for inv, d in routed if inv.agave["job_id"] == "J107"))

    def test_no_tagged_invoice_auto_forwards(self):
        _, routed = run(ROOT / "data")
        self.assertFalse([inv.invoice_id for inv, d in routed if inv.tags and d != "AP REVIEW"])

    def test_raising_the_bar_drops_job_j103(self):
        g, _ = run(ROOT / "data", threshold=0.95)
        self.assertNotEqual(g["J103"]["decision"], "AUTO-FORWARD")

    def test_sample_is_reproducible(self):
        before = (ROOT / "data" / "invoices.csv").read_bytes()
        subprocess.run([sys.executable, str(ROOT / "data" / "generate_sample.py")], check=True, capture_output=True)
        self.assertEqual(before, (ROOT / "data" / "invoices.csv").read_bytes())


class EvalTests(unittest.TestCase):
    def test_eval_set_passes(self):
        r = subprocess.run([sys.executable, str(ROOT / "eval" / "run_eval.py")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("30 of 30 cases match; unsafe auto-forwards: 0", r.stdout)


if __name__ == "__main__":
    unittest.main()

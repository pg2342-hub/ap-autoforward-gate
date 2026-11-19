"""Run the gate on the hand-built eval set and compare with the hand-written labels.

Pass bar: 30 of 30 routes and tag sets match, and zero unsafe misses (an invoice labeled
AP REVIEW that the gate auto-forwards).
"""
import csv
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
import gate  # noqa: E402

jobs, vendors, lines, pilot, invoices = gate.load(HERE / "data")
gate.tag_invoices(invoices, jobs, vendors, lines, date.fromisoformat(pilot["pilot_start"]))
g = gate.job_gate(invoices, jobs, date.fromisoformat(pilot["gate_window_end"]), 20, 0.90)
routed = {inv.invoice_id: (inv, dest) for inv, dest in gate.route(invoices, g, date.fromisoformat(pilot["gate_window_end"]))}

expect = list(csv.DictReader(open(HERE / "expected.csv")))
ok = unsafe = 0
for e in expect:
    inv, dest = routed[e["invoice_id"]]
    want_tags = set(filter(None, e["expected_tags"].split(";")))
    good = dest == e["expected_route"] and set(inv.tags) == want_tags
    ok += good
    if e["expected_route"] == "AP REVIEW" and dest != "AP REVIEW":
        unsafe += 1
    if not good:
        print(f"MISMATCH {e['invoice_id']}: got {dest} {sorted(inv.tags)}, want {e['expected_route']} {sorted(want_tags)}")
print(f"Job gate: " + ", ".join(f"{j} {v['ok']}/{v['n']} {v['decision']}" for j, v in g.items()))
print(f"{ok} of {len(expect)} cases match; unsafe auto-forwards: {unsafe}")
sys.exit(0 if ok == len(expect) and unsafe == 0 else 1)

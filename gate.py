"""AP auto-forward gate for an Agave AP Automation pilot.

Reads an export of Agave's suggested coding and AP's final coding, then answers two
questions a CSE has to answer at the end of week 2 of an onboarding:

1. Which jobs have earned auto-forward to the PM (AP accepted Agave's coding unchanged
   on at least 90% of at least 20 invoices)?
2. Which invoices must AP still clear before sync, even on those jobs, and why?

Usage:
    python gate.py                      # runs on the bundled synthetic sample in data/
    python gate.py --data path/to/export --min-invoices 20 --threshold 0.90
    python gate.py --out report.md      # also writes a markdown report

Standard library only (Python 3.9+).
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

CODING_FIELDS = ("job_id", "cost_code", "cost_type", "commitment_id")

# Tag codes. Every tag puts the invoice in AP's queue before sync, whatever the job's gate status.
TAG_TEXT = {
    "NO_COMMITMENT": "No PO or subcontract match",
    "OVERBILL": "Would bill the contract line past its scheduled value",
    "UNALLOCATED": "Coded lines do not add up to the invoice total (net of tax)",
    "NEW_VENDOR": "Vendor added to the vendor master after the pilot started",
    "DUPLICATE": "Same vendor and invoice number, or same vendor and amount within 14 days",
    "TAX_NO_TAX_ON_MATERIALS": "Materials invoice with no sales tax: check the exemption or accrue use tax",
    "TAX_SUB_CHARGED_ON_CI": "Subcontractor charged sales tax on a capital improvement job (ST-124 on file)",
    "TAX_STATUS_UNKNOWN": "Job tax status (capital improvement or repair) not recorded at kickoff",
}


@dataclass
class Invoice:
    invoice_id: str
    received: date
    vendor_id: str
    vendor_invoice_no: str
    commitment_id: str
    commitment_line: str
    invoice_total: float
    tax_amount: float
    allocated: float
    agave: dict
    ap: dict  # AP's final coding; empty for invoices AP has not reviewed
    tags: list = field(default_factory=list)

    @property
    def job_id(self) -> str:
        # The job an invoice belongs to is the one AP confirmed, else Agave's suggestion.
        return self.ap.get("job_id") or self.agave["job_id"]

    @property
    def reviewed(self) -> bool:
        return bool(self.ap.get("job_id"))

    @property
    def accepted_unchanged(self) -> bool:
        return all(self.agave[f] == self.ap[f] for f in CODING_FIELDS)

    @property
    def net(self) -> float:
        return round(self.invoice_total - self.tax_amount, 2)


def _d(s: str) -> date:
    return date.fromisoformat(s)


def _read(path: Path) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def load(data_dir: Path):
    jobs = {r["job_id"]: r for r in _read(data_dir / "jobs.csv")}
    vendors = {r["vendor_id"]: r for r in _read(data_dir / "vendors.csv")}
    lines = {(r["commitment_id"], r["line"]): r for r in _read(data_dir / "commitment_lines.csv")}
    pilot = _read(data_dir / "pilot.csv")[0]
    invoices = []
    for r in _read(data_dir / "invoices.csv"):
        invoices.append(Invoice(
            invoice_id=r["invoice_id"], received=_d(r["received"]), vendor_id=r["vendor_id"],
            vendor_invoice_no=r["vendor_invoice_no"], commitment_id=r["commitment_id"],
            commitment_line=r["commitment_line"], invoice_total=float(r["invoice_total"]),
            tax_amount=float(r["tax_amount"]), allocated=float(r["allocated"]),
            agave={f: r[f"agave_{f}"] for f in CODING_FIELDS},
            ap={f: r[f"ap_{f}"] for f in CODING_FIELDS} if r["ap_job_id"] else {},
        ))
    invoices.sort(key=lambda i: (i.received, i.invoice_id))
    return jobs, vendors, lines, pilot, invoices


def tag_invoices(invoices, jobs, vendors, lines, pilot_start: date) -> None:
    """Apply the always-to-AP rules in receipt order (overbilling and duplicates depend on order)."""
    billed = {k: float(v["billed_to_date"]) for k, v in lines.items()}
    seen_numbers: set = set()
    seen_amounts: dict = defaultdict(list)
    for inv in invoices:
        tags = []
        job = jobs.get(inv.job_id, {})
        vendor = vendors[inv.vendor_id]

        num_key = (inv.vendor_id, inv.vendor_invoice_no.strip().upper())
        recent = [d for d in seen_amounts[(inv.vendor_id, inv.invoice_total)]
                  if inv.received - d <= timedelta(days=14)]
        if num_key in seen_numbers or recent:
            tags.append("DUPLICATE")
        seen_numbers.add(num_key)
        seen_amounts[(inv.vendor_id, inv.invoice_total)].append(inv.received)
        is_dup = "DUPLICATE" in tags

        if not inv.commitment_id:
            tags.append("NO_COMMITMENT")
        else:
            key = (inv.commitment_id, inv.commitment_line)
            line = lines.get(key)
            if line is None:
                tags.append("NO_COMMITMENT")
            else:
                if billed[key] + inv.net > float(line["scheduled_value"]) + 0.005:
                    tags.append("OVERBILL")
                if not is_dup:  # a repeat bill is not new billing on the line
                    billed[key] += inv.net

        if abs(inv.net - inv.allocated) > 0.005:
            tags.append("UNALLOCATED")

        if _d(vendor["added_on"]) >= pilot_start:
            tags.append("NEW_VENDOR")

        status = job.get("tax_status", "unknown")
        if status not in ("capital_improvement", "repair"):
            tags.append("TAX_STATUS_UNKNOWN")
        else:
            if vendor["vendor_type"] == "supplier" and inv.tax_amount == 0:
                tags.append("TAX_NO_TAX_ON_MATERIALS")
            if (vendor["vendor_type"] == "subcontractor" and status == "capital_improvement"
                    and inv.tax_amount > 0):
                tags.append("TAX_SUB_CHARGED_ON_CI")
        inv.tags = tags


def job_gate(invoices, jobs, window_end: date, min_invoices: int, threshold: float):
    """Per job: accepted-unchanged rate on AP-reviewed invoices received by window_end."""
    out = {}
    for job_id in jobs:
        checked = [i for i in invoices if i.reviewed and i.job_id == job_id and i.received <= window_end]
        n = len(checked)
        ok = sum(i.accepted_unchanged for i in checked)
        misses = defaultdict(int)
        for i in checked:
            for f in CODING_FIELDS:
                if i.agave[f] != i.ap[f]:
                    misses[f] += 1
        rate = ok / n if n else 0.0
        if n < min_invoices:
            decision = "STAY ON FULL REVIEW (too few invoices)"
        elif rate >= threshold:
            decision = "AUTO-FORWARD"
        else:
            decision = "STAY ON FULL REVIEW (below bar)"
        out[job_id] = {"n": n, "ok": ok, "rate": rate, "misses": dict(misses), "decision": decision}
    return out


def route(invoices, gate, window_end: date):
    """Route invoices received after the window: auto-forward only on a ready job with no tags."""
    routed = []
    for inv in invoices:
        if inv.received <= window_end:
            continue
        ready = gate.get(inv.agave["job_id"], {}).get("decision") == "AUTO-FORWARD"
        if ready and not inv.tags:
            routed.append((inv, "AUTO-FORWARD TO PM"))
        else:
            routed.append((inv, "AP REVIEW"))
    return routed


def report(jobs, gate, routed, invoices, args) -> str:
    L = []
    L.append("# AP auto-forward gate report\n")
    L.append(f"Gate: at least {args.threshold:.0%} of at least {args.min_invoices} AP-checked invoices "
             f"accepted unchanged on job, cost code, cost type, and commitment.\n")
    L.append("## 1. Which jobs are ready for auto-forward\n")
    L.append("| Job | Tax status | Checked | Accepted unchanged | Rate | Most-corrected field | Decision |")
    L.append("|---|---|--:|--:|--:|---|---|")
    for job_id, g in gate.items():
        worst = max(g["misses"], key=g["misses"].get) if g["misses"] else "-"
        L.append(f"| {job_id} {jobs[job_id]['name']} | {jobs[job_id]['tax_status']} | {g['n']} | {g['ok']} | "
                 f"{g['rate']:.0%} | {worst} | {g['decision']} |")
    ready = sum(g["decision"] == "AUTO-FORWARD" for g in gate.values())
    L.append(f"\n{ready} of {len(gate)} jobs ready.\n")

    L.append("## 2. Invoices after the window: where each one goes\n")
    auto = [r for r in routed if r[1].startswith("AUTO")]
    L.append(f"{len(auto)} of {len(routed)} invoices auto-forward to the PM; "
             f"{len(routed) - len(auto)} need AP before sync.\n")
    counts = defaultdict(int)
    for inv, dest in routed:
        for t in inv.tags:
            counts[t] += 1
    L.append("| Reason AP clears an invoice before sync | Invoices |")
    L.append("|---|--:|")
    for t, n in sorted(counts.items(), key=lambda x: -x[1]):
        L.append(f"| {TAG_TEXT[t]} | {n} |")
    not_ready = sum(1 for inv, dest in routed if dest == "AP REVIEW" and not inv.tags)
    L.append(f"| Job not yet on auto-forward (no other reason) | {not_ready} |")

    L.append("\n## 3. AP queue (invoices AP clears before sync, and why)\n")
    L.append("| Invoice | Received | Job | Vendor | Total | Reasons |")
    L.append("|---|---|---|---|--:|---|")
    for inv, dest in routed:
        if dest == "AP REVIEW":
            why = "; ".join(TAG_TEXT[t] for t in inv.tags) or "Job not yet on auto-forward"
            L.append(f"| {inv.invoice_id} | {inv.received} | {inv.agave['job_id']} | {inv.vendor_id} | "
                     f"{inv.invoice_total:,.2f} | {why} |")
    return "\n".join(L) + "\n"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", default=str(Path(__file__).parent / "data"))
    p.add_argument("--min-invoices", type=int, default=20)
    p.add_argument("--threshold", type=float, default=0.90)
    p.add_argument("--out", help="write the markdown report here")
    args = p.parse_args(argv)
    jobs, vendors, lines, pilot, invoices = load(Path(args.data))
    start, window_end = _d(pilot["pilot_start"]), _d(pilot["gate_window_end"])
    tag_invoices(invoices, jobs, vendors, lines, start)
    gate = job_gate(invoices, jobs, window_end, args.min_invoices, args.threshold)
    routed = route(invoices, gate, window_end)
    text = report(jobs, gate, routed, invoices, args)
    if args.out:
        Path(args.out).write_text(text)
    # Console: sections 1 and 2 only; the full AP queue goes to --out.
    print(text.split("## 3.")[0].rstrip())
    return gate, routed


if __name__ == "__main__":
    main()

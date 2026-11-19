"""Generate the bundled SYNTHETIC sample: a retail and hospitality fit-out GC on Sage 300 CRE.

Nothing here is real customer data. Job names, vendors, contracts, amounts, and coding
errors are invented so the gate can be shown end to end. Re-running with the same seed
produces the same files.
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).parent
rng = random.Random(20261207)
PILOT_START = date(2026, 12, 7)          # Monday of week 1
WINDOW_END = date(2026, 12, 18)          # end of week 2: the gate is decided on this window
PILOT_END = date(2027, 1, 1)             # end of week 4
TAX_RATE = 0.08875                        # NYC combined sales tax rate on materials

JOBS = [  # job_id, name, tax status, invoices in weeks 1-2, Agave suggestions AP changed, invoices in weeks 3-4
    ("J101", "Apparel flagship fit-out", "capital_improvement", 30, 1, 16),
    ("J102", "Restaurant fit-out", "capital_improvement", 26, 1, 14),
    ("J103", "Hospitality venue renovation", "capital_improvement", 24, 2, 14),
    ("J104", "Store refresh (repair work)", "repair", 22, 3, 12),
    ("J105", "Department store shop-in-shop", "capital_improvement", 25, 1, 14),
    ("J106", "Fast-casual restaurant (legacy cost codes)", "capital_improvement", 28, 7, 15),
    ("J107", "Showroom build-out", "unknown", 21, 1, 12),
    ("J108", "Store maintenance (repair work)", "repair", 9, 0, 6),
]
COST_CODES = {  # code: (description, typical vendor type)
    "01-500": ("Temporary facilities", "supplier"),
    "06-100": ("Rough carpentry", "supplier"),
    "08-710": ("Door hardware", "supplier"),
    "09-250": ("Gypsum board", "subcontractor"),
    "09-650": ("Resilient flooring", "subcontractor"),
    "09-900": ("Painting", "subcontractor"),
    "12-300": ("Millwork", "subcontractor"),
    "23-000": ("HVAC", "subcontractor"),
    "26-050": ("Electrical", "subcontractor"),
}
SUPPLIERS = ["V201 Metro Lumber Supply", "V202 Five Boroughs Hardware", "V203 Tri-State Rentals",
             "V204 Hudson Drywall Supply"]
SUBS = ["V301 Ironbound Drywall", "V302 Harbor Flooring", "V303 Northside Painting",
        "V304 Atlas Millwork", "V305 Empire Mechanical", "V306 Brightline Electric"]
NEW_VENDOR = "V399 Quickfix Glass"         # added to the vendor master after the pilot started

sub_for_code = {"09-250": "V301", "09-650": "V302", "09-900": "V303", "12-300": "V304",
                "23-000": "V305", "26-050": "V306"}
sup_codes = ["01-500", "06-100", "08-710"]


def money(lo, hi):
    return round(rng.uniform(lo, hi), 2)


def build():
    vendors = [{"vendor_id": v.split()[0], "name": " ".join(v.split()[1:]), "vendor_type": "supplier",
                "added_on": "2019-03-01"} for v in SUPPLIERS]
    vendors += [{"vendor_id": v.split()[0], "name": " ".join(v.split()[1:]), "vendor_type": "subcontractor",
                 "added_on": "2018-06-15"} for v in SUBS]
    vendors.append({"vendor_id": "V399", "name": "Quickfix Glass", "vendor_type": "supplier",
                    "added_on": "2026-12-21"})

    lines, invoices = [], []
    seq = 0
    for job_id, name, status, n_win, n_wrong, n_after in JOBS:
        # One subcontract per sub code and one PO per supplier code, per job.
        commitments = {}
        for code, (desc, vtype) in COST_CODES.items():
            vid = sub_for_code.get(code) or SUPPLIERS[sup_codes.index(code)].split()[0]
            cid = f"{'SC' if vtype == 'subcontractor' else 'PO'}-{job_id[1:]}-{code[:2]}{code[3:]}"
            sv = money(40000, 180000) if vtype == "subcontractor" else money(8000, 30000)
            commitments[code] = (cid, vid, vtype, sv)
            lines.append({"commitment_id": cid, "line": "1", "job_id": job_id, "vendor_id": vid,
                          "description": desc, "cost_code": code,
                          "cost_type": "S" if vtype == "subcontractor" else "M",
                          "scheduled_value": f"{sv:.2f}", "billed_to_date": f"{sv * rng.uniform(0.1, 0.4):.2f}"})

        def make(day, reviewed, wrong_field=None, **over):
            nonlocal seq
            seq += 1
            code = over.pop("code", rng.choice(list(COST_CODES)))
            cid, vid, vtype, sv = commitments[code]
            vtype = over.pop("vtype", vtype)
            vid = over.pop("vid", vid)
            net = money(900, 9000) if vtype == "subcontractor" else money(150, 2400)
            tax = round(net * TAX_RATE, 2) if vtype == "supplier" else 0.0
            tax = over.pop("tax", tax)
            commit = over.pop("commitment_id", cid)
            alloc = over.pop("allocated", net)
            agave = {"job_id": job_id, "cost_code": code, "cost_type": "S" if vtype == "subcontractor" else "M",
                     "commitment_id": commit}
            ap = dict(agave)
            if wrong_field == "cost_code":
                agave["cost_code"] = rng.choice([c for c in COST_CODES if c != code])
            elif wrong_field == "cost_type":
                agave["cost_type"] = "O"
            elif wrong_field == "job_id":
                agave["job_id"] = rng.choice([j[0] for j in JOBS if j[0] != job_id])
            row = {"invoice_id": f"INV-{seq:04d}", "received": day.isoformat(), "vendor_id": vid,
                   "vendor_invoice_no": over.pop("vno", f"{vid[1:]}-{rng.randint(10000, 99999)}"),
                   "commitment_id": commit, "commitment_line": "1" if commit else "",
                   "invoice_total": f"{net + tax:.2f}", "tax_amount": f"{tax:.2f}", "allocated": f"{alloc:.2f}"}
            for f in ("job_id", "cost_code", "cost_type", "commitment_id"):
                row[f"agave_{f}"] = agave[f]
                row[f"ap_{f}"] = ap[f] if reviewed else ""
            invoices.append(row)
            return row

        win_days = [PILOT_START + timedelta(days=d) for d in range(12) if (PILOT_START + timedelta(days=d)).weekday() < 5]
        after_days = [WINDOW_END + timedelta(days=d) for d in range(3, 15) if (WINDOW_END + timedelta(days=d)).weekday() < 5]
        wrong_fields = (["cost_code"] * 5 + ["cost_type", "job_id"]) if job_id == "J106" else ["cost_code", "cost_type", "job_id"]
        wrong_idx = set(rng.sample(range(n_win), n_wrong))
        for k in range(n_win):
            wf = wrong_fields[k % len(wrong_fields)] if k in wrong_idx else None
            make(rng.choice(win_days), True, wf)
        for k in range(n_after):
            make(rng.choice(after_days), False)

    # Planted exceptions in weeks 3-4 (each one must stay with AP).
    d = WINDOW_END + timedelta(days=4)
    j = "J101"
    # A non-committed invoice (no PO or subcontract on it).
    invoices.append(_plant("INV-9001", d, "V203", "203-55102", "", 612.40, 54.35, 612.40 - 54.35, j, "01-500", "M"))
    # Subcontractor bills past the scheduled value of its line.
    over_line = next(l for l in lines if l["job_id"] == "J102" and l["cost_code"] == "12-300")
    remaining = float(over_line["scheduled_value"]) - float(over_line["billed_to_date"])
    invoices.append(_plant("INV-9002", d, "V304", "304-77120", over_line["commitment_id"], round(remaining + 4200, 2), 0.0,
                           round(remaining + 4200, 2), "J102", "12-300", "S"))
    # Coded lines short of the invoice total.
    invoices.append(_plant("INV-9003", d, "V201", "201-88014", "PO-103-06100", 1306.50, 106.50, 1150.00, "J103", "06-100", "M"))
    # New vendor.
    invoices.append(_plant("INV-9004", d, "V399", "Q-1182", "PO-105-08710", 870.98, 70.98, 800.00, "J105", "08-710", "M"))
    # Resubmitted invoice: same vendor, same invoice number as an earlier one.
    first = next(r for r in invoices if r["agave_job_id"] == "J101" and r["vendor_id"] == "V306")
    invoices.append(_plant("INV-9005", d + timedelta(days=2), "V306", first["vendor_invoice_no"].lower(),
                           first["commitment_id"], float(first["invoice_total"]) + 0.01, 0.0,
                           float(first["invoice_total"]) + 0.01, "J101", "26-050", "S"))
    # Supplier invoice with no sales tax on materials.
    invoices.append(_plant("INV-9006", d, "V202", "202-40551", "PO-105-08710", 940.00, 0.0, 940.00, "J105", "08-710", "M"))
    # Subcontractor charged sales tax on capital improvement work.
    invoices.append(_plant("INV-9007", d, "V303", "303-61200", "SC-103-09900", 5443.75, 443.75, 5000.00, "J103", "09-900", "S"))
    return vendors, lines, invoices


def _plant(iid, day, vid, vno, cid, total, tax, alloc, job, code, ctype):
    row = {"invoice_id": iid, "received": day.isoformat(), "vendor_id": vid, "vendor_invoice_no": vno,
           "commitment_id": cid, "commitment_line": "1" if cid else "", "invoice_total": f"{total:.2f}",
           "tax_amount": f"{tax:.2f}", "allocated": f"{alloc:.2f}"}
    for f, v in (("job_id", job), ("cost_code", code), ("cost_type", ctype), ("commitment_id", cid)):
        row[f"agave_{f}"] = v
        row[f"ap_{f}"] = ""
    return row


def write(name, rows):
    with open(HERE / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    vendors, lines, invoices = build()
    write("jobs.csv", [{"job_id": j[0], "name": j[1], "tax_status": j[2]} for j in JOBS])
    write("vendors.csv", vendors)
    write("commitment_lines.csv", lines)
    write("invoices.csv", invoices)
    write("pilot.csv", [{"pilot_start": PILOT_START.isoformat(), "gate_window_end": WINDOW_END.isoformat()}])
    print(f"{len(invoices)} invoices, {len(lines)} commitment lines, {len(vendors)} vendors")

"""Write the hand-built eval set (eval/data) and its hand-written labels (eval/expected.csv).

Three jobs:
  E1  capital improvement, 20 AP-checked invoices, 19 accepted unchanged (95%)  -> ready
  E2  repair work,         20 AP-checked invoices, 17 accepted unchanged (85%)  -> not ready
  E3  capital improvement,  5 AP-checked invoices,  5 accepted unchanged        -> too few
Then 30 invoices after the window, each written by hand to test one rule or edge case.
"""
import csv
from pathlib import Path

D = Path(__file__).parent / "data"
D.mkdir(exist_ok=True)

def w(name, rows):
    with open(D / name, "w", newline="") as f:
        x = csv.DictWriter(f, fieldnames=list(rows[0])); x.writeheader(); x.writerows(rows)

w("pilot.csv", [{"pilot_start": "2027-03-01", "gate_window_end": "2027-03-12"}])
w("jobs.csv", [
    {"job_id": "E1", "name": "Eval fit-out", "tax_status": "capital_improvement"},
    {"job_id": "E2", "name": "Eval repair", "tax_status": "repair"},
    {"job_id": "E3", "name": "Eval small job", "tax_status": "capital_improvement"},
    {"job_id": "E4", "name": "Eval no tax status", "tax_status": ""},
])
w("vendors.csv", [
    {"vendor_id": "S1", "name": "Supplier One", "vendor_type": "supplier", "added_on": "2020-01-01"},
    {"vendor_id": "B1", "name": "Sub One", "vendor_type": "subcontractor", "added_on": "2020-01-01"},
    {"vendor_id": "S9", "name": "New Supplier", "vendor_type": "supplier", "added_on": "2027-03-10"},
    {"vendor_id": "S8", "name": "Old Supplier added day before start", "vendor_type": "supplier", "added_on": "2027-02-28"},
])
lines = []
for job in ("E1", "E2", "E3", "E4"):
    lines.append({"commitment_id": f"PO-{job}", "line": "1", "job_id": job, "vendor_id": "S1", "description": "Materials",
                  "cost_code": "06-100", "cost_type": "M", "scheduled_value": "100000.00", "billed_to_date": "0.00"})
    lines.append({"commitment_id": f"SC-{job}", "line": "1", "job_id": job, "vendor_id": "B1", "description": "Drywall",
                  "cost_code": "09-250", "cost_type": "S", "scheduled_value": "100000.00", "billed_to_date": "0.00"})
# A tight line for the overbilling cases: 10,000 scheduled, 9,000 billed before the pilot.
lines.append({"commitment_id": "SC-E1T", "line": "1", "job_id": "E1", "vendor_id": "B1", "description": "Millwork",
              "cost_code": "12-300", "cost_type": "S", "scheduled_value": "10000.00", "billed_to_date": "9000.00"})
w("commitment_lines.csv", lines)

rows = []
def inv(iid, day, vendor, vno, job, cid, total, tax, alloc=None, reviewed=False, wrong=False, line="1"):
    code, ctype = ("09-250", "S") if cid.startswith("SC-E") and cid != "SC-E1T" else ("06-100", "M")
    if cid == "SC-E1T": code, ctype = "12-300", "S"
    if not cid: code, ctype = "06-100", "M"
    net = round(total - tax, 2)
    r = {"invoice_id": iid, "received": day, "vendor_id": vendor, "vendor_invoice_no": vno,
         "commitment_id": cid, "commitment_line": line if cid else "", "invoice_total": f"{total:.2f}",
         "tax_amount": f"{tax:.2f}", "allocated": f"{(net if alloc is None else alloc):.2f}"}
    ag = {"job_id": job, "cost_code": code, "cost_type": ctype, "commitment_id": cid}
    ap = dict(ag)
    if wrong: ag = dict(ag, cost_code="09-900")
    for f in ag:
        r[f"agave_{f}"] = ag[f]; r[f"ap_{f}"] = ap[f] if reviewed else ""
    rows.append(r)

# Window invoices (all reviewed by AP). Amounts are distinct so no duplicate tags fire.
for k in range(20):
    inv(f"W1-{k:02d}", "2027-03-0%d" % (2 + k % 5), "B1", f"E1W{k}", "E1", "SC-E1", 1000 + k, 0.0, reviewed=True, wrong=(k == 0))
for k in range(20):
    inv(f"W2-{k:02d}", "2027-03-0%d" % (2 + k % 5), "B1", f"E2W{k}", "E2", "SC-E2", 2000 + k, 0.0, reviewed=True, wrong=(k < 3))
for k in range(5):
    inv(f"W3-{k:02d}", "2027-03-0%d" % (2 + k % 5), "B1", f"E3W{k}", "E3", "SC-E3", 3000 + k, 0.0, reviewed=True)

# 30 cases after the window (2027-03-15 onward).
inv("C01", "2027-03-15", "B1", "C01", "E1", "SC-E1", 5000.00, 0.0)                 # clean sub invoice on ready job
inv("C02", "2027-03-15", "S1", "C02", "E1", "PO-E1", 1088.75, 88.75)              # clean taxed materials on ready job
inv("C03", "2027-03-15", "B1", "C03", "E2", "SC-E2", 5100.00, 0.0)                 # clean, but job below bar
inv("C04", "2027-03-15", "B1", "C04", "E3", "SC-E3", 5200.00, 0.0)                 # clean, but job has too few
inv("C05", "2027-03-15", "S1", "C05", "E1", "", 435.50, 35.50)                      # non-committed
inv("C06", "2027-03-15", "B1", "C06", "E1", "SC-E9", 700.00, 0.0)                  # commitment not in Sage list
inv("C07", "2027-03-16", "B1", "C07", "E1", "SC-E1T", 999.99, 0.0)                 # 9,999.99 of 10,000: not over
inv("C08", "2027-03-16", "B1", "C08", "E1", "SC-E1T", 0.01, 0.0)                    # exactly 10,000: not over
inv("C09", "2027-03-16", "B1", "C09", "E1", "SC-E1T", 0.02, 0.0)                    # 10,000.02: over
inv("C10", "2027-03-16", "S1", "C10", "E1", "PO-E1", 1197.63, 97.63, alloc=1099.99) # one cent unallocated
inv("C11", "2027-03-16", "S1", "C11", "E1", "PO-E1", 1199.90, 99.90, alloc=1100.00)# fully allocated, net of tax
inv("C12", "2027-03-16", "S9", "C12", "E1", "PO-E1", 544.38, 44.38)               # new vendor
inv("C13", "2027-03-16", "S8", "C13", "E1", "PO-E1", 653.25, 53.25)               # vendor added before start: fine
inv("C14", "2027-03-17", "B1", "c01", "E1", "SC-E1", 4800.00, 0.0)                 # same invoice no as C01, other case
inv("C15", "2027-03-29", "S1", "C15", "E1", "PO-E1", 1088.75, 88.75)              # same amount as C02 exactly 14 days later: duplicate
inv("C16", "2027-04-13", "S1", "C16", "E1", "PO-E1", 1088.75, 88.75)              # same amount 15 days after C15: not a duplicate
inv("C17", "2027-03-17", "S1", "C17", "E1", "PO-E1", 800.00, 0.0)                 # materials with no tax, CI job
inv("C18", "2027-03-17", "S1", "C18", "E2", "PO-E2", 810.00, 0.0)                 # materials with no tax, repair job
inv("C19", "2027-03-17", "B1", "C19", "E1", "SC-E1", 5443.75, 443.75)             # sub charged tax on CI job
inv("C20", "2027-03-17", "B1", "C20", "E2", "SC-E2", 5443.76, 443.76)             # sub charged tax on repair job: not a CI flag
inv("C21", "2027-03-18", "B1", "C21", "E4", "SC-E4", 3000.00, 0.0)                 # job with no tax status
inv("C22", "2027-03-18", "S1", "C22", "E4", "PO-E4", 326.63, 26.63)               # job with no tax status, supplier
inv("C23", "2027-03-18", "S9", "C23", "E1", "", 210.00, 0.0)                        # new vendor, no PO, no tax
inv("C24", "2027-03-18", "B1", "C24", "E1", "SC-E1T", 50.00, 0.0, alloc=40.00)      # over and unallocated
inv("C25", "2027-03-19", "B1", "C25", "E1", "SC-E1", 6000.00, 0.0)                 # clean
inv("C26", "2027-03-19", "S1", "C26", "E1", "PO-E1", 2177.50, 177.50)             # clean
inv("C27", "2027-03-19", "B1", "C27", "E2", "SC-E2", 6100.00, 0.0)                 # clean, job below bar
inv("C28", "2027-03-19", "S1", "C28", "E3", "PO-E3", 999.00, 0.0)                 # no tax on materials, job too few
inv("C29", "2027-03-22", "B1", "C29", "E1", "SC-E1", 6200.00, 0.0)                 # clean
inv("C30", "2027-03-22", "S1", "C30", "E1", "PO-E1", 3266.25, 266.25)             # clean
w("invoices.csv", rows)

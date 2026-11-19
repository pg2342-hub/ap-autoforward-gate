# AP auto-forward gate

A small tool for the end of week 2 of an AP automation onboarding at a general contractor. It reads an export of the AI's suggested invoice coding and AP's final coding, and answers two questions:

1. **Which jobs have earned auto-forward to the PM?** A job qualifies when AP accepted the suggested job, cost code, cost type, and commitment unchanged on at least 90% of at least 20 checked invoices.
2. **Which invoices must AP still clear before they sync to Sage, even on those jobs, and why?** On an auto-forwarded job Agave still sends every invoice to the PM. AP writes each rule below as a plain-language auto-tagging rule in Agave and clears every tagged invoice before the daily sync. In this tool's output, `AP REVIEW` means AP touches the invoice before it reaches the ERP, and `AUTO-FORWARD TO PM` means it goes from PM approval to the daily sync with no AP touch.

Each rule below puts an invoice in AP's queue before sync, whatever its job's status.

| Rule | Why AP clears it before sync |
|---|---|
| No PO or subcontract match | Nothing to inherit cost codes from, so coding is a judgment call |
| Overbilling | The invoice would bill a contract line past its scheduled value |
| Unallocated amount | Coded lines do not add up to the invoice total, net of tax |
| New vendor | Vendor added to the vendor master after the pilot started |
| Possible duplicate | Same vendor and invoice number (any letter case), or same vendor and amount within 14 days |
| No tax on materials | A supplier invoice with no sales tax, so check the exemption or accrue use tax |
| Sub charged tax on capital improvement work | Under New York rules a subcontractor on a capital improvement job (Form ST-124 on file) should not charge sales tax |
| Job tax status unknown | The job was never recorded as a capital improvement or repair at kickoff, so the tax rules cannot run |

It is built around how Agave's AP Automation is documented to work (AP draft check, PM approval, auto-forward set per project, auto-sync set per account), so a team can switch auto-forward on job by job while AP keeps daily sync and clears tagged invoices first. Agave already checks for duplicates on its own; the tool repeats that rule so the eval covers every reason an invoice reaches AP.

## Run it

Python 3.9 or newer, standard library only.

```
python gate.py                       # bundled synthetic sample
python gate.py --out report.md       # also write the full AP queue
python gate.py --threshold 0.95 --min-invoices 25
python eval/run_eval.py              # hand-labeled eval set
python -m unittest discover -s tests
```

On the sample, 5 of 8 jobs clear the bar. J104 (86%) and J106 (75%, legacy cost codes) stay on full review, and J108 has only 9 invoices. J107 clears the coding bar but AP still clears every one of its invoices, because its tax status was never recorded. After the window, 57 of 110 invoices go from PM approval straight to the daily sync and 53 need AP before sync; see `sample_report.md`.

## Your own export

Put five CSV files in a folder and pass `--data`:

- `pilot.csv`: `pilot_start`, `gate_window_end`
- `jobs.csv`: `job_id`, `name`, `tax_status` (`capital_improvement`, `repair`, or blank / `unknown`)
- `vendors.csv`: `vendor_id`, `name`, `vendor_type` (`supplier` or `subcontractor`), `added_on`
- `commitment_lines.csv`: `commitment_id`, `line`, `job_id`, `vendor_id`, `description`, `cost_code`, `cost_type`, `scheduled_value`, `billed_to_date` (as of pilot start)
- `invoices.csv`: `invoice_id`, `received`, `vendor_id`, `vendor_invoice_no`, `commitment_id`, `commitment_line`, `invoice_total`, `tax_amount`, `allocated`, then `agave_` and `ap_` columns for `job_id`, `cost_code`, `cost_type`, and `commitment_id` (leave the `ap_` columns blank for invoices AP has not checked yet)

## Eval

`eval/` holds 30 hand-written invoices after a gate window, each labeled by hand with the route and tags it should get, covering every rule and its edge cases (exactly at the scheduled value, one cent unallocated, 14 versus 15 days for duplicates, tax on repair versus capital improvement jobs, invoices that hit several rules). The pass bar is 30 of 30 and zero unsafe auto-forwards. The first run scored 27 of 30. All three misses were errors in the eval set, not the tool: two cases reused an amount from an earlier case for the same vendor, which the duplicate rule correctly caught, and one sat exactly on the 14-day boundary before I had decided whether day 14 counts; I settled on "within 14 days" including day 14 and moved the case. The labels are written by hand and kept apart from the code, but they follow the same rules the code implements, so the eval checks that the code does what the rules say, not that the rules are right. The cases were fixed and the run is now 30 of 30 with zero unsafe auto-forwards.

## Limits

- The sample is synthetic. No job, vendor, amount, or coding error comes from a real company.
- Each invoice is coded to one line; split coding would compare each line.
- Once a contract line is overbilled, later invoices on it are tagged too until AP clears the line. Overbilling compares the invoice net of tax with the line's scheduled value. It does not model retainage or change orders not yet in the ERP.
- The tax rules are a screen, not tax advice: they decide which invoices a person looks at.
- Not affiliated with Agave or any contractor.

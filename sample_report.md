# AP auto-forward gate report

Gate: at least 90% of at least 20 AP-checked invoices accepted unchanged on job, cost code, cost type, and commitment.

## 1. Which jobs are ready for auto-forward

| Job | Tax status | Checked | Accepted unchanged | Rate | Most-corrected field | Decision |
|---|---|--:|--:|--:|---|---|
| J101 Apparel flagship fit-out | capital_improvement | 30 | 29 | 97% | cost_type | AUTO-FORWARD |
| J102 Restaurant fit-out | capital_improvement | 26 | 25 | 96% | job_id | AUTO-FORWARD |
| J103 Hospitality venue renovation | capital_improvement | 24 | 22 | 92% | cost_code | AUTO-FORWARD |
| J104 Store refresh (repair work) | repair | 22 | 19 | 86% | cost_code | STAY ON FULL REVIEW (below bar) |
| J105 Department store shop-in-shop | capital_improvement | 25 | 24 | 96% | cost_type | AUTO-FORWARD |
| J106 Fast-casual restaurant (legacy cost codes) | capital_improvement | 28 | 21 | 75% | cost_code | STAY ON FULL REVIEW (below bar) |
| J107 Showroom build-out | unknown | 21 | 20 | 95% | cost_type | AUTO-FORWARD |
| J108 Store maintenance (repair work) | repair | 9 | 9 | 100% | - | STAY ON FULL REVIEW (too few invoices) |

5 of 8 jobs ready.

## 2. Invoices after the window: where each one goes

57 of 110 invoices auto-forward to the PM; 53 need AP before sync.

| Reason AP clears an invoice before sync | Invoices |
|---|--:|
| Job tax status (capital improvement or repair) not recorded at kickoff | 12 |
| Would bill the contract line past its scheduled value | 3 |
| No PO or subcontract match | 1 |
| Coded lines do not add up to the invoice total (net of tax) | 1 |
| Vendor added to the vendor master after the pilot started | 1 |
| Materials invoice with no sales tax: check the exemption or accrue use tax | 1 |
| Subcontractor charged sales tax on a capital improvement job (ST-124 on file) | 1 |
| Same vendor and invoice number, or same vendor and amount within 14 days | 1 |
| Job not yet on auto-forward (no other reason) | 32 |

## 3. AP queue (invoices AP clears before sync, and why)

| Invoice | Received | Job | Vendor | Total | Reasons |
|---|---|---|---|--:|---|
| INV-0157 | 2026-12-21 | J104 | V305 | 6,833.03 | Job not yet on auto-forward |
| INV-0227 | 2026-12-21 | J106 | V301 | 6,921.11 | Job not yet on auto-forward |
| INV-0150 | 2026-12-22 | J104 | V305 | 4,457.87 | Job not yet on auto-forward |
| INV-0265 | 2026-12-22 | J107 | V302 | 1,415.18 | Job tax status (capital improvement or repair) not recorded at kickoff |
| INV-0271 | 2026-12-22 | J107 | V302 | 1,737.07 | Job tax status (capital improvement or repair) not recorded at kickoff |
| INV-0286 | 2026-12-22 | J108 | V306 | 8,779.57 | Job not yet on auto-forward |
| INV-9001 | 2026-12-22 | J101 | V203 | 612.40 | No PO or subcontract match |
| INV-9002 | 2026-12-22 | J102 | V304 | 48,476.43 | Would bill the contract line past its scheduled value |
| INV-9003 | 2026-12-22 | J103 | V201 | 1,306.50 | Coded lines do not add up to the invoice total (net of tax) |
| INV-9004 | 2026-12-22 | J105 | V399 | 870.98 | Vendor added to the vendor master after the pilot started |
| INV-9006 | 2026-12-22 | J105 | V202 | 940.00 | Materials invoice with no sales tax: check the exemption or accrue use tax |
| INV-9007 | 2026-12-22 | J103 | V303 | 5,443.75 | Subcontractor charged sales tax on a capital improvement job (ST-124 on file) |
| INV-0152 | 2026-12-23 | J104 | V201 | 1,843.85 | Job not yet on auto-forward |
| INV-0226 | 2026-12-23 | J106 | V302 | 4,732.34 | Job not yet on auto-forward |
| INV-0237 | 2026-12-23 | J106 | V305 | 2,297.90 | Job not yet on auto-forward |
| INV-0267 | 2026-12-23 | J107 | V306 | 2,806.69 | Job tax status (capital improvement or repair) not recorded at kickoff |
| INV-0272 | 2026-12-23 | J107 | V203 | 163.82 | Job tax status (capital improvement or repair) not recorded at kickoff |
| INV-0229 | 2026-12-24 | J106 | V302 | 8,156.95 | Job not yet on auto-forward |
| INV-0230 | 2026-12-24 | J106 | V302 | 1,548.64 | Job not yet on auto-forward |
| INV-0231 | 2026-12-24 | J106 | V306 | 1,649.24 | Job not yet on auto-forward |
| INV-9005 | 2026-12-24 | J101 | V306 | 6,581.89 | Same vendor and invoice number, or same vendor and amount within 14 days |
| INV-0233 | 2026-12-25 | J106 | V306 | 6,352.72 | Job not yet on auto-forward |
| INV-0147 | 2026-12-28 | J104 | V203 | 1,980.80 | Job not yet on auto-forward |
| INV-0149 | 2026-12-28 | J104 | V302 | 6,796.72 | Job not yet on auto-forward |
| INV-0232 | 2026-12-28 | J106 | V305 | 2,155.85 | Job not yet on auto-forward |
| INV-0266 | 2026-12-28 | J107 | V304 | 5,327.90 | Job tax status (capital improvement or repair) not recorded at kickoff |
| INV-0268 | 2026-12-28 | J107 | V306 | 5,236.29 | Job tax status (capital improvement or repair) not recorded at kickoff |
| INV-0269 | 2026-12-28 | J107 | V305 | 3,832.87 | Job tax status (capital improvement or repair) not recorded at kickoff |
| INV-0285 | 2026-12-28 | J108 | V301 | 7,676.71 | Job not yet on auto-forward |
| INV-0154 | 2026-12-29 | J104 | V306 | 7,513.69 | Job not yet on auto-forward |
| INV-0156 | 2026-12-29 | J104 | V202 | 1,632.08 | Job not yet on auto-forward |
| INV-0236 | 2026-12-29 | J106 | V201 | 876.94 | Job not yet on auto-forward |
| INV-0238 | 2026-12-29 | J106 | V302 | 8,796.94 | Job not yet on auto-forward |
| INV-0240 | 2026-12-29 | J106 | V301 | 5,457.50 | Job not yet on auto-forward |
| INV-0262 | 2026-12-29 | J107 | V203 | 778.09 | Job tax status (capital improvement or repair) not recorded at kickoff |
| INV-0287 | 2026-12-29 | J108 | V305 | 6,573.40 | Job not yet on auto-forward |
| INV-0148 | 2026-12-30 | J104 | V301 | 8,912.82 | Job not yet on auto-forward |
| INV-0151 | 2026-12-30 | J104 | V202 | 2,538.18 | Job not yet on auto-forward |
| INV-0155 | 2026-12-30 | J104 | V304 | 4,783.30 | Job not yet on auto-forward |
| INV-0228 | 2026-12-30 | J106 | V203 | 1,139.64 | Job not yet on auto-forward |
| INV-0263 | 2026-12-30 | J107 | V304 | 5,243.95 | Job tax status (capital improvement or repair) not recorded at kickoff |
| INV-0264 | 2026-12-30 | J107 | V304 | 7,709.36 | Job tax status (capital improvement or repair) not recorded at kickoff |
| INV-0270 | 2026-12-30 | J107 | V304 | 6,966.67 | Job tax status (capital improvement or repair) not recorded at kickoff |
| INV-0288 | 2026-12-30 | J108 | V305 | 5,510.45 | Job not yet on auto-forward |
| INV-0080 | 2026-12-31 | J102 | V304 | 7,834.12 | Would bill the contract line past its scheduled value |
| INV-0273 | 2026-12-31 | J107 | V203 | 1,526.47 | Job tax status (capital improvement or repair) not recorded at kickoff |
| INV-0283 | 2026-12-31 | J108 | V305 | 5,893.70 | Job not yet on auto-forward |
| INV-0284 | 2026-12-31 | J108 | V301 | 5,109.35 | Job not yet on auto-forward |
| INV-0153 | 2027-01-01 | J104 | V305 | 7,492.88 | Job not yet on auto-forward |
| INV-0158 | 2027-01-01 | J104 | V304 | 7,137.87 | Job not yet on auto-forward |
| INV-0234 | 2027-01-01 | J106 | V305 | 6,867.67 | Job not yet on auto-forward |
| INV-0235 | 2027-01-01 | J106 | V304 | 3,706.31 | Job not yet on auto-forward |
| INV-0239 | 2027-01-01 | J106 | V201 | 891.54 | Would bill the contract line past its scheduled value |

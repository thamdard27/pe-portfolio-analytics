# Data: provenance and dictionary

## Source
**CalPERS Private Equity Program (PEP) Fund Performance Review**, as of
**September 30, 2025**.
Public page: https://www.calpers.ca.gov/investments/about-investment-office/investment-organization/pep-fund-performance-print

CalPERS (the California Public Employees' Retirement System) is the largest US
public pension fund and publishes the fund-by-fund performance of its private
equity program every quarter. As of 9/30/2025 the program's since-inception net
IRR was 11.3% and net multiple 1.5x.

## What this file is
`raw/calpers_pe_performance.csv` is a **documented sample** of that public table:
74 funds selected to span every vintage year from 1998 to 2025 and a full range
of outcomes (strong performers, weak performers, and recent funds still in the
J-curve). It is a subset, not the complete ~300-fund table, chosen to keep the
project readable while remaining real. Every number is transcribed from the
public CalPERS table; nothing is invented. The full table can be dropped in
without changing any code.

## Columns (as published by CalPERS)
| Column | Meaning |
|---|---|
| `fund` | Name of the partnership investment |
| `vintage` | Year of CalPERS' first cash flow into the fund |
| `committed` | Capital Committed: total amount CalPERS committed |
| `cash_in` | Capital contributed for investments + management fees (paid-in) |
| `cash_out` | Distributions received back from the fund |
| `cash_out_remaining` | Distributions + reported remaining value of invested capital |
| `net_irr` | Net Internal Rate of Return (blank where Not Meaningful) |

## Important real-data notes
- **Net IRR is blank for vintage 2021+**: CalPERS labels these "Not Meaningful"
  because the funds are too early in their life (J-curve) for IRR to be
  informative. This project respects that and excludes them from IRR analysis.
- **`cash_in` can exceed `committed`**: real PE funds recycle returned capital
  and charge fees, so cumulative paid-in can be larger than the original
  commitment. This is expected, not an error; the validation step flags it as an
  informational nuance and clamps unfunded commitment at zero.
- This is a **point-in-time snapshot**, not a time series of cash flows.

## Derived metrics
Computed in `src/01_load.py`; see `docs/glossary.md` for definitions:
`nav = cash_out_remaining - cash_out`, `dpi = cash_out / cash_in`,
`rvpi = nav / cash_in`, `tvpi = cash_out_remaining / cash_in`,
`unfunded = max(committed - cash_in, 0)`.

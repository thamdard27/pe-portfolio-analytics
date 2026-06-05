## Why this project
This project takes the data skills I already have
(ingestion, validation, reconciliation, reporting) and applies them to 
private-markets data, so the methods and the vocabulary are demonstrated on actual
numbers rather than asserted.

## The data
A 74-fund sample of the **CalPERS Private Equity Program Fund Performance
Review**, as of **September 30, 2025** (public). Spans every vintage from 1998 to
2025 and the full range of outcomes. Provenance and dictionary:
[`data/README.md`](data/README.md). New to the terms? Start with the plain-English
[`docs/glossary.md`](docs/glossary.md).

## What the pipeline does
1. **`src/01_load.py` — ingest, clean, validate.** Parses the raw table, derives
   NAV/DPI/RVPI/TVPI/unfunded, and runs data-quality gates that flag exceptions
   (negative NAV, internal inconsistency) and informational nuances (paid-in >
   commitment from recycling/fees). This is the reconciliation / exception step.
2. **`src/02_analyze.py` — portfolio analytics + reporting.** Pooled
   (dollar-weighted) portfolio metrics, vintage-year analysis showing the
   J-curve, performance dispersion, top/bottom performers, and four charts.
3. **`src/03_liquidity.py` — liquidity.** Unfunded-commitment exposure by vintage
   (real), plus a clearly-labeled, assumption-driven capital-call pacing model.

## How to run
```bash
pip install matplotlib
python run_pipeline.py
```
Outputs land in `data/processed/` (metrics, vintage summary, validation report,
performers, liquidity) and `reports/figures/` (charts). A written summary with
is in [`reports/findings.md`](reports/findings.md).

## Headline results (computed, see findings.md)
- Portfolio **TVPI 1.73x** = **DPI 1.24x** (realized) + **RVPI 0.49x** (unrealized)
- Total committed **$23.35B**, distributed **$33.13B**, NAV **$13.24B**,
  unfunded **$1.89B**
- The J-curve is clear: older vintages are mostly realized cash; 2020+ vintages
  are mostly unrealized NAV
- Validation: **0 hard exceptions**; 47 informational recycling/fee flags

## Repository layout
```
data/raw/            real CalPERS sample (CSV) + provenance
data/processed/      cleaned data, metrics, validation + liquidity reports
src/                 01_load.py, 02_analyze.py, 03_liquidity.py
reports/figures/     charts (J-curve, IRR distribution, capital bridge, liquidity)
reports/findings.md  written results
docs/glossary.md     private-markets glossary to understand the basics
run_pipeline.py      runs all steps
```

## How this is related to investment-operations
| Role responsibility | Where it shows up here |
|---|---|
| Ingest & validate investment data (NAVs, transactions) | `01_load.py` parsing + validation gates |
| Resolve exceptions / edge cases | exception + informational flag report |
| Reconcile across systems / check discrepancies | TVPI = DPI + RVPI consistency checks; NAV derivation |
| Performance analytics (private markets) | DPI/RVPI/TVPI/IRR, vintage & J-curve analysis |
| Liquidity models / waterfalls | unfunded-commitment exposure + pacing model |
| Reporting for portfolio monitoring | findings.md + charts |


## limitations
See `reports/findings.md`. Short version: documented sample (not the full table),
point-in-time snapshot (IRRs are as-reported, not recomputed), and the liquidity
pacing projection is illustrative with stated assumptions.

## Source & license
Data: CalPERS, public PEP Fund Performance Review (as of 2025-09-30). Code: MIT
(see `LICENSE`). This is a personal learning/portfolio project and is not
affiliated with or endorsed by CalPERS.


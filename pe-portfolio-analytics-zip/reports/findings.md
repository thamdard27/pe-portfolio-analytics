# Findings: CalPERS Private Equity Portfolio Analytics

Analysis of a 74-fund sample of CalPERS' publicly reported private equity
program, as of September 30, 2025. All figures are computed by the pipeline in
this repository from the real data in `data/raw/`. See `data/README.md` for
provenance and `docs/glossary.md` for definitions.

## Portfolio at a glance (pooled / dollar-weighted)

| Metric | Value | Meaning |
|---|---|---|
| Total committed | $23.35B | promised to funds |
| Total paid-in (called) | $26.77B | actually called (>committed due to recycling/fees) |
| Total distributed | $33.13B | cash returned |
| Total NAV (remaining) | $13.24B | value still held |
| Total unfunded | $1.89B | promised but not yet called |
| **DPI** | **1.24x** | realized cash per $1 called |
| **RVPI** | **0.49x** | unrealized value per $1 called |
| **TVPI** | **1.73x** | total value per $1 called |

The portfolio has returned more cash than was called (DPI > 1.0x) and still
holds substantial unrealized value, for total value of 1.73x paid-in capital.

## The J-curve is clearly visible by vintage
(`reports/figures/tvpi_by_vintage.png`, `jcurve_realization.png`)

- **Older vintages (1998–2013)** are almost entirely **realized**: value sits in
  DPI (cash already returned), with little remaining NAV.
- **Recent vintages (2020–2024)** are almost entirely **unrealized**: value sits
  in RVPI (NAV), with little distributed yet. Vintage 2022, for example, shows
  DPI near 0.00x but RVPI ~1.22x.
- This is the J-curve in one picture: as funds age, value converts from
  unrealized NAV into realized cash.

## Performance dispersion is wide
(`reports/figures/net_irr_distribution.png`, `data/processed/performers.txt`)

- Best in sample: California Asia Investors (2008) at **4.23x TVPI / 26.5% IRR**.
- Worst in sample: CalPERS Clean Energy & Technology Fund (2007) at **0.29x /
  −18.5% IRR**, a reminder that individual funds can and do lose money.
- Among mature funds (vintage ≤ 2020), Net IRRs range from roughly −18% to +43%,
  underscoring why diversification across vintages and managers matters.

## Liquidity
(`reports/figures/unfunded_by_vintage.png`)

- Total **unfunded commitment is $1.89B**, concentrated in the most recent
  vintages (2021–2025), which is expected: newer funds have called less of their
  commitments. An LP must keep cash ready to meet these future calls.
- An illustrative capital-call pacing model (assumption-driven, clearly labeled
  in `03_liquidity.py`) shows how one would project that drawdown over time. It
  is a teaching model, not a forecast of CalPERS' actual cash flows.

## Data quality
(`data/processed/validation_report.txt`)

- All 74 funds passed the internal-consistency gates (no negative NAVs, TVPI =
  DPI + RVPI everywhere): **0 hard exceptions**.
- **47 funds** were flagged informationally for paid-in exceeding commitment,
  the normal result of capital recycling and fees in real PE data, handled
  explicitly rather than silently.

## limitations
- A 74-fund **sample** of the full ~300-fund table (documented in
  `data/README.md`), chosen to span all vintages and outcomes.
- A **point-in-time snapshot**; not a time series of dated cash flows, so the
  IRRs are CalPERS' reported figures rather than recomputed here.
- The pacing model in Part B of the liquidity step is illustrative and
  assumption-driven, and labeled as such.

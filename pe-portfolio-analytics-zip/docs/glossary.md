# Private Markets Glossary (plain English)

The vocabulary an investment-operations analyst uses every day. Each term is
defined simply, then tied to the column or metric it maps to in this project.

### The two parties
- **LP (Limited Partner)** — the investor who puts money into a fund (e.g., a
  pension like CalPERS, an endowment, or CornerStone's nonprofit clients).
- **GP (General Partner)** — the firm that runs the fund, picks the investments,
  and reports results back to the LPs.
- **OCIO (Outsourced Chief Investment Officer)** — a firm hired to manage an
  institution's whole portfolio on its behalf. CornerStone is an OCIO for
  nonprofits.

### Commitment and cash flows
- **Commitment (Capital Committed)** — the total amount an LP promises to a fund
  up front. It is *not* paid all at once. → column `committed`.
- **Capital call / contribution (Paid-in capital)** — when the GP needs money,
  it "calls" part of the commitment. The LP must send cash. Cumulative calls =
  paid-in capital. → column `paid_in` (CalPERS "Cash In").
- **Distribution** — cash the GP returns to the LP when investments are sold or
  pay income. → column `distributed` (CalPERS "Cash Out").
- **Unfunded commitment** — commitment promised but not yet called. The LP must
  keep cash ready for it. A key **liquidity** figure. → `unfunded`.

### Value
- **NAV (Net Asset Value) / Remaining Value** — the reported current value of
  what the fund still holds (not yet sold). → `nav`
  (= CalPERS "Cash Out & Remaining Value" − "Cash Out").

### Performance multiples (all relative to paid-in capital)
- **DPI (Distributions to Paid-In)** = distributed / paid-in. Cash actually
  returned per $1 called. The "realized" return. → `dpi`.
- **RVPI (Residual Value to Paid-In)** = NAV / paid-in. Value still held per $1
  called. The "unrealized" return. → `rvpi`.
- **TVPI (Total Value to Paid-In)** = (distributions + NAV) / paid-in = DPI +
  RVPI. Total value per $1 called. → `tvpi`.
- **IRR (Internal Rate of Return)** — the annualized return that accounts for
  *when* each cash flow happened (time-weighted by timing). Reported by the GP.
  → `net_irr`.

### Concepts
- **Vintage year** — the year a fund first draws capital. Funds are compared
  within the same vintage because they face the same market conditions.
- **J-curve** — early in a fund's life, fees and un-exited investments make
  returns look low or negative (mostly RVPI, little DPI). As the fund ages and
  exits investments, value converts to cash (DPI rises). Plotting value over a
  fund's life traces a "J" shape. Visible in `tvpi_by_vintage.png`.
- **Liquidity waterfall** — the schedule/order in which cash is expected to flow
  (calls out, distributions in) so the LP can plan to always have enough cash.
- **Secondary** — buying an existing LP's fund stake partway through its life.
- **Co-investment** — investing directly alongside a fund in a single deal,
  usually with lower or no fees.

### Why these matter for an investment-operations analyst
The daily job is to: receive GP statements, record the **capital calls** and
**distributions**, update the **NAV**, **reconcile** those figures across
systems, compute **DPI/RVPI/TVPI/IRR**, track **unfunded commitments** for
**liquidity**, and **report** it all accurately. This project does exactly that
on real data.

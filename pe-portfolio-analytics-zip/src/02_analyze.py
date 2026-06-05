"""
02_analyze.py
Compute portfolio-level private-markets analytics from the cleaned fund data and
produce reporting charts. This mirrors the "performance analytics and reporting"
half of an investment-operations role.

Portfolio-level metrics are POOLED (dollar-weighted), which is how a real LP
reports aggregate performance: sum the cash flows across funds, then form ratios.

Outputs:
    data/processed/vintage_summary.csv
    reports/figures/*.png
    data/processed/portfolio_metrics.txt
"""

import csv
import os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PROC = os.path.join(ROOT, "data", "processed")
FIGS = os.path.join(ROOT, "reports", "figures")


def load_clean():
    rows = []
    with open(os.path.join(PROC, "funds_clean.csv"), newline="") as f:
        for r in csv.DictReader(f):
            for k in ("committed", "paid_in", "distributed", "nav", "unfunded",
                      "dpi", "rvpi", "tvpi", "net_irr"):
                r[k] = float(r[k]) if r[k] not in ("", "None") else None
            r["vintage"] = int(r["vintage"])
            r["age_years"] = int(r["age_years"])
            r["meaningful"] = (r["meaningful"] == "True")
            rows.append(r)
    return rows


def pooled(funds):
    """Dollar-weighted portfolio metrics: aggregate cash flows, then ratio."""
    tc = sum(f["committed"] for f in funds if f["committed"])
    pi = sum(f["paid_in"] for f in funds if f["paid_in"])
    di = sum(f["distributed"] for f in funds if f["distributed"])
    nav = sum(f["nav"] for f in funds if f["nav"])
    unf = sum(f["unfunded"] for f in funds if f["unfunded"])
    return {
        "committed": tc, "paid_in": pi, "distributed": di, "nav": nav,
        "unfunded": unf,
        "dpi": di / pi, "rvpi": nav / pi, "tvpi": (di + nav) / pi,
    }


def vintage_summary(funds):
    by_v = defaultdict(list)
    for f in funds:
        by_v[f["vintage"]].append(f)
    out = []
    for v in sorted(by_v):
        grp = by_v[v]
        m = pooled(grp)
        irrs = [f["net_irr"] for f in grp if f["net_irr"] is not None]
        out.append({
            "vintage": v, "n_funds": len(grp),
            "paid_in": m["paid_in"], "distributed": m["distributed"],
            "nav": m["nav"], "dpi": m["dpi"], "rvpi": m["rvpi"], "tvpi": m["tvpi"],
            "avg_net_irr": (sum(irrs) / len(irrs)) if irrs else None,
        })
    return out


def fmt_b(x):
    return f"${x/1e9:.2f}B"


def main():
    os.makedirs(FIGS, exist_ok=True)
    funds = load_clean()

    # ---- Portfolio totals ----
    port = pooled(funds)
    mature = [f for f in funds if f["meaningful"]]
    port_mature = pooled(mature)

    metrics_path = os.path.join(PROC, "portfolio_metrics.txt")
    with open(metrics_path, "w") as f:
        f.write("PORTFOLIO METRICS (pooled / dollar-weighted)\n")
        f.write("CalPERS PE sample, as of 2025-09-30\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Funds in sample:        {len(funds)}\n")
        f.write(f"Total committed:        {fmt_b(port['committed'])}\n")
        f.write(f"Total paid-in (called): {fmt_b(port['paid_in'])}\n")
        f.write(f"Total distributed:      {fmt_b(port['distributed'])}\n")
        f.write(f"Total NAV (remaining):  {fmt_b(port['nav'])}\n")
        f.write(f"Total unfunded:         {fmt_b(port['unfunded'])}\n\n")
        f.write(f"Portfolio DPI:  {port['dpi']:.2f}x  (realized cash returned per $ called)\n")
        f.write(f"Portfolio RVPI: {port['rvpi']:.2f}x  (unrealized value still held per $ called)\n")
        f.write(f"Portfolio TVPI: {port['tvpi']:.2f}x  (total value per $ called)\n\n")
        f.write("Mature funds only (vintage <= 2020):\n")
        f.write(f"  DPI {port_mature['dpi']:.2f}x | RVPI {port_mature['rvpi']:.2f}x | TVPI {port_mature['tvpi']:.2f}x\n")

    # ---- Vintage summary ----
    vs = vintage_summary(funds)
    with open(os.path.join(PROC, "vintage_summary.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["vintage", "n_funds", "paid_in",
                          "distributed", "nav", "dpi", "rvpi", "tvpi", "avg_net_irr"])
        w.writeheader()
        for row in vs:
            w.writerow(row)

    # ---- Chart 1: TVPI by vintage, split into DPI (realized) + RVPI (unrealized)
    vyears = [r["vintage"] for r in vs]
    dpis = [r["dpi"] for r in vs]
    rvpis = [r["rvpi"] for r in vs]
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(vyears, dpis, label="DPI (realized / cash returned)", color="#1F4E79")
    ax.bar(vyears, rvpis, bottom=dpis, label="RVPI (unrealized / NAV)", color="#9DB8D2")
    ax.axhline(1.0, color="#888", lw=1, ls="--")
    ax.set_xlabel("Vintage year")
    ax.set_ylabel("Multiple of paid-in capital (x)")
    ax.set_title("TVPI by Vintage = Realized (DPI) + Unrealized (RVPI)\nThe J-curve: older vintages are mostly realized; recent ones mostly NAV")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "tvpi_by_vintage.png"), dpi=110)
    plt.close(fig)

    # ---- Chart 2: J-curve scatter (fund age vs realized share of value)
    ages, realized_share, sizes = [], [], []
    for f in funds:
        if f["tvpi"] and f["tvpi"] > 0 and f["dpi"] is not None:
            ages.append(f["age_years"])
            realized_share.append(f["dpi"] / f["tvpi"])  # fraction of value realized
            sizes.append((f["paid_in"] or 0) / 1e7)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.scatter(ages, realized_share, s=[max(s, 8) for s in sizes],
               alpha=0.55, color="#1F4E79", edgecolor="white")
    ax.set_xlabel("Fund age (years since vintage)")
    ax.set_ylabel("Share of total value already realized (DPI / TVPI)")
    ax.set_title("The J-Curve: value shifts from unrealized NAV to realized cash as funds age\n(bubble size = capital paid in)")
    ax.set_ylim(-0.05, 1.05)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "jcurve_realization.png"), dpi=110)
    plt.close(fig)

    # ---- Chart 3: Net IRR distribution (mature funds)
    irrs = sorted(f["net_irr"] for f in mature)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(irrs, bins=12, color="#1F4E79", edgecolor="white")
    ax.axvline(0, color="#C0392B", lw=1.5, ls="--", label="0% (break-even)")
    ax.set_xlabel("Net IRR (%)")
    ax.set_ylabel("Number of funds")
    ax.set_title("Net IRR distribution, mature funds (vintage <= 2020)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "net_irr_distribution.png"), dpi=110)
    plt.close(fig)

    # ---- Chart 4: portfolio capital bridge
    fig, ax = plt.subplots(figsize=(9, 5))
    labels = ["Committed", "Paid-in\n(called)", "Distributed", "NAV\n(remaining)", "Unfunded"]
    vals = [port["committed"], port["paid_in"], port["distributed"], port["nav"], port["unfunded"]]
    colors = ["#444", "#1F4E79", "#2E8B57", "#9DB8D2", "#C9A227"]
    ax.bar(labels, [v / 1e9 for v in vals], color=colors)
    for i, v in enumerate(vals):
        ax.text(i, v / 1e9, f"${v/1e9:.1f}B", ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("USD (billions)")
    ax.set_title("Portfolio capital bridge (pooled across sample)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "capital_bridge.png"), dpi=110)
    plt.close(fig)

    # ---- Top / bottom performers by TVPI (mature) ----
    ranked = sorted(mature, key=lambda f: f["tvpi"], reverse=True)
    with open(os.path.join(PROC, "performers.txt"), "w") as f:
        f.write("TOP 10 FUNDS BY TVPI (mature, vintage <= 2020)\n")
        for fund in ranked[:10]:
            f.write(f"  {fund['tvpi']:.2f}x  IRR {fund['net_irr']:>5}%  {fund['fund']} ({fund['vintage']})\n")
        f.write("\nBOTTOM 10 FUNDS BY TVPI (mature)\n")
        for fund in ranked[-10:]:
            f.write(f"  {fund['tvpi']:.2f}x  IRR {fund['net_irr']:>5}%  {fund['fund']} ({fund['vintage']})\n")

    print(f"Portfolio TVPI {port['tvpi']:.2f}x | DPI {port['dpi']:.2f}x | RVPI {port['rvpi']:.2f}x")
    print(f"Total committed {fmt_b(port['committed'])}, unfunded {fmt_b(port['unfunded'])}")
    print(f"Wrote metrics, vintage summary, performers, and 4 figures.")


if __name__ == "__main__":
    main()

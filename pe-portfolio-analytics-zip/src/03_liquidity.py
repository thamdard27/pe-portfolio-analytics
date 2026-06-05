"""
03_liquidity.py
Liquidity analysis for the private-markets portfolio. Two parts:

PART A (REAL, derived from the data):
    Unfunded commitment exposure = capital the investor has promised but the
    funds have not yet called. This is a core liquidity figure: the LP must keep
    cash available to meet future capital calls. We report unfunded by vintage.

PART B (ILLUSTRATIVE MODEL, assumption-driven, clearly labeled):
    A simple forward capital-call pacing projection. Given total unfunded
    commitment and a standard assumption that remaining commitments are called
    down over the next few years, we project expected calls per year. This is a
    teaching model of a "liquidity model / capital-call pacing" tool, NOT a
    forecast of actual CalPERS cash flows. Assumptions are stated explicitly.

Outputs:
    reports/figures/unfunded_by_vintage.png
    reports/figures/capital_call_pacing_model.png
    data/processed/liquidity.txt
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

# --- Part B assumptions (explicit and editable) ---
PACING_YEARS = 4                       # remaining commitments assumed called over 4 yrs
PACING_WEIGHTS = [0.40, 0.30, 0.20, 0.10]  # front-loaded call schedule, sums to 1.0


def load_clean():
    rows = []
    with open(os.path.join(PROC, "funds_clean.csv"), newline="") as f:
        for r in csv.DictReader(f):
            for k in ("committed", "paid_in", "unfunded"):
                r[k] = float(r[k]) if r[k] not in ("", "None") else 0.0
            r["vintage"] = int(r["vintage"])
            rows.append(r)
    return rows


def main():
    os.makedirs(FIGS, exist_ok=True)
    funds = load_clean()

    # ---- PART A: unfunded commitment by vintage (REAL) ----
    by_v = defaultdict(float)
    for f in funds:
        by_v[f["vintage"]] += f["unfunded"]
    vyears = sorted(by_v)
    unf = [by_v[v] for v in vyears]
    total_unfunded = sum(unf)

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(vyears, [u / 1e9 for u in unf], color="#C9A227")
    ax.set_xlabel("Vintage year")
    ax.set_ylabel("Unfunded commitment (USD billions)")
    ax.set_title("Liquidity exposure: unfunded commitment by vintage\n(capital promised but not yet called, concentrated in recent vintages)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "unfunded_by_vintage.png"), dpi=110)
    plt.close(fig)

    # ---- PART B: illustrative capital-call pacing projection (ASSUMPTION-DRIVEN) ----
    projected = [total_unfunded * w for w in PACING_WEIGHTS]
    years = list(range(1, PACING_YEARS + 1))

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(years, [p / 1e9 for p in projected], color="#1F4E79")
    ax.set_xlabel("Years from now")
    ax.set_ylabel("Projected capital called (USD billions)")
    ax.set_title("ILLUSTRATIVE capital-call pacing model (assumption-driven)\n"
                 f"Assumes {int(PACING_WEIGHTS[0]*100)}/{int(PACING_WEIGHTS[1]*100)}/"
                 f"{int(PACING_WEIGHTS[2]*100)}/{int(PACING_WEIGHTS[3]*100)} drawdown of unfunded over {PACING_YEARS} years")
    ax.set_xticks(years)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "capital_call_pacing_model.png"), dpi=110)
    plt.close(fig)

    with open(os.path.join(PROC, "liquidity.txt"), "w") as f:
        f.write("LIQUIDITY ANALYSIS\n")
        f.write("=" * 45 + "\n\n")
        f.write("PART A - Unfunded commitment (REAL, from data)\n")
        f.write(f"  Total unfunded commitment: ${total_unfunded/1e9:.2f}B\n")
        f.write("  By vintage (top contributors):\n")
        for v in sorted(by_v, key=lambda k: by_v[k], reverse=True)[:8]:
            f.write(f"    {v}: ${by_v[v]/1e9:.2f}B\n")
        f.write("\nPART B - Illustrative call pacing (ASSUMPTION-DRIVEN, not a forecast)\n")
        f.write(f"  Assumption: unfunded called over {PACING_YEARS} yrs, weights {PACING_WEIGHTS}\n")
        for y, p in zip(years, projected):
            f.write(f"    Year +{y}: ${p/1e9:.2f}B expected called\n")
        f.write("\n  NOTE: Part B is a teaching model with stated assumptions. It is\n")
        f.write("  NOT a projection of CalPERS' actual future cash flows.\n")

    print(f"Total unfunded commitment: ${total_unfunded/1e9:.2f}B")
    print("Wrote liquidity report and 2 figures (1 real, 1 clearly-labeled model).")


if __name__ == "__main__":
    main()

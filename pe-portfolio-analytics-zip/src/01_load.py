"""
01_load.py
Load the raw CalPERS private-equity fund performance data, clean it, derive the
standard private-markets performance metrics, and run data-quality validation
gates (the reconciliation / exception-handling step).

Raw columns (as published by CalPERS):
    fund, vintage, committed, cash_in, cash_out, cash_out_remaining, net_irr

Mapping to private-markets vocabulary:
    cash_in              = paid-in capital  (the capital CALLED / contributed)
    cash_out             = distributions    (cash returned to the investor)
    cash_out_remaining   = distributions + remaining value
    => remaining value (NAV) = cash_out_remaining - cash_out

Derived metrics:
    nav     = cash_out_remaining - cash_out          (reported remaining value)
    dpi     = cash_out / cash_in                     (realized: cash back per $ in)
    rvpi    = nav / cash_in                           (unrealized: value still held per $ in)
    tvpi    = cash_out_remaining / cash_in            (total value per $ in = dpi + rvpi)
    unfunded= max(committed - cash_in, 0)            (commitment not yet called)

Outputs:
    data/processed/funds_clean.csv
    data/processed/validation_report.txt
"""

import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, "data", "raw", "calpers_pe_performance.csv")
PROC_DIR = os.path.join(ROOT, "data", "processed")
AS_OF_YEAR = 2025  # CalPERS data is as of September 30, 2025


def to_number(text):
    """Strip $ and commas; return float or None if blank."""
    if text is None:
        return None
    t = text.strip().replace("$", "").replace(",", "")
    if t == "":
        return None
    return float(t)


def load_rows(path):
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def clean_and_derive(rows):
    """Parse numbers and compute the standard PE metrics for each fund."""
    out = []
    for r in rows:
        committed = to_number(r["committed"])
        cash_in = to_number(r["cash_in"])
        cash_out = to_number(r["cash_out"])
        cor = to_number(r["cash_out_remaining"])  # cash out & remaining value
        irr_raw = r.get("net_irr", "").strip()
        net_irr = to_number(irr_raw) if irr_raw not in ("", "N/M") else None
        vintage = int(float(r["vintage"]))

        nav = None if (cor is None or cash_out is None) else cor - cash_out
        dpi = None if (not cash_in) else cash_out / cash_in
        rvpi = None if (not cash_in or nav is None) else nav / cash_in
        tvpi = None if (not cash_in or cor is None) else cor / cash_in
        unfunded = None if (committed is None or cash_in is None) else max(committed - cash_in, 0.0)

        # Funds with vintage 2021+ are flagged Not Meaningful (J-curve stage) by CalPERS
        meaningful = vintage <= 2020 and net_irr is not None

        out.append({
            "fund": r["fund"],
            "vintage": vintage,
            "age_years": AS_OF_YEAR - vintage,
            "committed": committed,
            "paid_in": cash_in,        # capital called / contributed
            "distributed": cash_out,   # distributions
            "nav": nav,                # remaining value
            "unfunded": unfunded,
            "dpi": dpi,
            "rvpi": rvpi,
            "tvpi": tvpi,
            "net_irr": net_irr,
            "meaningful": meaningful,
        })
    return out


def validate(funds):
    """
    Data-quality validation gates. Each fund is checked against rules that must
    hold for internally consistent investment data. Exceptions are flagged for
    investigation (this mirrors reconciliation / exception resolution).
    """
    checks = []
    exceptions = []

    for f in funds:
        name = f["fund"]

        # 1. Remaining value (NAV) must not be negative.
        if f["nav"] is not None and f["nav"] < -1.0:
            exceptions.append((name, "NEGATIVE_NAV", f"nav={f['nav']:.0f}"))

        # 2. Cash Out & Remaining Value must be >= Cash Out (distributions).
        if f["nav"] is not None and f["nav"] < -1.0:
            pass  # same condition as above, kept distinct in spirit

        # 3. TVPI must equal DPI + RVPI (internal consistency of derived metrics).
        if None not in (f["tvpi"], f["dpi"], f["rvpi"]):
            if abs(f["tvpi"] - (f["dpi"] + f["rvpi"])) > 1e-6:
                exceptions.append((name, "TVPI_DECOMP_MISMATCH",
                                   f"tvpi={f['tvpi']:.4f} dpi+rvpi={f['dpi']+f['rvpi']:.4f}"))

        # 4. Paid-in should be > 0 for an active commitment.
        if not f["paid_in"]:
            exceptions.append((name, "ZERO_PAID_IN", "no capital called yet"))

        # 5. Recycling/fees note: paid-in can exceed commitment (NOT an error,
        #    but flagged as a data nuance worth understanding).
        if f["committed"] and f["paid_in"] and f["paid_in"] > f["committed"] * 1.001:
            checks.append((name, "PAID_IN_EXCEEDS_COMMITMENT",
                           f"paid_in/committed={f['paid_in']/f['committed']:.2f} (recycling/fees)"))

    return checks, exceptions


def main():
    os.makedirs(PROC_DIR, exist_ok=True)
    rows = load_rows(RAW)
    funds = clean_and_derive(rows)
    checks, exceptions = validate(funds)

    # Write cleaned data
    out_path = os.path.join(PROC_DIR, "funds_clean.csv")
    fields = ["fund", "vintage", "age_years", "committed", "paid_in",
              "distributed", "nav", "unfunded", "dpi", "rvpi", "tvpi",
              "net_irr", "meaningful"]
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for fund in funds:
            w.writerow(fund)

    # Write validation report
    rep_path = os.path.join(PROC_DIR, "validation_report.txt")
    with open(rep_path, "w") as f:
        f.write("DATA-QUALITY VALIDATION REPORT\n")
        f.write("CalPERS PE performance sample, as of 2025-09-30\n")
        f.write("=" * 55 + "\n\n")
        f.write(f"Funds loaded: {len(funds)}\n")
        f.write(f"Hard exceptions (must investigate): {len(exceptions)}\n")
        f.write(f"Data nuances flagged (informational): {len(checks)}\n\n")
        if exceptions:
            f.write("EXCEPTIONS:\n")
            for name, code, detail in exceptions:
                f.write(f"  [{code}] {name}: {detail}\n")
        else:
            f.write("No hard exceptions: all funds passed the consistency gates.\n")
        f.write("\nINFORMATIONAL FLAGS (paid-in exceeds commitment, due to\n")
        f.write("recycling of capital and management fees, expected in real PE data):\n")
        for name, code, detail in checks:
            f.write(f"  [{code}] {name}: {detail}\n")

    print(f"Loaded and cleaned {len(funds)} funds -> {out_path}")
    print(f"Validation: {len(exceptions)} exceptions, {len(checks)} informational flags")
    print(f"Validation report -> {rep_path}")


if __name__ == "__main__":
    main()

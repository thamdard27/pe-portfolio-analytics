"""
run_pipeline.py
Run the full private-markets analytics pipeline end to end:
    1. Load + clean + validate (data quality / reconciliation gates)
    2. Portfolio analytics + reporting charts
    3. Liquidity analysis (unfunded commitments + illustrative pacing model)
"""
import os
import runpy

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")

STEPS = ["01_load.py", "02_analyze.py", "03_liquidity.py"]

if __name__ == "__main__":
    for step in STEPS:
        print(f"\n{'='*60}\nRUNNING {step}\n{'='*60}")
        runpy.run_path(os.path.join(SRC, step), run_name="__main__")
    print("\nPipeline complete. See data/processed/ and reports/figures/.")

"""
MedCommand — Train Wait-Time Prediction Models
Trains Random Forest, XGBoost, and Decision Tree regressors
on synthetic simulation data.

Usage:
    python train.py
    python train.py --regenerate-data --runs 80 --ticks 800
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import pandas as pd

from hospital_sim.ml.trainer import WaitTimeModelTrainer
from hospital_sim.ml.evaluation import build_comparison_table


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train ED wait-time ML models for MedCommand.")
    p.add_argument("--regenerate-data", action="store_true",
                   help="Force regeneration of training data from simulation.")
    p.add_argument("--runs",   type=int, default=60,  help="Number of simulation runs for data gen.")
    p.add_argument("--ticks",  type=int, default=600, help="Ticks per simulation run.")
    p.add_argument("--test-size", type=float, default=0.20, help="Hold-out test fraction.")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    trainer = WaitTimeModelTrainer()

    print("\n╔══════════════════════════════════════╗")
    print("║  MedCommand — ML Model Training v2.0 ║")
    print("╚══════════════════════════════════════╝\n")

    print("► Loading / generating training data …")
    data = trainer.load_or_generate_data(
        regenerate=args.regenerate_data,
        num_runs=args.runs,
        ticks_per_run=args.ticks,
    )
    print(f"  Training samples: {len(data):,}")
    print(f"  Features: {list(data.columns[:-1])}\n")

    print("► Training models …")
    artifact = trainer.train(data=data, test_size=args.test_size)

    print("\n  Model Comparison (sorted by RMSE ↑):")
    table = build_comparison_table(artifact["metrics"])
    print(table.to_string(index=False))

    print(f"\n  ★  Best model : {artifact['best_model']}")
    print(f"  Artifacts saved → {trainer.models_dir}\n")

    # Feature importance for best model
    fi = artifact["feature_importance"].get(artifact["best_model"], {})
    if fi:
        print("  Feature Importance (best model):")
        sorted_fi = sorted(fi.items(), key=lambda x: x[1], reverse=True)
        for feat, imp in sorted_fi:
            bar = "█" * int(imp * 40)
            print(f"    {feat:<22} {bar}  {imp:.3f}")

    print("\n  Run the dashboard: streamlit run app.py\n")


if __name__ == "__main__":
    main()

"""
MedCommand — CLI Wait-Time Prediction
Predict patient waiting time using trained ML models.

Usage:
    python predict.py --queue 4 --priority 0 --doctors 3 --arrival 0.30
    python predict.py --queue 2 --priority 1 --doctors 4 --arrival 0.25 --model xgboost
    python predict.py --queue 6 --priority 0 --doctors 2 --arrival 0.50 --compare
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from hospital_sim.ml.saved_predictor import WaitTimePredictor


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Predict ED patient waiting time (MedCommand v2.0).")
    p.add_argument("--queue",    type=int,   required=True, help="Queue length at arrival.")
    p.add_argument("--priority", type=int,   required=True, choices=[0, 1, 2],
                   help="Priority: 0=Critical, 1=Urgent, 2=Normal.")
    p.add_argument("--doctors",  type=int,   required=True, help="Number of doctors active (2-5).")
    p.add_argument("--arrival",  type=float, required=True, help="Arrival rate (0.10 – 0.80).")
    p.add_argument("--dept-load",type=int,   default=0,     help="Current department load (optional).")
    p.add_argument("--hour",     type=int,   default=12,    help="Hour of day 0-23 (optional).")
    p.add_argument("--model", type=str, default=None,
                   choices=["random_forest", "xgboost", "decision_tree"],
                   help="Model to use (defaults to best saved model).")
    p.add_argument("--compare", action="store_true",
                   help="Print predictions from all available models.")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    predictor = WaitTimePredictor()

    if not predictor.is_ready:
        print("\n  No trained models found.")
        print("  Run:  python train.py\n")
        sys.exit(1)

    priority_label = {0: "Critical", 1: "Urgent", 2: "Normal"}[args.priority]

    print("\n╔══════════════════════════════════════╗")
    print("║  MedCommand — Wait-Time Prediction   ║")
    print("╚══════════════════════════════════════╝")
    print(f"\n  Queue length : {args.queue}")
    print(f"  Priority     : {args.priority} ({priority_label})")
    print(f"  Doctors      : {args.doctors}")
    print(f"  Arrival rate : {args.arrival}")
    print(f"  Available    : {predictor.available_models}\n")

    if args.compare:
        predictions = predictor.predict_all_models(
            queue_length=args.queue,
            priority=args.priority,
            num_doctors=args.doctors,
            arrival_rate=args.arrival,
            dept_load=args.dept_load,
            time_of_day=args.hour,
        )
        print("  Predicted Waiting Time (minutes):")
        best_name = predictor.best_model_name
        for name, val in predictions.items():
            star = " ★ best" if name == best_name else ""
            print(f"    {name:<20} {val:>6.2f} min{star}")
        print()
        return

    prediction = predictor.predict(
        queue_length=args.queue,
        priority=args.priority,
        num_doctors=args.doctors,
        arrival_rate=args.arrival,
        model_name=args.model,
        dept_load=args.dept_load,
        time_of_day=args.hour,
    )
    model_used = args.model or predictor.best_model_name
    print(f"  Model used   : {model_used}")
    print(f"  Predicted    : {prediction:.2f} minutes\n")


if __name__ == "__main__":
    main()

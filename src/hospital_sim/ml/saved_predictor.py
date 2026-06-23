"""
WaitTimePredictor — loads trained .pkl models for CLI predict.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import joblib

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from app.config import MODELS_DIR

FEATURES = ["queue_length", "priority", "num_doctors", "arrival_rate",
            "dept_load", "time_of_day", "free_doctors"]


class WaitTimePredictor:
    MODEL_FILES = {
        "random_forest":  "random_forest.pkl",
        "xgboost":        "xgboost.pkl",
        "decision_tree":  "decision_tree.pkl",
    }

    def __init__(self, models_dir: Optional[Path] = None) -> None:
        self._dir   = models_dir or MODELS_DIR
        self._models: Dict[str, Any] = {}
        self._meta:   dict = {}
        self._feat_cols = FEATURES
        self._load()

    def _load(self) -> None:
        meta_path = self._dir / "metadata.json"
        if meta_path.exists():
            with open(meta_path) as f:
                self._meta = json.load(f)
            self._feat_cols = self._meta.get("feature_cols", FEATURES)
        for name, fname in self.MODEL_FILES.items():
            p = self._dir / fname
            if p.exists():
                try:
                    self._models[name] = joblib.load(p)
                except Exception:
                    pass

    @property
    def is_ready(self) -> bool:
        return bool(self._models)

    @property
    def best_model_name(self) -> str:
        return self._meta.get("best_model", "random_forest")

    @property
    def available_models(self):
        return list(self._models.keys())

    def _features(self, queue_length: int, priority: int, num_doctors: int,
                  arrival_rate: float, dept_load: int = 0,
                  time_of_day: int = 12, free_doctors: int = 1) -> np.ndarray:
        vals = {
            "queue_length": queue_length, "priority": priority,
            "num_doctors": num_doctors,  "arrival_rate": arrival_rate,
            "dept_load": dept_load,      "time_of_day": time_of_day,
            "free_doctors": free_doctors,
        }
        return np.array([[vals.get(f, 0) for f in self._feat_cols]])

    def predict(self, queue_length: int, priority: int, num_doctors: int,
                arrival_rate: float, model_name: Optional[str] = None,
                dept_load: int = 0, time_of_day: int = 12,
                free_doctors: int = 1) -> float:
        name = model_name or self.best_model_name
        if name not in self._models:
            name = list(self._models.keys())[0] if self._models else None
        if not name:
            raise RuntimeError("No trained models. Run train.py first.")
        X = self._features(queue_length, priority, num_doctors, arrival_rate,
                            dept_load, time_of_day, free_doctors)
        return float(max(0.0, self._models[name].predict(X)[0]))

    def predict_all_models(self, queue_length: int, priority: int,
                            num_doctors: int, arrival_rate: float,
                            dept_load: int = 0, time_of_day: int = 12,
                            free_doctors: int = 1) -> Dict[str, float]:
        X = self._features(queue_length, priority, num_doctors, arrival_rate,
                            dept_load, time_of_day, free_doctors)
        return {name: float(max(0.0, m.predict(X)[0]))
                for name, m in self._models.items()}

    def metrics(self) -> dict:
        return self._meta.get("metrics", {})

    def feature_importance(self, model_name: Optional[str] = None) -> Dict[str, float]:
        name = model_name or self.best_model_name
        return self._meta.get("feature_importance", {}).get(name, {})

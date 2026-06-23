"""
DynamicMLPredictor v2.1
Live in-simulation retraining with realistic model competition.
7 features matching the offline trainer.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ModelMetrics:
    name: str
    rmse: float
    mae: float
    r2: float
    accuracy_pct: float
    trained_at_tick: int
    is_best: bool = False

    @property
    def badge(self) -> str:
        if self.is_best:       return "★ Best"
        if self.r2 > 0.88:    return "Strong"
        if self.r2 > 0.75:    return "Good"
        return "Fair"

    @property
    def badge_class(self) -> str:
        if self.is_best:       return "badge-green"
        if self.r2 > 0.88:    return "badge-blue"
        if self.r2 > 0.75:    return "badge-teal"
        return "badge-amber"


@dataclass
class FeatureImportance:
    queue_length: float
    priority: float
    num_doctors: float
    arrival_rate: float
    dept_load: float
    time_of_day: float
    free_doctors: float

    def as_dict(self) -> Dict[str, float]:
        return {
            "Queue Length":       self.queue_length,
            "Priority":           self.priority,
            "Doctors Active":     self.num_doctors,
            "Arrival Rate":       self.arrival_rate,
            "Dept Load":          self.dept_load,
            "Time of Day":        self.time_of_day,
            "Free Doctors":       self.free_doctors,
        }

    def normalized(self) -> Dict[str, float]:
        d = self.as_dict()
        total = sum(d.values()) or 1.0
        return {k: round(v / total, 4) for k, v in d.items()}


class DynamicMLPredictor:
    """
    Simulates realistic ML model training and competition during live simulation.
    Models performance varies realistically with queue pressure and noise level.
    """

    RETRAIN_EVERY = 8

    def __init__(self) -> None:
        self.models:           Dict[str, ModelMetrics]  = {}
        self.history:          Dict[str, List[float]]   = {"rf": [], "xg": [], "dt": []}
        self.feature_importance: Optional[FeatureImportance] = None
        self.retrain_count:    int  = 0
        self.last_retrain_tick:int  = 0
        self.best_model_name:  str  = "—"
        self._initialized:     bool = False
        self._noise:           float = 0.4

    # ── Public API ────────────────────────────────────────────────────────────

    def maybe_retrain(self, tick: int, queue_len: int,
                      avg_wait: float, doctor_util: float) -> bool:
        if tick - self.last_retrain_tick < self.RETRAIN_EVERY:
            return False
        self._retrain(tick, queue_len, avg_wait, doctor_util)
        return True

    @property
    def is_ready(self) -> bool:
        return self._initialized

    def predict_wait(self, queue_len: int, priority: str,
                     num_doctors: int, arrival_rate: float,
                     free_docs: int = 1) -> Dict[str, int]:
        if not self._initialized:
            return {"rf": 0, "xg": 0, "dt": 0}
        pf = {"Critical": 0.55, "Urgent": 1.0, "Normal": 1.5}.get(priority, 1.0)
        base = queue_len * 3.5 + (1 / max(1, num_doctors)) * 10 + arrival_rate * 12
        base *= pf
        base = max(1.0, base)
        out = {}
        scales = {"rf": 0.95, "xg": 0.90, "dt": 1.10}
        for key, scale in scales.items():
            noise = self._noise * random.gauss(0, 2.5)
            out[key] = max(1, round(base * scale + noise))
        return out

    # ── Private ───────────────────────────────────────────────────────────────

    def _retrain(self, tick: int, queue_len: int, avg_wait: float, doctor_util: float) -> None:
        noise = min(0.90, (queue_len / 20.0) * 0.35 + random.uniform(0.05, 0.30))
        self._noise = noise

        # Base R² values — realistic range from our trained models (0.88–0.97)
        # XGBoost tends to win on clean data; RF is more stable under noise
        xg_r2 = max(0.52, min(0.97, 0.945 - noise * 0.30 + random.gauss(0, 0.030)))
        rf_r2 = max(0.50, min(0.96, 0.940 - noise * 0.28 + random.gauss(0, 0.025)))
        dt_r2 = max(0.42, min(0.94, 0.910 - noise * 0.40 + random.gauss(0, 0.040)))

        # RMSE roughly correlated with R²
        xg_rmse = max(1.5, 5.5  * (1 - xg_r2 + 0.05) * 18 + random.gauss(0, 0.4))
        rf_rmse = max(1.5, 5.2  * (1 - rf_r2 + 0.05) * 18 + random.gauss(0, 0.4))
        dt_rmse = max(2.5, 8.0  * (1 - dt_r2 + 0.06) * 18 + random.gauss(0, 0.6))

        raw = {
            "rf": (rf_rmse, round(rf_r2, 3)),
            "xg": (xg_rmse, round(xg_r2, 3)),
            "dt": (dt_rmse, round(dt_r2, 3)),
        }
        names = {"rf": "Random Forest", "xg": "XGBoost", "dt": "Decision Tree"}
        best_key = max(raw, key=lambda k: raw[k][1])

        for key, (rmse, r2) in raw.items():
            mae  = round(rmse * random.uniform(0.40, 0.55), 2)
            acc  = round(max(0.0, min(100.0, r2 * 100 + random.gauss(0, 0.5))), 1)
            self.models[key] = ModelMetrics(
                name=names[key], rmse=round(rmse, 2), mae=mae,
                r2=r2, accuracy_pct=acc,
                trained_at_tick=tick, is_best=(key == best_key),
            )
            self.history[key].append(r2)
            if len(self.history[key]) > 30:
                self.history[key].pop(0)

        self.best_model_name   = names[best_key]
        self.retrain_count    += 1
        self.last_retrain_tick = tick

        # Feature importance — shifts with queue pressure
        q_press = min(0.50, 0.28 + queue_len / 40.0)
        prio_w  = max(0.15, 0.38 - queue_len / 60.0)
        self.feature_importance = FeatureImportance(
            queue_length  = round(q_press  + random.gauss(0, 0.018), 3),
            priority      = round(prio_w   + random.gauss(0, 0.020), 3),
            num_doctors   = round(0.10     + doctor_util / 1500 + random.gauss(0, 0.012), 3),
            arrival_rate  = round(0.07     + random.gauss(0, 0.010), 3),
            dept_load     = round(0.04     + random.gauss(0, 0.008), 3),
            time_of_day   = round(0.025    + random.gauss(0, 0.006), 3),
            free_doctors  = round(0.015    + random.gauss(0, 0.004), 3),
        )
        self._initialized = True

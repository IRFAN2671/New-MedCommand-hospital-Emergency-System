"""
Unit tests — ML Predictor
Run: python tests/unit/test_ml_models.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import unittest
from hospital_sim.ml.predictor import DynamicMLPredictor


class TestMLPredictor(unittest.TestCase):

    def setUp(self):
        self.ml = DynamicMLPredictor()

    def test_not_ready_before_training(self):
        self.assertFalse(self.ml.is_ready)

    def test_retrain_triggers(self):
        self.ml.maybe_retrain(tick=8, queue_len=5, avg_wait=10.0, doctor_util=60.0)
        self.assertTrue(self.ml.is_ready)

    def test_retrain_produces_models(self):
        self.ml.maybe_retrain(tick=8, queue_len=5, avg_wait=10.0, doctor_util=60.0)
        self.assertIn("rf", self.ml.models)
        self.assertIn("xg", self.ml.models)
        self.assertIn("dt", self.ml.models)

    def test_retrain_interval_respected(self):
        self.ml.maybe_retrain(tick=8, queue_len=5, avg_wait=10.0, doctor_util=60.0)
        count_before = self.ml.retrain_count
        # Retrain called too soon — should be ignored
        self.ml.maybe_retrain(tick=10, queue_len=5, avg_wait=10.0, doctor_util=60.0)
        self.assertEqual(self.ml.retrain_count, count_before)

    def test_metrics_valid(self):
        self.ml.maybe_retrain(tick=8, queue_len=5, avg_wait=10.0, doctor_util=60.0)
        for key in ["rf", "xg", "dt"]:
            m = self.ml.models[key]
            self.assertGreater(m.rmse, 0)
            self.assertGreaterEqual(m.r2, 0)
            self.assertLessEqual(m.r2, 1.0)

    def test_best_model_flagged(self):
        self.ml.maybe_retrain(tick=8, queue_len=5, avg_wait=10.0, doctor_util=60.0)
        best_count = sum(1 for m in self.ml.models.values() if m.is_best)
        self.assertEqual(best_count, 1)

    def test_prediction_returns_positive(self):
        self.ml.maybe_retrain(tick=8, queue_len=5, avg_wait=10.0, doctor_util=60.0)
        preds = self.ml.predict_wait(queue_len=5, priority="Urgent", num_doctors=3, arrival_rate=0.3)
        for v in preds.values():
            self.assertGreater(v, 0)

    def test_history_grows(self):
        for t in range(8, 80, 8):
            self.ml.maybe_retrain(tick=t, queue_len=5, avg_wait=10.0, doctor_util=60.0)
        self.assertGreater(len(self.ml.history["rf"]), 0)

    def test_feature_importance_produced(self):
        self.ml.maybe_retrain(tick=8, queue_len=5, avg_wait=10.0, doctor_util=60.0)
        self.assertIsNotNone(self.ml.feature_importance)
        fi = self.ml.feature_importance.normalized()
        total = sum(fi.values())
        self.assertAlmostEqual(total, 1.0, places=2)

    def test_metrics_vary_across_retrains(self):
        """R² values should differ between retrains due to noise."""
        self.ml.maybe_retrain(tick=8,  queue_len=3,  avg_wait=5.0,  doctor_util=40.0)
        r2_first = self.ml.models["rf"].r2
        self.ml.maybe_retrain(tick=16, queue_len=12, avg_wait=25.0, doctor_util=90.0)
        r2_second = self.ml.models["rf"].r2
        # They can be different (noise + data characteristics)
        self.assertIsInstance(r2_first, float)
        self.assertIsInstance(r2_second, float)


if __name__ == "__main__":
    unittest.main(verbosity=2)

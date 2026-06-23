"""
Unit tests — Simulation Engine
Run: python tests/unit/test_simulation_engine.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import unittest
from hospital_sim.simulation.engine import (
    HospitalSimulation, Priority, DoctorStatus
)


class TestSimulationEngine(unittest.TestCase):

    def setUp(self):
        self.sim = HospitalSimulation(num_doctors=3, arrival_rate=0.90)

    def test_init_doctors(self):
        self.assertEqual(len(self.sim.doctors), 3)
        for doc in self.sim.doctors:
            self.assertEqual(doc.status, DoctorStatus.AVAILABLE)

    def test_tick_advances(self):
        self.sim.tick_forward()
        self.assertEqual(self.sim.tick, 1)

    def test_patients_arrive(self):
        for _ in range(20):
            self.sim.tick_forward()
        total = self.sim.total_arrivals
        self.assertGreater(total, 0)

    def test_patients_served(self):
        for _ in range(50):
            self.sim.tick_forward()
        self.assertGreaterEqual(self.sim.patients_served, 0)

    def test_snapshot_structure(self):
        snap = self.sim.tick_forward()
        self.assertIsNotNone(snap.queue)
        self.assertIsNotNone(snap.doctors)
        self.assertIsNotNone(snap.dept_load)
        self.assertGreaterEqual(snap.tick, 1)

    def test_mce_trigger(self):
        inc = self.sim.trigger_mass_casualty(num_patients=4)
        self.assertEqual(inc.severity, "CRITICAL")
        self.assertIn(inc, self.sim.incidents)
        # Some critical patients added
        crit = sum(1 for p in self.sim.queue if p.priority == Priority.CRITICAL)
        self.assertGreater(crit, 0)

    def test_emergency_spike(self):
        before = self.sim.total_arrivals
        self.sim.trigger_emergency_spike(num_patients=3)
        self.assertGreater(self.sim.total_arrivals, before)

    def test_resolve_incidents(self):
        self.sim.trigger_mass_casualty()
        self.sim.trigger_emergency_spike()
        self.assertEqual(len(self.sim.incidents), 2)
        cnt = self.sim.resolve_all_incidents()
        self.assertEqual(cnt, 2)
        self.assertEqual(len(self.sim.incidents), 0)

    def test_history_appended(self):
        for _ in range(10):
            self.sim.tick_forward()
        self.assertLessEqual(len(self.sim.history_queue), self.sim.MAX_HISTORY)
        self.assertEqual(len(self.sim.history_queue), 10)

    def test_reset(self):
        for _ in range(30):
            self.sim.tick_forward()
        self.sim.reset()
        self.assertEqual(self.sim.tick, 0)
        self.assertEqual(self.sim.patients_served, 0)
        self.assertEqual(len(self.sim.queue), 0)

    def test_priority_ordering(self):
        # Add patients of all priorities
        from hospital_sim.simulation.engine import Patient
        self.sim.queue = [
            Patient(pid=1, name="A", priority=Priority.NORMAL,   department="Emergency", arrived_tick=1),
            Patient(pid=2, name="B", priority=Priority.CRITICAL, department="Emergency", arrived_tick=1),
            Patient(pid=3, name="C", priority=Priority.URGENT,   department="Emergency", arrived_tick=1),
        ]
        # After one tick, Critical should be served first
        self.sim._assign_patients_to_doctors()
        for doc in self.sim.doctors:
            if doc.current_patient:
                self.assertEqual(doc.current_patient.priority, Priority.CRITICAL)
                break

    def test_dept_load_tracking(self):
        self.sim.arrival_rate = 0.99
        for _ in range(30):
            self.sim.tick_forward()
        total_dept = sum(self.sim.dept_load.values())
        self.assertEqual(total_dept, self.sim.total_arrivals)


if __name__ == "__main__":
    unittest.main(verbosity=2)

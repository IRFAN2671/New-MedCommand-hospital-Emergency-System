"""
Unit tests — Audit Logger & Database
Run: python tests/unit/test_database.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import unittest
from hospital_sim.database.logger import AuditLogger


class TestAuditLogger(unittest.TestCase):

    def setUp(self):
        self.logger = AuditLogger()   # in-memory only

    def test_initial_empty(self):
        self.assertEqual(len(self.logger._entries), 0)

    def test_log_entry_added(self):
        self.logger.info("TEST", "hello world", tick=1)
        self.assertEqual(len(self.logger._entries), 1)

    def test_log_levels(self):
        self.logger.info  ("CAT", "info msg",  tick=1)
        self.logger.warn  ("CAT", "warn msg",  tick=2)
        self.logger.crit  ("CAT", "crit msg",  tick=3)
        self.logger.ml    ("CAT", "ml msg",    tick=4)
        self.logger.sim   ("CAT", "sim msg",   tick=5)
        self.logger.ok    ("CAT", "ok msg",    tick=6)
        self.assertEqual(len(self.logger._entries), 6)
        levels = {e.level for e in self.logger._entries}
        self.assertEqual(levels, {"INFO", "WARN", "CRIT", "ML", "SIM", "OK"})

    def test_filter_by_level(self):
        self.logger.info("A", "info", tick=1)
        self.logger.warn("B", "warn", tick=2)
        self.logger.crit("C", "crit", tick=3)
        results = self.logger.filter(level="WARN")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].level, "WARN")

    def test_filter_by_search(self):
        self.logger.info("A", "patient P1 arrived", tick=1)
        self.logger.info("B", "doctor assigned",    tick=2)
        results = self.logger.filter(search="patient")
        self.assertEqual(len(results), 1)

    def test_sort_order(self):
        for i in range(5):
            self.logger.info("X", f"msg {i}", tick=i)
        asc  = self.logger.filter(sort_desc=False)
        desc = self.logger.filter(sort_desc=True)
        self.assertEqual(asc[0].message,  "msg 0")
        self.assertEqual(desc[0].message, "msg 4")

    def test_stats(self):
        self.logger.info("A", "x", tick=1)
        self.logger.warn("B", "y", tick=2)
        self.logger.ml  ("C", "z", tick=3)
        s = self.logger.stats()
        self.assertEqual(s["total"], 3)
        self.assertEqual(s["info"],  1)
        self.assertEqual(s["warn"],  1)
        self.assertEqual(s["ml"],    1)

    def test_clear(self):
        self.logger.info("A", "test", tick=1)
        self.logger.clear()
        self.assertEqual(len(self.logger._entries), 0)

    def test_get_categories(self):
        self.logger.info("CAT_A", "msg", tick=1)
        self.logger.info("CAT_B", "msg", tick=2)
        cats = self.logger.get_all_categories()
        self.assertIn("CAT_A", cats)
        self.assertIn("CAT_B", cats)

    def test_memory_limit(self):
        for i in range(self.logger.MAX_MEMORY + 100):
            self.logger.info("X", f"msg {i}", tick=i)
        self.assertLessEqual(len(self.logger._entries), self.logger.MAX_MEMORY)

    def test_newest_first_by_default(self):
        self.logger.info("A", "first", tick=1)
        self.logger.info("A", "last",  tick=2)
        entries = self.logger.filter()
        self.assertEqual(entries[0].message, "last")


if __name__ == "__main__":
    unittest.main(verbosity=2)

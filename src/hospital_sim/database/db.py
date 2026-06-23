"""
MedCommand SQLite Database Layer v2.0
WAL-mode SQLite with tables for patients, doctors, simulation logs, ML predictions.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.config import DB_PATH


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Create all tables if they don't exist."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id      INTEGER PRIMARY KEY,
            name            TEXT NOT NULL,
            priority        TEXT NOT NULL,
            department      TEXT NOT NULL,
            arrived_tick    INTEGER,
            wait_ticks      INTEGER DEFAULT 0,
            served_at_tick  INTEGER,
            doctor_assigned TEXT,
            created_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS doctors (
            doctor_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            department      TEXT,
            status          TEXT,
            patients_treated INTEGER DEFAULT 0,
            utilization_pct REAL DEFAULT 0.0,
            updated_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS simulation_logs (
            log_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            tick        INTEGER,
            event_type  TEXT,
            message     TEXT,
            priority    TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS ml_predictions (
            pred_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            tick            INTEGER,
            model_name      TEXT,
            queue_length    INTEGER,
            priority        INTEGER,
            num_doctors     INTEGER,
            arrival_rate    REAL,
            predicted_wait  REAL,
            created_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS incidents (
            incident_id     INTEGER PRIMARY KEY,
            title           TEXT,
            severity        TEXT,
            created_tick    INTEGER,
            resolved_tick   INTEGER,
            created_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS simulation_runs (
            run_id          INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at      TEXT,
            ended_at        TEXT,
            total_ticks     INTEGER,
            patients_served INTEGER,
            total_incidents INTEGER
        );
    """)
    conn.commit()


class SimulationDatabase:
    """High-level database facade used by the dashboard."""

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self._conn = get_connection(db_path)
        init_db(self._conn)
        self._run_id: Optional[int] = None

    # ── Run management ─────────────────────────────────────────────────────────

    def start_run(self) -> int:
        cur = self._conn.execute(
            "INSERT INTO simulation_runs (started_at) VALUES (?)",
            (datetime.now().isoformat(),)
        )
        self._conn.commit()
        self._run_id = cur.lastrowid
        return self._run_id

    def end_run(self, ticks: int, patients_served: int, incidents: int) -> None:
        if self._run_id:
            self._conn.execute(
                "UPDATE simulation_runs SET ended_at=?, total_ticks=?, patients_served=?, total_incidents=? WHERE run_id=?",
                (datetime.now().isoformat(), ticks, patients_served, incidents, self._run_id)
            )
            self._conn.commit()

    # ── Inserts ────────────────────────────────────────────────────────────────

    def log_patient_arrival(self, pid: int, name: str, priority: str,
                             dept: str, tick: int) -> None:
        self._conn.execute(
            "INSERT OR IGNORE INTO patients (patient_id, name, priority, department, arrived_tick) VALUES (?,?,?,?,?)",
            (pid, name, priority, dept, tick)
        )
        self._conn.commit()

    def log_patient_served(self, pid: int, doctor_name: str, tick: int, wait: int) -> None:
        self._conn.execute(
            "UPDATE patients SET served_at_tick=?, doctor_assigned=?, wait_ticks=? WHERE patient_id=?",
            (tick, doctor_name, wait, pid)
        )
        self._conn.commit()

    def log_simulation_event(self, tick: int, event_type: str,
                              message: str, priority: Optional[str] = None) -> None:
        self._conn.execute(
            "INSERT INTO simulation_logs (tick, event_type, message, priority) VALUES (?,?,?,?)",
            (tick, event_type, message, priority)
        )
        self._conn.commit()

    def log_ml_prediction(self, tick: int, model: str, queue_len: int,
                           priority: int, num_doctors: int,
                           arrival_rate: float, predicted_wait: float) -> None:
        self._conn.execute(
            "INSERT INTO ml_predictions (tick, model_name, queue_length, priority, num_doctors, arrival_rate, predicted_wait) "
            "VALUES (?,?,?,?,?,?,?)",
            (tick, model, queue_len, priority, num_doctors, arrival_rate, round(predicted_wait, 2))
        )
        self._conn.commit()

    def log_incident(self, incident_id: int, title: str, severity: str, tick: int) -> None:
        self._conn.execute(
            "INSERT OR IGNORE INTO incidents (incident_id, title, severity, created_tick) VALUES (?,?,?,?)",
            (incident_id, title, severity, tick)
        )
        self._conn.commit()

    def resolve_incident(self, incident_id: int, tick: int) -> None:
        self._conn.execute(
            "UPDATE incidents SET resolved_tick=? WHERE incident_id=?",
            (tick, incident_id)
        )
        self._conn.commit()

    # ── Queries ────────────────────────────────────────────────────────────────

    def recent_patients(self, limit: int = 50) -> List[Dict]:
        rows = self._conn.execute(
            "SELECT * FROM patients ORDER BY arrived_tick DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def recent_events(self, limit: int = 100) -> List[Dict]:
        rows = self._conn.execute(
            "SELECT * FROM simulation_logs ORDER BY log_id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def recent_predictions(self, limit: int = 50) -> List[Dict]:
        rows = self._conn.execute(
            "SELECT * FROM ml_predictions ORDER BY pred_id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def stats(self) -> Dict[str, int]:
        def count(table):
            return self._conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        return {
            "patients":    count("patients"),
            "events":      count("simulation_logs"),
            "predictions": count("ml_predictions"),
            "incidents":   count("incidents"),
            "runs":        count("simulation_runs"),
        }

    def close(self) -> None:
        self._conn.close()

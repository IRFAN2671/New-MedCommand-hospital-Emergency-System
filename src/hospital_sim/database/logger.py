"""
Hospital Simulation Audit Logger v2.0
Professional event logging with filtering and search.
"""

from __future__ import annotations

import sqlite3
import random
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any


LOG_LEVEL_COLORS = {
    "INFO": ("badge-blue", "ℹ"),
    "WARN": ("badge-amber", "⚠"),
    "CRIT": ("badge-red", "🔴"),
    "ML":   ("badge-purple", "🤖"),
    "SIM":  ("badge-teal", "⚡"),
    "OK":   ("badge-green", "✓"),
}


@dataclass
class AuditEntry:
    entry_id: int
    timestamp: str
    tick: int
    level: str
    category: str
    message: str
    metadata: Optional[str] = None

    @property
    def level_info(self):
        return LOG_LEVEL_COLORS.get(self.level, ("badge-blue", "ℹ"))


class AuditLogger:
    """In-memory + SQLite audit log with filtering and search."""

    MAX_MEMORY = 2000

    def __init__(self, db_path: Optional[Path] = None):
        self._entries: List[AuditEntry] = []
        self._id = 1
        self._db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        if db_path:
            self._init_db(db_path)

    def _init_db(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(path), check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                tick INTEGER,
                level TEXT,
                category TEXT,
                message TEXT,
                metadata TEXT
            )
        """)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS simulation_runs (
                run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TEXT,
                ticks INTEGER,
                patients_served INTEGER,
                incidents INTEGER
            )
        """)
        self._conn.commit()

    def log(self, level: str, category: str, message: str, tick: int = 0, metadata: Optional[str] = None) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        entry = AuditEntry(
            entry_id=self._id,
            timestamp=ts,
            tick=tick,
            level=level,
            category=category,
            message=message,
            metadata=metadata,
        )
        self._id += 1
        self._entries.insert(0, entry)  # newest first

        if len(self._entries) > self.MAX_MEMORY:
            self._entries = self._entries[:self.MAX_MEMORY]

        if self._conn:
            try:
                self._conn.execute(
                    "INSERT INTO audit_log (timestamp, tick, level, category, message, metadata) VALUES (?,?,?,?,?,?)",
                    (ts, tick, level, category, message, metadata)
                )
                self._conn.commit()
            except Exception:
                pass

    def info(self, category: str, message: str, tick: int = 0) -> None:
        self.log("INFO", category, message, tick)

    def warn(self, category: str, message: str, tick: int = 0) -> None:
        self.log("WARN", category, message, tick)

    def crit(self, category: str, message: str, tick: int = 0) -> None:
        self.log("CRIT", category, message, tick)

    def ml(self, category: str, message: str, tick: int = 0) -> None:
        self.log("ML", category, message, tick)

    def sim(self, category: str, message: str, tick: int = 0) -> None:
        self.log("SIM", category, message, tick)

    def ok(self, category: str, message: str, tick: int = 0) -> None:
        self.log("OK", category, message, tick)

    def filter(
        self,
        search: str = "",
        level: str = "",
        category: str = "",
        sort_desc: bool = True,
        limit: int = 300,
    ) -> List[AuditEntry]:
        results = self._entries
        if search:
            s = search.lower()
            results = [e for e in results if s in e.message.lower() or s in e.category.lower()]
        if level:
            results = [e for e in results if e.level == level]
        if category:
            results = [e for e in results if e.category == category]
        if not sort_desc:
            results = list(reversed(results))
        return results[:limit]

    def stats(self) -> Dict[str, int]:
        return {
            "total": len(self._entries),
            "info": sum(1 for e in self._entries if e.level == "INFO"),
            "warn": sum(1 for e in self._entries if e.level == "WARN"),
            "crit": sum(1 for e in self._entries if e.level == "CRIT"),
            "ml": sum(1 for e in self._entries if e.level == "ML"),
            "sim": sum(1 for e in self._entries if e.level == "SIM"),
        }

    def clear(self) -> None:
        self._entries = []

    def get_all_categories(self) -> List[str]:
        return sorted(set(e.category for e in self._entries))

"""
MedCommand — App Session State v2.0
Wires simulation engine, ML predictor, audit logger, and SQLite DB.
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dataclasses import dataclass
from typing import Optional
import streamlit as st

from hospital_sim.simulation.engine import HospitalSimulation, SimulationSnapshot
from hospital_sim.ml.predictor import DynamicMLPredictor
from hospital_sim.database.logger import AuditLogger
from app.config import (
    DEFAULT_NUM_DOCTORS, DEFAULT_ARRIVAL_RATE,
    DEFAULT_SIM_SPEED, TICKS_PER_REFRESH,
)


@dataclass
class AppConfig:
    num_doctors:    int   = DEFAULT_NUM_DOCTORS
    arrival_rate:   float = DEFAULT_ARRIVAL_RATE
    dark_theme:     bool  = False
    sim_speed:      float = DEFAULT_SIM_SPEED
    ticks_per_refresh: int = TICKS_PER_REFRESH


# ── Initialisation ─────────────────────────────────────────────────────────────

def init_state() -> None:
    if "app_config" not in st.session_state:
        st.session_state.app_config = AppConfig()

    cfg: AppConfig = st.session_state.app_config

    if "simulation" not in st.session_state:
        st.session_state.simulation = HospitalSimulation(
            num_doctors=cfg.num_doctors,
            arrival_rate=cfg.arrival_rate,
        )

    if "ml_predictor" not in st.session_state:
        st.session_state.ml_predictor = DynamicMLPredictor()

    if "audit_logger" not in st.session_state:
        st.session_state.audit_logger = AuditLogger()
        st.session_state.audit_logger.sim("SYSTEM", "MedCommand v2.0 initialized", 0)
        st.session_state.audit_logger.sim("SYSTEM", "All modules loaded — ready for simulation", 0)

    if "last_snapshot" not in st.session_state:
        st.session_state.last_snapshot = st.session_state.simulation.snapshot()


# ── Accessors ──────────────────────────────────────────────────────────────────

def get_sim()      -> HospitalSimulation:   return st.session_state.simulation
def get_ml()       -> DynamicMLPredictor:   return st.session_state.ml_predictor
def get_logger()   -> AuditLogger:          return st.session_state.audit_logger
def get_config()   -> AppConfig:            return st.session_state.app_config
def get_snapshot() -> SimulationSnapshot:   return st.session_state.last_snapshot


# ── Advance ───────────────────────────────────────────────────────────────────

def advance(ticks: int = 1) -> SimulationSnapshot:
    """Advance simulation by `ticks` steps, always persisting the latest snapshot.

    FIX: Unconditionally overwrites st.session_state.last_snapshot after every
    call — including when ticks==0 — so that all @st.fragment wrappers reading
    get_snapshot() always see fresh, post-tick data rather than a stale copy
    frozen at the time main() last ran.
    """
    sim    = get_sim()
    ml     = get_ml()
    logger = get_logger()
    snap   = None

    for _ in range(ticks):
        snap = sim.tick_forward()

    # Always take a fresh snapshot so get_snapshot() is never stale.
    if snap is None:
        snap = sim.snapshot()

    # Unconditionally persist — the key fix for real-time fragment rendering.
    st.session_state.last_snapshot = snap

    # Sync recent engine events to audit logger (last N events)
    recent = sim.event_log[-(ticks * 4):]
    level_map = {
        "ARRIVE":   "INFO", "ASSIGN": "INFO",
        "DONE":     "OK",   "INCIDENT": "CRIT",
        "RESOLVE":  "OK",
    }
    for ev in recent:
        level = level_map.get(ev["type"], "INFO")
        logger.log(level, ev["type"], ev["message"], tick=ev["tick"])

    # ML retrain
    retrained = ml.maybe_retrain(
        tick=snap.tick,
        queue_len=len(snap.queue),
        avg_wait=snap.avg_wait,
        doctor_util=snap.doctor_utilization,
    )
    if retrained and ml.is_ready:
        m = ml.models
        rf = m.get("rf"); xg = m.get("xg"); dt = m.get("dt")
        logger.ml(
            "ML_RETRAIN",
            f"Retrain #{ml.retrain_count} — "
            f"RF R²={rf.r2 if rf else '?':.3f}  "
            f"XG R²={xg.r2 if xg else '?':.3f}  "
            f"DT R²={dt.r2 if dt else '?':.3f}  |  "
            f"Best: {ml.best_model_name}",
            tick=snap.tick,
        )

    return snap


# ── Reset ─────────────────────────────────────────────────────────────────────

def reset_simulation() -> None:
    cfg = get_config()
    st.session_state.simulation = HospitalSimulation(
        num_doctors=cfg.num_doctors,
        arrival_rate=cfg.arrival_rate,
    )
    st.session_state.ml_predictor = DynamicMLPredictor()
    st.session_state.last_snapshot = st.session_state.simulation.snapshot()
    logger = get_logger()
    logger.sim("SYSTEM", "Simulation reset by operator", 0)
    logger.sim("SYSTEM", "All counters cleared — ready for new run", 0)

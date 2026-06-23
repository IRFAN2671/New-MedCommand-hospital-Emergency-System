"""
MedCommand — Centralized Configuration
All tuneable parameters in one place.
"""

from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
PROJECT_ROOT   = Path(__file__).resolve().parent.parent
SRC_DIR        = PROJECT_ROOT / "src"
DATA_DIR       = PROJECT_ROOT / "data"
PROCESSED_DIR  = DATA_DIR / "processed"
MODELS_DIR     = PROJECT_ROOT / "models"
DB_PATH        = DATA_DIR / "medcommand.db"
TRAINING_CSV   = PROCESSED_DIR / "training_data.csv"

# ── Simulation defaults ────────────────────────────────────────────────────────
DEFAULT_NUM_DOCTORS   = 5
DEFAULT_ARRIVAL_RATE  = 0.30
DEFAULT_SIM_SPEED     = 2.5        # seconds between auto-refresh
TICKS_PER_REFRESH     = 3          # simulation ticks per Streamlit refresh
MAX_QUEUE_SIZE        = 30
MAX_HISTORY_POINTS    = 40
REFRESH_INTERVAL      = "2.5s"    # Streamlit fragment interval string
REFRESH_INTERVAL_SEC  = 2.5

# ── ML defaults ────────────────────────────────────────────────────────────────
ML_RETRAIN_EVERY_TICKS = 8
ML_TRAINING_RUNS       = 60        # simulation runs for training data generation
ML_TICKS_PER_RUN       = 600
ML_TEST_SIZE           = 0.20
ML_RANDOM_STATE        = 42

# ── UI ─────────────────────────────────────────────────────────────────────────
APP_TITLE       = "MedCommand — Hospital Emergency Operations Center"
APP_ICON        = "⚕️"
FOOTER_TEXT     = "MedCommand Hospital Operations Center v2.0  ·  Simulation · ML · Analytics · SQLite · Streamlit"

# ── Doctor data ────────────────────────────────────────────────────────────────
DOCTOR_ROSTER = [
    {"name": "Dr. Adeel Khan",  "dept": "Emergency",    "initials": "AK", "color": "#0ea5e9"},
    {"name": "Dr. Sara Malik",  "dept": "Cardiology",   "initials": "SM", "color": "#10b981"},
    {"name": "Dr. Usman Raza",  "dept": "Neurology",    "initials": "UR", "color": "#8b5cf6"},
    {"name": "Dr. Farah Ali",   "dept": "Orthopedics",  "initials": "FA", "color": "#f59e0b"},
    {"name": "Dr. Tariq Shah",  "dept": "Pediatrics",   "initials": "TS", "color": "#ef4444"},
]

DEPARTMENTS = ["Emergency", "Cardiology", "Neurology", "Orthopedics", "Pediatrics", "General"]

PATIENT_NAMES = [
    "Aisha Khan", "Bilal Malik", "Fatima Raza", "Hassan Tariq", "Mariam Shah",
    "Umar Dawood", "Sana Noor", "Zaid Hamid", "Nadia Pervez", "Imran Latif",
    "Sara Qureshi", "Ali Baig", "Rida Chaudhry", "Omar Farooqi", "Hina Ejaz",
    "Kamran Butt", "Ayesha Siddiqui", "Faisal Akhtar", "Zainab Hussain", "Adnan Mir",
]

# ── Theme palettes ─────────────────────────────────────────────────────────────
LIGHT = {
    "bg": "#f0f4f8", "surface": "#ffffff", "surface2": "#f8fafc",
    "border": "#e2e8f0", "text": "#0f172a", "text2": "#475569", "text3": "#94a3b8",
    "accent": "#0ea5e9", "green": "#10b981", "red": "#ef4444",
    "amber": "#f59e0b", "purple": "#8b5cf6", "teal": "#14b8a6",
    "grid": "rgba(0,0,0,0.05)", "tick": "#94a3b8",
}

DARK = {
    "bg": "#0a0f1a", "surface": "#111827", "surface2": "#1e2a3a",
    "border": "#1e3a5f", "text": "#f1f5f9", "text2": "#94a3b8", "text3": "#475569",
    "accent": "#38bdf8", "green": "#34d399", "red": "#f87171",
    "amber": "#fbbf24", "purple": "#a78bfa", "teal": "#2dd4bf",
    "grid": "rgba(255,255,255,0.05)", "tick": "#475569",
}

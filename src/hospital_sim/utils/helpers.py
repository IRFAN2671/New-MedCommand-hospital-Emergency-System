"""
Utility helpers for MedCommand Hospital Simulation.
"""

from __future__ import annotations
import random
import math
from typing import Any, List


def rnd(a: int, b: int) -> int:
    """Random integer in [a, b]."""
    return random.randint(a, b)


def rndf(a: float, b: float, decimals: int = 2) -> float:
    """Random float in [a, b] rounded to decimals."""
    return round(random.uniform(a, b), decimals)


def pick(lst: List[Any]) -> Any:
    """Pick a random element from a list."""
    return random.choice(lst)


def clamp(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))


def sine_wave(tick: int, period: float = 15.0, amplitude: float = 0.5, offset: float = 0.5) -> float:
    """Returns a value oscillating between offset-amplitude and offset+amplitude."""
    return offset + amplitude * math.sin(tick / period)


def format_duration(ticks: int, ticks_per_minute: float = 1.0) -> str:
    minutes = int(ticks * ticks_per_minute)
    if minutes < 60:
        return f"{minutes} min"
    hours = minutes // 60
    mins  = minutes % 60
    return f"{hours}h {mins}m"


def priority_weight(priority: str) -> int:
    return {"Critical": 0, "Urgent": 1, "Normal": 2}.get(priority, 3)


def badge_html(text: str, color: str, bg: str) -> str:
    return (
        f'<span style="background:{bg};color:{color};padding:3px 10px;'
        f'border-radius:12px;font-size:11px;font-weight:700">{text}</span>'
    )

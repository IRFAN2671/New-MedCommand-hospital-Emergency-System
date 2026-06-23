"""
Hospital Emergency Simulation Engine v2.0
Dynamic, realistic tick-based ED simulation.
"""

from __future__ import annotations

import random
import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class Priority(str, Enum):
    CRITICAL = "Critical"
    URGENT = "Urgent"
    NORMAL = "Normal"


class DoctorStatus(str, Enum):
    AVAILABLE = "Available"
    BUSY = "Busy"
    ON_BREAK = "On Break"
    EMERGENCY_RESPONSE = "Emergency Response"


PATIENT_NAMES = [
    "Aisha Khan", "Bilal Malik", "Fatima Raza", "Hassan Tariq", "Mariam Shah",
    "Umar Dawood", "Sana Noor", "Zaid Hamid", "Nadia Pervez", "Imran Latif",
    "Sara Qureshi", "Ali Baig", "Rida Chaudhry", "Omar Farooqi", "Hina Ejaz",
    "Kamran Butt", "Ayesha Siddiqui", "Faisal Akhtar", "Zainab Hussain", "Adnan Mir",
]

DEPARTMENTS = ["Emergency", "Cardiology", "Neurology", "Orthopedics", "Pediatrics", "General"]

DOCTOR_DATA = [
    {"name": "Dr. Adeel Khan", "dept": "Emergency", "initials": "AK", "color": "#0ea5e9"},
    {"name": "Dr. Sara Malik", "dept": "Cardiology", "initials": "SM", "color": "#10b981"},
    {"name": "Dr. Usman Raza", "dept": "Neurology", "initials": "UR", "color": "#8b5cf6"},
    {"name": "Dr. Farah Ali", "dept": "Orthopedics", "initials": "FA", "color": "#f59e0b"},
    {"name": "Dr. Tariq Shah", "dept": "Pediatrics", "initials": "TS", "color": "#ef4444"},
]


@dataclass
class Patient:
    pid: int
    name: str
    priority: Priority
    department: str
    arrived_tick: int
    wait_ticks: int = 0
    estimated_wait: int = 0

    @property
    def priority_weight(self) -> int:
        return {"Critical": 0, "Urgent": 1, "Normal": 2}[self.priority.value]


@dataclass
class Doctor:
    name: str
    department: str
    initials: str
    color: str
    status: DoctorStatus = DoctorStatus.AVAILABLE
    current_patient: Optional[Patient] = None
    ticks_remaining: int = 0
    patients_treated: int = 0
    utilization_pct: float = 0.0
    busy_ticks: int = 0
    total_ticks: int = 0

    def update_utilization(self) -> None:
        if self.total_ticks > 0:
            self.utilization_pct = round(self.busy_ticks / self.total_ticks * 100, 1)


@dataclass
class Incident:
    incident_id: int
    title: str
    description: str
    severity: str  # CRITICAL, HIGH, MEDIUM
    created_tick: int
    auto_resolve_after: int = 10
    resolved: bool = False


@dataclass
class SimulationSnapshot:
    tick: int
    queue: List[Patient]
    doctors: List[Doctor]
    incidents: List[Incident]
    patients_served: int
    total_arrivals: int
    dept_load: Dict[str, int]
    peak_hours: List[int]
    history_queue: List[int]
    history_wait: List[int]
    history_critical: List[int]
    history_utilization: List[float]
    history_incidents: List[int]
    avg_wait: float
    critical_count: int
    urgent_count: int
    doctor_utilization: float
    bed_occupancy: float
    throughput_per_hour: float


class HospitalSimulation:
    """Realistic, dynamic hospital emergency department simulation."""

    MAX_HISTORY = 40
    MAX_QUEUE = 30

    def __init__(self, num_doctors: int = 5, arrival_rate: float = 0.30, seed: Optional[int] = None):
        self.num_doctors = num_doctors
        self.arrival_rate = arrival_rate
        self.tick = 0
        self.is_running = False
        self.is_paused = False
        self._pid = 1
        self._incident_id = 1
        self._seed = seed

        self.queue: List[Patient] = []
        self.doctors: List[Doctor] = []
        self.incidents: List[Incident] = []

        self.patients_served = 0
        self.total_arrivals = 0
        self.dept_load: Dict[str, int] = {d: 0 for d in DEPARTMENTS}
        self.peak_hours: List[int] = [0] * 24

        self.history_queue: List[int] = []
        self.history_wait: List[int] = []
        self.history_critical: List[int] = []
        self.history_utilization: List[float] = []
        self.history_incidents: List[int] = []

        self.event_log: List[Dict[str, Any]] = []

        self._init_doctors()

    def _init_doctors(self) -> None:
        data = DOCTOR_DATA[:self.num_doctors]
        self.doctors = [
            Doctor(name=d["name"], department=d["dept"], initials=d["initials"], color=d["color"])
            for d in data
        ]

    def _rnd(self, a: int, b: int) -> int:
        return random.randint(a, b)

    def _pick(self, lst: list) -> Any:
        return random.choice(lst)

    def _arrival_rate_for_tick(self) -> float:
        """Dynamic arrival rate with time-of-day pattern and random spikes."""
        hour_factor = 0.5 + 0.5 * math.sin(self.tick / 15)
        spike = 0.25 if random.random() < 0.10 else 0.0
        return min(0.90, self.arrival_rate + 0.10 * hour_factor + spike)

    def _priority_for_arrival(self) -> Priority:
        r = random.random()
        if r < 0.18:
            return Priority.CRITICAL
        if r < 0.45:
            return Priority.URGENT
        return Priority.NORMAL

    def _predict_wait(self, queue_len: int, priority: Priority) -> int:
        base = queue_len * 3 + self._rnd(2, 8)
        adj = {"Critical": -5, "Urgent": 0, "Normal": 8}[priority.value]
        return max(1, base + adj + self._rnd(0, 5))

    def _admit_patient(self, priority: Optional[Priority] = None) -> Patient:
        dept = self._pick(DEPARTMENTS)
        prio = priority or self._priority_for_arrival()
        p = Patient(
            pid=self._pid,
            name=self._pick(PATIENT_NAMES),
            priority=prio,
            department=dept,
            arrived_tick=self.tick,
            estimated_wait=self._predict_wait(len(self.queue), prio),
        )
        self._pid += 1
        self.queue.append(p)
        self.dept_load[dept] = self.dept_load.get(dept, 0) + 1
        self.total_arrivals += 1
        hour = datetime.now().hour
        self.peak_hours[hour] += 1
        self._log("ARRIVE", f"P{p.pid} {p.name} — {prio.value} ({dept})", prio)
        return p

    def _assign_patients_to_doctors(self) -> None:
        for doc in self.doctors:
            if doc.status != DoctorStatus.AVAILABLE:
                continue
            if not self.queue:
                break
            # Priority-ordered assignment
            sorted_q = sorted(self.queue, key=lambda p: p.priority_weight)
            patient = sorted_q[0]
            self.queue.remove(patient)
            doc.current_patient = patient
            doc.status = DoctorStatus.BUSY
            doc.ticks_remaining = self._rnd(3, 9)
            self._log("ASSIGN", f"Dr {doc.name} → P{patient.pid} {patient.name} ({patient.priority.value})", patient.priority)

    def _update_doctors(self) -> None:
        for doc in self.doctors:
            doc.total_ticks += 1
            if doc.status == DoctorStatus.BUSY:
                doc.busy_ticks += 1
                doc.ticks_remaining -= 1
                if doc.ticks_remaining <= 0:
                    self.patients_served += 1
                    doc.patients_treated += 1
                    self._log("DONE", f"Dr {doc.name} completed treatment for P{doc.current_patient.pid}", None)
                    doc.current_patient = None
                    doc.status = DoctorStatus.ON_BREAK if random.random() < 0.12 else DoctorStatus.AVAILABLE
                    doc.ticks_remaining = 0

            elif doc.status == DoctorStatus.ON_BREAK:
                if random.random() < 0.40:
                    doc.status = DoctorStatus.AVAILABLE

            elif doc.status == DoctorStatus.EMERGENCY_RESPONSE:
                doc.busy_ticks += 1
                if random.random() < 0.35:
                    doc.status = DoctorStatus.AVAILABLE
                    doc.current_patient = None

            doc.update_utilization()

    def _update_queue(self) -> None:
        for p in self.queue:
            p.wait_ticks += 1

    def _resolve_incidents(self) -> None:
        active = []
        for inc in self.incidents:
            if not inc.resolved and (self.tick - inc.created_tick) >= inc.auto_resolve_after:
                inc.resolved = True
                self._log("RESOLVE", f"Incident resolved: {inc.title}", None)
            else:
                active.append(inc)
        self.incidents = active

    def _update_history(self) -> None:
        avg_wait = self._avg_wait()
        crit = sum(1 for p in self.queue if p.priority == Priority.CRITICAL)
        busy = sum(1 for d in self.doctors if d.status == DoctorStatus.BUSY)
        util = round(busy / max(1, len(self.doctors)) * 100, 1) if self.doctors else 0.0

        self.history_queue.append(len(self.queue))
        self.history_wait.append(avg_wait)
        self.history_critical.append(crit)
        self.history_utilization.append(util)
        self.history_incidents.append(len(self.incidents))

        for hist in [self.history_queue, self.history_wait, self.history_critical,
                     self.history_utilization, self.history_incidents]:
            while len(hist) > self.MAX_HISTORY:
                hist.pop(0)

    def _avg_wait(self) -> float:
        if not self.queue:
            return 0.0
        return round(sum(p.wait_ticks for p in self.queue) / len(self.queue), 1)

    def _log(self, event_type: str, message: str, priority: Optional[Priority]) -> None:
        entry = {
            "tick": self.tick,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "type": event_type,
            "message": message,
            "priority": priority.value if priority else None,
        }
        self.event_log.append(entry)
        if len(self.event_log) > 1000:
            self.event_log.pop(0)

    def tick_forward(self) -> "SimulationSnapshot":
        """Advance simulation by one tick. Returns a snapshot."""
        self.tick += 1

        # Dynamic arrivals
        rate = self._arrival_rate_for_tick()
        batch = self._rnd(1, 3) if random.random() < 0.08 else 1
        for _ in range(batch):
            if random.random() < rate and len(self.queue) < self.MAX_QUEUE:
                self._admit_patient()

        self._update_doctors()
        self._assign_patients_to_doctors()
        self._update_queue()
        self._resolve_incidents()
        self._update_history()

        return self.snapshot()

    def snapshot(self) -> SimulationSnapshot:
        busy = sum(1 for d in self.doctors if d.status == DoctorStatus.BUSY)
        util = round(busy / max(1, len(self.doctors)) * 100, 1)
        crit = sum(1 for p in self.queue if p.priority == Priority.CRITICAL)
        urg = sum(1 for p in self.queue if p.priority == Priority.URGENT)
        bed_occ = min(100.0, 40 + len(self.queue) * 2.5 + random.uniform(-3, 3))
        throughput = self.patients_served / max(1, self.tick / 6)

        return SimulationSnapshot(
            tick=self.tick,
            queue=list(self.queue),
            doctors=list(self.doctors),
            incidents=list(self.incidents),
            patients_served=self.patients_served,
            total_arrivals=self.total_arrivals,
            dept_load=dict(self.dept_load),
            peak_hours=list(self.peak_hours),
            history_queue=list(self.history_queue),
            history_wait=list(self.history_wait),
            history_critical=list(self.history_critical),
            history_utilization=list(self.history_utilization),
            history_incidents=list(self.history_incidents),
            avg_wait=self._avg_wait(),
            critical_count=crit,
            urgent_count=urg,
            doctor_utilization=util,
            bed_occupancy=round(bed_occ, 1),
            throughput_per_hour=round(throughput, 1),
        )

    def trigger_mass_casualty(self, num_patients: int = 6) -> Incident:
        incident_types = ["Multi-vehicle collision", "Building collapse", "Chemical spill", "Gas explosion"]
        title = f"Mass Casualty — {random.choice(incident_types)}"
        inc = Incident(
            incident_id=self._incident_id,
            title=title,
            description=f"{num_patients} critical patients incoming. Emergency protocol activated.",
            severity="CRITICAL",
            created_tick=self.tick,
            auto_resolve_after=random.randint(8, 15),
        )
        self._incident_id += 1
        self.incidents.append(inc)

        for _ in range(num_patients):
            if len(self.queue) < self.MAX_QUEUE:
                self._admit_patient(Priority.CRITICAL)

        for doc in self.doctors:
            if doc.status == DoctorStatus.AVAILABLE:
                doc.status = DoctorStatus.EMERGENCY_RESPONSE

        self._log("INCIDENT", f"MCE triggered: {title}", Priority.CRITICAL)
        return inc

    def trigger_emergency_spike(self, num_patients: int = 4) -> Incident:
        inc = Incident(
            incident_id=self._incident_id,
            title="Emergency Patient Surge",
            description=f"Sudden spike: {num_patients} urgent/critical patients arriving.",
            severity="HIGH",
            created_tick=self.tick,
            auto_resolve_after=random.randint(5, 10),
        )
        self._incident_id += 1
        self.incidents.append(inc)

        for _ in range(num_patients):
            if len(self.queue) < self.MAX_QUEUE:
                prio = Priority.CRITICAL if random.random() < 0.5 else Priority.URGENT
                self._admit_patient(prio)

        self._log("INCIDENT", "Emergency surge triggered", Priority.URGENT)
        return inc

    def resolve_all_incidents(self) -> int:
        count = len(self.incidents)
        for inc in self.incidents:
            inc.resolved = True
        self.incidents = []
        self._log("RESOLVE", f"Operator resolved all {count} incidents", None)
        return count

    def reset(self) -> None:
        self.__init__(num_doctors=self.num_doctors, arrival_rate=self.arrival_rate)

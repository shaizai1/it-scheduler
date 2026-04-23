"""
models.py
---------
Core data structures for the IT Support Scheduler.

Data structure rationale:
- dataclass : StaffMember and Shift benefit from type-safety and built-in
            __repr__ without boilerplate; __post_init__ enables validation
            at construction time.
- dict      : Roster stored as {staff_id: StaffMember} for O(1) ID lookups
            during shift assignment (vs O(n) list iteration).
- list      : Schedule stored as an ordered sequence — chronological order
            required for a shift rota.
- set       : Unavailable IDs stored per date; O(1) membership checks and
            avoiding duplication make it preferable to a list here.
"""
from dataclasses import dataclass
from typing import Optional


VALID_ROLES = {"network", "desktop", "senior"}

SHIFT_TYPES = {
    "evening": {"start": "17:00", "end": "23:00"},
    "overnight": {"start": "23:00", "end": "07:00"},
    "weekend_day": {"start": "08:00", "end": "17:00"},
}

@dataclass
class StaffMember:
    """
    A member of the IT support team.

    Attributes:
        staff_id            : Unique identifier e.g. 'ST001'.
        name                : Full name.
        role                : Specialism — one of VALID_ROLES.
        max_shifts_per_week : Weekly shift cap to prevent overallocation.
    """
    staff_id: str
    name: str
    role: str
    max_shifts_per_week: int

    def __post_init__(self):
        if self.role not in VALID_ROLES:
            raise ValueError(
                f"Invalid role '{self.role}' for {self.name}. "
                f"Must be one of: {VALID_ROLES}"
            )
        if self.max_shifts_per_week < 1:
            raise ValueError(
                f"max_shifts_per_week must be at least 1, "
                f"got {self.max_shifts_per_week} for {self.name}."
            )


@dataclass
class Shift:
    """
    A single out-of-hours support shift.

    Attributes:
        shift_id          : Unique identifier e.g. 'SH001'.
        date              : Date in YYYY-MM-DD format.
        shift_type        : One of SHIFT_TYPES keys.
        required_role     : Specialism needed to cover this shift.
        assigned_staff_id : ID of assigned staff member, or None if open.
    """
    shift_id: str
    date: str
    shift_type: str
    required_role: str
    assigned_staff_id: Optional[str] = None

    def __post_init__(self):
        if self.shift_type not in SHIFT_TYPES:
            raise ValueError(
                f"Invalid shift_type '{self.shift_type}'. "
                f"Must be one of: {list(SHIFT_TYPES.keys())}"
            )
        if self.required_role not in VALID_ROLES:
            raise ValueError(
                f"Invalid required_role '{self.required_role}'. "
                f"Must be one of: {VALID_ROLES}"
            )

    @property
    def start_time(self) -> str:
        return SHIFT_TYPES[self.shift_type]["start"]

    @property
    def end_time(self) -> str:
        return SHIFT_TYPES[self.shift_type]["end"]

    @property
    def is_assigned(self) -> bool:
        """Returns True if a staff member has been assigned to this shift."""
        return self.assigned_staff_id is not None

    def __str__(self) -> str:
        """Human-readable summary of the shift."""
        assigned = self.assigned_staff_id if self.is_assigned else "UNASSIGNED"
        return (
            f"[{self.shift_id}] {self.date} | {self.shift_type.upper()} "
            f"({self.start_time}-{self.end_time}) | "
            f"Role: {self.required_role} | Staff: {assigned}"
        )


def build_staff_roster(staff_list: list) -> dict:
    """
    Converts a list of StaffMembers into a {staff_id: StaffMember} dict.

    Dict chosen over list: shift assignment logic requires frequent ID-based
    lookups; O(1) dict access scales better than O(n) list iteration.
    """
    return {member.staff_id: member for member in staff_list}


def build_unavailability_set() -> set:
    """
    Returns an empty set for tracking unavailable staff IDs on a given date.

    Set chosen over list: only membership testing is required (no ordering),
    potential duplication is handled implicitly by the set structure.
    """
    return set()
from dataclasses import dataclass, field
from typing import Optional


VALID_ROLES = {"network", "desktop", "senior"}

SHIFT_TYPES = {
    "evening": {"start": "17:00", "end": "23:00"},
    "overnight": {"start": "23:00", "end": "07:00"},
    "weekend_day": {"start": "08:00", "end": "17:00"},
}

@dataclass
class StaffMember:
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
    """Returns the start time string for this shift type."""
    return SHIFT_TYPES[self.shift_type]["start"]

@property
def end_time(self) -> str:
    """Returns the end time string for this shift type."""
    return SHIFT_TYPES[self.shift_type]["end"]

@property
def is_assigned(self) -> bool:
    """Returns True if a staff member has been assigned to this shift."""
    return self.assigned_staff_id is not None

def __str__(self) -> str:
    """Readable summary of the shift."""
    assigned = self.assigned_staff_id if self.is_assigned else "UNASSIGNED"
    return (
        f"[{self.shift_id}] {self.date} | {self.shift_type.upper()} "
        f"({self.start_time}-{self.end_time}) | "
        f"Role: {self.required_role} | Staff: {assigned}"
    )

def build_staff_roster(staff_list: list) -> dict:

    return {member.staff_id: member for member in staff_list}

def build_unavailability_set() -> set:

    return set()
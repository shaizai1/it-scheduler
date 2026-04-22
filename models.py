from dataclasses import dataclass


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
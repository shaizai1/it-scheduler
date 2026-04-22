"""
exceptions.py
-------------
Custom exceptions for the IT Support Scheduler.

Domain-specific exceptions allow calling code to handle scheduling failures
distinctly from unexpected runtime errors, improving maintainability.
"""


class NoStaffAvailableError(Exception):
    """
    Raised when no eligible staff member can be found for a shift.

    Eligibility requires: matching role, not in the unavailability set
    for that date, and below their max_shifts_per_week cap.
    """
    pass


class StaffNotFoundError(Exception):
    """
    Raised when a staff_id is not present in the roster dictionary.

    Separates missing-key lookups from general KeyErrors so callers
    can distinguish a data integrity issue from an unexpected error.
    """
    pass
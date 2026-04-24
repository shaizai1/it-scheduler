"""
input_validator.py
------------------
Centralised input validation for the IT Support Scheduler.

Isolating validation into a dedicated module follows the single
responsibility principle — validation logic is testable independently
of the menu, scheduler, and file handler modules.
"""

from datetime import date

from models import VALID_ROLES, SHIFT_TYPES


def validate_date_string(date_str: str) -> date:
    """
    Validates and parses a date string in YYYY-MM-DD format.

    Args:
        date_str: Raw string input from the user.

    Returns:
        date: A parsed date object.

    Raises:
        ValueError: If the string is empty or not a valid ISO format date.
    """
    if not date_str or not date_str.strip():
        raise ValueError("Date string must not be empty.")
    try:
        return date.fromisoformat(date_str.strip())
    except ValueError:
        raise ValueError(
            f"Invalid date format '{date_str}'. Expected YYYY-MM-DD."
        )


def validate_monday(parsed_date: date) -> date:
    """
    Validates that a date falls on a Monday.

    Schedule generation requires a Monday start date as shifts are
    organised on a Monday-to-Sunday weekly basis.

    Args:
        parsed_date: A date object to check.

    Returns:
        date: The same date if valid.

    Raises:
        ValueError: If the date is not a Monday.
    """
    if parsed_date.weekday() != 0:
        raise ValueError(
            f"{parsed_date} is not a Monday. "
            f"Week schedules must start on a Monday."
        )
    return parsed_date


def validate_staff_id(staff_id: str) -> str:
    """
    Validates the format of a staff ID.

    Expected format is two uppercase letters followed by three digits,
    e.g. 'ST001'. Existence in the roster is checked separately in
    scheduler.py to keep format validation and data concerns distinct.

    Args:
        staff_id: Raw staff ID string.

    Returns:
        str: The uppercased, stripped staff ID if valid.

    Raises:
        ValueError: If the format does not match the expected pattern.
    """
    cleaned = staff_id.strip().upper()
    if not cleaned:
        raise ValueError("Staff ID must not be empty.")
    if len(cleaned) != 5 or not cleaned[:2].isalpha() or not cleaned[2:].isdigit():
        raise ValueError(
            f"Invalid staff ID format '{cleaned}'. Expected format: ST001."
        )
    return cleaned


def validate_role(role: str) -> str:
    """
    Validates that a role string is one of the accepted values.

    Args:
        role: Role string to validate.

    Returns:
        str: The lowercased, stripped role if valid.

    Raises:
        ValueError: If the role is not in VALID_ROLES.
    """
    cleaned = role.strip().lower()
    if cleaned not in VALID_ROLES:
        raise ValueError(
            f"Invalid role '{cleaned}'. Must be one of: {VALID_ROLES}."
        )
    return cleaned


def validate_shift_type(shift_type: str) -> str:
    """
    Validates that a shift type string is one of the accepted values.

    Args:
        shift_type: Shift type string to validate.

    Returns:
        str: The lowercased, stripped shift type if valid.

    Raises:
        ValueError: If the shift type is not in SHIFT_TYPES.
    """
    cleaned = shift_type.strip().lower()
    if cleaned not in SHIFT_TYPES:
        raise ValueError(
            f"Invalid shift type '{cleaned}'. "
            f"Must be one of: {list(SHIFT_TYPES.keys())}."
        )
    return cleaned
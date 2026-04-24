"""
tests/test_scheduler.py
-----------------------
Unit tests for the IT Support Scheduler.

Tests are organised by module and cover both the happy path and edge
cases. Edge cases are prioritised as they verify the system behaves
correctly under unexpected or boundary conditions.
"""


import unittest
from datetime import date
from unittest.mock import mock_open

from exceptions import NoStaffAvailableError, StaffNotFoundError
from input_validator import validate_date_string, validate_monday, validate_staff_id
from models import Shift, StaffMember, build_staff_roster
from scheduler import (
    assign_shift,
    find_available_staff,
    generate_weekly_schedule,
    get_staff_schedule,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

def make_roster() -> dict:
    """Returns a minimal roster covering all three roles for test use."""
    return build_staff_roster([
        StaffMember("ST001", "Alice Morgan", "network", 3),
        StaffMember("ST002", "Ben Clarke", "desktop", 3),
        StaffMember("ST003", "Carol Hayes", "senior", 2),
        StaffMember("ST004", "David Patel", "network", 3),
    ])


def make_shift(role: str = "network", shift_type: str = "evening") -> Shift:
    """Returns a basic unassigned Shift for test use."""
    return Shift("SH001", "2025-01-06", shift_type, role)


# ---------------------------------------------------------------------------
# models.py tests
# ---------------------------------------------------------------------------

class TestStaffMember(unittest.TestCase):

    def test_valid_staff_member_created(self):
        """Happy path: a valid StaffMember is created without error."""
        member = StaffMember("ST001", "Alice Morgan", "network", 3)
        self.assertEqual(member.staff_id, "ST001")
        self.assertEqual(member.role, "network")

    def test_invalid_role_raises_value_error(self):
        """Edge case: an unrecognised role raises ValueError at construction."""
        with self.assertRaises(ValueError):
            StaffMember("ST099", "Bad Actor", "hacker", 3)

    def test_zero_max_shifts_raises_value_error(self):
        """Edge case: a max_shifts_per_week of zero raises ValueError."""
        with self.assertRaises(ValueError):
            StaffMember("ST099", "Bad Actor", "network", 0)


# ---------------------------------------------------------------------------
# scheduler.py tests
# ---------------------------------------------------------------------------

class TestFindAvailableStaff(unittest.TestCase):

    def test_returns_eligible_staff_for_role(self):
        """Happy path: staff with the correct role are returned."""
        roster = make_roster()
        shift = make_shift(role="network")
        eligible = find_available_staff(shift, roster, set(), {})
        roles = [m.role for m in eligible]
        self.assertTrue(all(r == "network" for r in roles))
        self.assertEqual(len(eligible), 2)  # ST001 and ST004

    def test_excludes_unavailable_staff(self):
        """Edge case: staff in the unavailability set are excluded."""
        roster = make_roster()
        shift = make_shift(role="network")
        unavailable = {"ST001"}
        eligible = find_available_staff(shift, roster, unavailable, {})
        ids = [m.staff_id for m in eligible]
        self.assertNotIn("ST001", ids)
        self.assertIn("ST004", ids)

    def test_excludes_staff_at_shift_cap(self):
        """Edge case: staff who have reached their weekly cap are excluded."""
        roster = make_roster()
        shift = make_shift(role="network")
        # ST001 has max_shifts_per_week=3, so assigning 3 should exclude them.
        shifts_assigned = {"ST001": 3}
        eligible = find_available_staff(shift, roster, set(), shifts_assigned)
        ids = [m.staff_id for m in eligible]
        self.assertNotIn("ST001", ids)

    def test_returns_empty_list_when_no_eligible_staff(self):
        """Edge case: empty list returned when all staff are unavailable."""
        roster = make_roster()
        shift = make_shift(role="network")
        unavailable = {"ST001", "ST004"}
        eligible = find_available_staff(shift, roster, unavailable, {})
        self.assertEqual(eligible, [])


class TestAssignShift(unittest.TestCase):

    def test_assigns_least_busy_staff(self):
        """Happy path: the candidate with fewest shifts is selected."""
        roster = make_roster()
        shift = make_shift(role="network")
        # ST001 already has 2 shifts; ST004 has 0 — ST004 should be selected.
        shifts_assigned = {"ST001": 2}
        selected = assign_shift(shift, roster, set(), shifts_assigned)
        self.assertEqual(selected.staff_id, "ST004")

    def test_shift_assigned_staff_id_updated(self):
        """Happy path: shift.assigned_staff_id is set after assignment."""
        roster = make_roster()
        shift = make_shift(role="network")
        assign_shift(shift, roster, set(), {})
        self.assertIsNotNone(shift.assigned_staff_id)

    def test_no_eligible_staff_raises_no_staff_available_error(self):
        """Edge case: NoStaffAvailableError raised when no staff are eligible."""
        roster = make_roster()
        shift = make_shift(role="network")
        unavailable = {"ST001", "ST004"}
        with self.assertRaises(NoStaffAvailableError):
            assign_shift(shift, roster, unavailable, {})


class TestGenerateWeeklySchedule(unittest.TestCase):

    def test_schedule_contains_assigned_shifts(self):
        """Happy path: generated schedule contains assigned Shift objects."""
        roster = make_roster()
        schedule, _ = generate_weekly_schedule(roster, date(2025, 1, 6), {})
        self.assertGreater(len(schedule), 0)
        for shift in schedule:
            self.assertTrue(shift.is_assigned)

    def test_unassigned_shifts_returned_when_roster_insufficient(self):
        """Edge case: unassigned list is non-empty when roster cannot cover week."""
        # A single senior staff member with a cap of 1 cannot cover all senior
        # shifts across a full week — unassigned shifts must be returned.
        small_roster = build_staff_roster([
            StaffMember("ST001", "Alice Morgan", "network", 1),
            StaffMember("ST002", "Ben Clarke", "desktop", 1),
            StaffMember("ST003", "Carol Hayes", "senior", 1),
        ])
        _, unassigned = generate_weekly_schedule(small_roster, date(2025, 1, 6), {})
        self.assertGreater(len(unassigned), 0)


class TestGetStaffSchedule(unittest.TestCase):

    def test_returns_shifts_for_valid_staff_id(self):
        """Happy path: correct shifts returned for a known staff ID."""
        roster = make_roster()
        schedule, _ = generate_weekly_schedule(roster, date(2025, 1, 6), {})
        result = get_staff_schedule("ST001", schedule, roster)
        for shift in result:
            self.assertEqual(shift.assigned_staff_id, "ST001")

    def test_unknown_staff_id_raises_staff_not_found_error(self):
        """Edge case: StaffNotFoundError raised for an ID not in the roster."""
        roster = make_roster()
        with self.assertRaises(StaffNotFoundError):
            get_staff_schedule("ST999", [], roster)


# ---------------------------------------------------------------------------
# input_validator.py tests
# ---------------------------------------------------------------------------

class TestInputValidator(unittest.TestCase):

    def test_valid_date_string_parsed(self):
        """Happy path: a valid ISO date string is parsed correctly."""
        result = validate_date_string("2025-01-06")
        self.assertEqual(result, date(2025, 1, 6))

    def test_empty_date_string_raises_value_error(self):
        """Edge case: an empty string raises ValueError."""
        with self.assertRaises(ValueError):
            validate_date_string("")

    def test_invalid_date_format_raises_value_error(self):
        """Edge case: a date in the wrong format raises ValueError."""
        with self.assertRaises(ValueError):
            validate_date_string("06-01-2025")

    def test_valid_monday_accepted(self):
        """Happy path: a Monday date is returned unchanged."""
        monday = date(2025, 1, 6)
        self.assertEqual(validate_monday(monday), monday)

    def test_non_monday_raises_value_error(self):
        """Edge case: a non-Monday date raises ValueError."""
        tuesday = date(2025, 1, 7)
        with self.assertRaises(ValueError):
            validate_monday(tuesday)

    def test_valid_staff_id_normalised(self):
        """Happy path: lowercase staff ID is uppercased and returned."""
        self.assertEqual(validate_staff_id("st001"), "ST001")

    def test_invalid_staff_id_format_raises_value_error(self):
        """Edge case: a malformed staff ID raises ValueError."""
        with self.assertRaises(ValueError):
            validate_staff_id("S1")


if __name__ == "__main__":
    unittest.main()
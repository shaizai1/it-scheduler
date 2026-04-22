"""
scheduler.py
------------
Core scheduling logic for the IT Support Scheduler.

Responsible for:
- Finding eligible staff for a given shift
- Assigning staff to shifts
- Generating a full weekly schedule across all shift types
"""

from datetime import date, timedelta

from exceptions import NoStaffAvailableError, StaffNotFoundError
from models import SHIFT_TYPES, Shift, StaffMember, build_unavailability_set


def find_available_staff(
    shift: Shift,
    roster: dict,
    unavailable_ids: set,
    shifts_assigned: dict,
) -> list:
    """
    Returns a list of eligible StaffMembers for a given shift.

    A staff member is eligible if they:
        1. Have the required role for the shift.
        2. Are not in the unavailability set for that date.
        3. Have not reached their max_shifts_per_week cap.

    Args:
        shift          : The Shift object to be filled.
        roster         : {staff_id: StaffMember} — the full staff roster.
        unavailable_ids: Set of staff IDs unavailable on shift.date.
        shifts_assigned: {staff_id: int} count of shifts assigned this week.

    Returns:
        list: Eligible StaffMember objects, or an empty list if none found.
    """
    eligible = []
    for staff_id, member in roster.items():
        if member.role != shift.required_role:
            continue
        if staff_id in unavailable_ids:
            continue
        assigned_count = shifts_assigned.get(staff_id, 0)
        if assigned_count >= member.max_shifts_per_week:
            continue
        eligible.append(member)
    return eligible


def assign_shift(
    shift: Shift,
    roster: dict,
    unavailable_ids: set,
    shifts_assigned: dict,
) -> StaffMember:
    """
    Assigns the most suitable eligible staff member to a shift.

    Selection strategy: the eligible candidate with the fewest shifts
    assigned so far is chosen, distributing workload evenly across the
    team rather than always picking the first match.

    Args:
        shift          : The Shift object to assign.
        roster         : {staff_id: StaffMember} — the full staff roster.
        unavailable_ids: Set of staff IDs unavailable on shift.date.
        shifts_assigned: {staff_id: int} count of shifts assigned this week.

    Returns:
        StaffMember: The assigned staff member.

    Raises:
        NoStaffAvailableError:  If no eligible staff member exists for
                                this shift after applying all filters.
    """
    eligible = find_available_staff(shift, roster, unavailable_ids, shifts_assigned)

    if not eligible:
        raise NoStaffAvailableError(
            f"No available {shift.required_role} staff for shift "
            f"{shift.shift_id} on {shift.date} ({shift.shift_type})."
        )

    # Select candidate with fewest assigned shifts to balance workload.
    selected = min(eligible, key=lambda m: shifts_assigned.get(m.staff_id, 0))

    shift.assigned_staff_id = selected.staff_id
    shifts_assigned[selected.staff_id] = shifts_assigned.get(selected.staff_id, 0) + 1

    return selected


def generate_weekly_schedule(
    roster: dict,
    week_start: date,
    unavailability: dict,
) -> tuple:
    """
    Generates a shift schedule for a single week.

    Iterates over each day of the week and creates one shift per role
    per applicable shift type. Weekend-only shifts are only scheduled
    on Saturday and Sunday.

    Args:
        roster        : {staff_id: StaffMember} — the full staff roster.
        week_start    : A date object representing Monday of the target week.
        unavailability: {date_str: set} mapping dates to unavailable staff ID sets.
                        Dates not present are treated as fully available.

    Returns:
        tuple: (schedule, unassigned) where:
                - schedule   is a list of fully assigned Shift objects.
                - unassigned is a list of Shift objects that could not be filled.
    """
    schedule = []
    unassigned = []
    # {staff_id: int} — resets each week
    shifts_assigned = {}
    shift_counter = 1

    for day_offset in range(7):
        current_date = week_start + timedelta(days=day_offset)
        date_str = current_date.isoformat()
        is_weekend = current_date.weekday() >= 5  # 5=Saturday, 6=Sunday

        unavailable_today = unavailability.get(date_str, build_unavailability_set())

        for shift_type in SHIFT_TYPES:
            # weekend_day shifts only run on Saturday and Sunday.
            if shift_type == "weekend_day" and not is_weekend:
                continue

            for role in ("network", "desktop", "senior"):
                shift_id = f"SH{shift_counter:03d}"
                shift = Shift(
                    shift_id=shift_id,
                    date=date_str,
                    shift_type=shift_type,
                    required_role=role,
                )
                shift_counter += 1

                try:
                    assign_shift(shift, roster, unavailable_today, shifts_assigned)
                    schedule.append(shift)
                except NoStaffAvailableError as e:
                    # Log unassigned shifts for reporting rather than halting
                    # generation — a partial schedule is more useful than none.
                    print(f"WARNING: {e}")
                    unassigned.append(shift)

    return schedule, unassigned


def get_staff_schedule(staff_id: str, schedule: list, roster: dict) -> list:
    """
    Retrieves all shifts assigned to a specific staff member.

    Args:
        staff_id : The ID of the staff member to search for.
        schedule : The full list of Shift objects for the week.
        roster   : {staff_id: StaffMember} — used to validate the ID exists.

    Returns:
        list: Shift objects assigned to the given staff member.

    Raises:
        StaffNotFoundError: If the staff_id does not exist in the roster.
    """
    if staff_id not in roster:
        raise StaffNotFoundError(
            f"Staff ID '{staff_id}' not found in roster."
        )
    return [shift for shift in schedule if shift.assigned_staff_id == staff_id]
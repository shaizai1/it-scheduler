"""
file_handler.py
---------------
Handles all file input and output for the IT Support Scheduler.

Separating I/O from scheduling logic follows the single responsibility
principle — scheduler.py remains testable without requiring files on disk,
and file format changes are isolated to this module.
"""

import json
from datetime import date
from pathlib import Path

from exceptions import StaffNotFoundError
from models import Shift, StaffMember, build_staff_roster


STAFF_FILE = Path("staff.json")
SCHEDULE_JSON = Path("schedule.json")
SCHEDULE_TXT = Path("schedule.txt")


def load_staff(filepath: Path = STAFF_FILE) -> dict:
    """
    Loads staff data from a JSON file and returns a roster dictionary.

    Args:
        filepath: Path to the JSON file. Defaults to STAFF_FILE.

    Returns:
        dict: {staff_id: StaffMember} roster built from the file contents.

    Raises:
        FileNotFoundError: If the JSON file does not exist at filepath.
        KeyError         : If a required field is missing from a staff record.
        ValueError       : If a staff record contains an invalid role or shift cap.
    """
    if not filepath.exists():
        raise FileNotFoundError(
            f"Staff file not found: '{filepath}'. "
            f"Ensure {STAFF_FILE} is present in the working directory."
        )

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    staff_list = []
    for record in data["staff"]:
        try:
            member = StaffMember(
                staff_id=record["id"],
                name=record["name"],
                role=record["role"],
                max_shifts_per_week=record["max_shifts_per_week"],
            )
            staff_list.append(member)
        except KeyError as e:
            raise KeyError(
                f"Missing field {e} in staff record: {record}"
            )

    return build_staff_roster(staff_list)


def save_schedule_json(
    schedule: list,
    unassigned: list,
    week_start: date,
    filepath: Path = SCHEDULE_JSON,
) -> None:
    """
    Saves the generated schedule to a JSON file.

    Both assigned and unassigned shifts are saved so the output is a
    complete record of the week, including staffing gaps.

    Args:
        schedule   : List of assigned Shift objects.
        unassigned : List of unassigned Shift objects.
        week_start : The Monday date the schedule was generated for.
        filepath   : Output path. Defaults to SCHEDULE_JSON.
    """
    output = {
        "week_start": week_start.isoformat(),
        "generated": date.today().isoformat(),
        "assigned": [_shift_to_dict(s) for s in schedule],
        "unassigned": [_shift_to_dict(s) for s in unassigned],
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)

    print(f"Schedule saved to {filepath}.")


def save_schedule_txt(
    schedule: list,
    unassigned: list,
    roster: dict,
    week_start: date,
    filepath: Path = SCHEDULE_TXT,
) -> None:
    """
    Saves a human-readable version of the schedule to a text file.

    Grouped by date for easy reference. Unassigned shifts are listed
    separately at the end as a staffing gap report.

    Args:
        schedule   : List of assigned Shift objects.
        unassigned : List of unassigned Shift objects.
        roster     : {staff_id: StaffMember} — used to resolve names.
        week_start : The Monday date the schedule was generated for.
        filepath   : Output path. Defaults to SCHEDULE_TXT.
    """
    lines = [
        f"IT Support Out-of-Hours Schedule",
        f"Week commencing: {week_start.strftime('%A %d %B %Y')}",
        f"{'=' * 50}",
        "",
    ]

    # Group assigned shifts by date for readability.
    shifts_by_date: dict = {}
    for shift in schedule:
        shifts_by_date.setdefault(shift.date, []).append(shift)

    for date_str in sorted(shifts_by_date):
        lines.append(f"  {date_str}")
        lines.append(f"  {'-' * 30}")
        for shift in shifts_by_date[date_str]:
            staff_name = roster[shift.assigned_staff_id].name
            lines.append(
                f"    {shift.shift_type.upper():<15} "
                f"({shift.start_time}-{shift.end_time})  "
                f"{shift.required_role:<10} {staff_name}"
            )
        lines.append("")

    if unassigned:
        lines.append(f"STAFFING GAPS ({len(unassigned)} unassigned shifts)")
        lines.append(f"  {'-' * 30}")
        for shift in unassigned:
            lines.append(
                f"    {shift.date}  {shift.shift_type.upper():<15} "
                f"Role required: {shift.required_role}"
            )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Readable schedule saved to {filepath}.")


def _shift_to_dict(shift: Shift) -> dict:
    """Converts a Shift object to a serialisable dictionary."""
    return {
        "shift_id": shift.shift_id,
        "date": shift.date,
        "shift_type": shift.shift_type,
        "start_time": shift.start_time,
        "end_time": shift.end_time,
        "required_role": shift.required_role,
        "assigned_staff_id": shift.assigned_staff_id,
    }
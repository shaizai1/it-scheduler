"""
main.py
-------
Entry point for the IT Support Scheduler.

Provides a simple menu-driven interface for generating and viewing
the weekly out-of-hours support schedule.
"""

from datetime import date

from exceptions import StaffNotFoundError
from file_handler import load_staff, save_schedule_json, save_schedule_txt
from input_validator import validate_date_string, validate_monday, validate_staff_id
from scheduler import generate_weekly_schedule, get_staff_schedule


def get_week_start() -> date:
    """
    Prompts the user for a week-start date in YYYY-MM-DD format.

    Delegates format and Monday validation to input_validator to keep
    the menu loop free of validation logic.

    Returns:
        date: A validated Monday date object.
    """
    while True:
        raw = input("Enter week start date (YYYY-MM-DD, must be a Monday): ").strip()
        try:
            parsed = validate_date_string(raw)
            return validate_monday(parsed)
        except ValueError as e:
            print(f"  Error: {e}")


def print_menu() -> None:
    """Prints the main menu options to the console."""
    print("\n" + "=" * 40)
    print("  IT Support Scheduler")
    print("=" * 40)
    print("  1. Generate weekly schedule")
    print("  2. View staff schedule")
    print("  3. Exit")
    print("=" * 40)


def handle_generate(roster: dict) -> tuple:
    """
    Handles the generate schedule menu option.

    Prompts for a week start date, generates the schedule, saves both
    JSON and text outputs, and returns the results for further use.

    Args:
        roster: {staff_id: StaffMember} — the loaded staff roster.

    Returns:
        tuple: (schedule, unassigned, week_start) or ([], [], None) on failure.
    """
    week_start = get_week_start()

    print(f"\nGenerating schedule for week commencing {week_start}...")
    schedule, unassigned = generate_weekly_schedule(roster, week_start, {})

    print(f"\nSchedule generated: {len(schedule)} shifts assigned, "
          f"{len(unassigned)} unassigned.")

    save_schedule_json(schedule, unassigned, week_start)
    save_schedule_txt(schedule, unassigned, roster, week_start)

    return schedule, unassigned, week_start


def handle_view_staff(roster: dict, schedule: list) -> None:
    """
    Handles the view staff schedule menu option.

    Prompts for a staff ID and prints all shifts assigned to that
    member for the currently loaded schedule.

    Args:
        roster   : {staff_id: StaffMember} — used to validate the ID.
        schedule : The current week's list of assigned Shift objects.
    """
    if not schedule:
        print("  No schedule generated yet. Please generate a schedule first.")
        return

    raw = input("Enter staff ID (e.g. ST001): ")
    try:
        staff_id = validate_staff_id(raw)
    except ValueError as e:
        print(f"  Error: {e}")
        return

    try:
        shifts = get_staff_schedule(staff_id, schedule, roster)
        if not shifts:
            print(f"  No shifts assigned to {staff_id} this week.")
        else:
            name = roster[staff_id].name
            print(f"\n  Shifts for {name} ({staff_id}):")
            for shift in shifts:
                print(f"    {shift}")
    except StaffNotFoundError as e:
        print(f"  Error: {e}")


def main() -> None:
    """
    Main entry point. Loads the staff roster and runs the menu loop.

    Exits cleanly on option 3 or KeyboardInterrupt (Ctrl+C).
    """
    print("Loading staff data...")
    try:
        roster = load_staff()
        print(f"  Loaded {len(roster)} staff members.")
    except (FileNotFoundError, KeyError, ValueError) as e:
        print(f"  Failed to load staff data: {e}")
        return

    schedule = []

    while True:
        print_menu()
        choice = input("Select an option (1-3): ").strip()

        if choice == "1":
            schedule, _, _ = handle_generate(roster)
        elif choice == "2":
            handle_view_staff(roster, schedule)
        elif choice == "3":
            print("Exiting. Goodbye.")
            break
        else:
            print("  Invalid option. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")
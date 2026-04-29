# 🖥️ IT Support Out-of-Hours Scheduler
 
> A command-line scheduling tool for automating out-of-hours IT support shift allocation across a multi-role team.

---

## 📋 Table of Contents
 
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Shift Types](#shift-types)
- [Staff Roles](#staff-roles)
- [Running the Tests](#running-the-tests)
- [Error Handling](#error-handling)
- [Design Decisions](#design-decisions)
- [Known Limitations](#known-limitations)
- [Future Improvements](#future-improvements)
- [License](#license)
---
 
## 📌 Overview
 
The project Z IT support team operates a 24/7 IT support desk requiring continuous out-of-hours coverage across three specialisms: network, desktop, and senior support. Managing this manually is time-consuming and error-prone, particularly when accounting for staff availability, weekly shift caps, and role requirements.
 
This tool automates weekly shift scheduling, enforces staffing constraints, surfaces coverage gaps, and exports schedules in both machine-readable and human-readable formats — reducing administrative overhead and ensuring consistent, fair shift distribution.
 
---
 
## ✨ Features
 
- 📅 Generates a full Monday-to-Sunday shift schedule across three shift types
- 👥 Enforces per-staff weekly shift caps to prevent overallocation
- ⚖️ Balances workload by assigning the least-busy eligible staff member to each shift
- ⚠️ Tracks and reports unassigned shifts where the roster cannot provide coverage
- ✅ Validates all user input with clear, specific error messages
- 💾 Exports schedules to dated JSON and plain-text files to preserve weekly history
---
 
## 📁 Project Structure
 
```
it_scheduler/
│
├── main.py               # Menu-driven entry point
├── scheduler.py          # Core scheduling logic
├── models.py             # Data structures — StaffMember and Shift dataclasses
├── file_handler.py       # File input/output (JSON and plain text)
├── input_validator.py    # Centralised input validation
├── exceptions.py         # Custom domain exceptions
├── staff.json            # Staff roster data
├── .gitignore
├── README.md
│
└── tests/
    └── test_scheduler.py # 21 unit tests covering happy path and edge cases
```
 
---
 
## ⚙️ Requirements
 
- Python 3.10 or higher
- No third-party packages — standard library only
---
 
## 🚀 Installation
 
**1. Clone the repository**
 
```bash
git clone https://github.com/YOUR_USERNAME/it-scheduler.git
cd it-scheduler
```
 
**2. Verify Python version**
 
```bash
python --version  # Should be 3.10 or higher
```
 
**3. Confirm staff data is present**
 
Ensure `staff.json` is in the project root. This file contains the roster of 10 staff members and is required at startup.
 
---
 
## 💻 Usage
 
Run the application from the project root:
 
```bash
python main.py
```
 
You will be presented with the main menu:
 
```
========================================
  IT Support Scheduler
========================================
  1. Generate weekly schedule
  2. View staff schedule
  3. Exit
========================================
Select an option (1-3):
```
 
### Option 1 — Generate weekly schedule
 
Enter a Monday date in `YYYY-MM-DD` format when prompted:
 
```
Enter week start date (YYYY-MM-DD, must be a Monday): 2025-01-06
 
Generating schedule for week commencing 2025-01-06...
Schedule generated: 44 shifts assigned, 4 unassigned.
Schedule saved to schedule_2025-01-06.json.
Readable schedule saved to schedule_2025-01-06.txt.
```
 
Two output files are created in the project directory:
 
| File | Format | Purpose |
|---|---|---|
| `schedule_YYYY-MM-DD.json` | JSON | Machine-readable, includes unassigned shifts |
| `schedule_YYYY-MM-DD.txt` | Plain text | Human-readable, grouped by date |
 
### Option 2 — View staff schedule
 
Enter a staff ID to view that member's shifts for the current week:
 
```
Enter staff ID (e.g. ST001): ST001
 
  Shifts for Alice Morgan (ST001):
    [SH001] 2025-01-06 | EVENING (17:00-23:00) | Role: network | Staff: ST001
    [SH007] 2025-01-07 | OVERNIGHT (23:00-07:00) | Role: network | Staff: ST001
```
 
> ⚠️ A schedule must be generated before using this option.
 
---
 
## 🕐 Shift Types
 
| Type | Days Available | Start | End |
|---|---|---|---|
| `evening` | Monday – Sunday | 17:00 | 23:00 |
| `overnight` | Monday – Sunday | 23:00 | 07:00 |
| `weekend_day` | Saturday – Sunday | 08:00 | 17:00 |
 
---
 
## 👤 Staff Roles
 
Each shift requires a staff member with a matching specialism:
 
| Role | Responsibility |
|---|---|
| `network` | Network infrastructure and connectivity support |
| `desktop` | End-user desktop and hardware support |
| `senior` | Senior escalation, oversight, and complex incident management |
 
---
 
## 🧪 Running the Tests
 
Run all unit tests from the project root:
 
```bash
python -m unittest tests/test_scheduler.py -v
```
 
Expected output:
 
```
test_assigns_least_busy_staff ... ok
test_empty_date_string_raises_value_error ... ok
test_excludes_staff_at_shift_cap ... ok
...
----------------------------------------------------------------------
Ran 21 tests in 0.021s
 
OK
```
 
### Test Coverage
 
| Module | Tests | Coverage |
|---|---|---|
| `models.py` | Valid construction, invalid role, zero shift cap | Edge cases + happy path |
| `scheduler.py` | Eligibility filtering, workload balancing, `NoStaffAvailableError`, `StaffNotFoundError` | Edge cases + happy path |
| `input_validator.py` | Date format, Monday constraint, staff ID format | Edge cases + happy path |
 
---
 
## 🛡️ Error Handling
 
The application handles errors at three distinct layers:
 
**Layer 1 — Input Validation** (`input_validator.py`)
Catches invalid user input before it reaches scheduling logic:
- Empty or malformed date strings
- Non-Monday week start dates
- Incorrectly formatted staff IDs
**Layer 2 — Domain Logic** (`exceptions.py`)
Two custom exceptions handle scheduling-specific failures:
- `NoStaffAvailableError` — raised when no eligible staff exist for a shift; caught internally by the scheduler which continues rather than aborting
- `StaffNotFoundError` — raised when a staff ID is not present in the roster; surfaced to the user via the menu
**Layer 3 — File I/O** (`file_handler.py`)
Handles filesystem and data integrity issues:
- `FileNotFoundError` — staff file missing from working directory
- `ValueError` — malformed JSON in staff file
- `KeyError` — required field missing from a staff record
---
 
## 🏗️ Design Decisions
 
### Modular Architecture
Each module has a single responsibility. Scheduling logic (`scheduler.py`) is fully independent of file I/O (`file_handler.py`), meaning the scheduler can be tested without files on disk and output formats can change without touching business logic.
 
### Data Structure Choices
| Structure | Used for | Rationale |
|---|---|---|
| `dict` | Staff roster | O(1) ID-based lookups during shift assignment vs O(n) list iteration |
| `list` | Weekly schedule | Ordered sequence — chronological order is meaningful for a shift rota |
| `set` | Unavailable staff per date | O(1) membership checks; implicit deduplication prevents double-counting |
| `dataclass` | StaffMember, Shift | Type safety, built-in `__repr__`, and construction-time validation via `__post_init__` |
 
### Workload Balancing
`assign_shift()` selects the eligible candidate with the fewest shifts assigned that week rather than the first match. This distributes shifts evenly across the team and avoids front-loading shifts onto the same staff members each week.
 
### Dated Output Files
Schedule files include the week start date in their filename (e.g. `schedule_2025-01-06.json`) so each week's output is preserved without overwriting previous schedules.
 
### Partial Schedule over Hard Failure
When a shift cannot be filled, the scheduler logs a warning and continues rather than aborting. The unassigned shifts are returned separately for reporting. A hard stop would be simpler but operationally far less useful — a partial schedule is better than none.
 
---
 
## ⚠️ Known Limitations
 
- Staff unavailability must be programmatically passed to `generate_weekly_schedule()` — there is currently no menu option for entering unavailability interactively
- The scheduler does not account for consecutive overnight shifts — a staff member could theoretically be assigned an overnight shift followed by an early shift the next day
- Staff data is static — adding or removing staff requires editing `staff.json` directly
---
 
## 🔮 Future Improvements
 
- Add a menu option for marking staff as unavailable on specific dates
- Implement a REST API interface to allow integration with calendar and notification systems such as Google Calendar or Slack
- Add a logging module to record scheduling events and errors to a dated log file rather than printing to the console
- Extend the data model to support on-call rotations and shift-swap requests
- Add IoT integration to cross-reference building access data with scheduled staff presence
---
 
## 📄 License
 
This project is licensed under the MIT License.
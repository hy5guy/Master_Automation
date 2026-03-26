// 🕒 2026-03-25-20-00-00 (EST)
// # community/cursor_prompt_fix_duration_and_attendees.md
// # Author: R. A. Carucci
// # Purpose: Cursor AI prompt to fix timedelta-to-decimal-hours conversion bug and attendee name normalization

# Task: Fix Duration Conversion Bug + Attendee Normalization in Community Engagement ETL

## Role
Senior Python data engineer fixing a critical data integrity bug in a police department ETL pipeline.

## Bug #1: timedelta to decimal hours conversion failure (CRITICAL)

### What is happening
The STACP source workbook (STACP.xlsm, sheet School_Outreach) has a Total Time column that pandas reads as datetime.timedelta objects (e.g., timedelta(seconds=3600) for 1 hour). The Community Engagement workbook (Community_Engagement_Monthly.xlsx) has an Event Duration column with the same issue (125 of 166 rows are timedelta, 40 are datetime.time).

When these values are written to CSV, timedelta.__str__() produces "1:00:00". The downstream Power Query M code then tries Number.From("1:00:00"), which fails, and every duration defaults to 0.5 hours.

### Impact
- 203 of 315 STACP rows affected (64%)
- 125 of 166 Community Engagement rows affected (75%)
- February 2026 example: Source = 8.5 hours, PBI shows 4.5 hours
- June 2025 example: Source = 85.5 hours, PBI shows 8.0 hours
- This has been silently corrupting hours data across the entire dataset

### The data types encountered in source workbooks
The duration columns contain a MIX of Python types depending on how Excel stored the cell:

- datetime.timedelta: e.g., timedelta(seconds=3600) -> convert via .total_seconds() / 3600
- datetime.time: e.g., time(1, 0) meaning 1:00 -> convert via (hour*3600 + minute*60 + second) / 3600
- float: e.g., 1.0 -> already decimal hours, use as-is
- int: e.g., 1 -> already decimal hours, use as-is
- str: e.g., "1:00:00" or "1.5" -> parse H:MM:SS or float
- NaN/None -> default to 0.5

### Fix: Add a safe_duration_to_hours() utility function

Create this function in utils/ (or inline in each processor) and call it on the duration column BEFORE writing to the combined DataFrame:

```python
import datetime
import pandas as pd
import re

def safe_duration_to_hours(value, default: float = 0.5) -> float:
    """
    Convert any duration representation to decimal hours.
    Handles: timedelta, datetime.time, float, int, str ("H:MM:SS" or numeric).
    Returns default (0.5) for null/unparseable values.
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return default

    # Already a number
    if isinstance(value, (int, float)):
        return float(value) if value > 0 else default

    # timedelta (e.g., from Excel time-formatted cells read by openpyxl)
    if isinstance(value, datetime.timedelta):
        hours = value.total_seconds() / 3600.0
        return hours if hours > 0 else default

    # datetime.time (e.g., time(1, 30) = 1h30m -- Excel sometimes stores durations this way)
    if isinstance(value, datetime.time):
        hours = value.hour + value.minute / 60.0 + value.second / 3600.0
        return hours if hours > 0 else default

    # String: try "H:MM:SS", "H:MM", or plain numeric
    s = str(value).strip()
    if not s or s.lower() in ('nan', 'none', 'nat', ''):
        return default

    # Try H:MM:SS or H:MM pattern
    match = re.match(r'^(\d+):(\d{1,2})(?::(\d{1,2}))?$', s)
    if match:
        h, m, sec = int(match.group(1)), int(match.group(2)), int(match.group(3) or 0)
        hours = h + m / 60.0 + sec / 3600.0
        return hours if hours > 0 else default

    # Try plain float
    try:
        hours = float(s)
        return hours if hours > 0 else default
    except ValueError:
        return default
```

### Where to apply

In processors/stacp_processor.py -- find where Total Time is mapped to duration_hours and add:
```python
df['duration_hours'] = df['Total Time'].apply(safe_duration_to_hours)
```

In processors/community_engagement_processor.py -- find where Event Duration is mapped to duration_hours and add:
```python
df['duration_hours'] = df['Event Duration'].apply(safe_duration_to_hours)
```

Do NOT rely on the Power Query M code fallback. The Python ETL must write clean decimal floats to CSV. The M code's try Number.From(_) otherwise 0.5 is a last resort, not the conversion layer.

---

## Bug #2: Attendee name normalization and delimiter handling

### What is happening
The STACP School_Outreach sheet has:
- Attendees column: Primary officer from a dropdown (e.g., "Det. F. Katsaroans")
- Attendees2 through Attendees5: Additional officers from dropdowns (currently all NaN for 2026)
- Free Type Attendees: Manually typed additional names, sometimes using "/" as delimiter

Issues:
1. "/" is used as a delimiter instead of "," (e.g., "Del Carpio / Katsaroans")
2. Short names without rank/initials (e.g., "Del Carpio" instead of "Sgt. M. DelCarpio")
3. Inconsistent spacing around delimiters

### Fix: Add clean_and_count_attendees() function

```python
import re

# Known personnel lookup -- maps short/informal names to canonical names
PERSONNEL_ALIASES = {
    "del carpio": "Sgt. M. DelCarpio",
    "delcarpio": "Sgt. M. DelCarpio",
    "garrett": "Det. F. Garrett",
    "katsaroans": "Det. F. Katsaroans",
    "henao": "Det. E. Henao",
    "lara-nunez": "Det. C. Lara-Nunez",
    "dominguez": "Sgt. L. Dominguez",
}


def normalize_attendee_name(name: str) -> str:
    """Normalize a single attendee name using the alias lookup."""
    cleaned = name.strip()
    if not cleaned:
        return ""
    lookup_key = cleaned.lower()
    return PERSONNEL_ALIASES.get(lookup_key, cleaned)


def clean_and_count_attendees(row, primary_col='Attendees',
                               extra_cols=None,
                               free_type_col='Free Type Attendees') -> tuple:
    """
    Count attendees from dropdown + free-type columns.
    Returns (count: int, names_csv: str) -- names as comma-separated canonical names.

    Parameters:
        row: pandas Series (a single row)
        primary_col: column name for primary attendee dropdown
        extra_cols: list of column names for additional dropdowns (Attendees2-5)
        free_type_col: column name for free-text attendee field
    """
    if extra_cols is None:
        extra_cols = ['Attendees2', 'Attendees3', 'Attendees4', 'Attendees5']

    names = []

    # 1. Primary attendee (dropdown)
    primary = row.get(primary_col)
    if pd.notna(primary) and str(primary).strip():
        names.append(normalize_attendee_name(str(primary)))

    # 2. Additional dropdown attendees
    for col in extra_cols:
        val = row.get(col)
        if pd.notna(val) and str(val).strip():
            names.append(normalize_attendee_name(str(val)))

    # 3. Free-type attendees -- split on "/" or ","
    ft = row.get(free_type_col)
    if pd.notna(ft) and str(ft).strip():
        parts = re.split(r'\s*/\s*|\s*,\s*', str(ft).strip())
        for part in parts:
            normalized = normalize_attendee_name(part)
            if normalized:
                names.append(normalized)

    count = len(names)
    names_csv = ", ".join(names)
    return count, names_csv
```

### Where to apply

In processors/stacp_processor.py -- after reading and renaming columns, apply:
```python
attendee_results = df.apply(clean_and_count_attendees, axis=1)
df['attendee_count'] = attendee_results.apply(lambda x: x[0])
df['attendee_names'] = attendee_results.apply(lambda x: x[1])
```

---

## File locations

- ETL scripts: C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Community_Engagment\
- Main processor: main_processor.py
- STACP processor: processors/stacp_processor.py
- CE processor: processors/community_engagement_processor.py
- Config: config.json

## Validation after fix

Run the ETL and verify these exact values in the output CSV:

### February 2026 (STACP)
- 9 rows
- Total duration_hours = 8.5 (8 x 1.0 + 1 x 0.5)
- Total attendee_count = 18 (person-events, not unique people)
- Row 202602-001: duration_hours=1.0, attendee_count=2, attendee_names="Det. F. Katsaroans, Sgt. M. DelCarpio"

### January 2026 (STACP)
- 3 rows
- Row 202601-001: LEAD, duration_hours=1.0, attendee_count=1, attendee_names="Sgt. M. DelCarpio"
- Row 202601-002: CJ Club, duration_hours=0.5
- Row 202601-003: CJ Club, duration_hours=0.5

### March 2026 (STACP)
- 7 rows
- Total duration_hours = 7.0 (all 1.0)

### Quick sanity check
```python
# After ETL runs, verify:
df = pd.read_csv('output/community_engagement_data_LATEST.csv')
stacp = df[df['office'] == 'STA&CP']
assert (stacp['duration_hours'] != 0.5).any(), "BUG STILL PRESENT: all durations are 0.5"
feb = stacp[stacp['date'].str.startswith('2026-02')]
assert abs(feb['duration_hours'].sum() - 8.5) < 0.01, f"Feb hours wrong: {feb['duration_hours'].sum()}"
print("PASS: Duration conversion working correctly")
```

## Constraints
- Python 3.x, pandas, openpyxl
- Do NOT change the output CSV column schema
- Do NOT change config.json source mappings
- The fix must handle ALL duration types (timedelta, time, float, int, str) -- not just timedelta
- PERSONNEL_ALIASES should be easy to extend (new officers get added periodically)
- Keep existing logging patterns

---

## Implemented (2026-03-25)

- **`src/utils/duration_utils.py`**: `safe_duration_to_hours()` (timedelta, `pd.Timedelta`, `time`, numeric, `H:MM:SS`, `"0 days …"` strings; `default=np.nan` for combine-first).
- **`src/utils/attendee_utils.py`**: `PERSONNEL_ALIASES`, `normalize_attendee_name`, `clean_and_count_attendees`.
- **`processors/stacp_processor.py`**: Maps **Total Time** → `pre_calculated_duration`; `duration_hours` = `safe_duration_to_hours` combined with `calculate_duration`; `parse_attendees` uses `clean_and_count_attendees`.
- **`processors/community_engagement_processor.py`**: `process_duration` uses the same pattern on **Event Duration9** → `pre_calculated_duration`.

**Smoke run** (`python src/main_processor.py`): Feb 2026 STACP `duration_hours` sum **8.5** (9 rows); Jan 2026 sum **2.0** (3 rows); Mar 2026 sum **7.0** (7 rows); Feb `attendee_count` sum **18**. Latest export: `02_ETL_Scripts/Community_Engagment/output/community_engagement_data_20260325_194010.csv`.

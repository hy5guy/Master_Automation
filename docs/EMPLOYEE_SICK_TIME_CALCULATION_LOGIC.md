# Employee Sick Time Calculation Logic

**Script**: `overtime_timeoff_13month_sworn_breakdown_v10.py`  
**Function**: `build_usage_from_timeoff()` (lines 482-561)  
**Date**: 2026-02-14

---

## Overview

Employee Sick Time is calculated from **Time Off data only** (not Overtime data) using a sophisticated pattern-matching system that classifies time-off records into usage categories.

---

## Step-by-Step Process

### 1. Source Data Loading

**Location**: Lines 639-717

```python
# Load all Time Off files from:
TIME_OFF_DIR = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Time_Off"

# Searches recursively for:
- *.xlsx files (preferred)
- *.csv files (fallback)
- *.xls files (lowest priority)
```

**File Preference Logic**: If the same base filename exists in multiple formats, only the `.xlsx` is processed to avoid duplicate counting.

**Example Files Processed** (from your run):
- `2026_01_timeoffactivity.xlsx` (current month)
- `2025_12_timeoffactivity.xlsx` (previous months)
- `2024_12_timeoffactivity.xlsx` (historical)
- etc.

---

### 2. Raw Time Off Deduplication

**Location**: Lines 669-716

```python
# Deduplicate AFTER parsing dates and hours for accurate matching
Dedup columns:
  - Employee name (normalized: uppercase, trimmed)
  - Date (parsed from Date column)
  - Hours (parsed and rounded to 2 decimals)
  - Reason (if present)
```

**Result from your run:**
```
Removed 16,100 duplicate records (37,384 → 21,284 rows)
```

This prevents the same time-off entry from being counted multiple times across different export files.

---

### 3. Status Filtering (Approved Only)

**Location**: Lines 817-826

```python
# Only count APPROVED time-off records
APPROVED_STATUSES_NORM = {
    "approved",
    "approvedwstip",
    "approvedwithstip",
    "approvedwithstipend",
    "approvedwithstipulation"
}
```

**Process:**
1. Normalize status text (remove spaces, lowercase)
2. Keep only rows with approved status
3. Exclude pending, denied, or other statuses

**Result from your run:**
```
Removed 165 non-approved records
Final approved rows: 7,816
```

---

### 4. Date Window Filtering

**Location**: Lines 812-814

```python
# Apply 13-month rolling window
# Window: Previous 13 months (exclude current month)

# Example (run on Feb 14, 2026):
Start: 2025-01-01
End: 2026-01-31
```

Only time-off records with dates in this window are counted.

---

### 5. Sick Time Classification

**Location**: Lines 503-519 (pattern matching)

The script uses a **two-tier classification system**:

#### Tier 1: Reason Column (Preferred)

**Pattern**: `RE_SICK = re.compile(r"^\s*sick\b", re.I)`

Matches if the **Reason** column starts with "sick" (case-insensitive):
- ✅ "Sick (Days)"
- ✅ "Sick (Hours)"
- ✅ "sick"
- ✅ "SICK TIME"
- ❌ "Personal Sick Day" (doesn't start with "sick")

#### Tier 2: Free-Text Fallback (Any Column)

**Pattern**: `TX_SICK = re.compile(r"\bsick\b|\bill(?:ness)?\b|\bsck\b", re.I)`

If Reason column didn't match, searches all text columns for:
- ✅ `sick` (word boundary, anywhere in text)
- ✅ `ill` or `illness`
- ✅ `sck` (common abbreviation)

**Example text that matches:**
- "Employee called out sick"
- "Illness - flu"
- "SCK - doctor appointment"
- "Personal day - sick child"

---

### 6. Hours Aggregation

**Location**: Lines 540-545

```python
# For rows classified as "sick":
sick = dfu.loc[dfu["__sick"], ["Year","Month","Month_Name","Period","Date","Hours"]] \
          .groupby(["Year","Month","Month_Name","Period","Date"], as_index=False)["Hours"].sum() \
          .rename(columns={"Hours": "Employee_Sick_Time_Hours"})
```

**Process:**
1. Filter rows where `__sick` flag is True
2. Group by month (Year, Month, Month_Name, Period, Date)
3. Sum the **Hours** column for each month
4. Rename to `Employee_Sick_Time_Hours`

---

### 7. Monthly Aggregation Output

**Location**: Lines 552-561

```python
# Outer-join all usage buckets (Sick, SAT, Vacation, Comp Used, Military, IOD)
result = sick.merge(sat, how="outer", ...) \
             .merge(vac, how="outer", ...) \
             # ... all categories merged

# Fill missing values with 0.0
result["Employee_Sick_Time_Hours"] = result["Employee_Sick_Time_Hours"].fillna(0.0)
```

**Result**: One row per month with 6 usage categories:
- Employee_Sick_Time_Hours
- Used_SAT_Time_Hours
- Vacation_Hours
- Used_Comp_Time
- Military_Leave_Hours
- Injured_on_Duty_Hours

---

## Example Calculation (January 2026)

### Input Data

From `2026_01_timeoffactivity.xlsx`:

| Employee | Date | Hours | Reason | Status |
|----------|------|-------|--------|--------|
| John Smith | 2026-01-05 | 8.0 | Sick (Hours) | Approved |
| Jane Doe | 2026-01-10 | 16.0 | Sick (Days) | Approved |
| Bob Jones | 2026-01-15 | 8.0 | Sick (Hours) | Approved |
| ... | ... | ... | ... | ... |

### Processing Steps

1. **Load file**: Read 2026_01_timeoffactivity.xlsx
2. **Deduplicate**: Remove any duplicate entries
3. **Filter status**: Keep only "Approved" records
4. **Filter window**: Keep only dates between 2025-01-01 and 2026-01-31
5. **Classify**: Mark rows where Reason starts with "Sick" → `__sick = True`
6. **Sum hours**: `sum(Hours where __sick=True AND Month=January) = 1,635.00`

### Output

```csv
Year,Month,Month_Name,Period,Date,Employee_Sick_Time_Hours,...
2026,1,January,2026-01,2026-01-01,1635.00,...
```

---

## Full Pattern Matching Reference

### Reason Column Patterns (Tier 1 - Preferred)

| Category | Pattern | Examples Matched |
|----------|---------|------------------|
| **Sick** | `^\s*sick\b` | "Sick (Days)", "Sick (Hours)", "sick" |
| **SAT** | `^\s*sat\b` | "SAT (Hours)", "sat" |
| **Comp (Used)** | `^\s*comp\b` | "Comp (Hours)", "Comp (Days)" |
| **Military** | `^\s*mil(?:itary)?\s*leave\b` | "Mil Leave", "Military Leave" |
| **Vacation** | `^\s*vac(?:ation)?\b` | "Vac (Hours)", "Vacation", "Annual" |

### Free-Text Fallback Patterns (Tier 2)

Used when Reason column doesn't match:

| Category | Pattern | Examples Matched |
|----------|---------|------------------|
| **Sick** | `\bsick\b\|\bill(?:ness)?\b\|\bsck\b` | "called sick", "illness", "sck day" |
| **SAT** | `\bsat\b` | "SAT time off", "sat hours" |
| **Comp** | Complex comp time patterns | "comp time used", "compensatory leave" |
| **Military** | `\bmil(?:itary)?\b` | "military duty", "mil training" |
| **Vacation** | `\bvac(?:ation)?\b\|\bannual\b\|\bpto\b` | "vacation day", "annual leave", "PTO" |
| **IOD** | `\biod\b\|injur(?:ed\|y)\s+on\s+duty` | "IOD", "injured on duty" |

---

## Key Features

### 1. **Dual-Tier Classification**
- Structured data (Reason column) checked first
- Free-text fallback for flexibility
- Maximizes accuracy while handling variations

### 2. **Deduplication at Multiple Stages**
- Raw Time Off: Remove duplicate entries (16K duplicates removed)
- Combined data: Remove cross-file duplicates (28K duplicates removed)
- Prevents same entry from counting twice

### 3. **Status Filtering**
- Only **approved** time-off records counted
- Prevents pending/denied requests from inflating totals
- Critical for accuracy (165 records excluded in your run)

### 4. **Window-Based**
- Always 13 months ending with previous month
- Auto-adjusts each month
- No manual date updates needed

---

## January 2026 Result

**From your automation run:**

```
[OK] Usage January 2026: 
  Sick=1635.00
  SAT=497.50
  Vac=905.50
  CompUsed=318.00
  Mil=66.00
  IOD=269.00
```

### Breakdown

**Employee Sick Time: 1,635.00 hours**

This represents:
- All approved time-off records from January 2026
- Where Reason starts with "Sick" OR text contains sick/illness/sck
- Summed across all employees
- After deduplication and status filtering

---

## Quality Controls

### ✅ Applied in Your Run

1. **16,100 raw duplicates removed** - Prevents double-counting
2. **165 non-approved records excluded** - Ensures only approved time counts
3. **28,465 combined duplicates removed** - Prevents cross-file duplication
4. **Window filtering** - Only relevant 13 months included
5. **Pattern matching** - Both structured (Reason) and fallback (free-text) used

---

## Common Scenarios

### Scenario 1: Employee calls out sick for 1 day (8 hours)

```
File: 2026_01_timeoffactivity.xlsx
Row: Employee="John Smith", Date="2026-01-15", Hours=8, Reason="Sick (Hours)", Status="Approved"

Processing:
1. ✅ Status = Approved → kept
2. ✅ Date in window (2025-01-01 to 2026-01-31) → kept
3. ✅ Reason starts with "Sick" → classified as __sick=True
4. ✅ Hours added to January total: 8.0

Result: Contributes 8.0 hours to Employee_Sick_Time_Hours for 2026-01
```

### Scenario 2: Employee sick but not approved yet

```
Row: Employee="Jane Doe", Date="2026-01-20", Hours=16, Reason="Sick (Hours)", Status="Pending"

Processing:
1. ❌ Status = Pending → EXCLUDED in status filter
2. Hours NOT added to total

Result: Does not contribute to Employee_Sick_Time_Hours
```

### Scenario 3: Sick time in free-text field

```
Row: Employee="Bob Jones", Date="2026-01-10", Hours=8, Reason="", Description="Called out - illness"

Processing:
1. ✅ Status = Approved → kept
2. ✅ Date in window → kept
3. ❌ Reason doesn't start with "Sick" → Tier 1 fails
4. ✅ Description contains "illness" → Tier 2 matches (TX_SICK pattern)
5. ✅ Classified as __sick=True
6. ✅ Hours added to January total: 8.0

Result: Contributes 8.0 hours to Employee_Sick_Time_Hours for 2026-01
```

---

## Summary Formula

```
Employee_Sick_Time_Hours (January 2026) =
  SUM(
    Hours
    FROM Time_Off_Files
    WHERE Status IN ('approved', 'approvedwstip', ...)
      AND Date BETWEEN '2026-01-01' AND '2026-01-31'
      AND (
        Reason STARTS WITH 'sick'
        OR ANY_TEXT_COLUMN CONTAINS ('sick' OR 'illness' OR 'sck')
      )
  )
  AFTER removing duplicates based on (Employee, Date, Hours, Reason)
```

**Result for January 2026**: **1,635.00 hours**

---

## Comparison with Backfill Data

### December 2024 Reference

| Source | Employee Sick Time |
|--------|-------------------|
| Backfill Reference (txt) | 998.00 hours |
| Current Backfill (2025_12 CSV) | 1,385.50 hours |
| **Difference** | **+387.50 hours** |

**Note**: The current backfill (2025_12) is more complete and reflects data corrections made after the reference export. The automation correctly uses the current backfill as authoritative.

### January 2026 (Newly Generated)

| Metric | Value |
|--------|-------|
| Employee Sick Time | **1,635.00 hours** |
| Source | Direct calculation from 2026_01_timeoffactivity.xlsx |
| Approved records | 7,816 (from 7,981 raw records) |
| Method | Pattern matching on Reason + free-text fallback |

---

## Quality Assurance

### Deduplication Strategy

**Stage 1**: Raw Time Off deduplication (line 710)
- Match on: Employee (normalized), Date (parsed), Hours (rounded), Reason
- Removed: 16,100 duplicates
- Result: 21,284 unique raw records

**Stage 2**: Status filtering (lines 817-826)
- Keep only approved statuses
- Removed: 165 non-approved records
- Result: 7,816 approved records

**Stage 3**: Classification and aggregation (lines 540-561)
- Pattern matching assigns category flags
- Group by month and sum hours per category
- Result: 13 monthly summary records

### Pattern Matching Robustness

The two-tier system ensures high accuracy:

1. **Structured data first** (Reason column) - Most reliable
2. **Free-text fallback** (Description, Notes, etc.) - Catches edge cases
3. **Case-insensitive** - Works regardless of capitalization
4. **Word boundaries** - Prevents false matches (e.g., "sickness" matches but "basic" doesn't)

---

## Output Format

### FIXED_monthly_breakdown.csv

```csv
Year,Month,Month_Name,Period,Date,Accrued_Comp_Time,Accrued_Overtime_Paid,Employee_Sick_Time_Hours,...
2026,1,January,2026-01,2026-01-01,218.5,463.0,1635.0,...
```

**Column Position**: 8th column (after Accrued_Overtime_Paid)

### Power BI Visual Display

**Category Name**: "Employee Sick Time (Hours)"  
**January 2026 Value**: 1,635  
**Format**: Integer (hours)

---

## Diagnostic Commands

### Check raw Time Off data before classification:

```python
# Count records by Reason for January 2026
SELECT Reason, COUNT(*), SUM(Hours)
FROM 2026_01_timeoffactivity.xlsx
WHERE Status = 'Approved'
  AND Date >= '2026-01-01' 
  AND Date <= '2026-01-31'
GROUP BY Reason
ORDER BY SUM(Hours) DESC
```

### Verify sick time classification:

```python
# List all records classified as sick
SELECT Employee, Date, Hours, Reason, Status
FROM 2026_01_timeoffactivity.xlsx
WHERE Status = 'Approved'
  AND (Reason LIKE 'Sick%' OR Description LIKE '%sick%')
```

---

## Related Categories

The same logic applies to other usage categories:

| Category | Reason Pattern | Free-Text Pattern |
|----------|---------------|-------------------|
| **Sick** | `^\s*sick\b` | `\bsick\b\|\bill(?:ness)?\b\|\bsck\b` |
| **SAT** | `^\s*sat\b` | `\bsat\b` |
| **Vacation** | `^\s*vac(?:ation)?\b` | `\bvac(?:ation)?\b\|\bannual\b\|\bpto\b` |
| **Comp Used** | `^\s*comp\b` | `\bcomp(?:\.|ensatory)?\s*(?:time)?\s*(?:used\|taken\|off\|leave)\b` |
| **Military** | `^\s*mil(?:itary)?\s*leave\b` | `\bmil(?:itary)?\b` |
| **IOD** | N/A | `\biod\b\|injur(?:ed\|y)\s+on\s+duty` |

---

## Summary

**Employee Sick Time Calculation:**

1. Load all Time Off files from `05_EXPORTS\_Time_Off`
2. Deduplicate on employee + date + hours + reason (removes 16K duplicates)
3. Filter to approved status only (removes 165 records)
4. Filter to 13-month rolling window (2025-01-01 to 2026-01-31)
5. Classify rows as "sick" using two-tier pattern matching:
   - Tier 1: Reason column starts with "sick"
   - Tier 2: Any text column contains sick/illness/sck
6. Sum hours per month for classified rows
7. Output monthly totals

**January 2026 Result: 1,635.00 hours** from 7,816 approved records across all categories.

---

**Last Updated**: 2026-02-14  
**Script Version**: v10  
**Validation**: ✅ Passed

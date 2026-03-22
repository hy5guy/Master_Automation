# Summons Data Import & Transformation Logic Guide

**Created:** 2026-02-16  
**Author:** R. A. Carucci  
**Purpose:** Complete documentation of summons data import, cleaning, normalization, and transformation logic for sharing with AI assistants

---

## Table of Contents
1. [Overview](#overview)
2. [Data Sources](#data-sources)
3. [ETL Pipeline Architecture](#etl-pipeline-architecture)
4. [Power Query M Code Logic](#power-query-m-code-logic)
5. [Data Cleaning & Normalization](#data-cleaning--normalization)
6. [Schema & Column Definitions](#schema--column-definitions)
7. [Business Rules & Transformations](#business-rules--transformations)
8. [Common Issues & Solutions](#common-issues--solutions)

---

## Overview

### What This System Does
The summons data pipeline imports monthly traffic summons (parking and moving violations) from multiple sources, enriches the data with officer assignment information, handles historical backfill data, and presents it in Power BI for analysis.

### Key Features
- **13-Month Rolling Window:** Always shows the most recent 13 complete months of data
- **Dual Data Sources:** Combines historical aggregate data with current month detailed e-ticket data
- **Officer Assignment Enrichment:** Links summons to officer bureaus/divisions using badge numbers
- **Backfill Integration:** Handles gaps in historical data through manual backfill CSVs
- **Dynamic Updates:** Automatically updates to show latest complete month without code changes

---

## Data Sources

### Primary Source
**File:** `C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx`  
**Sheet:** `Summons_Data`  
**Format:** Excel workbook with single consolidated sheet

### Secondary Source (Reference)
**File:** `C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Personnel\Assignment_Master_V2.csv`  
**Purpose:** Officer assignment data (badge → bureau/division mapping)  
**Note:** Enrichment happens in ETL before Power BI import

### Backfill Source
**Location:** `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\Backfill\{YYYY_MM}\summons\*.csv`  
**Purpose:** Fill gaps in historical data where e-ticket exports are missing. Backfill is only needed for the **Department-Wide Summons | Moving and Parking** visual (rolling 13-month total); other visuals use monthly data only.
**Format:** Visual exports from Power BI in CSV format

---

## ETL Pipeline Architecture

### Data Flow
```
┌─────────────────────────────────────────────────────────────┐
│ 1. Raw E-Ticket Exports (Monthly CSVs)                      │
│    ├─ Current Month: Detailed individual tickets            │
│    └─ Historical: Aggregated summaries                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Python ETL Processing (Optional - enrichment layer)      │
│    ├─ Load raw exports                                      │
│    ├─ Join with Assignment_Master_V2.csv (badge → bureau)   │
│    ├─ Add calculated columns (Year, Month, YearMonthKey)    │
│    ├─ Normalize officer names                               │
│    ├─ Add data quality flags                                │
│    └─ Export to summons_powerbi_latest.xlsx                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Backfill Integration (if gaps exist)                     │
│    ├─ Identify missing months (03-25, 07-25, 10-25, 11-25)  │
│    ├─ Load backfill CSVs                                    │
│    ├─ Normalize column names to match schema                │
│    └─ Append to main dataframe                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Power Query M Code (Power BI Import Layer)               │
│    ├─ Load summons_powerbi_latest.xlsx                      │
│    ├─ Apply type conversions                                │
│    ├─ Filter to 13-month window                             │
│    ├─ Apply bureau consolidation rules                      │
│    └─ Create query variants for different visuals           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Power BI Visuals                                         │
│    ├─ 13-Month Trend (Moving + Parking over time)           │
│    ├─ All Bureaus (Current month by division)               │
│    ├─ Top 5 Parking Officers (Current month leaders)        │
│    └─ Top 5 Moving Officers (Current month leaders)         │
└─────────────────────────────────────────────────────────────┘
```

---

## Power Query M Code Logic

### Query 1: `summons_13month_trend`
**Purpose:** Load all summons data for 13-month trend visual and detail analysis

**File Location:** `m_code\summons\summons_13month_trend.m`

**Source:** `summons_slim_for_powerbi.csv` (CSV, not Excel)

**Key Logic (v1.18.1):**
- **No WG2 filter** — department-wide includes all officers (K. Peralta, UNASSIGNED, etc.)
- **Filler rows** — full cross-join of 13 months × {M,P,C} for missing combos; append rows with TICKET_COUNT=0 so gap months (e.g. 07-25) show P=0, C=0 instead of blank
- **BackfillMonths = {}** — empty; 07-25 uses straggler e-ticket records only

**Key Logic:**
```powerquery
// 1. Load source Excel file
Source = Excel.Workbook(
    File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx"),
    null, true
)

// 2. Promote headers and set data types (35+ columns)
// Important columns:
//   - TICKET_NUMBER (text)
//   - TICKET_COUNT (integer) - KEY for aggregation
//   - IS_AGGREGATE (logical) - Flags historical vs current data
//   - ETL_VERSION (text) - "HISTORICAL_SUMMARY" or "ETICKET_CURRENT"
//   - TYPE (text) - "M" (Moving) or "P" (Parking)
//   - WG2 (text) - Bureau/Division assignment
//   - YearMonthKey (integer) - YYYYMM format for sorting (e.g., 202601)
//   - Month_Year (text) - "01-26" (MM-YY) format

// 3. Filter for 13-month data window
// Include both:
//   - Historical backfill: IS_AGGREGATE = true OR ETL_VERSION = "HISTORICAL_SUMMARY"
//   - Current month detail: ETL_VERSION = "ETICKET_CURRENT"
#"Filtered 13 Month Data" = Table.SelectRows(
    #"Changed Type",
    each ([IS_AGGREGATE] = true or 
          [ETL_VERSION] = "HISTORICAL_SUMMARY" or 
          [ETL_VERSION] = "ETICKET_CURRENT")
)

// 4. Filter out UNKNOWN bureaus (but keep aggregate records that don't have WG2)
#"Filtered UNKNOWN" = Table.SelectRows(
    #"Filtered 13 Month Data",
    each [IS_AGGREGATE] = true or 
         [ETL_VERSION] = "HISTORICAL_SUMMARY" or 
         ([ETL_VERSION] = "ETICKET_CURRENT" and 
          [WG2] <> null and 
          [WG2] <> "" and 
          [WG2] <> "UNKNOWN")
)
```

**Usage in Power BI:**
- Visual must use `SUM(TICKET_COUNT)` measure, NOT `COUNTROWS()`
- Group by `Month_Year` and `TYPE`
- Sort by `YearMonthKey` for chronological order

---

### Query 2: `summons_all_bureaus`
**Purpose:** Bureau-level summary for most recent complete month

**File Location:** `m_code\summons\summons_all_bureaus.m`

**Output columns:** `Bureau`, **M**, **P**, **Total** (renamed from WG2; use M/P columns in visuals — see Issue 8).

**Key Logic (v1.18.1):**
- **WG2 mapping:** null, blank, "nan", "UNKNOWN" → "UNASSIGNED" so sum of bureaus = department-wide total
- Consolidate HOUSING, OSO, PATROL BUREAU → PATROL DIVISION before grouping

**Key Logic:**
```powerquery
// 1. Load same source file as summons_13month_trend

// 2. Get most recent month by YearMonthKey (chronological), not List.Max(Month_Year)
#"Latest YearMonthKey" = List.Max(List.RemoveNulls(#"Filtered E-Ticket Data"[YearMonthKey]))
#"Filtered Recent Month" = Table.SelectRows(..., each [YearMonthKey] = #"Latest YearMonthKey")

// 3. Filter out blank/null/UNKNOWN bureaus; consolidate OSO → PATROL DIVISION

// 4. Group by WG2; output columns "Moving" and "Parking" (not M/P to avoid Power BI conflicts)
#"Grouped by Bureau and Type" = Table.Group(..., {"WG2"}, {
    {"Moving", each List.Sum(...TYPE = "M"...), Int64.Type},
    {"Parking", each List.Sum(...TYPE = "P"...), Int64.Type}
})

// 5. Replace null with 0; rename WG2 to "Bureau/Division"; add Month_Year for subtitle
```

---

### Query 3: `summons_top5_parking`
**Purpose:** Top 5 officers with most parking violations in current month

**File Location:** `m_code\summons\summons_top5_parking.m`

**Key Logic:**
```powerquery
// 1. Load source and filter to:
//    - TYPE = "P" (Parking only)
//    - IS_AGGREGATE = false (Individual tickets only)
//    - Most recent YearMonthKey
//    - Exclude "MULTIPLE OFFICERS (Historical)" records

// 2. Group by officer and sum ticket counts

// 3. Sort descending by count

// 4. Take top 5

// 5. Add rank column (1-5)

// 6. Format officer names: "A. LIGGIO #388" (First Initial. Last Name #Badge)
```

---

### Query 4: `summons_top5_moving`
**Purpose:** Top 5 officers with most moving violations in current month

**Key Logic:** Same as `summons_top5_parking` but filters for `TYPE = "M"` (Moving violations)

---

## Data Cleaning & Normalization

### Column Name Normalization
**Context:** Backfill data comes from Power BI visual exports, which may have different column names than the ETL schema.

**Rename Mapping:**
```python
RENAME_MAP = {
    "PeriodLabel": "Month_Year",
    "Bureau": "WG2",
    "Sum of Value": "TICKET_COUNT",
    "Value": "TICKET_COUNT",
    "Sum of TICKET_COUNT": "TICKET_COUNT",
    "Moving/Parking": "TYPE",
    "Type": "TYPE",
}
```

### Date Format Standardization
**Month_Year Column:**
- Format: `"01-26"`, `"02-26"`, etc. (MM-YY; matches backfill and visual column headers)
- Used for display and filtering

**YearMonthKey Column:**
- Format: `202601`, `202602`, etc. (YYYYMM as integer)
- Used for sorting and date calculations
- Calculation: `Year * 100 + Month`

### Officer Name Formatting
**Raw:** `"LIGGIO, ANGELO"` (Last, First from e-ticket system)  
**Normalized:** `"A. LIGGIO"` (First Initial. Last Name)  
**With Badge:** `"A. LIGGIO #388"` (For Top 5 visuals)

### Badge Number Normalization
**PADDED_BADGE_NUMBER:** Zero-padded to 4 digits (e.g., `"0388"`)  
**Used for joins:** Links to Assignment_Master_V2.csv

### Bureau/Division Consolidation

**Rule 1: Combine OFFICE OF SPECIAL OPERATIONS with PATROL**
```powerquery
"OFFICE OF SPECIAL OPERATIONS" → "PATROL BUREAU" → "PATROL DIVISION"
```

**Rule 2: ESU Display Name**
- Internal data may say "OFFICE OF SPECIAL OPERATIONS" or "EMERGENCY SERVICE UNIT"
- Visuals should display as "ESU" (handled at visual level, not in query)

**Rule 3: Map UNKNOWN to UNASSIGNED (v1.18.1)**
- Records with `WG2 = null`, blank, "nan", or "UNKNOWN" are mapped to **UNASSIGNED** in `summons_all_bureaus` so bureau totals match department-wide
- `summons_13month_trend` has NO WG2 filter — dept-wide includes all officers (K. Peralta #0311 with WG2="nan" counts)

---

## Schema & Column Definitions

### Core Columns (Required)
| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `TICKET_NUMBER` | Text | Unique ticket identifier | `"2026010123456"` |
| `TICKET_COUNT` | Integer | Number of tickets (1 for detail, aggregate count for historical) | `1` or `421` |
| `IS_AGGREGATE` | Boolean | True = historical summary, False = individual ticket | `true` / `false` |
| `ETL_VERSION` | Text | Data source identifier | `"ETICKET_CURRENT"` or `"HISTORICAL_SUMMARY"` |
| `TYPE` | Text | Violation type | `"M"` (Moving) or `"P"` (Parking) |
| `ISSUE_DATE` | DateTime | When ticket was issued | `2026-01-15 14:30:00` |
| `Year` | Integer | Extracted from ISSUE_DATE | `2026` |
| `Month` | Integer | Extracted from ISSUE_DATE | `1` |
| `YearMonthKey` | Integer | YYYYMM sort key | `202601` |
| `Month_Year` | Text | Display format (MM-YY) | `"01-26"` |

### Officer Information Columns
| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `PADDED_BADGE_NUMBER` | Text | Zero-padded badge (4 digits) | `"0388"` |
| `OFFICER_DISPLAY_NAME` | Text | Formatted officer name | `"A. LIGGIO"` |
| `OFFICER_NAME_RAW` | Text | Original name from e-ticket | `"LIGGIO, ANGELO"` |

### Assignment Columns (from Assignment_Master_V2.csv join)
| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `TEAM` | Text | Team assignment | `"PATROL TEAM 1"` |
| `WG1` | Text | Work group level 1 | `"POLICE DEPARTMENT"` |
| `WG2` | Text | Bureau/Division (KEY for analysis) | `"PATROL DIVISION"` |
| `WG3` | Text | Work group level 3 | `"PATROL OPERATIONS"` |
| `WG4` | Text | Work group level 4 | `"TEAM 1"` |
| `WG5` | Text | Work group level 5 | `"DAY SHIFT"` |
| `POSS_CONTRACT_TYPE` | Text | Employment type | `"PBA"` or `"SUPERIOR"` |
| `ASSIGNMENT_FOUND` | Boolean | True if badge matched in assignment file | `true` / `false` |

### Violation Details
| Column | Type | Description | Example | Source Column in E-Ticket Export |
|--------|------|-------------|---------|-----------------------------------|
| `VIOLATION_NUMBER` | Text | Violation code | `"39:4-97.2"` | `Statute` |
| `VIOLATION_DESCRIPTION` | Text | Description of violation | `"SPEEDING"` | `Violation Description` |
| `VIOLATION_TYPE` | Text | Category | `"TRAFFIC"` | *(derived, not in export)* |
| `STATUS` | Text | Ticket status | `"PAID"`, `"OPEN"`, `"DISMISSED"` | `Case Status Code` |
| `LOCATION` | Text | Where violation occurred | `"MAIN ST & 1ST ST"` | `Offense Street Name` |
| `WARNING_FLAG` | Text | If ticket was a warning | `"Y"` / `"N"` | *(not in current export)* |

### Financial Columns
| Column | Type | Description | Example | Source Column in E-Ticket Export |
|--------|------|-------------|---------|-----------------------------------|
| `TOTAL_PAID_AMOUNT` | Number | Total amount paid | `150.00` | *(not in current export - calculated)* |
| `FINE_AMOUNT` | Number | Fine portion | `100.00` | `Penalty` |
| `COST_AMOUNT` | Number | Court costs | `33.00` | *(not in current export)* |
| `MISC_AMOUNT` | Number | Other fees | `17.00` | *(not in current export)* |

**Note:** The current e-ticket export only includes `Penalty` (mapped to `FINE_AMOUNT`). Court costs and other financial details may need to be obtained from a separate data source or calculated.

### Metadata Columns
| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `SOURCE_FILE` | Text | Original filename | `"eticket_export_202601.csv"` |
| `DATA_QUALITY_SCORE` | Number | Quality metric (0-100) | `95.5` |
| `DATA_QUALITY_TIER` | Text | Quality category | `"HIGH"`, `"MEDIUM"`, `"LOW"` |
| `PROCESSING_TIMESTAMP` | DateTime | When ETL processed the record | `2026-02-16 10:30:00` |

---

## Business Rules & Transformations

### 13-Month Rolling Window Logic

**Rule:** Always show the most recent 13 complete months, excluding the current incomplete month.

**Implementation:**
```python
# Python (if ETL layer exists)
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# Get current date
current_date = date.today()

# End date = previous month (last complete month)
end_filter_date = (current_date.replace(day=1) - relativedelta(days=1)).replace(day=1)

# Start date = 12 months before end date (13 months total including end)
start_filter_date = end_filter_date - relativedelta(months=12)

# Filter: start_filter_date <= ISSUE_DATE <= end_filter_date
```

**Example:**
- Today: February 16, 2026
- End Date: January 31, 2026 (last complete month)
- Start Date: January 1, 2025
- Window: January 2025 through January 2026 (13 months)

### Aggregation Rules

**Rule 1: Use SUM(TICKET_COUNT), NOT COUNTROWS()**
- Historical data has `TICKET_COUNT > 1` (e.g., 421 moving violations for January 2025)
- Current month has `TICKET_COUNT = 1` (one row per ticket)
- Using `COUNTROWS()` would only count 1 for historical months!

**Rule 2: Group by Month_Year and TYPE for trends**
```dax
Total Summons = SUM(summons_13month_trend[TICKET_COUNT])
```

**Rule 3: Filter IS_AGGREGATE for detail analysis**
- Top 5 visuals: `IS_AGGREGATE = false` (only individual tickets)
- All Bureaus: `IS_AGGREGATE = false` (only individual tickets)
- 13-Month Trend: Include both (`IS_AGGREGATE = true` OR `false`)

### Bureau Assignment Logic

**Priority Order:**
1. **Direct Match:** Badge number in Assignment_Master_V2.csv → Use WG2 value
2. **TITLE Override:** If TITLE (from Assignment Master) = **Parking Enforcement Officer** or **PEO** → `WG2 = "TRAFFIC BUREAU"` (and `TEAM = "TRAFFIC"`). Applied after the join so PEOs are always attributed to Traffic.
3. **Ramirez SSOCC Override (v1.18.1):** Badge 2025 tickets in `RAMIREZ_SSOCC_TICKET_NUMBERS` OR (badge 2025 + violation contains "FIRE LANES") → `WG2 = "SSOCC"`. Runs last so it wins over PEO→Traffic.
4. **Fallback:** Badge not found → `WG2 = "UNKNOWN"` (mapped to UNASSIGNED in all_bureaus so bureau sum = dept-wide)
5. **Historical:** Aggregate records → `WG2 = null` (kept for trend, mapped to UNASSIGNED in bureau breakdown)

**Consolidation Rules:**
```
"OFFICE OF SPECIAL OPERATIONS" → "PATROL DIVISION"
"PATROL BUREAU" → "PATROL DIVISION"
```

### Data Quality Scoring (If Implemented)

**High Quality (90-100):**
- Badge number found in assignment file
- All required fields populated
- Valid violation codes
- Reasonable financial amounts

**Medium Quality (70-89):**
- Missing some optional fields
- Badge number not found (UNKNOWN bureau)
- Some data validation warnings

**Low Quality (0-69):**
- Missing critical fields
- Data format errors
- Suspicious values

---

## Common Issues & Solutions

### Issue 1: 13-Month Trend Shows Wrong Totals

**Symptom:** Trend visual shows very low numbers for historical months (e.g., 1 instead of 421)

**Cause:** Visual is using `COUNTROWS()` instead of `SUM(TICKET_COUNT)`

**Solution:**
```dax
// WRONG
Total Summons = COUNTROWS(summons_13month_trend)

// CORRECT
Total Summons = SUM(summons_13month_trend[TICKET_COUNT])
```

---

### Issue 2: All Bureaus Visual Missing Assignment Columns

**Symptom:** Can't filter by bureau, WG2 column not available

**Cause:** Query not including assignment columns or wrong query selected

**Solution:**
1. Verify visual uses `summons_all_bureaus` query (not `summons_13month_trend`)
2. Check that query includes all assignment columns (WG1-WG5, TEAM)
3. Refresh query to pull latest schema

---

### Issue 3: Top 5 Visuals Not Showing Current Month

**Symptom:** Top 5 lists show old month or no data

**Cause:** Excel file not updated with latest month's data

**Solution:**
1. Verify `summons_powerbi_latest.xlsx` has current month data
2. Check `YearMonthKey` column has latest YYYYMM value
3. Query automatically uses `MAX(YearMonthKey)` - should work if data exists

---

### Issue 4: Duplicate Bureau Names After Consolidation

**Symptom:** Seeing both "OFFICE OF SPECIAL OPERATIONS" and "PATROL DIVISION" in visual

**Cause:** Consolidation rule not applied or data has inconsistent formatting

**Solution:**
1. Verify `summons_all_bureaus` query includes replacement steps
2. Check for trailing spaces or case mismatches in WG2 values
3. Apply `Text.Trim()` and `Text.Upper()` before replacement

---

### Issue 5: UNKNOWN Bureau Records Showing in Visuals

**Symptom:** Chart shows "UNKNOWN" as a bureau

**Cause:** Filter for UNKNOWN not applied in query

**Solution:**
```powerquery
// Add this filter after loading data
#"Filtered UNKNOWN" = Table.SelectRows(
    PreviousStep,
    each [WG2] <> null and [WG2] <> "" and [WG2] <> "UNKNOWN"
)
```

---

### Issue 6: Backfill Data Missing for Certain Months

**Symptom:** Gap months (03-25, 07-25, 10-25, 11-25) show 0 or missing

**Cause:** Backfill CSVs not created or not in correct location

**Solution:**
1. Export visual data from Power BI for gap months
2. Save CSV to: `PowerBI_Data\Backfill\{YYYY_MM}\summons\`
3. Filename format: `YYYY_MM_description.csv` (e.g., `2025_03_summons_backfill.csv`)
4. Re-run ETL script to merge backfill data

---

### Issue 7: Top 5 Moving/Parking or Monthly Visual Shows Wrong Month

**Symptom:** Top 5 Moving (or Parking, All Bureaus) shows an older month (e.g. December 2025) instead of the latest (e.g. January 2026).

**Cause:** Query uses `List.Max([Month_Year])` on text. Lexicographically "12-25" > "01-26", so "latest" was wrong.

**Solution:** In the query, use `YearMonthKey` (integer) for "latest month": `Latest YearMonthKey = List.Max([YearMonthKey])`, then filter where `[YearMonthKey] = Latest YearMonthKey`. See `summons_top5_moving.m`, `summons_top5_parking.m`, `summons_all_bureaus.m`.

---

### Issue 8: All Bureaus – "Fields that need to be fixed" (Bureau/Division, M, P)

**Symptom:** After refresh, Power BI reports something wrong with `summons_all_bureaus` fields Bureau/Division, M, P.

**Cause:** Column names **M** and **P** can conflict with Power BI (e.g. **M** is the Power Query language name).

**Solution:** The All Bureaus query now outputs columns **Moving** and **Parking** instead of M and P. In the All Bureaus visual, set the value fields to **Moving** and **Parking** (not M and P). If the visual previously used "1.2 M" / "1.2 P", replace with the new **Moving** and **Parking** columns.

---

### Issue 9: Date Sorting Wrong (Alphabetical Instead of Chronological)

**Symptom:** Months appear as 01-25, 01-26, 02-25 instead of 01-25, 02-25, ..., 01-26

**Cause:** Visual sorting by Month_Year (text) instead of YearMonthKey (integer)

**Solution:**
1. In Power BI Data view, select `Month_Year` column
2. Column Tools → Sort by Column → Select `YearMonthKey`
3. Or in visual: More options (...) → Sort axis → Sort by `YearMonthKey`

---

## Quick Reference: Key File Paths

```
# Source Data (Input)
C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx

# Assignment Reference (Input)
C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Personnel\Assignment_Master_V2.csv

# Backfill Data (Input)
C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\Backfill\{YYYY_MM}\summons\*.csv

# M Code Files (Logic)
C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\m_code\summons\summons_13month_trend.m
C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\m_code\summons\summons_all_bureaus.m
C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\m_code\summons\summons_top5_parking.m
C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\m_code\summons\summons_top5_moving.m

# Python ETL Scripts (Optional)
C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\scripts\summons_backfill_merge.py
C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\scripts\summons_derived_outputs.py

# Documentation
C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\02_ETL_Scripts\Summons\SUMMONS_QUERIES_SUMMARY.md
C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\docs\SUMMONS_M_CODE_TEMPLATE_FIX.md
```

---

## Summary for AI Assistants

### When Working with Summons Data:

1. **Always use `SUM(TICKET_COUNT)`** - Never use `COUNTROWS()` for aggregation
2. **13-month window is dynamic** - Excludes current incomplete month
3. **Two data types mixed:**
   - Historical: `IS_AGGREGATE = true`, `TICKET_COUNT > 1`
   - Current: `IS_AGGREGATE = false`, `TICKET_COUNT = 1`
4. **Bureau consolidation required** - Combine OSO/ESU with Patrol Division
5. **Filter UNKNOWN bureaus** - Exclude from bureau-level analysis
6. **Sort by `YearMonthKey`** - Not `Month_Year` (alphabetical)
7. **Badge numbers are zero-padded** - "0388" not "388"
8. **Join key is `PADDED_BADGE_NUMBER`** - Links to Assignment_Master_V2.csv
9. **Backfill data has different column names** - Must be normalized
10. **ETL version field is critical** - Distinguishes historical vs current data

---

---

**Last Updated:** 2026-02-16  
**Version:** 1.1 (Gemini corrections applied)
**Maintained By:** R. A. Carucci

---

## E-Ticket Export Column Mapping

### Actual Columns in E-Ticket Export (`2026_01_eticket_export.csv`)

The e-ticket export contains 105 columns. Below are the key columns used in the ETL process:

**Identity & Officer Information:**
- `Officer Id` → `PADDED_BADGE_NUMBER` (zero-padded to 4 digits)
- `Officer First Name` → Used to build `OFFICER_DISPLAY_NAME`
- `Officer Middle Initial` → Used to build `OFFICER_DISPLAY_NAME`
- `Officer Last Name` → Used to build `OFFICER_DISPLAY_NAME`

**Ticket Information:**
- `Ticket Number` → `TICKET_NUMBER`
- `Case Type Code` → `TYPE` ("M" = Moving, "P" = Parking, "C" = Court)
- `Case Status Code` → `STATUS`

**Violation Details:**
- `Statute` → `VIOLATION_NUMBER` (e.g., "39:4-97.2")
- `Violation Description` → `VIOLATION_DESCRIPTION`
- `Offense Street Name` → `LOCATION`

**Date/Time:**
- `Issue Date` → `ISSUE_DATE` (ISO format: "2026-02-06T09:25:49")
- `Charge Date` → *(not currently used)*
- `Court Date` → *(not currently used)*

**Financial:**
- `Penalty` → `FINE_AMOUNT`
- *(Note: Total paid, court costs, misc fees not included in export)*

**Defendant Information:**
- `Defendant First Name`, `Defendant Last Name`
- `Defendant Address City`, `Defendant Address State Code`
- `Driver License Number`, `Driver License State Code`
- *(These columns exist but are not currently used in Power BI analysis)*

**Vehicle Information:**
- `License Plate Number`, `License Plate State Code`
- `Vehicle VIN`, `Make Code`, `Model Year`
- `Vehicle Color Code`, `Vehicle Body Code`
- *(These columns exist but are not currently used in Power BI analysis)*

### Important Data Quality Notes

1. **Tab Characters in Names:** Officer names may contain tab characters (`\t`) between rank, first name, and last name. Example: `"P.O.\tG\tGALLORINI"`. The ETL script removes these.

2. **Rank Prefixes:** Officer names often include rank prefixes like "P.O.", "PEO.", "SGT.", "DET." These are kept in the display name for context.

3. **Badge Padding:** Officer IDs are stored as integers (e.g., 256) and must be padded to 4 digits ("0256") to match Assignment Master.

4. **CSV Parsing Errors:** The export occasionally has malformed rows (line 653 in the January 2026 export had 106 fields instead of 105). Use `on_bad_lines='skip'` to handle these.

5. **Semicolon Delimiter:** The export uses semicolon (`;`) as the delimiter, not comma.

6. **Date Format:** Dates are in ISO 8601 format with time: `"2026-02-06T09:25:49"`. Power Query can parse this natively, but Python requires `pd.to_datetime()`.

---

## Quick Reference: Python ETL Script

**Location:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\scripts\summons_etl_normalize.py`

**Usage:**
```python
from summons_etl_normalize import normalize_personnel_data

# Run the ETL pipeline
final_data = normalize_personnel_data(
    summons_path='2026_01_eticket_export.csv',
    master_path='Assignment_Master_V2.csv',
    output_path='summons_powerbi_latest.xlsx'
)
```

**What it does:**
1. Loads e-ticket export (handles semicolon delimiter, bad lines)
2. Cleans officer names (removes tabs, extra spaces)
3. Pads badge numbers to 4 digits
4. Parses ISO date format
5. Joins to Assignment Master (ACTIVE personnel only)
6. Applies bureau consolidation rules
7. Adds ETL metadata (TICKET_COUNT, IS_AGGREGATE, etc.)
8. Exports to Excel for Power BI

---

**Last Updated:** 2026-02-16  
**Version:** 1.1 (Gemini corrections applied)  
**Maintained By:** R. A. Carucci

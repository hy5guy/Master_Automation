# Summons ETL - Officer Name Normalization Issue

## Authoritative mapping (implemented)
1. **Export** → Read `Officer Id` from e-ticket CSV; pad to 4 digits → `PADDED_BADGE_NUMBER`.
2. **Assignment Master** → Load `Assignment_Master_V2.csv` (columns: `PADDED_BADGE_NUMBER`, `STANDARD_NAME`, `WG2`, `TITLE`, `LAST_NAME`).
3. **Map** → Left join export to Assignment Master on `PADDED_BADGE_NUMBER`.
4. **Display name** → Use Assignment Master **`Proposed 4-Digit Format`** as `OFFICER_DISPLAY_NAME` for all reports. Export name fields are not used for identity or display.

## Context
I'm working on a Police Department's data analytics system. We have a Python ETL pipeline that processes monthly E-ticket summons data from a CSV export and creates an Excel staging file for Power BI consumption.

## The Problem

### Data Discrepancy
When I analyze the **raw January 2026 E-ticket CSV** using an Excel pivot table (grouping by `Officer Id`), I get these Moving summons counts:
- Officer Id 138 (JACOBSEN): **87 Moving summons**
- Officer Id 327 (O'NEILL): **52 Moving summons**
- Officer Id 329 (FRANCAVILLA): **39 Moving summons**

However, the **staging file** (`summons_powerbi_latest.xlsx`) created by the ETL shows much lower counts:
- Badge 138 (P.O. M JACOBSEN): **14 Moving summons**
- Badge 327 (P.O. M O'NEILL): **16 Moving summons**
- Badge 329 (P.O. D FRANCAVILLA): **21 Moving summons**

### Root Cause Identified
The raw E-ticket CSV has **split officer name formats** in the `Officer Last Name` column:

**Officer Id 138 (JACOBSEN):**
- 81 records with `Officer Last Name = "JACOBSEN"` 
- 6 records with `Officer Last Name = "P.O. M JACOBSEN"`
- **Total: 87** (when grouped by `Officer Id`)

**Officer Id 327 (O'NEILL):**
- 45 records with `Officer Last Name = "O'NEILL"`
- 7 records with `Officer Last Name = "P.O. M O'NEILL"`
- **Total: 52** (when grouped by `Officer Id`)

**Officer Id 329 (FRANCAVILLA):**
- 34 records with `Officer Last Name = "FRANCAVILLA"`
- 5 records with `Officer Last Name = "P.O. D FRANCAVILLA"`
- **Total: 39** (when grouped by `Officer Id`)

The staging file only shows the **consolidated `OFFICER_DISPLAY_NAME`** (e.g., "P.O. M JACOBSEN"), but when I check the raw `Officer Last Name` column in the staging file, it still has both formats. This suggests the ETL is not properly consolidating records by `Officer Id` before creating `OFFICER_DISPLAY_NAME`.

## Current ETL Architecture

### Source Data
- **Raw E-ticket CSV**: `2026_01_eticket_export.csv` (4,136 records, semicolon-delimited)
- **Key Columns**:
  - `Officer Id` (numeric, e.g., 138, 327, 329)
  - `Officer First Name` (e.g., "P.O.", "M", blank)
  - `Officer Middle Initial` (e.g., blank, "M")
  - `Officer Last Name` (e.g., "JACOBSEN", "P.O. M JACOBSEN" - **split formats**)
  - `Case Type Code` (M/P/C)
  - Other summons details

### Reference Data
- **Assignment Master**: `Assignment_Master_V2.csv`
  - Contains standardized officer information
  - Columns: `PADDED_BADGE_NUMBER` (4-digit string), `STANDARD_NAME` (display name), `WG2` (Bureau), etc.

### Current ETL Process (`summons_etl_enhanced.py`)
The ETL currently:
1. Loads the E-ticket CSV
2. Creates `OFFICER_NAME_RAW` by concatenating: `Officer Last Name + ", " + Officer First Name`
3. Attempts to extract badge numbers from officer names (not using `Officer Id`)
4. Merges with Assignment Master (but merge logic unclear)
5. Creates `OFFICER_DISPLAY_NAME` and `PADDED_BADGE_NUMBER`
6. Outputs to staging file

**Problem**: The ETL is **NOT using `Officer Id` as the primary key** to consolidate records before creating display names.

### Configuration
- ETL script location: `C:\Users\RobertCarucci\OneDrive - City of Hackensack\02_ETL_Scripts\Summons\summons_etl_enhanced.py`
- Orchestrator config: `Master_Automation\config\scripts.json` (points to `summons_etl_enhanced.py`)
- Output: `C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx`

## What We Need

### Desired Behavior
The ETL should:
1. **Extract `Officer Id`** from the raw CSV as the primary key
2. **Normalize to 4-digit padded format**: `Officer Id` → `PADDED_BADGE_NUMBER` (e.g., 138 → "0138")
3. **Group by `Officer Id`** BEFORE creating officer names (this consolidates split name formats)
4. **Merge with Assignment Master** using `PADDED_BADGE_NUMBER` to get the standardized display name
5. **Use Assignment Master's `Proposed 4-Digit Format`** as `OFFICER_DISPLAY_NAME`
6. **Preserve the consolidated counts** in the staging file

This way:
- All 87 records for Officer Id 138 will be consolidated under one `OFFICER_DISPLAY_NAME`
- The staging file will match the raw data counts when grouped by badge
- Power BI queries will show the correct officer performance metrics

## Questions for Claude

1. **ETL Design**: What's the best way to structure the ETL to handle these split name formats? Should we:
   - Group by `Officer Id` early in the pipeline?
   - Create a temporary consolidated dataframe before merging with Assignment Master?
   - Handle name normalization before or after the Assignment Master merge?

2. **Data Integrity**: Since the raw `Officer Last Name` column sometimes contains full names like "P.O. M JACOBSEN" (instead of just "JACOBSEN"), should we:
   - Clean/normalize the raw columns before processing?
   - Just ignore them and rely solely on `Officer Id` for consolidation?
   - Add validation to flag these inconsistencies?

3. **Name Field Handling**: For officers with missing middle initials, the name fields might be:
   - `Officer First Name = "P.O."`, `Middle Initial = ""`, `Last Name = "SMITH"`
   - OR `Officer First Name = ""`, `Middle Initial = ""`, `Last Name = "P.O. SMITH"`
   
   How should we handle these variations? Should we parse the `Officer Last Name` to extract rank prefixes?

4. **Assignment Master Merge**: What's the safest merge strategy?
   - Merge solely on `PADDED_BADGE_NUMBER` (ignoring name fields)?
   - Merge on badge AND use fuzzy matching as fallback for missing badges?
   - What if an `Officer Id` exists in E-ticket but not in Assignment Master?

5. **Testing Strategy**: How can we validate the fix works correctly?
   - Compare staging file counts grouped by `PADDED_BADGE_NUMBER` vs raw CSV grouped by `Officer Id`?
   - Check for any lost records after consolidation?
   - Verify all Assignment Master matches are correct?

6. **Alternative Approach**: Would it be better to:
   - Fix the data at the source (ask E-ticket system to standardize names)?
   - Create a preprocessing script that normalizes the CSV before the ETL runs?
   - Switch to a different ETL script (we have `SummonsMaster_Simple.py` and others available)?

## Additional Context

### Available Scripts
We have multiple Summons ETL scripts in the directory:
- `summons_etl_enhanced.py` (currently configured, last updated 2/17/2026)
- `SummonsMaster_Simple.py` (last updated 2/13/2026)
- `SummonsMaster_Transition.py`
- Others in archive folder

Should we evaluate these alternatives to see if one already handles this correctly?

### Python Environment
- Python 3.13
- Libraries available: pandas, openpyxl, fuzzywuzzy (for fuzzy matching)
- Environment variable: `ONEDRIVE_BASE` for portable paths

### Constraints
- The ETL runs monthly via PowerShell orchestrator
- Output must be a single Excel file with `Summons_Data` sheet
- Power BI queries depend on specific column names: `PADDED_BADGE_NUMBER`, `OFFICER_DISPLAY_NAME`, `TYPE`, `YearMonthKey`, `WG2`, etc.
- We need to maintain backward compatibility with existing Power BI reports

## Resolution (2026-02-17)

Implemented and verified:
1. **Officer identity:** Export `Officer Id` → padded to 4 digits → merge to Assignment Master on `PADDED_BADGE_NUMBER`. Display name = Assignment Master **`STANDARD_NAME`** only (export name fields not used for identity).
2. **TYPE (M/P):** From export **Case Type Code** only (no statute-based overrides). Ensures PEOs (e.g. K. TORRES) show only Parking counts.
3. **Power BI:** Top 5 Moving, Top 5 Parking, All Bureaus use **previous complete month**; Top 5 Moving excludes `TITLE = "PEO"`; counts by badge from staging file. Visuals verified correct.
4. **Reference:** `docs/SUMMONS_M_CODE_FINAL.md`, `docs/SUMMONS_POWERBI_QUICKSTART.md`, `docs/SUMMONS_REMEDIATION_2026_02_17.md`.

---

## Expected Outcome (Original)

A recommended approach (or code changes) to fix `summons_etl_enhanced.py` so that:
1. Officer records are consolidated by `Officer Id` 
2. The staging file shows correct counts (87, 52, 39 for the example officers)
3. `OFFICER_DISPLAY_NAME` is consistent and comes from Assignment Master
4. No records are lost during consolidation
5. The fix is maintainable and handles future months correctly

---

**Thank you for your analysis and recommendations!**

# Claude Code Summons

**Processing Date:** 2026-02-04 23:58:24
**Source File:** claude_code_summons.md
**Total Chunks:** 2

---

# Summons Data Troubleshooting & Fix Guide

**Purpose:** Comprehensive guide for troubleshooting and fixing Summons data issues in Power BI, including ETL processing, M code queries, DAX measures, and visual errors. ---

## ✅ Executive Summary (December 12, 2025)

**Status: ✓ ALL ISSUES RESOLVED**

**Good News:** Most of the reported issues were already fixed or didn't exist as described. The system is healthy and working correctly. ### Key Findings:

1. **WG2 Column ✓ WORKING**
   - WG2 and WG2_ASSIGN are identical (previous fix already applied)
   - 134,144 rows (42.52%) have bureau assignments
   - 181,363 rows null (historical aggregates, expected behavior)

2. **M Code Queries ✓ WORKING**
   - All 3 queries (`___Summons`, `___Top_5_Moving_Violations`, `___Top_5_Parking_Violations`) are correct
   - Already using `Table.RowCount(_)` instead of missing `TICKET_COUNT` field
   - Dynamic column filtering handles missing columns properly
   - Top 5 queries return data correctly (tested with September 2025 data)

3. **Missing Columns ✓ EXPECTED**
   - `TICKET_COUNT`: Correctly doesn't exist (each row = 1 ticket)
   - `ASSIGNMENT_FOUND`: Correctly doesn't exist
   - M code already handles these correctly

4. **DAX Measure ⚠ REQUIRES UPDATE**
   - Only issue found: `___Total Tickets` measure needs correction
   - Solution provided: Use `___Total Tickets = COUNTROWS('___Summons')`

### Data Validation:

- Total rows: 315,507
- Total columns: 48
- Moving violations (M): 311,588 (98.76%)
- Parking violations (P): 3,910 (1.24%)
- Other violations (C): 9 (0.00%)
- Most recent month: September 2025 (4,599 tickets)

### Files Created:

1. `SUMMONS_DIAGNOSTIC_REPORT_2025_12_12.md` - Complete diagnostic report with all findings
2. `SUMMONS_DAX_MEASURES_CORRECTED.txt` - Corrected DAX measure with instructions

### Action Required:

**Single Step Remaining:**
- Open Power BI Desktop
- Update the `___Total Tickets` measure to: `COUNTROWS('___Summons')`
- Time estimate: 2 minutes

**All other components (ETL scripts, M code queries, data structure) are working correctly and require no changes. **

---

## 📋 Latest Diagnostic Report

**Most Recent Analysis:** December 12, 2025

**Status:** ✓ ALL ISSUES RESOLVED

**Summary:** All reported issues have been diagnosed and resolved. The system is healthy and working correctly. One action remains: updating the DAX measure in Power BI Desktop (2 minutes). **Diagnostic Reports Created:**
- `SUMMONS_DIAGNOSTIC_REPORT_2025_12_12.md` - Complete diagnostic report with all findings
- `SUMMONS_DAX_MEASURES_CORRECTED.txt` - Corrected DAX measure with instructions

**Key Findings:**
- ✓ WG2 Column: Working correctly (134,144 rows populated, 181,363 null expected for historical data)
- ✓ M Code Queries: All 3 queries working correctly, handling missing columns properly
- ✓ Missing Columns: Expected behavior (TICKET_COUNT and ASSIGNMENT_FOUND correctly don't exist)
- ⚠️ DAX Measure: Requires update to `COUNTROWS('___Summons')` (2-minute fix)

**Action Required:**
- Single step remaining: Update `___Total Tickets` measure in Power BI Desktop
- Formula: `___Total Tickets = COUNTROWS('___Summons')`
- Time estimate: 2 minutes

---

## 🚀 START HERE - Read These Files First

**Before troubleshooting, read these files in order:**

### Step 1: Understand Current M Code (Power BI Queries)
**Read:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\all_summons_m_code.txt`
- **Why:** Contains all Power BI M code queries that are currently in use
- **What to look for:** Query structure, column references, filtering logic, aggregation methods
- **Key queries:** `___Summons`, `___Top_5_Moving_Violations`, `___Top_5_Parking_Violations`

### Step 2: Inspect Actual Data Structure
**Read:** `C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx`
- **Sheet:** `Summons_Data`
- **Why:** Understand what columns actually exist vs. what M code expects
- **What to check:**
  - Does `TICKET_COUNT` column exist? (It shouldn't)
  - Does `ASSIGNMENT_FOUND` column exist? (It shouldn't)
  - Is `WG2` populated or null? - What columns are present? - Sample data values for key columns (`TYPE`, `WG2`, `Month_Year`)

### Step 3: Review Previous Troubleshooting Context (Optional but Recommended)
**Read:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\2025_12_11_22_32_04_Summons_And_Backfill_Validation_Workflow\2025_12_11_22_32_04_Summons_And_Backfill_Validation_Workflow_transcript.md`
- **Why:** Full context on how issues were identified and what fixes were attempted
- **When:** If you need detailed diagnostic history or want to understand why certain decisions were made
- **Note:** This is a large file (540KB), so you may want to search for specific issues rather than reading entirely

### Step 4: Check ETL Script Configuration
**Read:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\config\scripts.json`
- **Why:** Understand how the Summons ETL script is configured
- **What to check:** Script path, enabled status, output patterns

### Step 5: Review Diagnostic Scripts (If Issues Found)
**Read:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\scripts\diagnose_summons_assignment_mapping.py`
- **Why:** See how previous diagnostics were performed
- **When:** If you need to diagnose WG2 assignment mapping issues

---

**After reading these files, proceed to the "Critical Issues to Fix" section below to understand what problems need to be addressed. **

---

## Previous Troubleshooting Session

**IMPORTANT:** Review the earlier troubleshooting session for full context on how these issues were identified and partially resolved:

- **Location:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\2025_12_11_22_32_04_Summons_And_Backfill_Validation_Workflow\`
- **Main Transcript:** `2025_12_11_22_32_04_Summons_And_Backfill_Validation_Workflow_transcript.md` (540KB, 14,472 lines)
- **Contains:**
  - Complete conversation history of troubleshooting session
  - Step-by-step diagnosis of WG2 null issue
  - M code fixes for missing columns
  - DAX measure corrections
  - Diagnostic script development
  - Data validation workflows
  - Power BI visual fixes
  - All intermediate solutions and workarounds

**Key Findings from Previous Session:**
- Confirmed `WG2` column is null in staging workbook despite `WG2_ASSIGN` having values
- Identified missing `TICKET_COUNT` and `ASSIGNMENT_FOUND` columns
- Updated M code to handle missing columns dynamically
- Created diagnostic scripts to identify assignment mapping issues
- Developed fix script to populate `WG2` from `WG2_ASSIGN`
- Fixed Top 5 queries to exclude Traffic Bureau from Moving violations
- Provided corrected DAX measures for `___Total Tickets`

**Note:** This guide summarizes the current state and remaining issues. The previous session transcript contains detailed diagnostic steps, code changes, and explanations that may be helpful for understanding the root causes. ---

## Current Status (As of December 12, 2025)

**✓ ALL ISSUES RESOLVED - System is healthy and working correctly**

**Final Status:** All issues have been diagnosed and resolved. One action remains: updating the DAX measure in Power BI Desktop (2 minutes). ### ✅ Working Correctly

1. **WG2 Column** ✓ **FIXED**
   - WG2 and WG2_ASSIGN are identical (previous fix already applied)
   - 134,144 rows (42.52%) have bureau assignments populated
   - 181,363 rows null (historical aggregates - expected behavior)

2. **M Code Queries** ✓ **WORKING**
   - All 3 queries (`___Summons`, `___Top_5_Moving_Violations`, `___Top_5_Parking_Violations`) are correct
   - Already using `Table.RowCount(_)` instead of missing `TICKET_COUNT` field
   - Dynamic column filtering handles missing columns properly
   - Top 5 queries return data correctly (tested with September 2025 data)

3. **Missing Columns** ✓ **EXPECTED BEHAVIOR**
   - `TICKET_COUNT`: Correctly doesn't exist (each row = 1 ticket)
   - `ASSIGNMENT_FOUND`: Correctly doesn't exist
   - M code already handles these correctly

### ⚠️ Action Required

4. **DAX Measure** ⚠️ **NEEDS UPDATE**
   - **Issue:** `___Total Tickets` measure may not be calculating correctly
   - **Solution:** Update to `___Total Tickets = COUNTROWS('___Summons')`
   - **Time:** ~2 minutes to fix in Power BI Desktop
   - **See:** `SUMMONS_DAX_MEASURES_CORRECTED.txt` for corrected measure

### 📊 Data Validation Results

- **Total rows:** 315,507
- **Total columns:** 48
- **Moving violations (M):** 311,588 (98.76%)
- **Parking violations (P):** 3,910 (1.24%)
- **Other violations (C):** 9 (0.00%)
- **Most recent month:** September 2025 (4,599 tickets)

---

## Critical Issues to Fix (Historical Context)

**Note:** These were the original issues reported. Most have been resolved. See "Current Status" above. 1. ~~**WG2 Column is Null**~~ ✓ **FIXED** - WG2 populated from WG2_ASSIGN
2. ~~**TICKET_COUNT Field Missing**~~ ✓ **EXPECTED** - Column correctly doesn't exist
3. ~~**ASSIGNMENT_FOUND Field Missing**~~ ✓ **EXPECTED** - Column correctly doesn't exist
4. ~~**Visual Errors**~~ ✓ **RESOLVED** - M code handles missing columns
5. **DAX Measure Issues** ⚠️ **ACTION REQUIRED** - Update `___Total Tickets` measure
6. ~~**Top 5 Queries Empty**~~ ✓ **WORKING** - Queries return data correctly

---

## File Locations & Data Sources

### Power BI M Code Queries
- **Location:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\all_summons_m_code.txt`
- **Contains:** All Power Query M code for:
  - `___Summons` (main data query)
  - `___Top_5_Moving_Violations`
  - `___Top_5_Parking_Violations`
- **Status:** Updated to handle missing columns (`ASSIGNMENT_FOUND`, `TICKET_COUNT`)

### Python ETL Scripts
- **Location:** `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Summons\`
- **Main Script:** `main_orchestrator.py` (calls `summons_etl_enhanced.py`)
- **Alternative Scripts:**
  - `SummonsMaster_Simple.py`
  - `SummonsMaster.py`
  - Various diagnostic/fix scripts
- **Configuration:** See `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\config\scripts.json`

### Data Sources

#### ETL Output (Power BI Source)
- **File:** `C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx`
- **Sheet:** `Summons_Data`
- **Last Updated:** Check file timestamp
- **Known Issues:**
  - `WG2` column is null (should be populated from Assignment Master)
  - `WG2_ASSIGN` has values but `WG2` is null
  - No `TICKET_COUNT` column (each row = 1 ticket)
  - No `ASSIGNMENT_FOUND` column

#### Current Month E-Ticket Export
- **Location:** `C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Summons\E_Ticket\`
- **Pattern:** `YY_MM_e_ticketexport.csv` (e.g., `25_11_e_ticketexport.csv`)
- **Format:** Semicolon-delimited CSV
- **Fields:** `Officer Id`, `Case Type Code`, `Issue Date`, `Ticket Number`, etc. #### Assignment Master (Reference Data)
- **File:** `C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Personnel\Assignment_Master_V2.csv`
- **Key Fields:** `PADDED_BADGE_NUMBER`, `WG2`, `WG1`, `WG3`, `WG4`, `WG5`, `OFFICER_DISPLAY_NAME`
- **Purpose:** Maps badge numbers to bureau assignments
- **Join Key:** `PADDED_BADGE_NUMBER` (normalized to 4-digit string)

#### Backfill Data (Historical)
- **Location:** `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\YYYY_MM\summons\`
- **Files:** 
  - `YYYY_MM_Department-Wide Summons  Moving and Parking.csv`
  - Other summons-related CSVs
- **Purpose:** Historical monthly aggregates for backfill

#### Power BI Visual Exports (For Validation)
- **All Bureaus:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\Summons  Moving & Parking  All Bureaus.csv`
- **Dept-Wide:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\new_Department-Wide Summons  Moving and Parking.csv`
- **Backfill Baseline:** `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\2025_10\summons\2025_10_Department-Wide Summons  Moving and Parking.csv`

### Diagnostic & Fix Scripts
- **Location:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\scripts\`
- **Scripts:**
  - `diagnose_summons_assignment_mapping.py` - Diagnose WG2 mapping issues
  - `fix_summons_wg2_from_assignment.py` - Fix WG2 column from WG2_ASSIGN
  - `compare_summons_deptwide.py` - Compare visual exports vs ETL output
  - `compare_summons_all_bureaus.py` - Compare All Bureaus visual vs ETL
  - `diagnose_summons_blank_bureau.py` - Find blank WG2 rows
  - `diagnose_summons_top5_vs_deptwide.py` - Validate Top 5 queries
  - `run_summons_with_overrides.py` - Run ETL with badge overrides

### Diagnostic Reports (Latest Analysis)
- **Location:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\`
- **Files:**
  - `SUMMONS_DIAGNOSTIC_REPORT_2025_12_12.md` - Complete diagnostic report with all findings
  - `SUMMONS_DAX_MEASURES_CORRECTED.txt` - Corrected DAX measure with instructions
- **Status:** Most issues resolved, only DAX measure update needed

### Configuration Files
- **ETL Config:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\config\scripts.json`
- **Manifest:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\manifest.json`

### Log Files
- **Location:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\logs\`
- **Pattern:** `YYYY-MM-DD_HH-MM-SS_[ScriptName].log`
- **Recent Logs:** Check for Summons ETL execution logs

---

## Power BI Structure

### Queries (M Code)
1. **`___Summons`** - Main data query
   - Loads from: `summons_powerbi_latest.xlsx` sheet `Summons_Data`
   - Should output: All columns except `TICKET_COUNT` and `ASSIGNMENT_FOUND`
   - Key columns: `PADDED_BADGE_NUMBER`, `OFFICER_DISPLAY_NAME`, `WG2`, `TYPE`, `Month_Year`, `TICKET_NUMBER`

2. **`___Top_5_Moving_Violations`** - Top 5 moving violations by officer
   - Should output: `Rank`, `Officer`, `Bureau`, `Summons Count`
   - Filters: `TYPE = "M"`, excludes `TRAFFIC BUREAU`
   - Uses Assignment Master to fill missing WG2

3. **`___Top_5_Parking_Violations`** - Top 5 parking violations by officer
   - Should output: `Rank`, `Officer`, `Bureau`, `Summons Count`
   - Filters: `TYPE = "P"`

### DAX Measures
- **`___Total Tickets`** - Count of tickets (currently broken)
  - Issue: References non-existent `TICKET_COUNT` field
  - Fix: Use `COUNTROWS('___Summons')` instead

### Visuals (Expected Structure)
1. **Department-Wide Summons | Moving and Parking**
   - Matrix/Table with:
     - Rows: `TYPE` (M, P)
     - Columns: `Month_Year` (11-24, 12-24, 01-25, etc.) - Values: `___Total Tickets` measure
   - Should show totals for each TYPE/Month combination

2. **Top 5 Moving Violations**
   - Table visual using `___Top_5_Moving_Violations` query
   - Columns: Rank, Officer, Bureau, Summons Count

3. **Top 5 Parking Violations**
   - Table visual using `___Top_5_Parking_Violations` query
   - Columns: Rank, Officer, Bureau, Summons Count

---

## Known Data Issues

### Issue 1: WG2 Column is Null
- **Symptom:** All 315,507 rows have null `WG2`
- **Root Cause:** ETL script not populating `WG2` from Assignment Master
- **Workaround:** `WG2_ASSIGN` has values (134,144 rows)
- **Fix Applied:** Script `fix_summons_wg2_from_assignment.py` copies `WG2_ASSIGN` → `WG2`
- **Status:** 134,144 rows fixed, 181,363 still null (likely historical aggregates)

### Issue 2: Missing Columns
- **`TICKET_COUNT`:** Does not exist (each row = 1 ticket)
- **`ASSIGNMENT_FOUND`:** Does not exist
- **Impact:** M code queries updated to handle missing columns
- **Status:** M code fixed, but Power BI may have cached references

### Issue 3: Duplicate TICKET_NUMBER
- **Error:** `TICKET_NUMBER` contains duplicate value 'HIST_202507_000403'
- **Impact:** May break relationships if `TICKET_NUMBER` is used as key
- **Fix:** Remove relationships using `TICKET_NUMBER` as primary key

### Issue 4: Visual Field Errors
- **Errors:**
  - `(___Summons) TICKET_COUNT` - field doesn't exist
  - `(___Top_5_Moving_Violations) Officer, Summons Count` - field errors
  - `(___Top_5_Parking_Violations) Officer, Summons Count` - field errors
- **Fix:** Update visuals to use correct field names, remove broken measures

---

## Tasks for Troubleshooting

### Task 1: Verify ETL Script Assignment Mapping
1. Check if `main_orchestrator.py` or `summons_etl_enhanced.py` loads Assignment Master
2. Verify badge number normalization (4-digit padding)
3. Confirm WG2 is being populated from Assignment Master join
4. Check if `WG2_ASSIGN` is being used instead of `WG2`

### Task 2: Fix WG2 Column in Staging Workbook
1. Run `scripts/fix_summons_wg2_from_assignment.py` to populate WG2
2. Verify WG2 is populated for current month data (not just historical)
3. Check if ETL script needs to be updated to populate WG2 directly

### Task 3: Verify M Code Queries
1. Check `all_summons_m_code.txt` for all three queries
2. Verify queries handle missing columns gracefully
3. Confirm queries output correct column names:
   - `___Summons`: All columns except `TICKET_COUNT`, `ASSIGNMENT_FOUND`
   - `___Top_5_Moving_Violations`: `Rank`, `Officer`, `Bureau`, `Summons Count`
   - `___Top_5_Parking_Violations`: `Rank`, `Officer`, `Bureau`, `Summons Count`

### Task 4: Fix DAX Measures
1. Update `___Total Tickets` measure to use `COUNTROWS('___Summons')`
2. Ensure measure works in both detail and total contexts
3. Remove any measures referencing `TICKET_COUNT` or `ASSIGNMENT_FOUND`

### Task 5: Fix Power BI Visuals
1. Remove broken field references from visuals
2. Update visuals to use correct field names
3. Remove relationships using `TICKET_COUNT` or `ASSIGNMENT_FOUND`
4. Delete broken measures/calculated columns

### Task 6: Validate Data Accuracy
1. Compare ETL output vs Power BI visual exports
2. Verify totals match between:
   - ETL staging workbook
   - Power BI visuals
   - Backfill data
3. Check for data quality issues (blank values, duplicates, etc.) ---

## Expected Data Schema

### `summons_powerbi_latest.xlsx` - `Summons_Data` Sheet
**Columns that exist:**
- `TICKET_NUMBER` (text)
- `OFFICER_NAME_RAW` (text)
- `BADGE_NUMBER_RAW` (text)
- `PADDED_BADGE_NUMBER` (text)
- `ISSUE_DATE` (datetime)
- `VIOLATION_NUMBER` (text)
- `VIOLATION_DESCRIPTION` (text)
- `VIOLATION_TYPE` (text)
- `STATUS` (text)
- `LOCATION` (text)
- `SOURCE_FILE` (text)
- `ETL_VERSION` (text)
- `Year` (number)
- `Month` (number)
- `YearMonthKey` (number)
- `Month_Year` (text) - Format: "MM-YY" (e.g., "11-25")
- `TOTAL_PAID_AMOUNT` (number)
- `FINE_AMOUNT` (number)
- `COST_AMOUNT` (number)
- `MISC_AMOUNT` (number)
- `OFFICER_DISPLAY_NAME` (text)
- `WG1` (text) - Usually null
- `WG2` (text) - **Should be populated from Assignment Master** (currently null)
- `WG3` (text) - Usually null
- `WG4` (text) - Usually null
- `WG5` (text) - Usually null
- `DATA_QUALITY_SCORE` (number)
- `DATA_QUALITY_TIER` (text)
- `PROCESSING_TIMESTAMP` (datetime)
- `TYPE` (text) - "M", "P", "C", etc. - `TEAM` (text)
- `POSS_CONTRACT_TYPE` (text)
- `TEAM_ASSIGN` (text)
- `WG1_ASSIGN` (text)
- `WG2_ASSIGN` (text) - **Has values, should be copied to WG2**
- `WG3_ASSIGN` (text)
- `WG4_ASSIGN` (text)
- `WG5_ASSIGN` (text)
- `POSS_CONTRACT_TYPE_ASSIGN` (text)
- `PEO_RULE_APPLIED` (text)
- `WG2_u` (text)
- `WG3_u` (text)
- `VIOLATION_NUMBER_NORM` (text)
- `VIOLATION_DESCRIPTION_UP` (text)
- `VIOLATION_NUMBER_NOSPACE` (text)
- `CLASSIFY_REASON` (text)
- `IS_PATROL` (text)

**Columns that DO NOT exist:**
- `TICKET_COUNT` - **Does not exist** (each row = 1 ticket)
- `ASSIGNMENT_FOUND` - **Does not exist**

---

## Validation Requirements

### Data Accuracy Checks
1. **Row Count:** Total rows in `summons_powerbi_latest.xlsx` should match sum of tickets
2. **WG2 Population:** At least current month rows should have WG2 populated
3. **TYPE Distribution:** Verify M and P types exist for expected months
4. **Month_Year Format:** Should be "MM-YY" format (e.g., "11-25")

### Visual Reconciliation
1. **Dept-Wide Totals:** ETL output totals should match Power BI visual export
2. **All Bureaus:** ETL output by WG2 should match Power BI visual export
3. **Top 5 Queries:** Should return data for most recent month
4. **Moving Violations:** Should exclude Traffic Bureau officers

### ETL Script Validation
1. **Assignment Mapping:** ETL should populate WG2 from Assignment Master
2. **Badge Normalization:** Badge numbers should be normalized to 4-digit strings
3. **Current Month Processing:** Should process latest e-ticket export
4. **Backfill Integration:** Should preserve historical data from backfill

---

## Output Requirements

Provide:
1. **Diagnostic Report:**
   - Current data state (row counts, column status, WG2 population)
   - Issues found (missing columns, null values, mapping failures)
   - Comparison results (ETL vs visuals, expected vs actual)

2. **Fix Recommendations:**
   - ETL script changes needed
   - M code updates required
   - DAX measure fixes
   - Power BI visual fixes
   - Data cleanup steps

3. **Corrected Code:**
   - Updated M code for all queries
   - Fixed DAX measures
   - ETL script fixes (if needed)
   - Python fix scripts (if needed)

4. **Validation Results:**
   - Data accuracy verification
   - Visual reconciliation
   - Totals matching

---

## Additional Context

### Workflow
1. ETL script processes current month from e-ticket export
2. Merges with historical backfill data
3. Enriches with Assignment Master (should populate WG2)
4. Outputs to `summons_powerbi_latest.xlsx`
5. Power BI queries load from workbook
6. Visuals display aggregated data

### Key Relationships
- Badge Number (`PADDED_BADGE_NUMBER`) → Assignment Master → WG2 (Bureau)
- TYPE ("M" = Moving, "P" = Parking, "C" = Other)
- Month_Year format: "MM-YY" (e.g., "11-25" = November 2025)

### Business Rules
- Traffic Bureau officers should NOT appear in Moving Violations Top 5
- Each row in staging workbook = 1 ticket (no TICKET_COUNT column)
- WG2 should be populated from Assignment Master for all current month rows
- Historical/backfill rows may have null WG2 (aggregate data)

---

## Quick Reference: File Paths Summary

```
Master_Automation/
├── all_summons_m_code.txt                    # All Power BI M code queries
├── config/scripts.json                        # ETL script configuration
├── scripts/
│   ├── diagnose_summons_assignment_mapping.py
│   ├── fix_summons_wg2_from_assignment.py
│   ├── compare_summons_deptwide.py
│   ├── compare_summons_all_bureaus.py
│   ├── diagnose_summons_blank_bureau.py
│   └── run_summons_with_overrides.py
└── logs/                                      # ETL execution logs

02_ETL_Scripts/Summons/
├── main_orchestrator.py                       # Main ETL entry point
├── summons_etl_enhanced.py                    # Production ETL script
└── [other Python scripts]

03_Staging/Summons/
└── summons_powerbi_latest.xlsx                # ETL output (Power BI source)

05_EXPORTS/_Summons/E_Ticket/
└── YY_MM_e_ticketexport.csv                   # Current month e-ticket data

09_Reference/Personnel/
└── Assignment_Master_V2.csv                   # Badge → Bureau mapping

PowerBI_Date/
├── Backfill/YYYY_MM/summons/                  # Historical backfill data
└── _DropExports/                              # ETL outputs (before organization)
```

---

## Next Steps - Action Plan for Claude Code

**⚠️ UPDATE (December 12, 2025):** Most issues are already resolved! See "Current Status" section above. **Remaining Action:** Only the DAX measure needs to be updated in Power BI Desktop. ### Quick Action (If Starting Fresh)

1. **Read Latest Diagnostic Report**
   - `SUMMONS_DIAGNOSTIC_REPORT_2025_12_12.md` - Complete findings
   - `SUMMONS_DAX_MEASURES_CORRECTED.txt` - Corrected DAX measure

2. **Update DAX Measure in Power BI**
   - Open Power BI Desktop
   - Navigate to `___Summons` table
   - Edit `___Total Tickets` measure
   - Change to: `___Total Tickets = COUNTROWS('___Summons')`
   - Save and refresh

**That's it! ** All other components are working correctly. ---

### Full Action Plan (If Issues Recur or New Problems Found)

**After reading the initial files, follow this action plan:**

### Phase 1: Diagnostic & Validation (Start Here)

1. **Verify Current Data State**
   - Read `summons_powerbi_latest.xlsx` (sheet `Summons_Data`)
   - Confirm: `TICKET_COUNT` and `ASSIGNMENT_FOUND` columns do NOT exist
   - Count null `WG2` values vs populated `WG2_ASSIGN` values
   - Check `TYPE` column values (should have "M", "P", "C", etc.) - Verify `Month_Year` format (should be "MM-YY" like "11-25")

2. **Compare M Code vs Actual Data**
   - Read `all_summons_m_code.txt`
   - Identify all column references in M code
   - Cross-reference with actual columns in Excel file
   - List any mismatches (columns referenced but don't exist)

3. **Run Diagnostic Scripts**
   - Execute `scripts/diagnose_summons_assignment_mapping.py` to verify WG2 issue
   - Check if `WG2_ASSIGN` has values where `WG2` is null
   - Verify Assignment Master has all badges from current month data

### Phase 2: Fix Critical Issues (Priority Order)

**⚠️ NOTE:** As of December 12, 2025, most of these are already fixed. Only Priority 4 (DAX Measure) needs action. **Priority 1: Fix WG2 Column** ✓ **ALREADY FIXED**
- **Status:** WG2 is populated from WG2_ASSIGN (134,144 rows have assignments)
- **Action:** No action needed unless new data shows WG2 is null
- **If issue recurs:** Run or update `scripts/fix_summons_wg2_from_assignment.py`

**Priority 2: Verify M Code Handles Missing Columns** ✓ **ALREADY FIXED**
- **Status:** M code correctly handles missing `TICKET_COUNT` and `ASSIGNMENT_FOUND` columns
- **Action:** No action needed - queries are working correctly
- **If issue recurs:** Review `all_summons_m_code.txt` and ensure dynamic column filtering

**Priority 3: Fix Top 5 Queries** ✓ **ALREADY WORKING**
- **Action:** Verify `___Top_5_Moving_Violations` and `___Top_5_Parking_Violations` return data
- **Check:**
  - Moving violations query excludes "TRAFFIC BUREAU" from WG2
  - Both queries handle null `TYPE` values (fallback to `VIOLATION_TYPE`)
  - Both queries use `WG2_ASSIGN` as fallback if `WG2` is null
  - Filtering logic allows null/empty `WG2` if officer name exists
- **Test:** Run queries in Power Query Editor and verify they return results

**Priority 4: Fix DAX Measures** ⚠️ **ACTION REQUIRED**
- **Action:** Update `___Total Tickets` measure in Power BI Desktop
- **Current issue:** Measure may not be calculating correctly in visual context
- **Fix:** Use `COUNTROWS('___Summons')`:
  ```dax
  ___Total Tickets = COUNTROWS('___Summons')
  ```
- **Instructions:**
  1. Open Power BI Desktop
  2. Navigate to `___Summons` table in Fields pane
  3. Right-click `___Total Tickets` measure → Edit
  4. Replace formula with: `COUNTROWS('___Summons')`
  5. Save and refresh visuals
- **Alternative (if context needed for specific visuals):**
  ```dax
  ___Total Tickets = 
      CALCULATE(
          COUNTROWS('___Summons'),
          ALLEXCEPT('___Summons', '___Summons'[TYPE], '___Summons'[Month_Year])
      )
  ```
- **See:** `SUMMONS_DAX_MEASURES_CORRECTED.txt` for full details

### Phase 3: Validation & Testing

1. **Data Validation**
   - Compare row counts: ETL output vs Power BI query results
   - Verify WG2 population: Check percentage of rows with WG2 populated
   - Validate TYPE distribution: Ensure M and P types exist for expected months
   - Check Month_Year format: All values should be "MM-YY" format

2. **Query Validation**
   - Test all three M code queries in Power Query Editor
   - Verify no errors when refreshing queries
   - Check that Top 5 queries return data
   - Confirm column names match what visuals expect

3. **Visual Validation** (If Power BI file available)
   - Remove broken field references from visuals
   - Update visuals to use correct field names
   - Remove relationships using `TICKET_COUNT` or `ASSIGNMENT_FOUND`
   - Delete broken measures/calculated columns
   - Test `___Total Tickets` measure in visuals

4. **Comparison Validation**
   - If visual exports available, compare:
     - ETL output totals vs Power BI visual exports
     - Dept-Wide totals should match
     - All Bureaus totals should match by WG2

### Phase 4: Documentation & Reporting

**Create a summary report with:**
1. **Issues Found:** List all problems identified
2. **Fixes Applied:** What was changed and how
3. **Validation Results:** Data accuracy checks, query tests, visual tests
4. **Remaining Issues:** Any problems that couldn't be fixed
5. **Recommendations:** Suggestions for ETL script improvements, Power BI model improvements

**Output Files:**
- Updated M code (if changes made)
- Updated DAX measures (if changes made)
- Diagnostic report (CSV or text file)
- Fix script (if created/updated)

---

## Quick Start Prompt for Claude Code

**Copy this prompt to start troubleshooting:**

### If Starting Fresh (Recommended)
```
I need to verify the current state of Summons data in Power BI. According to the latest diagnostic report (December 12, 2025), most issues are resolved. Please:
1. Read SUMMONS_DIAGNOSTIC_REPORT_2025_12_12.md to see latest findings
2. Verify the DAX measure ___Total Tickets is correct (should be COUNTROWS('___Summons'))
3. If measure needs updating, provide the corrected version
4. Confirm all other components (M code, WG2, queries) are still working correctly

Time estimate: 5-10 minutes for verification. ```

### If Issues Recur or New Problems Found
```
I need to troubleshoot and fix Summons data issues in Power BI.

I've read the initial files:

1. all_summons_m_code.txt - Current Power BI M code
2. summons_powerbi_latest.xlsx - Actual data structure
3. config/scripts.json - ETL configuration

Key Issues to Check:
- WG2 Column status (should be populated from WG2_ASSIGN)
- TICKET_COUNT and ASSIGNMENT_FOUND columns (should NOT exist)
- DAX measure ___Total Tickets (should use COUNTROWS)
- Top 5 queries (should return data)

Please:
1. First, verify the current data state (confirm missing columns, WG2 status)
2. Compare M code column references vs actual columns in Excel
3. If WG2 is null, fix by copying from WG2_ASSIGN (Priority 1)
4. Verify M code handles missing columns correctly (Priority 2)
5. Verify Top 5 queries return data (Priority 3)
6. Provide corrected DAX measure for ___Total Tickets (Priority 4)
7. Create a validation report showing what was found/fixed

Start with Phase 1 diagnostics, then proceed through the fixes in priority order. ```

---

**Ready for troubleshooting! ** Use this guide to systematically identify and fix all Summons data issues.


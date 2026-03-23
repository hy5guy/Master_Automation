# In Person Training Query Fix

**Current state (workspace, 2026-03):** Production M is **`m_code/training/___In_Person_Training.m`**. It loads **`Policy_Training_Monthly.xlsx`** (`Training_Log` / `Training_Log_Clean`), not only `InPerson_Prior_Month_List`. YTD and report-month filtering are in **DAX**. See **`docs/POLICY_TRAINING_AUTOMATION_AND_COST_VISUAL.md`**. The notes below describe an earlier troubleshooting thread.

## Issue
The query `___In_Person_Training` is only showing data from November 2025, but it should be updating with current data.

## Root Cause
The query loads from the sheet `InPerson_Prior_Month_List` which is designed to contain only the **prior month's** data. Since we're now in January 2026, the "prior month" should be December 2025, but the data only goes up to November 2025.

## Available Data
- **InPerson_Prior_Month_List**: 16 rows, November 2025 only (2025-11-03 to 2025-11-24)
- **Training_Log_Clean**: 269 rows, all data from 2024-11-04 to 2025-11-24

## Solutions

### Option 1: Change Query to Use Training_Log_Clean (Recommended if you want all data)
Change the query to load from `Training_Log_Clean` instead of `InPerson_Prior_Month_List`:
- This sheet contains ALL training records, not just the prior month
- You can add a date filter in the M code if you only want recent months

### Option 2: Run the ETL Script to Update Data
The ETL script `src\policy_training_etl.py` needs to be run to:
- Process new data from the source file
- Update the `InPerson_Prior_Month_List` sheet with December 2025 data

### Option 3: Add Date Filter to Show Recent Months
If you want to keep using `InPerson_Prior_Month_List` but show more than just the prior month, you could:
- Switch to `Training_Log_Clean` 
- Add a filter for the last 3-6 months in the M code

## Recommendation
Since the query name is `___In_Person_Training` (not "Prior Month"), it seems like you want all training data, not just the prior month. **Option 1** (using `Training_Log_Clean`) is the best solution.

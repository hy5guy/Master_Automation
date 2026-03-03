# In Person Training Query - Issue Summary

## Problem
The query `___In_Person_Training` is only showing data from November 2025, but the source file has December 2025 data.

## Findings
1. **Source file** (`Policy_Training_Monthly.xlsx`) has December 2025 data (24 rows)
2. **ETL output** (`policy_training_outputs.xlsx`) sheet `InPerson_Prior_Month_List` only has November 2025 (16 rows)
3. **ETL output** sheet `Training_Log_Clean` has data through November 2025, but not December 2025

## Root Cause
The ETL script (`src\policy_training_etl.py`) needs to be run to process the December 2025 data from the source file and update the output file.

## Solutions

### Solution 1: Run ETL Script (Required for December 2025 Data)
Run the Policy Training ETL script to process new data:
- Location: `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Policy_Training_Monthly\src\policy_training_etl.py`
- This will update all sheets in the output file, including December 2025 data

### Solution 2: Use Training_Log_Clean Sheet (If You Want All Available Data)
I've created an updated query (`___In_Person_Training_UPDATED.m`) that:
- Uses `Training_Log_Clean` sheet (has all available data, not just prior month)
- Filters for "In-Person" delivery type
- Maintains the same column structure and logic as the original query

**Note:** This will show all data currently in the ETL output (through November 2025), but you'll still need to run the ETL to get December 2025 data.

## Recommended Action
1. **Run the ETL script** to process December 2025 data
2. If you want all data (not just prior month), use the updated query with `Training_Log_Clean`
3. Refresh the query in Power BI

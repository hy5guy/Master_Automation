# In Person Training Query - Solution

## Issue
The query `___In_Person_Training` is only showing data from November 2025, but the source file has December 2025 data (24 rows).

## Root Cause
1. The query loads from `InPerson_Prior_Month_List` sheet, which only contains the prior month's data
2. The ETL script hasn't been run to process December 2025 data from the source file
3. The `Training_Log_Clean` sheet also doesn't have December 2025 data yet (needs ETL run)

## Solution Options

### Option 1: Run the ETL Script (Recommended)
Run the Policy Training ETL script to process the new data:
- Script: `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Policy_Training_Monthly\src\policy_training_etl.py`
- This will update both `Training_Log_Clean` and `InPerson_Prior_Month_List` sheets

### Option 2: Change Query to Use Training_Log_Clean
I've created an updated M code file (`___In_Person_Training_UPDATED.m`) that:
- Uses `Training_Log_Clean` sheet instead of `InPerson_Prior_Month_List`
- Filters for "In-Person" delivery type
- Has all the same column mappings and logic

**Note:** This will show all available data (currently through November 2025), but you'll still need to run the ETL to get December 2025 data.

### Option 3: Query Source File Directly (Quick Fix)
If you need immediate access to December 2025 data, you could modify the query to load directly from the source file:
- Source: `C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Policy_Training\Policy_Training_Monthly.xlsx`
- Table: `Training_Log`
- Filter: `Delivery Method = "In-Person"`

This is not recommended for production as it bypasses the ETL processing.

## Recommended Action
1. Run the ETL script to process December 2025 data
2. If you want all data (not just prior month), use the updated query with `Training_Log_Clean`
3. Refresh the query in Power BI

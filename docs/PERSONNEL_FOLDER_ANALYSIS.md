# Personnel Folder and Summons Script Analysis

**Date:** 2026-02-13  
**Purpose:** Verify personnel file usage and streamline Personnel folder

**Note (2026-03-23):** Summons personnel enrichment in this workspace is driven by **`scripts/summons_etl_normalize.py`** (via **`run_summons_etl.py`**). References below to **`summons_etl_enhanced.py`** describe the older `02_ETL_Scripts/Summons/` script if still in use elsewhere.

---

## Key Finding: Assignment_Master_V2.csv Status

### Canonical File Analysis
**File:** `09_Reference\Personnel\Assignment_Master_V2.csv`
- **Size:** 61.9 KB (63,424 bytes)
- **Rows:** 387 total rows
- **Data Rows:** 166 personnel records (221 empty/header rows)
- **Columns:** 42 columns
- **Key Columns:** FULL_NAME, BADGE_NUMBER, TEAM, STATUS, RANK (all present)
- **Last Modified:** 2026-02-04 16:35:34

### **CRITICAL ISSUE:** Empty Rows at Top

The CSV has empty rows that need to be cleaned. The schema doc says 168 records, but we have 166 non-null rows out of 387 total (221 empty rows).

---

## Summons Script Personnel File Usage

### Main Production Script: `summons_etl_enhanced.py`

**Personnel File Used:**
```python
self.assignment_master_path = self.base_path / "01_SourceData" / "Assignment_Master.xlsx"
```

**Location:** `01_SourceData\Assignment_Master.xlsx`

### Problem: **WRONG LOCATION**

The script is looking for:
- ❌ `01_SourceData\Assignment_Master.xlsx` (OLD LOCATION)

The canonical file is at:
- ✅ `09_Reference\Personnel\Assignment_Master_V2.csv` (CORRECT LOCATION)

### Other Scripts Using Assignment_Master_V2.csv (Correctly)

**Production scripts:** 7 scripts found
1. `SummonsMaster_Simple.py` - Uses `09_Reference\Personnel\Assignment_Master_V2.csv` ✅
2. `SummonsMaster.py` - Uses `09_Reference\Personnel\Assignment_Master_V2.csv` ✅
3. `SummonsMaster_Transition.py` - Uses `09_Reference\Personnel\Assignment_Master_V2.csv` ✅
4. `SummonsMaster_Drop_In.py` - Uses `09_Reference\Personnel\Assignment_Master_V2.csv` ✅
5. `create_clean_output.py` - Uses `09_Reference\Personnel\Assignment_Master_V2.csv` ✅

**Archive scripts:** Many use old path `_Hackensack_Data_Repository\ASSIGNED_SHIFT\Assignment_Master_V2.xlsx`

---

## Personnel Folder Files

### Files to KEEP

**Root Level (Essential):**
1. ✅ `Assignment_Master_V2.csv` - **CANONICAL** (61.9 KB, 2026-02-04) - **NEEDS CLEANUP** (remove empty rows)
2. ✅ `2025_12_29_assigned_shift.csv` - Recent shift schedule (18.0 KB, 2026-01-05)
3. ✅ `Assignment_Master_SCHEMA.md` - Documentation (keep)

**Archive Folders (Keep):**
4. ✅ `99_Archive/` - Historical versions (12 CSV files, 11 XLSX files)
5. ✅ `backups/` - Backup copies (1 CSV file)

### Files to REVIEW/REMOVE

**Root Level (Potentially Outdated):**
- ❌ `Assignment_Master_V2.xlsx` (59.7 KB, 2025-10-08) - **OLDER than canonical CSV**
  - Check if any scripts need this
  - If not needed, move to 99_Archive

---

## Required Actions

### 1. Fix summons_etl_enhanced.py Path ❌ CRITICAL

**Current (Line 66):**
```python
self.assignment_master_path = self.base_path / "01_SourceData" / "Assignment_Master.xlsx"
```

**Should be:**
```python
self.assignment_master_path = self.base_path / "09_Reference" / "Personnel" / "Assignment_Master_V2.csv"
```

### 2. Clean Assignment_Master_V2.csv ❌ CRITICAL

**Problem:** File has 221 empty rows at the top (387 total rows, only 166 with data)

**Action:** Clean the CSV to remove empty rows:
```powershell
python -c "
import pandas as pd
df = pd.read_csv('09_Reference/Personnel/Assignment_Master_V2.csv')
# Drop completely empty rows
df_clean = df.dropna(how='all')
# Also drop rows where all key columns are null
key_cols = ['FULL_NAME', 'BADGE_NUMBER', 'TEAM', 'STATUS', 'RANK']
existing_keys = [c for c in key_cols if c in df_clean.columns]
df_clean = df_clean.dropna(subset=existing_keys, how='all')
# Save
df_clean.to_csv('09_Reference/Personnel/Assignment_Master_V2_CLEANED.csv', index=False)
print(f'Cleaned: {len(df)} -> {len(df_clean)} rows')
"
```

### 3. Archive Outdated Assignment_Master_V2.xlsx

**File:** `Assignment_Master_V2.xlsx` (59.7 KB, 2025-10-08)  
**Status:** Older than canonical CSV (2026-02-04)

**Action:**
```powershell
Move-Item "09_Reference\Personnel\Assignment_Master_V2.xlsx" `
          "09_Reference\Personnel\99_Archive\2025_10_08_Assignment_Master_V2.xlsx"
```

### 4. Verify December 2025 Summons Backfill

**Created:** `PowerBI_Data\Backfill\2025_12\summons\2025_12_department_wide_summons.csv` ✅

**Data:** 26 rows (13 months × 2 types: M and P)
- M (Moving): 452 (12-24) through 436 (12-25)
- P (Parking): 1778 (12-24) through 2874 (12-25)

**Ready for processing** once other issues fixed.

---

## Comparison: Which Scripts Need Which Files

### Scripts Using Correct Path (09_Reference\Personnel\Assignment_Master_V2.csv)
✅ Most SummonsMaster_*.py scripts  
✅ create_clean_output.py  
✅ test scripts

### Scripts Using OLD Path (01_SourceData or _Hackensack_Data_Repository)
❌ summons_etl_enhanced.py (main_orchestrator calls this!)  
❌ Many rolling_13_month_etl_*.py scripts  
❌ badge fix scripts

---

## Summary

### Issues Found:
1. ❌ **CRITICAL:** `summons_etl_enhanced.py` uses wrong personnel file path
2. ❌ **DATA QUALITY:** `Assignment_Master_V2.csv` has 221 empty rows (needs cleaning)
3. ❌ **OUTDATED:** `Assignment_Master_V2.xlsx` in root is older than canonical CSV

### Personnel Data Status:
- ✅ Canonical CSV exists and has 166 personnel records
- ❌ Empty rows need cleanup
- ❌ Root folder needs streamlining (move .xlsx to archive)

### Next Steps:
1. Clean Assignment_Master_V2.csv (remove empty rows)
2. Update summons_etl_enhanced.py path
3. Move outdated .xlsx to archive
4. Test Summons ETL with corrected path
5. Process December 2025 backfill data

*Analysis completed: 2026-02-13*

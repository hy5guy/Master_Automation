# Response Time Source Migration - timereport Folder

**Date**: February 9, 2026  
**Status**: Validation Updated  
**Impact**: Response Times Monthly Generator workflow

---

## Summary of Changes

### What Changed
Response Time data source has moved from `monthly_export` to `timereport` folder structure:

**Old Path**:
```
C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_CAD\monthly_export
```

**New Path**:
```
C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_CAD\timereport
```

### New Directory Structure

The timereport folder follows a clean separation pattern:

```
timereport/
├── monthly/
│   └── 2026_01_timereport.xlsx
└── yearly/
    ├── 2017/
    │   └── 2017_full_timereport.xlsx
    ├── 2018/
    │   └── 2018_full_timereport.xlsx
    ├── 2019/
    │   └── 2019_full_timereport.xlsx
    ├── 2020/
    │   └── 2020_full_timereport.xlsx
    ├── 2021/
    │   └── 2021_full_timereport.xlsx
    ├── 2022/
    │   └── 2022_full_timereport.xlsx
    ├── 2023/
    │   └── 2023_full_timereport.xlsx
    ├── 2024/
    │   └── 2024_full_timereport.xlsx
    └── 2025/
        └── 2025_full_timereport.xlsx
```

**Key Benefits**:
- Monthly and yearly reports are cleanly separated
- Reduces risk of overlap and double-counting
- Follows established best practice (same pattern recommended for Arrests)

---

## Changes Made

### 1. Updated Validation in `run_all_etl.ps1`

**File**: `scripts\run_all_etl.ps1`  
**Lines**: 187-217, 218-248

**Changes**:
1. Updated "Response Times" validation case
   - Changed base path from `monthly_export` to `timereport`
   - Added note: "Source moved to timereport folder (2026-02-09)"

2. Added "Response Times Monthly Generator" validation case
   - New case handles the specific script name from config
   - Uses same timereport base path
   - Provides specific error messages and directory listing on failure

**Expected Format**: `YYYY/YYYY_MM_Monthly_CAD.xlsx`

**Example**: For January 2026:
```
C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_CAD\timereport\2026\2026_01_Monthly_CAD.xlsx
```

---

## Testing Sequence

### Step 1: Validate Inputs

```powershell
# Run dry-run mode to validate all inputs
.\scripts\run_all_etl.ps1 -DryRun

# Expected output: Zero missing-input flags for Response Times
# Should show: "CAD timereport export found: [path]"
```

### Step 2: Run Response Times Only

```powershell
# Execute Response Times Monthly Generator only
.\scripts\run_etl_script.ps1 -ScriptName "Response Times Monthly Generator"

# Note: Script must exist in configured location:
# C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Response_Times\response_time_monthly_generator.py
```

### Step 3: Verify Outputs

```powershell
# Check for output files in PowerBI drop folder
Get-ChildItem "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\_DropExports" -Filter "*response*"

# Expected output pattern (from config):
# PowerBI_Data\Backfill\*\response_time\*_Average_Response_Times__Values_are_in_mmss.csv
```

### Step 4: Power BI Refresh

1. Open Power BI report
2. Click "Refresh"
3. Verify:
   - No data load errors
   - Date ranges are correct
   - Record counts match expectations
   - No duplicate entries

---

## Configuration Reference

### scripts.json - Response Times Configuration

**Order 5**: Response Times Diagnostic (Disabled)
```json
{
  "name": "Response Times Diagnostic",
  "path": "C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\02_ETL_Scripts\\Response_Times",
  "script": "response_time_diagnostic.py",
  "enabled": false,
  "output_to_powerbi": false,
  "order": 5,
  "timeout_minutes": 30
}
```

**Order 5.5**: Response Times Monthly Generator (Enabled)
```json
{
  "name": "Response Times Monthly Generator",
  "path": "C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\02_ETL_Scripts\\Response_Times",
  "script": "response_time_monthly_generator.py",
  "enabled": true,
  "output_to_powerbi": false,
  "order": 5.5,
  "timeout_minutes": 30,
  "notes": "Generates monthly CSV files for Power BI. Requires CAD source file to be synced locally."
}
```

---

## Next Steps (Pending)

### Python Script Updates Required

The following Python scripts need to be updated to use the new timereport path:

1. **response_time_monthly_generator.py**
   - Update input path to: `C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_CAD\timereport`
   - Add logic to select monthly vs yearly data
   - Implement recursive folder scanning if needed
   - Add logging for selected input files

2. **response_time_diagnostic.py** (if re-enabled)
   - Update input path to timereport folder
   - Update comparison logic for new folder structure

### Power BI M Query Updates

**File**: `m_code/response_time_calculator.m`

**Decision Required**: Determine Power BI data source strategy

**Option A**: Power BI reads directly from timereport
- Update M query base path to timereport folder
- Update file selection logic for monthly folder
- Test with new path structure

**Option B**: Power BI continues reading from Backfill (RECOMMENDED)
- Keep M query unchanged
- Python scripts handle transformation
- Maintain current data flow architecture

---

## Rollback Plan

If issues arise, revert changes:

```powershell
# 1. Revert validation changes in run_all_etl.ps1
git checkout -- scripts\run_all_etl.ps1

# 2. Test with old path
.\scripts\run_all_etl.ps1 -DryRun

# 3. Verify old monthly_export path still exists and has data
Test-Path "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_CAD\monthly_export"
```

---

## Related Documentation

- `docs\IMPLEMENTATION_CHECKLIST_2026_02_09.md` - Complete implementation guide
- `config\scripts.json` - ETL orchestration configuration
- `config\response_time_filters.json` - Response time specific filters
- `scripts\run_all_etl.ps1` - Main orchestrator with validation
- `m_code\response_time_calculator.m` - Power BI M query

---

## Questions to Address

Before proceeding with Python script updates:

1. Does `response_time_monthly_generator.py` exist and is it functional?
2. What is the expected monthly file naming pattern in timereport/monthly/?
   - Current observed: `2026_01_timereport.xlsx`
   - Expected by validation: `2026/2026_01_Monthly_CAD.xlsx`
3. Should the script process monthly files, yearly files, or both?
4. What is the correct output location for Power BI integration?
5. Are there any special filtering requirements from `config\response_time_filters.json`?

---

## Status Checklist

- [x] Updated validation in run_all_etl.ps1 for "Response Times"
- [x] Added validation case for "Response Times Monthly Generator"
- [x] Documented new timereport folder structure
- [x] Created testing sequence guide
- [ ] Update response_time_monthly_generator.py (pending script review)
- [ ] Update response_time_diagnostic.py (pending script review)
- [ ] Decide on Power BI data source strategy
- [ ] Update M query if needed
- [ ] Test end-to-end data flow
- [ ] Verify Power BI report accuracy
- [ ] Update CHANGELOG.md

---

**Last Updated**: February 9, 2026  
**Migration Phase**: Validation Layer Complete, Python Scripts Pending

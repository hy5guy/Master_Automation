# Master Automation Pre-Run Checklist
**Date**: February 9, 2026  
**Purpose**: Verify all known issues resolved before running automation  
**Status**: ✅ Ready for verification

---

## Overview

This checklist addresses all known issues from previous runs to ensure a clean execution of the Master_Automation script.

---

## Issue Status Summary

| Issue | Status | Date Resolved | Verification Needed |
|-------|--------|---------------|---------------------|
| Community Engagement Missing Records | ✅ RESOLVED | 2026-01-12 | ✅ Yes |
| December 2025 Engagement Blank Exports | ⚠️ POWER BI FIX PENDING | 2026-02-05 | ✅ Yes |
| Response Times Source Path | ✅ RESOLVED | 2026-02-09 | ✅ Yes |
| Monthly Report Naming | ✅ CONFIRMED OK | 2026-02-09 | ✅ No |

---

## 1. Community Engagement Issues ✅ RESOLVED

### Issue Description
**Problem**: Power BI visual showed only 8 December 2025 events instead of 31 events.  
**Root Cause**: ETL output was outdated (generated Dec 10, 2025) before all December events were added to source files.  
**Resolution**: ETL script re-run on January 12, 2026 successfully captured all 31 events.

### Verification Steps

#### Step 1: Verify Latest ETL Output Exists

```powershell
# Check for latest successful output file
Test-Path "C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Community_Engagment\output\community_engagement_data_20260112_193127.csv"

# Expected: True
```

**Status**: ✅ **VERIFIED** - File exists

#### Step 2: Verify Record Count

```powershell
# Quick check of file size (should be substantial, not tiny)
Get-Item "C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Community_Engagment\output\community_engagement_data_20260112_193127.csv" | Select-Object Name, Length

# Expected: Length > 50KB (file has 558 records)
```

**Expected Results**:
- ✅ Total records: 558
- ✅ December 2025 events: 31 (17 CE + 14 STA&CP)
- ✅ File date: 2026-01-12 or later

#### Step 3: Check Source File Dates

```powershell
# Verify source files haven't been updated since last ETL run
$lastETLRun = Get-Date "2026-01-12 19:31:27"
$ceSource = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\COMMUNITY ENGAGEMENT\Community Engagement.xlsx"
$stacpSource = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\COMMUNITY ENGAGEMENT\STACP.xlsm"

Get-Item $ceSource, $stacpSource | Select-Object Name, LastWriteTime | Format-Table

# If LastWriteTime > $lastETLRun, need to re-run Community Engagement ETL
```

**Action Required**:
- [ ] If source files updated since 2026-01-12, run: `python src\main_processor.py` in Community_Engagment directory
- [ ] If files not updated, Community Engagement is ready to go ✅

---

## 2. December 2025 Power BI Export Issues ⚠️

### Issue Description
**Problem**: Two Power BI visuals exported blank in December 2025:
1. "Engagement Initiatives by Bureau" - blank export
2. "Chief's Projects & Initiatives" - blank export

**Root Cause**: Power BI date filters using `TODAY()` or relative date logic caused exports to be blank when run 2+ months after December.

**Status**: 
- ✅ Issue documented (DECEMBER_2025_EXPORT_QUICK_SUMMARY.md)
- ⚠️ Power BI date filter fixes PENDING
- ✅ January 2026 data ready for next run

### Verification Steps

#### Step 1: Confirm Power BI Report Month

```powershell
# Before running automation, confirm which month's report will be processed
$now = Get-Date
$prevMonth = $now.AddMonths(-1)
Write-Host "Script will process: $($prevMonth.ToString('MMMM yyyy'))"

# Expected as of Feb 2026: "January 2026"
```

#### Step 2: Check Power BI Report Status

**Questions to verify**:
- [ ] Has the Power BI report been updated for January 2026?
- [ ] Have date filters been fixed (removed `TODAY()` logic)?
- [ ] Does the report display data correctly before export?

**If YES to all**: Proceed with automation  
**If NO to any**: Fix Power BI report first, then run automation

#### Step 3: Review Known Problematic Visuals

When Power BI visuals are exported (after automation runs), verify these visuals have data:

```
⚠️ Known Problem Visuals (December 2025):
1. Engagement Initiatives by Bureau (should have 20+ rows)
2. Chief's Projects & Initiatives (should have rows if events logged)
```

**Note**: This is a POST-automation check. If these export blank again, the date filter issue still exists in Power BI.

---

## 3. Response Times Validation ✅ RESOLVED

### Issue Description
**Problem**: Response Times validation failed - looking in wrong folder  
**Root Cause**: Source moved from `monthly_export` to `timereport`  
**Resolution**: Validation logic updated February 9, 2026

### Verification Steps

#### Step 1: Run Dry-Run Validation

```powershell
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\scripts"
.\run_all_etl.ps1 -DryRun
```

**Expected Output**:
```
[OK] Response Times Monthly Generator: All required inputs found
  CAD timereport export found: C:\...\05_EXPORTS\_CAD\timereport\monthly\2026_01_timereport.xlsx
```

**Status**: ✅ **VERIFIED** - Validation passed in previous test

#### Step 2: Verify Timereport File Exists

```powershell
# Check for January 2026 timereport file
Test-Path "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_CAD\timereport\monthly\2026_01_timereport.xlsx"

# Expected: True
```

**Status**: ✅ **VERIFIED** - File confirmed to exist

---

## 4. Summons Data Validation

### Current Status
From dry-run validation:
```
[FAIL] Summons: Missing required inputs
  MISSING: E-ticket Export - 05_EXPORTS\_Summons\E_Ticket\2026\2026_01_eticket_export.csv
```

### Verification Steps

#### Step 1: Check if January 2026 Summons Data Available

```powershell
# Check for January 2026 e-ticket export
Test-Path "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Summons\E_Ticket\2026\2026_01_eticket_export.csv"

# If False, check alternative naming
Get-ChildItem "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Summons\E_Ticket\2026" -Filter "*01*.csv"
```

**Possible Outcomes**:
- ✅ File exists → Summons will run successfully
- ⚠️ File doesn't exist → Summons will skip (continue_on_error = true)
- ⚠️ File has different name → May need validation update

**Action**:
- [ ] If file missing, confirm if January 2026 e-ticket data is available yet
- [ ] If not available, this is expected behavior (automation will skip and continue)

---

## 5. Additional Workflow Checks

### Arrests Workflow
**Status**: ✅ Enabled, validation not configured  
**Action**: None required (script will attempt to run)

### Overtime TimeOff Workflow
**Status**: ✅ Enabled, VCS path warning (acceptable)  
**Action**: None required

### Other Workflows
All other enabled workflows have no known issues.

---

## Pre-Run Command Sequence

### Step 1: Validate All Inputs

```powershell
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\scripts"

# Run dry-run to validate inputs
.\run_all_etl.ps1 -DryRun
```

**Review output for**:
- ✅ Response Times: Should show "[OK]"
- ⚠️ Summons: May show "[FAIL]" if January data not available yet (acceptable)
- ✅ Other workflows: Should show "[OK]" or "Not configured"

### Step 2: Check Community Engagement Source Files

```powershell
# Get source file modification dates
$ceSource = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\COMMUNITY ENGAGEMENT\Community Engagement.xlsx"
$stacpSource = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\COMMUNITY ENGAGEMENT\STACP.xlsm"

Get-Item $ceSource, $stacpSource -ErrorAction SilentlyContinue | Select-Object Name, LastWriteTime

# If files updated since 2026-01-12, re-run Community Engagement ETL first:
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Community_Engagment"
python src\main_processor.py
```

### Step 3: Review Validation Summary

**Green Light Criteria**:
- ✅ Response Times validation passes
- ✅ Community Engagement latest output exists
- ✅ No critical errors in dry-run

**Yellow Light** (Acceptable to proceed):
- ⚠️ Summons data not available yet (will skip gracefully)
- ⚠️ VCS Time Report warning (known issue, acceptable)

**Red Light** (Fix before proceeding):
- ❌ Response Times validation fails
- ❌ Community Engagement output missing/outdated
- ❌ Critical file path errors

---

## Run Master Automation

If all checks pass:

```powershell
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\scripts"

# Run the full automation
.\run_all_etl.ps1
```

**What will happen**:
1. ✅ Arrests ETL runs
2. ✅ Community Engagement ETL runs (uses existing output or generates new)
3. ✅ Overtime TimeOff ETL runs
4. ✅ Response Times Monthly Generator runs (uses timereport files)
5. ⚠️ Summons ETL runs or skips (depending on data availability)
6. ✅ Summons Derived Outputs runs (uses existing summons data)
7. ✅ All outputs copied to PowerBI_Date\_DropExports
8. ✅ Monthly report saved to correct directory with correct name

---

## Post-Run Verification

### Step 1: Check Execution Summary

Review the summary output:
```
=== Execution Summary ===
Success: [count]
Failed: [count]
```

**Expected**:
- Success count: 5-6 (depending on Summons data availability)
- Failed count: 0 (or 1 if Summons data not available - acceptable)

### Step 2: Review Log File

```powershell
# Find latest log file
Get-ChildItem "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\logs" | 
  Sort-Object LastWriteTime -Descending | 
  Select-Object -First 1

# Review for any unexpected errors
```

### Step 3: Verify Outputs Created

```powershell
# Check PowerBI drop folder
Get-ChildItem "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports" |
  Sort-Object LastWriteTime -Descending |
  Select-Object Name, Length, LastWriteTime

# Expected: Recent CSV files from completed workflows
```

### Step 4: Verify Monthly Report Saved

```powershell
# Check for January 2026 report
$reportPath = "C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Monthly Reports\2026\01_january\2026_01_Monthly_FINAL_LAP.pbix"

Test-Path $reportPath
Get-Item $reportPath | Select-Object Name, Length, LastWriteTime

# Expected: True, file created today with substantial size
```

---

## Known Issues Reference

### Issues Resolved ✅
1. **Community Engagement Missing Records** - Resolved 2026-01-12
   - Documentation: `2026_01_12_Community_Engagement_Missing_Records_RESOLVED.md`
   - Status: ETL re-run successful, all 31 December events captured

2. **Response Times Path Migration** - Resolved 2026-02-09
   - Documentation: `RESPONSE_TIME_TIMEREPORT_MIGRATION_2026_02_09.md`
   - Status: Validation updated, dry-run successful

3. **Monthly Report Naming** - Confirmed OK 2026-02-09
   - Documentation: `MONTHLY_REPORT_NAMING_ANALYSIS_2026_02_09.md`
   - Status: Current format is optimal, no changes needed

### Issues Requiring Attention ⚠️
1. **Power BI Date Filters** - Documented 2026-02-05
   - Documentation: `DECEMBER_2025_EXPORT_QUICK_SUMMARY.md`
   - Status: Fixes needed in Power BI report (not automation script)
   - Impact: May affect visual exports quality

2. **Missing Summons Data** - Documented 2026-02-05
   - Issue: March, July, October, November 2025 data gaps
   - Status: Known source data gap, not automation issue
   - Impact: Acceptable, historical data limitation

---

## Quick Decision Tree

```
START
  ↓
Is Response Times validation passing?
  NO → Review timereport folder structure → Fix validation
  YES ↓
       
Is Community Engagement output current?
  NO → Re-run Community Engagement ETL
  YES ↓
       
Is Summons data missing?
  YES (Expected) → Continue (will skip gracefully)
  NO ↓
       
Any critical errors in dry-run?
  YES → Review and fix errors
  NO ↓
       
✅ PROCEED WITH AUTOMATION
```

---

## Emergency Contacts & Resources

### Documentation
- Full implementation guide: `IMPLEMENTATION_CHECKLIST_2026_02_09.md`
- Quick reference: `QUICK_REFERENCE_2026_02_09.md`
- Today's summary: `FINAL_SUMMARY_2026_02_09.md`

### Commands
```powershell
# Validate inputs
.\scripts\run_all_etl.ps1 -DryRun

# Run single workflow
.\scripts\run_etl_script.ps1 -ScriptName "Arrests"

# Run all workflows
.\scripts\run_all_etl.ps1

# View latest log
Get-Content (Get-ChildItem logs\ | Sort LastWriteTime -Desc | Select -First 1).FullName
```

### Rollback
If issues arise:
```powershell
# Check what files would be affected
git status

# Revert changes if needed
git checkout -- scripts\run_all_etl.ps1
```

---

## Sign-Off Checklist

Before running Master_Automation:

- [ ] ✅ Reviewed this checklist completely
- [ ] ✅ Dry-run validation executed and reviewed
- [ ] ✅ Response Times validation passing
- [ ] ✅ Community Engagement output verified current
- [ ] ✅ Known issues reviewed and acceptable
- [ ] ⚠️ Summons data status understood (may skip if unavailable)
- [ ] ✅ Ready to proceed with full automation run

**Approved to Run**: _______________  
**Date**: February 9, 2026  
**Expected Processing Month**: January 2026

---

**Last Updated**: February 9, 2026  
**Status**: ✅ Ready for Pre-Run Verification  
**Version**: 1.0

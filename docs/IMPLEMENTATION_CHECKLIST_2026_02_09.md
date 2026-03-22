# Implementation Checklist - February 9, 2026

## Executive Summary

Master_Automation runs ETL scripts **sequentially** based on configured order. One script failure does not stop the rest. Parallel execution is noted as a future enhancement only.

**Key operational patterns:**
- Preview + validate inputs: `.\scripts\run_all_etl.ps1 -DryRun`
- Run one workflow: `.\scripts\run_etl_script.ps1 -ScriptName "Arrests"`
- Run full sequence: `.\scripts\run_all_etl.ps1`

---

## 1. Arrest Exports - Directory Layout

### Current State
- Script location: `02_ETL_Scripts\Arrests\arrest_python_processor.py`
- Configured in `config\scripts.json` (Order: 1, Enabled: true)

### Recommendation
**Keep monthly and yearly exports separated in different subfolders.**

**DO NOT** move both monthly and yearly exports into one root folder.

### Reasoning
- Mixed roots raise overlap and double-count risk
- Overlap already triggered dedup fixes in related pipelines
- Separation reduces repeat risk

### Update Required?
**YES** - When `arrest_python_processor.py` assumes a flat folder and your exports now sit under subfolders.

**NO** - When `arrest_python_processor.py` already scans recursively and filters cleanly.

### Arrest Script Update Checklist

If update is required:

- [ ] Set one base path (arrest export root)
- [ ] Walk subfolders recursively
- [ ] Filter by filename pattern (monthly vs yearly)
- [ ] Prefer `.xlsx` when multiple formats exist for the same export
- [ ] Log the selected input file path each run
- [ ] Test with dry run: `.\scripts\run_all_etl.ps1 -DryRun`
- [ ] Test single execution: `.\scripts\run_etl_script.ps1 -ScriptName "Arrests"`

### Validation Steps

```powershell
# 1. Dry run validation
.\scripts\run_all_etl.ps1 -DryRun

# 2. Check for missing-input flags in output
# Expected: zero missing-input flags for Arrests

# 3. Run Arrests only
.\scripts\run_etl_script.ps1 -ScriptName "Arrests"

# 4. Verify outputs in PowerBI_Data\_DropExports
# 5. Refresh Power BI and verify data integrity
```

---

## 2. Response Times - Source Moved to timereport

### Current State
- **New source folder**: `C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_CAD\timereport`
- Current config location: `02_ETL_Scripts\Response_Times`
- Enabled scripts in `config\scripts.json`:
  - "Response Times Diagnostic" (Order: 5, **Disabled**)
  - "Response Times Monthly Generator" (Order: 5.5, **Enabled**)

### Current Response Time Design

1. **Monthly Generator Script** (`response_time_monthly_generator.py`)
   - Outputs monthly CSV files in PowerBI_Date Backfill structure
   - Pattern: `PowerBI_Data\Backfill\*\response_time\*_Average_Response_Times__Values_are_in_mmss.csv`

2. **Power BI M Query** (`m_code/response_time_calculator.m`)
   - Updated for OneDrive paths and overlap handling
   - Reads from PowerBI_Data\Backfill structure

3. **Diagnostic Script** (`response_time_diagnostic.py`)
   - Compares backfill vs recalculated data
   - **Currently disabled** by default

### Update Targets

#### Target 1: Response Time Python Input Path

**Search for hardcoded references** to old export locations:
- `monthly_export` folder references
- Consolidated `ResponseTime_CAD` workbook references
- Replace with: `C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_CAD\timereport`

**Files to check:**
- `response_time_monthly_generator.py`
- `response_time_diagnostic.py`
- Any configuration files or path constants

#### Target 2: Dry-Run Validation Checks

**Update location**: `scripts\run_all_etl.ps1` (Lines 187-216)

Current validation checks for:
```powershell
"C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_CAD\monthly_export"
```

**Action Required**:
- [ ] Update validation path from `monthly_export` to `timereport`
- [ ] Update filename pattern if changed
- [ ] Current pattern: `YYYY/YYYY_MM_Monthly_CAD.xlsx`
- [ ] Verify pattern matches timereport exports

#### Target 3: Power BI Query Base Path

**Decision point**: Where will Power BI read from?

**Option A**: Power BI reads directly from timereport exports
- [ ] Update M code query base path to timereport
- [ ] Test Power BI refresh
- [ ] Verify data integrity

**Option B**: Power BI keeps reading from PowerBI_Data\Backfill
- [ ] Keep M code unchanged
- [ ] Keep Python layer as transformer
- [ ] Verify Python outputs to correct location

### Fast Test Sequence

```powershell
# 1. Run dry-run validation
.\scripts\run_all_etl.ps1 -DryRun

# Expected: Zero missing-input flags for Response Times

# 2. Run Response Times only
.\scripts\run_etl_script.ps1 -ScriptName "Response Times Monthly Generator"

# 3. Verify outputs land in PowerBI_Data\_DropExports
Get-ChildItem "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\_DropExports" -Filter "*response*"

# 4. Refresh Power BI and verify data
```

---

## 3. Implementation Priority

### High Priority (Complete First)

1. **Response Times timereport migration**
   - Currently enabled and active
   - Directly impacts monthly reporting
   - Clear path: update input paths in Python scripts
   - Update validation in run_all_etl.ps1

### Medium Priority

2. **Arrest directory structure validation**
   - Verify if current script already handles subfolders
   - If not, implement recursive folder scanning
   - Test with both monthly and yearly exports

---

## 4. Verification Checklist

### Before Any Changes

- [ ] Backup current configuration: `config\scripts.json`
- [ ] Backup current scripts in `02_ETL_Scripts`
- [ ] Document current input/output paths
- [ ] Run successful baseline: `.\scripts\run_all_etl.ps1 -DryRun`

### After Response Times Update

- [ ] Updated Python script paths to timereport
- [ ] Updated validation in run_all_etl.ps1
- [ ] Dry-run shows zero missing inputs
- [ ] Single script execution successful
- [ ] Outputs appear in PowerBI_Data\_DropExports
- [ ] Power BI refresh successful
- [ ] Data integrity verified (record counts, date ranges)

### After Arrests Update (If Required)

- [ ] Script scans subfolders recursively
- [ ] Filename filtering implemented
- [ ] File format preference set (.xlsx preferred)
- [ ] Logging added for selected input files
- [ ] Dry-run shows zero missing inputs
- [ ] Single script execution successful
- [ ] Outputs appear in PowerBI_Data\_DropExports
- [ ] Power BI refresh successful
- [ ] Data integrity verified (no duplicates, correct counts)

---

## 5. Key Files Reference

### Configuration
- `config\scripts.json` - Main orchestration configuration
- `config\response_time_filters.json` - Response time specific filters

### Orchestration Scripts
- `scripts\run_all_etl.ps1` - Main orchestrator with validation
- `scripts\run_etl_script.ps1` - Single script runner

### ETL Scripts
- `02_ETL_Scripts\Arrests\arrest_python_processor.py`
- `02_ETL_Scripts\Response_Times\response_time_monthly_generator.py`
- `02_ETL_Scripts\Response_Times\response_time_diagnostic.py`

### Power BI Integration
- `m_code\response_time_calculator.m` - M query for Power BI
- `PowerBI_Data\_DropExports\` - Output destination for Power BI

### Export Locations
- **Arrests**: `05_EXPORTS\_ARREST\` (structure TBD)
- **Response Times**: `05_EXPORTS\_CAD\timereport\` (NEW)
- **Response Times (old)**: `05_EXPORTS\_CAD\monthly_export\` (DEPRECATED)

---

## 6. Rollback Plan

If issues arise after changes:

### Response Times Rollback

```powershell
# 1. Revert Python script changes
git checkout -- "C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Response_Times\*.py"

# 2. Revert validation changes
git checkout -- scripts\run_all_etl.ps1

# 3. Test with old path
.\scripts\run_all_etl.ps1 -DryRun
```

### Arrests Rollback

```powershell
# 1. Revert arrest processor
git checkout -- "C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Arrests\arrest_python_processor.py"

# 2. Test
.\scripts\run_etl_script.ps1 -ScriptName "Arrests"
```

---

## 7. Next Steps

1. **Immediate**: Update Response Times for timereport source
2. **Validation**: Run full dry-run cycle
3. **Testing**: Execute Response Times single script
4. **Verification**: Confirm Power BI data integrity
5. **Documentation**: Update CHANGELOG.md with changes
6. **Review**: Assess Arrests directory structure needs

---

## 8. Questions to Answer

Before proceeding with Arrests update:

1. Does `arrest_python_processor.py` currently scan subfolders?
2. What is the current directory structure under `05_EXPORTS\_ARREST\`?
3. Are monthly and yearly exports currently mixed or separated?
4. What filename patterns are used for monthly vs yearly?
5. Are there multiple file formats (.csv, .xlsx) for the same export?

---

## Document History

| Date       | Author | Changes                          |
|------------|--------|----------------------------------|
| 2026-02-09 | System | Initial implementation checklist |

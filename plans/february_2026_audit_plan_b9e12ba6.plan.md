---
name: February 2026 Audit Plan
overview: Comprehensive audit and preparation plan for February 2026 monthly reporting cycle to ensure 100% ETL success and seamless orchestrated execution via run_all_etl.ps1
todos:
  - id: infrastructure-validation
    content: Run Pre_Flight_Validation.py and verify path portability with environment variables
    status: completed
  - id: source-data-check
    content: Validate January 2026 source files exist (E-Ticket, CAD timereport, VCS exports)
    status: completed
  - id: config-integrity
    content: Audit scripts.json and visual_export_mapping.json for correct 13-month enforcement (24/32 visuals)
    status: completed
  - id: dry-run-validation
    content: Execute run_all_etl.ps1 -DryRun to validate all ETL workflows and input files
    status: completed
  - id: 13-month-verification
    content: Test 13-month window enforcement using validate_13_month_window.py on sample exports
    status: completed
  - id: backfill-strategy-check
    content: Verify hybrid strategy for Overtime/TimeOff and Response Times backfill integration
    status: completed
  - id: visual-normalization-test
    content: Test process_powerbi_exports.py smart date inference and normalization pipeline
    status: completed
  - id: visual-export-review
    content: Export January 2026 Power BI visuals and run systematic mapping review to identify new visuals
    status: pending
  - id: export-workflow-enhancement
    content: Create streamlined batch script for visual export processing with date prompting
    status: completed
  - id: production-execution
    content: Execute full ETL orchestration and monitor for 100% success rate and proper file generation
    status: completed
isProject: false
---

# February 2026 Monthly Reporting Cycle - Pre-Flight Audit & Preparation Plan

## Architecture Understanding ✅

I have analyzed the Master_Automation ecosystem and understand the architecture as defined in `[Claude.md](Claude.md)`. The system is a centralized orchestration hub that runs Python ETL scripts feeding into Power BI reports, with these key components:

### Current System State (v1.15.8)

- **Status**: 100% Operational (6/6 ETL workflows + Power BI queries)
- **Orchestrator**: `[scripts/run_all_etl.ps1](scripts/run_all_etl.ps1)` - Main PowerShell controller
- **Path Portability**: `[scripts/path_config.py](scripts/path_config.py)` handles OneDrive root discovery
- **13-Month Windows**: 24 of 32 Power BI visuals enforce rolling windows via `[Standards/config/powerbi_visuals/visual_export_mapping.json](Standards/config/powerbi_visuals/visual_export_mapping.json)`

## Pre-Flight Audit Sequence

### Phase 1: Infrastructure Validation

#### 1.1 Path Portability Verification

- **Objective**: Ensure all scripts correctly utilize `scripts/path_config.py` without hardcoded user paths
- **Key Files**: 
  - `[scripts/path_config.py](scripts/path_config.py)` - Centralized `get_onedrive_root()` function
  - `[scripts/run_all_etl.ps1](scripts/run_all_etl.ps1)` - Uses `$OneDriveBase` from environment variables
- **Validation**: Run existing `[scripts/Pre_Flight_Validation.py](scripts/Pre_Flight_Validation.py)` to check critical dependencies
- **Environment Variables**: Verify `ONEDRIVE_BASE` or `ONEDRIVE_HACKENSACK` are properly set

#### 1.2 Configuration Integrity Check

- **Primary Config**: `[config/scripts.json](config/scripts.json)` - Contains 5 enabled ETL scripts with correct paths
- **Visual Mapping**: `[Standards/config/powerbi_visuals/visual_export_mapping.json](Standards/config/powerbi_visuals/visual_export_mapping.json)` - 32 visuals with 24 enforcing 13-month windows
- **Response Time Filters**: `[config/response_time_filters.json](config/response_time_filters.json)` - Enhanced filtering rules

### Phase 2: 13-Month Window Validation

#### 2.1 Visual Export Mapping Audit

- **Target**: Verify 24 specific visuals identified in v1.15.0 correctly enforce rolling windows
- **Reference**: `[docs/13_MONTH_QUICK_REFERENCE.md](docs/13_MONTH_QUICK_REFERENCE.md)` - Lists all 24 enforced vs 8 non-enforced visuals
- **Validation Tool**: `[scripts/validate_13_month_window.py](scripts/validate_13_month_window.py)` - Can validate single files or scan folders
- **Key Enforcement**: Department-Wide Summons, Training Cost, Monthly Accrual, NIBRS Clearance Rate (with pattern matching)

#### 2.2 Smart Date Inference Verification

- **Feature**: v1.15.1 Smart Date Inference (95% accuracy vs 70% filename-only)
- **Process Script**: `[scripts/process_powerbi_exports.py](scripts/process_powerbi_exports.py)` - Reads CSV data to infer dates
- **Logic**: 13-month visuals use LAST period column; single-month visuals read Period/Month_Year column

### Phase 3: ETL Workflow Integrity

#### 3.1 Source Data Validation (January 2026 Data)

- **Summons**: `05_EXPORTS\_Summons\E_Ticket\2026\2026_01_eticket_export.csv`
- **Response Times**: `05_EXPORTS\_CAD\timereport\monthly\2026_01_timereport.xlsx`
- **Overtime/TimeOff**: VCS time report exports (location varies)
- **Validation**: `[scripts/run_all_etl.ps1](scripts/run_all_etl.ps1)` has built-in `Test-RequiredInputs` function

#### 3.2 Backfill Strategy Verification

- **Overtime/TimeOff**: Hybrid strategy using `[scripts/overtime_timeoff_with_backfill.py](scripts/overtime_timeoff_with_backfill.py)`
  - Current month from v10 ETL + historical months from `PowerBI_Date\Backfill\YYYY_MM\vcs_time_report\`
- **Response Times**: Uses validated Backfill data with January 14 methodology (v2.8.3)
- **Summons**: Current month from E-Ticket + backfill for gap months (03-25, 07-25, 10-25, 11-25)

### Phase 4: "One-Off" Workflow Integration

#### 4.1 Summons Automation Analysis

- **Current State**: `[scripts/summons_backfill_merge.py](scripts/summons_backfill_merge.py)` handles gap month merging
- **Integration Point**: Documented in `[docs/SUMMONS_BACKFILL_INJECTION_POINT.md](docs/SUMMONS_BACKFILL_INJECTION_POINT.md)`
- **Validation Tools**: Multiple diagnostic scripts for WG2 mapping, missing months, Top 5 vs Dept-Wide validation

#### 4.2 Response Time Stability Check

- **M-Code**: `[m_code/___ResponseTimeCalculator.m](m_code/___ResponseTimeCalculator.m)` v2.8.0 - Fixed 31% error rate to 0%
- **ETL Script**: `[02_ETL_Scripts/Response_Times/response_time_diagnostic.py](02_ETL_Scripts/Response_Times/response_time_diagnostic.py)` - Currently enabled as main processor
- **Backfill Priority**: Backfill > visual_export > outputs > _DropExports

### Phase 5: Visual Export Normalization

#### 5.1 Process Pipeline Verification

- **Orchestrator Integration**: `[scripts/run_all_etl.ps1](scripts/run_all_etl.ps1)` includes Visual Export Normalization phase
- **Normalizer**: `[scripts/normalize_visual_export_for_backfill.py](scripts/normalize_visual_export_for_backfill.py)` - Handles 13-month enforcement and PeriodLabel preservation
- **Processor**: `[scripts/process_powerbi_exports.py](scripts/process_powerbi_exports.py)` - Match patterns, smart date inference, enforce 13-month windows

#### 5.2 Monthly Accrual Special Handling

- **Backfill Override**: Uses `backfill_folder: "vcs_time_report"` instead of `target_folder: "vcs_time_report"` 
- **Integration**: Ensures `[scripts/overtime_timeoff_with_backfill.py](scripts/overtime_timeoff_with_backfill.py)` finds normalized files in correct location

## Visual Export Processing Enhancement

### Current System Analysis

The system already includes sophisticated visual export processing:

- **Smart Date Inference**: `[scripts/process_powerbi_exports.py](scripts/process_powerbi_exports.py)` reads CSV data for 95% accuracy vs 70% filename-only
- **Visual Mapping**: `[Standards/config/powerbi_visuals/visual_export_mapping.json](Standards/config/powerbi_visuals/visual_export_mapping.json)` with 32 visuals (24 enforce 13-month windows)
- **Automatic Processing**: `[scripts/run_all_etl.ps1](scripts/run_all_etl.ps1)` includes Visual Export Normalization phase

### Enhanced Visual Export Workflow

#### 1. Streamlined Export-to-Backfill Pipeline

Create an automated batch script that processes exports from `_DropExports` with date prompting:

```batch
@echo off
echo Visual Export Processing for Master Automation
set /p REPORT_DATE="Enter report date (YYYY-MM format, e.g., 2026-01): "
echo Processing exports for %REPORT_DATE%...
python scripts\process_powerbi_exports.py --report-date %REPORT_DATE% --auto-organize
```

#### 2. January 2026 Visual Export Review

- **Export all January 2026 visuals** to `_DropExports` folder
- **Run systematic mapping review** using existing `[scripts/process_powerbi_exports.py](scripts/process_powerbi_exports.py)`
- **Identify new visuals** not in current `[visual_export_mapping.json](Standards/config/powerbi_visuals/visual_export_mapping.json)`
- **Update mapping configuration** for any new visual types

#### 3. Automated Date Prefix Logic

The existing system uses smart date inference from CSV content:

- **13-Month Visuals**: Uses LAST period column (e.g., columns `["01-25", "02-25", ..., "01-26"]` → uses `"01-26"` → `2026_01`)
- **Single-Month Visuals**: Reads Period/Month_Year column value
- **Fallback**: Filename pattern or previous month

#### 4. Summons Processing Integration

Based on the attached summons scripts, the system includes:

- **ETL Normalization**: `[scripts/summons_etl_normalize.py](scripts/summons_etl_normalize.py)` - Handles E-Ticket data with HTML cleaning and badge mapping
- **Pipeline Orchestration**: `[scripts/run_summons_pipeline.py](scripts/run_summons_pipeline.py)` - Full pipeline with integrity reporting
- **Integrity Validation**: `[scripts/generate_summons_integrity_report.py](scripts/generate_summons_integrity_report.py)` - Match rate analysis and unknown badge investigation

## Execution Checklist

### Pre-Execution Validation

1. **Environment Setup**: Verify Python dependencies from `[requirements.txt](requirements.txt)` (pandas, openpyxl)
2. **Path Validation**: Run `[scripts/Pre_Flight_Validation.py](scripts/Pre_Flight_Validation.py)`
3. **Input Validation**: Execute `.\scripts\run_all_etl.ps1 -DryRun` to validate all source files
4. **13-Month Check**: Verify visual export mapping enforcement counts (24/32 visuals)
5. **Visual Export Review**: Export January 2026 visuals and run mapping analysis

### Execution Sequence

1. **January Visual Export**: Export all January 2026 Power BI visuals to `_DropExports`
2. **Visual Mapping Review**: Run `python scripts\process_powerbi_exports.py --dry-run` to identify new visuals
3. **Primary ETL**: `.\scripts\run_all_etl.ps1` (runs 5 enabled scripts in order)
4. **Visual Normalization**: Automatic phase in orchestrator for Monthly Accrual files
5. **Power BI Integration**: Automatic copy to `_DropExports` folder
6. **Organization**: `PowerBI_Date\tools\organize_backfill_exports.ps1`
7. **Monthly Report**: Automatic save to `Shared Folder\Compstat\Monthly Reports\YYYY\MM_monthname\`

### Post-Execution Validation

1. **Output Verification**: Check file counts and schemas using `[scripts/validate_outputs.py](scripts/validate_outputs.py)`
2. **13-Month Windows**: Validate key visuals using `[scripts/validate_13_month_window.py](scripts/validate_13_month_window.py)`
3. **Backfill Integrity**: Compare outputs against known baselines using comparison scripts
4. **Power BI Refresh**: Verify M-code queries load data correctly with 0% errors

## Risk Mitigation

### High-Risk Areas

1. **Summons WG2 Mapping**: Use `[scripts/run_summons_with_overrides.py](scripts/run_summons_with_overrides.py)` if badge assignment issues occur
2. **Response Time Source**: Fallback paths configured in orchestrator for timereport structure changes
3. **Overtime/TimeOff Personnel File**: `[Assignment_Master_V2.csv](Assignment_Master_V2.csv)` must exist in Master_Automation root

### Contingency Plans

1. **Individual Script Failures**: Use `.\scripts\run_etl_script.ps1 -ScriptName "ScriptName"` for targeted re-runs
2. **Visual Export Issues**: Manual normalization using `[scripts/normalize_visual_export_for_backfill.py](scripts/normalize_visual_export_for_backfill.py)`
3. **13-Month Window Failures**: Use `[scripts/validate_13_month_window.py](scripts/validate_13_month_window.py)` for diagnosis and correction

## Success Metrics

- **ETL Success Rate**: 100% (6/6 workflows complete)
- **13-Month Compliance**: 24/24 enforced visuals contain exactly 13 months
- **Data Integrity**: 0% Power BI M-code errors across all queries
- **Execution Time**: Target <3 minutes total (historical: 2.04 minutes)
- **File Generation**: ~60 output files across all workflows
- **Backfill Integration**: Seamless hybrid strategy for Overtime/TimeOff and Response Times

The system is well-architected with comprehensive error handling, validation tools, and documentation. The February 2026 cycle should execute smoothly with this preparation plan.
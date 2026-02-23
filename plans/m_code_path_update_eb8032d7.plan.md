---
name: M Code Path Update
overview: Bulk replace `C:\Users\carucci_r\` with `C:\Users\RobertCarucci\` across all 32 active M code files so the Power BI template works on this laptop.
todos:
  - id: bulk-replace
    content: Find-and-replace C:\Users\carucci_r\ with C:\Users\RobertCarucci\ in all 32 active M code files
    status: pending
  - id: verify
    content: Verify zero remaining carucci_r references in active M code files (excluding archive)
    status: pending
  - id: resume-paste
    content: Resume pasting updated M code into the Power BI template
    status: pending
isProject: false
---

# M Code Path Update: carucci_r to RobertCarucci

## Problem

All M code files hardcode `C:\Users\carucci_r\OneDrive - City of Hackensack\` which is the work desktop path. This laptop uses `C:\Users\RobertCarucci\OneDrive - City of Hackensack\`. Power BI queries fail with "DataSource.NotFound" errors on this machine.

## Fix

Single find-and-replace across 32 active M code files (archive files left unchanged):

**Replace:** `C:\Users\carucci_r\` **With:** `C:\Users\RobertCarucci\`

## Files to Change (32 active files, ~36 occurrences)

- `m_code/arrests/` -- 3 files (___Arrest_Categories, ___Arrest_Distro, ___Top_5_Arrests)
- `m_code/benchmark/` -- 1 file (___Benchmark)
- `m_code/community/` -- 2 files (___Combined_Outreach_All, ___chief_projects)
- `m_code/csb/` -- 1 file (___CSB_Monthly)
- `m_code/detectives/` -- 2 files (___Detectives, ___Det_case_dispositions_clearance)
- `m_code/drone/` -- 1 file (___Drone)
- `m_code/esu/` -- 3 files (ESU_13Month, MonthlyActivity, TrackedItems)
- `m_code/nibrs/` -- 1 file (___NIBRS_Monthly_Report)
- `m_code/overtime/` -- 1 file (___Overtime_Timeoff_v3, 2 occurrences)
- `m_code/parameters/` -- 2 files (RootExportPath, EtlRootPath)
- `m_code/patrol/` -- 3 files (___Patrol, ___Chief2, ___REMU)
- `m_code/response_time/` -- 1 file (___ResponseTimeCalculator, 2 occurrences)
- `m_code/shared/` -- 0 files (no hardcoded paths)
- `m_code/ssocc/` -- 2 files (___SSOCC_Data, TAS_Dispatcher_Incident)
- `m_code/stacp/` -- 3 files (___STACP_pt_1_2, STACP_DIAGNOSTIC, ___Social_Media)
- `m_code/summons/` -- 4 files (summons_13month_trend, summons_all_bureaus, summons_top5_moving, summons_top5_parking)
- `m_code/training/` -- 1 file (___Cost_of_Training)
- `m_code/traffic/` -- 1 file (___Traffic)
- `m_code/all_m_code_26_january_monthly.m` -- consolidated file (24 occurrences)

## Work Desktop Impact

After this change, the `.m` source files will sync to the work desktop via OneDrive and will say `RobertCarucci`. On Monday when you open the template on the work desktop:

- **If the work desktop username is `carucci_r`**: Use Power BI Desktop's **Data Source Settings** (File > Options > Data Source Settings) to remap the paths back, OR run the reverse replacement (`RobertCarucci` back to `carucci_r`) in the .m files on that machine.
- **If the work desktop username is also `RobertCarucci`**: Everything will just work.

## What is NOT changed

- Archive files (`m_code/archive/`) -- historical, not deployed
- Python scripts (`scripts/path_config.py` handles portability via env vars)
- `config/scripts.json` -- uses `carucci_r` but only runs on the work desktop


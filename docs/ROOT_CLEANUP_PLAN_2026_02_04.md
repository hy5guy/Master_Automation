# Root Directory Cleanup Plan

**Date:** 2026-02-04  
**Current Root Files:** 91 files (excluding directories)

---

## File Categorization

### ✅ KEEP in Root (Essential Files)
1. `.gitignore` - Git ignore configuration
2. `README.md` - Main documentation
3. `CHANGELOG.md` - Version history
4. `SUMMARY.md` - Project summary
5. `Claude.md` - AI assistant guide
6. `verify_migration.ps1` - Migration verification script
7. `Master_Automation.code-workspace` - VS Code workspace file

**Total to Keep: 7 files**

---

## 🗂️ MOVE to Archives/Organized Locations

### 1. Response Time Documentation → `docs/response_time/`
- `2026_01_14_18_22_57_RESPONSE_TIME_ETL_EXECUTIVE_SUMMARY.html`
- `2026_01_14_18_27_55_Response_Time_ETL_Enhanced_Filtering_Implementation.html`
- `2026_01_14_18_39_05_Response Time ETL - Comparison Table.pdf`
- `Executive Summary. Routine Response Time Metric Correction.pdf`
- `Response Time Calculation Correction - Executive Summary.pdf`
- `Response Time Calculation Methods - Executive Comparison 1.pdf`
- `Response Time Calculation Methods - Executive Comparison.pdf`
- `Response Time ETL - Executive Packet.pdf`
- `Response Time ETL Filtering Implementation.pdf`
- `Response_Time_Calculation_Methods_Comparison.docx`
- `RESPONSE_TIME_COMPARISON_TABLE_SCRPA_v2.html`
- `Response_Time_ETL_Executive_Summary.docx`
- `response_time_executive_summary.html`

**Subtotal: 13 files**

### 2. Exported Visual Data (Testing/Validation) → `outputs/visual_exports/`
- All timestamped CSV files from Power BI visuals:
  - `2026_01_14_15_04_03_Average Response Times  Values are in mmss.csv`
  - `2026_01_14_15_04_13_Response Times by Priority.csv`
  - `2026_01_14_16_51_24_Average Response Times  Values are in mmss.csv`
  - `2026_01_14_16_51_33_Response Times by Priority.csv`
  - `2026_01_12_15_20_17_Monthly Accrual and Usage Summary.csv`
  - `2026_01_12_16_40_41_Monthly Accrual and Usage Summary.csv`
  - `2026_01_12_18_48_07_Monthly Accrual and Usage Summary.csv`
  - `2026_01_12_18_51_47_Engagement Initiatives by Bureau.csv`
  - `2026_01_12_20_16_04_Training Cost by Delivery Method.csv`
  - `2026_01_12_20_16_14_In-Person Training.csv`
  - `2026_01_12_Monthly Accrual and Usage Summary.csv`
  - `2025_11_Monthly Accrual and Usage Summary.csv`
  - `2025_12_11_Monthly Accrual and Usage Summary.csv`
  - `2025_12_Monthly Accrual and Usage Summary.csv`
  - `Monthly Accrual and Usage Summary.csv`
  - `Training Cost by Delivery Method.csv`
  - And all summons-related CSV exports

**Subtotal: ~35 CSV files (visual exports)**

### 3. Summons Testing/Validation → `outputs/summons_validation/`
- `___Summons_preview_table_latest.csv`
- `___Summons_preview_table.csv`
- `___Summons_preview_table.xlsx`
- `25_11_e_ticketexport.csv`
- `Assignment_Master_V2.csv`
- All department-wide summons CSV files
- All "Top 5" summons CSV files
- `Excluded_Records__17_.csv`
- `summons_simple_processing.log`

**Subtotal: ~15 files**

### 4. Benchmark/Debug Scripts → `scripts/_testing/`
- `benchmark_r13.dax`
- `benchmark_restructure.py`
- `benchmark_migration_log.txt`
- `debug_aggregation_issue.py`

**Subtotal: 4 files**

### 5. Archived Workflows → `docs/archived_workflows/`
- `2025_12_11_22_32_04_Summons_And_Backfill_Validation_Workflow.7z`
- `2025_12_11_22_32_04_Summons_And_Backfill_Validation_Workflow.zip`
- `2025_12_11_22_32_04_Summons_And_Backfill_Validation_Workflow/` (directory)

**Subtotal: 2 archive files + 1 directory**

### 6. Configuration/Metadata → `outputs/metadata/`
- `2025_12_22_Master_Automation_directory_tree.json`
- `VERIFICATION_SUMMARY_20260113_180309.json`
- `VERIFICATION_SUMMARY_20260113_181537.json`
- `VERIFICATION_SUMMARY_20260113_181553.json`
- `VERIFICATION_SUMMARY_20260113_182109.json`
- `scripts.json` (duplicate - config already exists)

**Subtotal: 6 files**

### 7. Community Engagement Data → `outputs/community_engagement/`
- `Incident Count by Date and Event Type_UPDATED.csv`
- `Incident Count by Date and Event Type.csv`
- `Incident Distribution by Event Type_UPDATED.csv`
- `Incident Distribution by Event Type.csv`
- `Use of Force Incident Matrix_UPDATED.csv`
- `Use of Force Incident Matrix.csv`

**Subtotal: 6 files**

### 8. Miscellaneous Data → `outputs/misc/`
- `data.csv`
- `filter_incidents_response_types.csv`
- `2026_01_11_ChatGPT_Combined_Movers_and_Parkers_Summary__2023_2025_.csv`
- `2026_01_11_Detective Clearance Rate Performance.csv`

**Subtotal: 4 files**

### 9. Large Export Files → `outputs/large_exports/`
- `2026_01_14_18_40_58_EXPORT_timereport.xlsx` (19 MB)
- `2026_01_14_18_40_58_timereport.xlsx` (18 MB)

**Subtotal: 2 files**

---

## 🗑️ DELETE (Temporary/Unnecessary)

### Temporary/Untitled Files
- `Untitled-1.txt`
- `Untitled-2.txt`
- `VERSION` (no extension, single digit)
- `tree_report_error.log` (error log from old operation)
- `lets update the logic to backfill respon.lua` (temp script fragment)
- `-PD_BCI_LTP.gitignore` (duplicate gitignore from laptop)

**Subtotal: 6 files**

---

## Summary Statistics

| Category | Count | Action |
|----------|-------|--------|
| Keep in Root | 7 | No action |
| Response Time Docs | 13 | Move to `docs/response_time/` |
| Visual Exports | ~35 | Move to `outputs/visual_exports/` |
| Summons Validation | ~15 | Move to `outputs/summons_validation/` |
| Benchmark/Debug | 4 | Move to `scripts/_testing/` |
| Archived Workflows | 3 | Move to `docs/archived_workflows/` |
| Configuration/Metadata | 6 | Move to `outputs/metadata/` |
| Community Engagement | 6 | Move to `outputs/community_engagement/` |
| Miscellaneous Data | 4 | Move to `outputs/misc/` |
| Large Exports | 2 | Move to `outputs/large_exports/` |
| Delete | 6 | Delete |

**Total Files:** 91  
**After Cleanup:** 7 files in root  
**Files Organized:** 84 files moved to appropriate directories  
**Files Deleted:** 6 files

---

## Execution Plan

1. Create necessary directories
2. Move files to organized locations
3. Delete temporary files
4. Update .gitignore if needed
5. Verify cleanup success

---

**Plan created:** 2026-02-04  
**Status:** Ready for execution

Run pre-flight validation checks for a report month before executing the ETL pipeline.

Validates that all required source data, configuration files, personnel data, and visual export mappings are present and healthy.

## Input

The user provides:
- `$ARGUMENTS` — the report month in YYYY-MM format (e.g. 2026-02)

If no argument is provided, default to the previous complete month.

## Process

### Step 1: Run the pre-flight validator

```bash
python scripts/Pre_Flight_Validation.py --report-month {REPORT_MONTH}
```

Run from the `06_Workspace_Management` repo root. Set `PYTHONIOENCODING=utf-8` on Windows if needed.

### Step 2: Check export file presence

For each enabled ETL script in `config/scripts.json`, verify that the expected input files exist under `05_EXPORTS/`:

| Pipeline | Expected Location |
|----------|-------------------|
| Arrests | `05_EXPORTS/_Arrest/{YYYY}/month/{YYYY}_{MM}_*.xlsx` |
| Overtime | `05_EXPORTS/_Overtime/export/month/{YYYY}/{YYYY}_{MM}_otactivity.xlsx` |
| TimeOff | `05_EXPORTS/_Time_Off/export/month/{YYYY}/{YYYY}_{MM}_timeoffactivity.xlsx` |
| Response Times | `05_EXPORTS/_CAD/timereport/monthly/{YYYY}_{MM}_timereport.xlsx` |
| Summons | `05_EXPORTS/_Summons/E_Ticket/{YYYY}/month/{YYYY}_{MM}_eticket_export.csv` |
| Community Engagement | Shared Folder workbooks (config-driven, not file-based exports) |

For each, report: file count, total size, and newest file date.

### Step 3: Validate Personnel data

Check that `09_Reference/Personnel/Assignment_Master_V2.csv` exists, has >= 50 rows, and contains required columns (BADGE_NUMBER, LAST_NAME, FIRST_NAME, WG2, RANK). Note: actual row count is ~170+; the 50-row threshold is a minimum sanity check.

### Step 4: Validate visual export mapping

Read `Standards/config/powerbi_visuals/visual_export_mapping.json` and confirm it parses without error. Report the count of mapped visuals.

### Step 5: Check _DropExports inbox

List any CSV files sitting in `PowerBI_Data/_DropExports/` that haven't been processed yet. Report count and filenames.

### Step 6: Report

Present results as a checklist:

```
Pre-Flight Validation: {REPORT_MONTH}
=====================================
[PASS] Config files valid
[PASS] Assignment_Master_V2.csv (171 rows, columns: BADGE_NUMBER LAST_NAME FIRST_NAME WG2 RANK)
[PASS] Arrest exports found (3 files, 1.2 MB)
[FAIL] Overtime exports missing for {YYYY_MM}
[WARN] 4 unprocessed CSVs in _DropExports
...
```

## Critical Rules

1. Use `scripts/path_config.py` for OneDrive path resolution
2. Do not modify any files — this is read-only validation
3. Report PASS/FAIL/WARN status for each check
4. A single FAIL should not prevent reporting other checks

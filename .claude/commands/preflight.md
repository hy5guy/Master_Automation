Run pre-flight validation checks for a report month before executing the ETL pipeline.

Validates that all required source data, configuration files, personnel data, and visual export mappings are present and healthy.

## Input

The user provides:
- `$ARGUMENTS` — the report month in YYYY-MM format (e.g. 2026-02)

If no argument is provided, default to the previous complete month.

## Process

### Step 1: Run the pre-flight validator

```bash
cd /path/to/Master_Automation
python scripts/Pre_Flight_Validation.py --report-month {REPORT_MONTH}
```

### Step 2: Check export file presence

For each enabled ETL script in `config/scripts.json`, verify that the expected input files exist under `05_EXPORTS/`:

| Pipeline | Expected Location |
|----------|-------------------|
| Arrests | `05_EXPORTS/_Arrest/{YYYY}/{month_name}/` |
| Overtime | `05_EXPORTS/_Overtime/export/month/{YYYY}/` and `05_EXPORTS/_Time_Off/export/month/{YYYY}/` |
| Response Times | `05_EXPORTS/_CAD_Incident_Downloads/` |
| Summons | `05_EXPORTS/_Summons/E_Ticket/{YYYY}/{month_name}/` |
| Community Engagement | `02_ETL_Scripts/Community_Engagement/` inputs |

For each, report: file count, total size, and newest file date.

### Step 3: Validate Personnel data

Check that `09_Reference/Personnel/Assignment_Master_V2.csv` exists, has > 50 rows, and contains required columns (Badge, Last_Name, First_Name, Assignment, WG2, Rank).

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
[PASS] Assignment_Master_V2.csv (247 rows)
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

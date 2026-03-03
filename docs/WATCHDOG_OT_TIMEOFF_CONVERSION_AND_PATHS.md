# Export File Watchdog — OTActivity / TimeOffActivity Conversion & Paths

**Source**: Export_File_Watchdog (`02_ETL_Scripts/Export_File_Watchdog`)  
**Version**: 2.1.2  
**Last Updated**: 2026-02-10

---

## Overview

The Export File Watchdog is the only component that **converts** files; it converts **OTActivity** and **TimeOffActivity** `.xls` exports to `.xlsx` only. All other export types are **moved** only (no conversion). This document summarizes the conversion behavior and destination paths for OT/TimeOff.

---

## Conversion

- **Format**: `.xls` → `.xlsx` only. **No CSV** is generated (removed to preserve data types and encoding).
- **Scope**: Only files matching OTActivity or TimeOffActivity patterns in **Downloads** (OneDrive or local).
- **Method**: `FileConverter.convert_xls_to_xlsx()` — reads with `xlrd`, writes with `openpyxl`. Original `.xls` is moved to the same folder after a successful conversion.

---

## Filename Rules (Required Prefix)

Files **must** have a date prefix; bare `TimeOffActivity.xls` or `OTActivity.xls` are **not** processed.

| Type    | Pattern (example)           | Notes                    |
|---------|-----------------------------|---------------------------|
| Monthly | `YYYY_MM_TimeOffActivity.xls` | e.g. `2026_01_TimeOffActivity.xls` |
| Monthly | `YYYY_MM_OTActivity.xls`    | e.g. `2026_01_OTActivity.xls`      |
| Yearly  | `YYYY_all_TimeOffActivity.xls` | e.g. `2025_all_TimeOffActivity.xls` |
| Yearly  | `YYYY_all_OTActivity.xls`   | e.g. `2025_all_OTActivity.xls`     |

Matching is case-insensitive for the base name (e.g. `TimeOffActivity`, `timeoffactivity`).

---

## Destination Paths

Base root: `C:\Users\<user>\OneDrive - City of Hackensack\05_EXPORTS\`

### Time Off

| Period  | Target root                          | Subfolder | Full example |
|---------|--------------------------------------|-----------|--------------|
| Monthly | `05_EXPORTS\_Time_Off\export\month`  | `YYYY`    | `…\ _Time_Off\export\month\2026\` |
| Yearly  | `05_EXPORTS\_Time_Off\export\yearly`  | `YYYY`    | `…\ _Time_Off\export\yearly\2025\` |

**Example**: `2026_01_TimeOffActivity.xls` →  
`05_EXPORTS\_Time_Off\export\month\2026\`  
Output: `2026_01_timeoffactivity.xlsx` + original `2026_01_TimeOffActivity.xls` in same folder.

### Overtime

| Period  | Target root                            | Subfolder | Full example |
|---------|----------------------------------------|-----------|--------------|
| Monthly | `05_EXPORTS\_Overtime\export\month`    | `YYYY`    | `…\ _Overtime\export\month\2026\` |
| Yearly  | `05_EXPORTS\_Overtime\export\yearly`   | `YYYY`    | `…\ _Overtime\export\yearly\2025\` |

**Example**: `2025_all_OTActivity.xls` →  
`05_EXPORTS\_Overtime\export\yearly\2025\`  
Output: `2025_all_otactivity.xlsx` + original `.xls` in same folder.

---

## Other Export Types (No Conversion)

- **Legacy** (SCRPA CAD/RMS, Backtracet Arrests, etc.): **Move only**; no conversion. Some legacy rules accept `.xls` but move/rename only (content remains .xls).
- **New rules** (Monthly CAD/RMS, E_Ticket, LawSoft Arrest, etc.): **Move only**; no conversion.
- **Benchmark** (vehicle-pursuit, use-of-force, show-of-force): **Move only** (CSV).

---

## Quick Reference

| Export        | Conversion     | Monthly path (under 05_EXPORTS)     | Yearly path (under 05_EXPORTS)      |
|---------------|----------------|-------------------------------------|-------------------------------------|
| TimeOffActivity | .xls → .xlsx | `_Time_Off\export\month\YYYY`       | `_Time_Off\export\yearly\YYYY`      |
| OTActivity    | .xls → .xlsx   | `_Overtime\export\month\YYYY`       | `_Overtime\export\yearly\YYYY`      |

---

---

## Pipeline alignment (Master_Automation)

- **Overtime/TimeOff ETL** (`overtime_timeoff_with_backfill.py` and `overtime_timeoff_13month_sworn_breakdown_v10.py`) reads from `05_EXPORTS\_Overtime` and `05_EXPORTS\_Time_Off` via **rglob**, so it picks up files in both `export/month/YYYY` and `export/yearly/YYYY`. No code path hardcodes `full_year`; yearly files are expected under **`export/yearly/YYYY`** (watchdog v2.1.2).
- **Backfill wrapper** checks for current-month files in `export/month/{year}` only; yearly files are discovered automatically by v10 when building the 13-month window.
- **Conversion**: Watchdog produces **.xlsx only** (no CSV). v10 prefers .xlsx over .csv over .xls when multiple formats exist; with only .xlsx (and optional .xls) in the folder, behavior is unchanged.

*This document is maintained in Master_Automation/docs for cross-project reference. For full watchdog documentation see Export_File_Watchdog README and CHANGELOG.*

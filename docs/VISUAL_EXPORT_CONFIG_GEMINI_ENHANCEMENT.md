# Visual Export Config – Gemini Enhancement

**Date:** 2026-02-13  
**Version:** 1.15.5

## Overview

The production `visual_export_mapping.json` was enhanced by merging metadata from Gemini's `gemini_visual_export_config logic.json`. The processor `process_powerbi_exports.py` now supports a `backfill_folder` override and correctly routes Monthly Accrual to the Overtime/TimeOff backfill path.

## Key Changes

### 1. backfill_folder Override

When a mapping has `backfill_folder`, it overrides `target_folder` **only for the Backfill copy**. Processed exports still go to `Processed_Exports/{target_folder}/`.

| Mapping             | target_folder                | backfill_folder  | Processed Path                          | Backfill Path                          |
|---------------------|-----------------------------|------------------|-----------------------------------------|----------------------------------------|
| Monthly Accrual     | social_media_and_time_report| vcs_time_report  | Processed_Exports/social_media_and_time_report/ | Backfill/YYYY_MM/vcs_time_report/ |
| Department-Wide Summons | summons                   | (none)           | Processed_Exports/summons/              | Backfill/YYYY_MM/summons/              |

**Why:** `overtime_timeoff_with_backfill.py` reads from `Backfill/YYYY_MM/vcs_time_report/` and `Backfill/YYYY_MM/Time_Off/`. Monthly Accrual must land in `vcs_time_report` to be used.

### 2. Monthly Accrual Fix

- **Before:** Mapping had `target_folder: "social_media_and_time_report"`; backfill would copy there, but Overtime/TimeOff expects `vcs_time_report`.
- **After:** `backfill_folder: "vcs_time_report"` ensures the normalized CSV is copied to the correct backfill location.

### 3. Gemini Metadata Merged

Optional fields added to mappings for documentation and future smart inference:

- `page_name` – Power BI page (e.g. Arrests, Summons, Personnel)
- `date_column` – Column used for date inference (e.g. PeriodLabel, Month_Year)
- `data_format` – Long or Wide
- `time_period` – Single month, Rolling 13 months, etc.

### 4. New Visuals Added

- **Officer Summons Activity** → summons
- **SSOCC Virtual Patrol TAS Alert and Incident Activity** → ssocc
- **Chief's Projects alias** – "Chief Michael Antista's Projects and Initiatives" matches Chief Law Enforcement Executive Duties

## Config Location

- **Mapping:** `Standards/config/powerbi_visuals/visual_export_mapping.json`
- **Processor:** `scripts/process_powerbi_exports.py`
- **Normalizer:** `scripts/normalize_visual_export_for_backfill.py`
- **Gemini source:** `gemini_visual_export_config logic.json` (reference only)

## Normalizer Formats

| Format          | Visuals                               | Behavior |
|-----------------|----------------------------------------|----------|
| monthly_accrual | Monthly Accrual and Usage Summary      | Time_Category, PeriodLabel, Value; 13-month window |
| summons         | Department-Wide Summons, Top 5, etc.   | Bureau/WG2, TYPE, TICKET_COUNT; Wide→Long if needed |
| training_cost   | Training Cost by Delivery Method       | Delivery_Type, Period, Cost; Wide→Long if needed |

## Verification

Dry-run to preview processing:

```powershell
python scripts/process_powerbi_exports.py --dry-run
```

Run for real (from `_DropExports`):

```powershell
python scripts/process_powerbi_exports.py
```

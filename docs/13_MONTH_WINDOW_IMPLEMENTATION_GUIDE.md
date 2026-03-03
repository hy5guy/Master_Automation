# 13-Month Rolling Window Enforcement - Implementation Guide

// 🕒 2026-02-12-15-00-00
// Project: Master_Automation/PowerBI_Visual_Exports
// Author: R. A. Carucci
// Purpose: Add 13-month rolling data window validation to visual export pipeline

---

## Overview

Ensures all Power BI visual exports maintain a **consistent 13-month rolling window** ending with the previous complete month, preventing incomplete current-month data from affecting dashboards.

### Operational Rule

**Current Date**: February 12, 2026

| Component | Value | Calculation |
|-----------|-------|-------------|
| **End Date** | January 2026 (01-26) | Previous month from today |
| **Start Date** | January 2025 (01-25) | 12 months before end date |
| **Window** | 13 months | Start month + 12 months |
| **Periods** | 01-25, 02-25, ..., 12-25, 01-26 | Continuous rolling window |

**Key Principle**: Never include the current month (it may be incomplete).

---

## What Changed

### 1. Enhanced Normalizer Script ✅

**File**: `scripts/normalize_visual_export_for_backfill.py`

**New Functions**:
```python
def calculate_13_month_window(as_of_date: datetime | None = None) -> tuple[str, str, list[str]]:
    """
    Calculate 13-month rolling window ending with previous complete month.
    
    Returns:
        (start_period, end_period, all_periods)
        Periods in MM-YY format
    
    Example (today = 2026-02-12):
        ('01-25', '01-26', ['01-25', '02-25', ..., '01-26'])
    """

def enforce_13_month_window(df: pd.DataFrame, period_column: str = "Period") -> pd.DataFrame:
    """
    Filter dataframe to only include records from the 13-month rolling window.
    
    Behavior:
    - Normalizes period labels (strips "Sum of " prefix)
    - Filters to valid periods only
    - Logs removed periods and missing periods
    - Validates data coverage
    """
```

**Updated Normalizers**:
- `normalize_monthly_accrual()` - Added `enforce_window` parameter; keeps **PeriodLabel** for OT backfill
- `normalize_summons()` - Added `enforce_window` parameter
- `normalize_training_cost()` - Added `enforce_window` parameter

**New CLI Parameter**:
```bash
python scripts/normalize_visual_export_for_backfill.py \
  --input export.csv \
  --output normalized.csv \
  --enforce-13-month  # ← NEW FLAG
```

---

### 2. Updated Mapping Configuration ✅

**File**: `Standards/config/powerbi_visuals/visual_export_mapping.json`

**New Field**: `enforce_13_month_window` (boolean)

**Example**:
```json
{
  "visual_name": "Department-Wide Summons",
  "standardized_filename": "department_wide_summons",
  "requires_normalization": true,
  "normalizer_format": "summons",
  "is_backfill_required": true,
  "enforce_13_month_window": true,  // ← NEW FIELD
  "target_folder": "Summons"
}
```

**Visuals with 13-Month Enforcement** (24 total): See `docs/13_MONTH_QUICK_REFERENCE.md`.

**New Target Folders Added**:
- `STACP` - School Threat Assessment & Crime Prevention
- `Community_Engagement` - Social Media Posts
- `Executive` - Chief Executive Duties
- `Support_Services` - Records & Evidence Unit
- `SSOCC` - Safe Streets Operations Control Center

---

### 3. Process Script Updates ✅

**File**: `scripts/process_powerbi_exports.py`

**Changes Applied**:
1. **`find_mapping_for_file()`** - After `visual_name`, try **`match_pattern`** (regex) on normalized stem and stem-without-date; catch `re.error` and log warning. Then try `match_aliases`.
2. **`run_normalize()`** - Added parameter **`enforce_13_month: bool = False`**. When True, append **`"--enforce-13-month"`** to subprocess cmd (before `--dry-run` if present).
3. **Call sites** - Dry-run and production: set **`enforce_window = mapping.get("enforce_13_month_window", False)`** and pass into **`run_normalize(..., enforce_13_month=enforce_window)`**. Dry-run preview command includes `--enforce-13-month` when `enforce_window` is True.

---

## How It Works

### Data Flow

```
Power BI Export
    ↓
process_powerbi_exports.py
    ├── Read mapping JSON
    ├── Check enforce_13_month_window flag
    └── Call normalizer with --enforce-13-month
         ↓
normalize_visual_export_for_backfill.py
    ├── Calculate window: 01-25 to 01-26 (13 months)
    ├── Normalize period labels
    ├── Filter df[period_column].isin(['01-25', '02-25', ..., '01-26'])
    ├── Log removed periods (outside window)
    ├── Validate coverage (missing periods warning)
    └── Write filtered CSV
         ↓
Processed_Exports/{target_folder}/
         ↓
Backfill/{YYYY_MM}/{target_folder}/ (if backfill_required)
```

### Example Logs

**With Enforcement** (today = 2026-02-12):
```
INFO: Enforcing 13-month window: 01-25 through 01-26 (13 periods)
INFO: Filtered out 45 rows from 2 periods outside 13-month window: ['11-24', '12-24']
WARNING: 13-month window incomplete: 1 missing periods: ['03-25']
INFO: 13-month window validated: 12 periods present, 1,234 rows
```

**Without Enforcement**:
```
INFO: Normalizing Summons format
INFO: Wrote 1,279 rows to 2025_12_department_wide_summons.csv
```

---

## Deployment Steps

### Step 1: Backup Current Files
```powershell
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"

# Backup mapping
Copy-Item "Standards\config\powerbi_visuals\visual_export_mapping.json" `
          "Standards\config\powerbi_visuals\visual_export_mapping_BACKUP_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"

# Backup normalizer
Copy-Item "scripts\normalize_visual_export_for_backfill.py" `
          "scripts\normalize_visual_export_for_backfill_BACKUP_$(Get-Date -Format 'yyyyMMdd_HHmmss').py"
```

### Step 2: Deploy Updated Files
```powershell
# Mapping is already deployed (visual_export_mapping_CORRECTED.json → Standards/...)

# Normalizer: use scripts/normalize_visual_export_for_backfill.py (v2 logic deployed)

# Process script: patches applied in-place (match_pattern + enforce_13_month)
```

### Step 3: Test with Sample Export
```powershell
# Test standalone normalizer
python scripts\normalize_visual_export_for_backfill.py `
  --input "test_export.csv" `
  --output "test_normalized.csv" `
  --enforce-13-month `
  --dry-run

# Expected output:
# INFO: 13-month window: 01-25 to 01-26 (13 periods)
# INFO: Loaded 100 rows from test_export.csv
# INFO: Enforcing 13-month window: 01-25 through 01-26 (13 periods)
# [DRY RUN] Periods in output: ['01-25', '02-25', ..., '01-26']
```

### Step 4: Test Full Pipeline
```powershell
# Run dry-run
python scripts\process_powerbi_exports.py --dry-run

# Verify output shows --enforce-13-month flag for applicable visuals
# [DRY RUN] Would run: python ... --enforce-13-month

# Production run
python scripts\process_powerbi_exports.py
```

---

## Validation & Troubleshooting

### Validate 13-Month Window

**Validator script** (in `scripts/`):
```powershell
# Single file
python scripts\validate_13_month_window.py --input "Processed_Exports/Summons/2025_12_department_wide_summons.csv"

# Scan folder
python scripts\validate_13_month_window.py --scan-folder Processed_Exports/Summons --verbose
```

**Manual Check**:
```powershell
python -c "
import pandas as pd
df = pd.read_csv('Processed_Exports/Summons/2025_12_department_wide_summons.csv')
periods = sorted(df['Month_Year'].unique()) if 'Month_Year' in df.columns else sorted(df.get('Period', df.get('PeriodLabel', pd.Series())).unique())
print(f'Periods: {periods}')
print(f'Count: {len(periods)} (expected: 13)')
"
```

### Common Issues

#### Issue: "13-month window incomplete: X missing periods"
**Cause**: Source data missing certain months (gap months, no activity)

**Fix**: 
- **Expected behavior** for low-activity periods
- If unexpected, check source export date range in Power BI
- Verify backfill contains missing months

#### Issue: "Cannot enforce 13-month window: column 'Period' not found"
**Cause**: Normalizer uses PeriodLabel for monthly_accrual; others use Period or Month_Year.

**Fix**: Normalizer now detects period column in order: **PeriodLabel**, **Period**, **Month_Year**. Ensure export has one of these.

#### Issue: "Filtered out 200+ rows from 6 periods"
**Cause**: Export includes data outside 13-month window (older history or current month)

**Fix**: Expected behavior – enforcement is working. Verify removed periods are outside window.

---

## Verification Checklist

### Pre-Deployment
- [x] 32 visual mappings defined
- [x] 24 visuals have `enforce_13_month_window: true` (see 13_MONTH_QUICK_REFERENCE.md)
- [x] NIBRS has `match_pattern` for dynamic date range
- [x] Normalizer has `calculate_13_month_window()` and `enforce_13_month_window()`
- [x] CLI parameter `--enforce-13-month` added
- [x] Process script: match_pattern + enforce_13_month applied
- [x] PeriodLabel kept for monthly accrual (OT backfill)

### Post-Deployment
- [ ] Mapping JSON in Standards/config/powerbi_visuals/
- [ ] Normalizer script in scripts/ (v2 logic)
- [ ] Process script patched
- [ ] Standalone test: `--enforce-13-month --dry-run` works
- [ ] Pipeline test: exports processed with correct window
- [ ] Validation: CSV periods match expected 13-month window

---

## Monthly Execution Notes

**As each month rolls forward**:
- Window automatically adjusts (e.g., March 1, 2026: window becomes 02-25 to 02-26)
- No configuration changes needed
- NIBRS visual name will change; `match_pattern` continues to match

**Example Timeline**:
| Run Date | Window Start | Window End | Periods |
|----------|-------------|-----------|---------|
| Feb 12, 2026 | 01-25 | 01-26 | 01-25 ... 01-26 (13) |
| Mar 5, 2026 | 02-25 | 02-26 | 02-25 ... 02-26 (13) |
| Apr 15, 2026 | 03-25 | 03-26 | 03-25 ... 03-26 (13) |

---

## Summary

**Status**: ✅ **Deployed**

**Key Changes**:
- 13-month rolling window calculation in normalizer
- Automatic period filtering; PeriodLabel preserved for OT backfill
- 24 visuals configured for enforcement; 8 without
- NIBRS pattern matching for dynamic visual name
- Validation script: `scripts/validate_13_month_window.py`
- Docs: `docs/13_MONTH_WINDOW_CORRECTIONS.md`, `docs/13_MONTH_QUICK_REFERENCE.md`, `docs/13_MONTH_WINDOW_IMPLEMENTATION_GUIDE.md`

*Implementation Guide - 2026-02-12*

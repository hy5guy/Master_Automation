Validate that all 13-month rolling window data is complete and correctly bounded for the given report month.

Power BI visuals display exactly 13 months of data, ending at the previous complete month. This skill checks that all data sources conform to this window.

## Input

The user provides:
- `$ARGUMENTS` — the report month in YYYY-MM format (e.g. 2026-02)

If no argument is provided, default to the previous complete month.

## Process

### Step 1: Calculate the expected window

For report month YYYY-MM, the 13-month window is:
- **End**: previous month (e.g., for 2026-03 report → window ends 2026-02)
- **Start**: 13 months before end (e.g., 2025-02)

### Step 2: Run the 13-month window validator

```bash
python scripts/validate_13_month_window.py --report-month {YYYY-MM}
```

This checks all data sources listed in `visual_export_mapping.json` that have `enforce_13_month_window: true`.

### Step 3: Check response time exports specifically

```bash
python scripts/validate_response_time_exports.py
```

Validates CSV shapes and date coverage for response time data.

### Step 4: Spot-check backfill coverage

For each backfill-required visual (listed in `visual_export_mapping.json` with `is_backfill_required: true`):
- Check that `PowerBI_Data/Backfill/{YYYY_MM}/` contains the expected files
- Verify row counts are non-zero
- Check that date ranges span the full 13-month window

### Step 5: Report

Present results as:

```
13-Month Window Validation: {YYYY-MM}
Expected window: {START} through {END} (13 months)
======================================================
[PASS] Response Time — 13 months, 4,231 rows
[PASS] Department-Wide Summons — 13 months, 156 rows
[WARN] DFR Activity — 12 months (partial future month)
[FAIL] Training Cost — only 10 months found
...
```

## Flags

- `--accept-warn` — treat WARN (partial future month) as acceptable
- Report months where data is missing by name (e.g., "Missing: 2025-04, 2025-05")

## Reference

See `docs/13_MONTH_QUICK_REFERENCE.md` and `docs/13_MONTH_WINDOW_IMPLEMENTATION_GUIDE.md` for the full specification of window enforcement rules.

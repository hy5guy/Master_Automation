Run the full monthly ETL cycle for a given report month.

This skill orchestrates the complete monthly data processing pipeline:
pre-flight validation, export processing, ETL execution, and post-run validation.

## Input

The user provides:
- `$ARGUMENTS` — the report month in YYYY-MM format (e.g. 2026-02)

If no argument is provided, default to the previous complete month.

## Process

### Step 1: Resolve the report month

```python
from datetime import datetime, timedelta
prev = (datetime.today().replace(day=1) - timedelta(days=1))
report_month = prev.strftime("%Y-%m")  # e.g. "2026-02"
```

If the user passed `$ARGUMENTS`, use that instead.

### Step 2: Pre-flight validation

Run the pre-flight validation gate to check all source data, config, and personnel files:

```bash
python scripts/Pre_Flight_Validation.py --report-month {REPORT_MONTH}
```

Review the output. If any FAIL items appear, report them to the user and ask whether to continue or abort.

### Step 3: Process Power BI visual exports (if _DropExports has files)

```bash
python scripts/process_powerbi_exports.py --report-month {YYYY_MM} --dry-run
```

Show the user the dry-run summary. If they confirm, run without `--dry-run`:

```bash
python scripts/process_powerbi_exports.py --report-month {YYYY_MM}
```

### Step 4: Run enabled ETL scripts

Run each enabled ETL script sequentially using the PowerShell orchestrator or Python wrappers.
The canonical order from `config/scripts.json` is:

1. **Arrests** — `arrest_python_processor.py --report-month {REPORT_MONTH}`
2. **Community Engagement** — `deploy_production.py`
3. **Overtime TimeOff** — `overtime_timeoff_with_backfill.py --end-month {YYYY-MM}`
4. **Response Times** — `process_cad_data_13month_rolling.py --report-month {REPORT_MONTH}`
5. **Summons** — `run_summons_etl.py --month {YYYY_MM}`

For each script:
- Show the command before running
- Capture stdout/stderr
- Report success/failure
- Continue on error (but log it)

### Step 5: Post-run validation

```bash
python scripts/validate_exports.py --year-month {YYYY_MM}
```

### Step 6: Summary

Present a scorecard table:

| ETL Script | Status | Notes |
|------------|--------|-------|
| Arrests | PASS/FAIL | ... |
| Community Engagement | PASS/FAIL | ... |
| ... | ... | ... |

## Critical Rules

1. Always run pre-flight FIRST — never skip validation
2. Use `path_config.py` for all path resolution (never hardcode OneDrive paths)
3. Report month format: scripts use either `YYYY-MM` or `YYYY_MM` — convert as needed
4. If any ETL script fails, continue with remaining scripts but flag the failure
5. Never modify source export files — ETL scripts read from exports and write to staging/output

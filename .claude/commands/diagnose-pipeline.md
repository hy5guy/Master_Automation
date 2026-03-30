Diagnose issues in any ETL pipeline by running targeted checks and reporting findings.

This is a unified diagnostic tool that replaces the need to remember and run individual diagnostic scripts scattered across the `scripts/` directory.

## Input

The user provides:
- `$ARGUMENTS` — the pipeline name and optionally a report month

Format: `{pipeline} [YYYY-MM]`

Supported pipelines:
- `summons` — Summons e-ticket ETL (classification, badge mapping, DFR split, bureau assignment)
- `arrests` — Arrest data processing (file discovery, category mapping, 13-month window)
- `overtime` — Overtime/TimeOff with backfill (VCS time report, pay types, accrual matching)
- `response-time` — CAD response time calculations (call type categories, priority filtering)
- `community` — Community Engagement (outreach records, attendee parsing)
- `exports` — Power BI visual export routing (mapping matches, normalization)
- `personnel` — Assignment Master personnel data (badge-to-unit mapping, WG2/WG3/WG4 completeness)

## Process

### For `summons`:

1. Check for source files in `05_EXPORTS/_Summons/E_Ticket/{YYYY}/{month}/`
2. Run classification verification:
   ```bash
   python scripts/diagnose_summons_blank_bureau.py
   python scripts/diagnose_summons_assignment_mapping.py
   ```
3. Check for DFR records that should be split:
   ```bash
   python scripts/dfr_reconcile.py
   ```
4. Verify summons backfill integrity:
   ```bash
   python scripts/check_summons_backfill.py
   ```
5. Compare top-5 vs department-wide totals:
   ```bash
   python scripts/diagnose_summons_top5_vs_deptwide.py
   ```

### For `arrests`:

1. Check source file discovery in `05_EXPORTS/_Arrest/{YYYY}/{month}/`
2. Verify category mapping completeness
3. Check 13-month window coverage
4. Look for unknown/unmapped arrest categories

### For `overtime`:

1. Validate export file presence:
   ```bash
   python scripts/validate_exports.py --year-month {YYYY_MM}
   ```
2. Check December pay type alignment:
   ```bash
   python scripts/debug_december_paytypes.py
   ```
3. Compare VCS time report exports:
   ```bash
   python scripts/compare_vcs_time_report_exports.py
   ```

### For `response-time`:

1. Validate response time CSV shapes:
   ```bash
   python scripts/validate_response_time_exports.py
   ```
2. Compare calculation results:
   ```bash
   python scripts/compare_response_time_results.py
   ```

### For `personnel`:

1. Read `09_Reference/Personnel/Assignment_Master_V2.csv`
2. Check for blank WG2, WG3, WG4, TEAM columns
3. Check for duplicate badge numbers
4. Verify badge format consistency (numeric, no leading zeros dropped)
5. Report unmapped personnel (badges appearing in exports but not in Assignment_Master)

### For `exports`:

1. List unmatched files in _DropExports:
   ```bash
   python scripts/process_powerbi_exports.py --verify-only
   ```
2. Check `visual_export_mapping.json` for orphaned or unused entries
3. List stray files in Processed_Exports root (should be in category subdirectories)

## Output Format

```
Pipeline Diagnostic: {PIPELINE} ({REPORT_MONTH})
=================================================
[CHECK] Source files ............... 12 files found (OK)
[CHECK] Classification mapping .... 3 UNKNOWN records (WARN)
[CHECK] DFR split integrity ....... All DFR records routed (OK)
[CHECK] 13-month coverage ......... Missing 2025-03 (FAIL)
[CHECK] Backfill consistency ...... Matches production (OK)

Recommended Actions:
1. Investigate 3 UNKNOWN classification records (badges: 0412, 0519, 0738)
2. Obtain March 2025 summons export for backfill gap
```

## Critical Rules

1. This is read-only — never modify data files during diagnosis
2. Use existing diagnostic scripts where available (don't reinvent)
3. Always report the specific records/files causing issues, not just counts
4. If a diagnostic script doesn't exist for a check, read the data directly with pandas and report findings

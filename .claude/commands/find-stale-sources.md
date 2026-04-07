Identify source files that do not appear updated through a target report month.

Read-only scan of all ETL pipeline source workbooks and export files. Reports READY, STALE, or UNKNOWN status for each source using a content-first evidence hierarchy.

## Input

The user provides:
- `$ARGUMENTS` — the report month in YYYY-MM format (e.g. 2026-03)

If no argument is provided, default to the previous complete month.

## Process

### Step 1: Run the source freshness checker

```bash
python scripts/check_source_freshness.py --report-month {REPORT_MONTH}
```

Run from the `06_Workspace_Management` repo root. Set `PYTHONIOENCODING=utf-8` on Windows if needed.

### Step 2: Review the output table

The script checks these sources:

| Pipeline | Source Location | Evidence Strategy |
|----------|----------------|-------------------|
| Arrests | `05_EXPORTS/_Arrest/{YYYY}/month/` | File existence for target month |
| Overtime | `05_EXPORTS/_Overtime/export/month/{YYYY}/` | File existence for target month |
| TimeOff | `05_EXPORTS/_Time_Off/export/month/{YYYY}/` | File existence for target month |
| Response Times | `05_EXPORTS/_CAD/timereport/monthly/` | File existence for target month |
| Summons (E-Ticket) | `05_EXPORTS/_Summons/E_Ticket/{YYYY}/month/` | File existence for target month |
| Summons (Staging) | `03_Staging/Summons/summons_powerbi_latest.xlsx` | Content: date column max |
| CE: Community Engagement | `Shared Folder/.../Community_Engagement_Monthly.xlsx` | Content > tab-name > timestamp |
| CE: Stacp | `Shared Folder/.../STACP/STACP.xlsm` | Content > tab-name > timestamp |
| CE: Patrol | `Shared Folder/.../Patrol/patrol_monthly.xlsm` | Content > tab-name > timestamp |
| Policy Training | `Shared Folder/.../Policy_Training_Monthly.xlsx` | Content > tab-name > timestamp |

All paths resolved at runtime via `scripts/path_config.py` — no hardcoded OneDrive paths.

### Step 3: Interpret results

For each source, the script reports:

- **READY** — evidence confirms target month data is present
- **STALE** — evidence suggests target month data is missing
- **UNKNOWN** — file not found, unreadable, or evidence inconclusive

Evidence types (in preference order):
1. `content` — opened workbook, checked date column max value
2. `tab-name` — found month/year pattern in worksheet tab names
3. `file-timestamp` — fallback to file modification date
4. `not-found` — file or directory does not exist

### Step 4: Report

Present the output table to the user exactly as printed by the script. Then add:

1. A count summary (e.g. "7 READY, 2 STALE, 1 UNKNOWN")
2. For any STALE source, a recommended action:
   - Export files: "Export {month} data from {system} and place in {path}"
   - Workbooks: "Update {workbook} with {month} data entries"
3. For any UNKNOWN source, a troubleshooting step:
   - "Verify file exists and OneDrive sync is current"
   - "Check if workbook format has changed"

### Step 5: Log location

Confirm the log file was written:
```
Log: logs/stale_sources_{YYYYMM}.log
```

## Critical Rules

1. This is **read-only** — never modify any source file or workbook
2. Use `scripts/path_config.py` for all OneDrive path resolution
3. A failure in one pipeline check must not prevent other checks from running
4. Report all sources, even if READY — the full picture matters for pre-flight confidence

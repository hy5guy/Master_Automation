# Handoff Prompt — Summons ETL Enhancement Phase 2

**STATUS: ✅ COMPLETE (v1.19.1, 2026-03-21)**
All three tasks implemented and verified. Task 4 (DAX measures) is manual/MCP-only.

**Copy everything below this line into a new Claude Code conversation.**

---

## Context

You are continuing work on the Hackensack PD CompStat Power BI report and ETL infrastructure. The previous conversation completed:

- **v1.19.0 committed** (`af877bd` on branch `test-dfr-audit`): Fixed statute lookup paths, _DropExports routing, PowerBI_Date typos, created `dfr_reconcile.py`
- **DFR workbook backfilled**: All 79 rows in `dfr_directed_patrol_enforcement.xlsx` now have Description, Fine Amount, Source Type, Violation Type populated via `scripts/dfr_backfill_descriptions.py --apply`
- **M code updated**: `m_code/drone/DFR_Summons.m` has ViolationData merge fallback with cascading normalization
- **97 DAX measures documented**: `docs/POWER_BI_YTD_MEASURES_AND_PAGE_INSTRUCTIONS.md` — copy-paste ready, organized by page
- **Git repo note**: OneDrive sync corruption exists (one missing blob in parent commit). Commit works but `git show --stat HEAD~1` may error. A fresh clone would fix.

## Three Tasks To Complete

### Task 1: Wire DFR backfill into the main ETL pipeline

**File:** `run_summons_etl.py` (line ~145, after `export_to_dfr_workbook()`)

After the DFR export writes records to the workbook, call `dfr_backfill_descriptions.py`'s `backfill()` function to auto-populate Description/Fine/ViolationType from ViolationData. Currently this is a standalone script; it needs to be integrated.

```python
# After export_to_dfr_workbook(dfr_records, dfr_workbook):
from dfr_backfill_descriptions import backfill
backfill(apply=True)
```

The backfill function uses cascading statute normalization (exact → strip parens → strip trailing alpha to parent code) against the ViolationData sheet in the same workbook. It also adds missing subsection codes to ViolationData for future XLOOKUP success.

### Task 2: Add fee/fine amount enrichment to the FULL raw summons export

**File:** `scripts/summons_etl_normalize.py`

Currently `_load_statute_lookups()` loads Title39 and CityOrdinances lookups but `_classify_violation()` ignores them (uses raw Case Type Code per SUMMONS_REMEDIATION_2026_02_17). The fee schedule (`municipal-violations-bureau-schedule.json`) is not loaded at all.

**What to add:**
1. Load `municipal-violations-bureau-schedule.json` in `_load_statute_lookups()` (path: `09_Reference/LegalCodes/data/Title39/municipal-violations-bureau-schedule.json`) — returns dict keyed by statute → {description, fine_amount, case_type}
2. In `normalize_personnel_data()`, after TYPE classification (line ~272), add a new enrichment step that looks up each row's STATUTE against: fee schedule → Title39 → CityOrdinances (cascading)
3. Add new columns to the DataFrame: `FINE_AMOUNT` (float), `VIOLATION_CATEGORY` (from Categorized JSONs)
4. Add these columns to the `slim_cols` list in `write_three_tier_output()` (line ~325)
5. This enrichment applies to ALL summons (not just DFR) — the full raw export gets fee/fine data for Summons_YTD revenue KPIs

**Reference files to load:**
- `09_Reference/LegalCodes/data/Title39/municipal-violations-bureau-schedule.json` — fee schedule with fine_amount
- `09_Reference/LegalCodes/data/Title39/Title39_Lookup_Dict.json` — already loaded (1,413 entries)
- `09_Reference/LegalCodes/data/Title39/Title39_Categorized.json` — categories for Title39 statutes
- `09_Reference/LegalCodes/data/CityOrdinances/CityOrdinances_Lookup_Dict.json` — already loaded (1,743 entries)
- `09_Reference/LegalCodes/data/CityOrdinances/CityOrdinances_Categorized.json` — categories for ordinances

**Important:** Do NOT change `_classify_violation()` — it correctly uses raw Case Type Code (M/P/C). The enrichment adds FINE_AMOUNT and VIOLATION_CATEGORY as new columns alongside the existing TYPE.

### Task 3: Add VIOLATION_CATEGORY column using Categorized JSONs

Part of Task 2. The Categorized JSONs have structure like:
```json
{"categories": {"Unlicensed Driver": ["39:3-40", ...], "Parking": ["88-6", ...], ...}}
```

Build a reverse lookup: statute → category. Apply cascading normalization (exact → strip parens → parent code) same as dfr_backfill_descriptions.py uses.

### Task 4 (if Power BI Desktop is still open): Add DAX measures to .pbix

The user has `Monthly_Report_Template.pbix` open in Power BI Desktop. If you can connect to it, add the ~97 DAX measures from `docs/POWER_BI_YTD_MEASURES_AND_PAGE_INSTRUCTIONS.md` directly into the model. All measures use `pReportMonth` parameter for the YTD window.

## Key File Locations

| File | Purpose |
|------|---------|
| `run_summons_etl.py` | Main ETL orchestrator — wire in backfill here |
| `scripts/summons_etl_normalize.py` | Core normalization — add enrichment here |
| `scripts/dfr_backfill_descriptions.py` | DFR workbook backfill (standalone, needs wiring) |
| `scripts/dfr_export.py` | DFR workbook writer (skips formula columns) |
| `scripts/dfr_reconcile.py` | Reconciliation report (standalone) |
| `m_code/drone/DFR_Summons.m` | Power BI M code with ViolationData fallback |
| `docs/POWER_BI_YTD_MEASURES_AND_PAGE_INSTRUCTIONS.md` | 97 DAX measures reference |
| `CLAUDE.md` | Project instructions (version 1.19.0) |
| `CHANGELOG.md` | Keep a Changelog format |

## Legal Code Reference Files

```
09_Reference/LegalCodes/data/
├── Title39/
│   ├── Title39_Lookup_Dict.json          (1,413 entries)
│   ├── Title39_Categorized.json          (categories → statute lists)
│   ├── municipal-violations-bureau-schedule.json  (1,203 entries with fine_amount)
│   └── *.lnk files (shortcuts, ignore)
└── CityOrdinances/
    ├── CityOrdinances_Lookup_Dict.json   (1,743 entries)
    ├── CityOrdinances_Categorized.json   (categories → statute lists)
    └── *.lnk files (shortcuts, ignore)
```

## Current Data Model (for DAX measures)

Tables with "Tracked Items" pattern (unpivoted month-over-month):
- `___REMU` (PeriodDate, Tracked Items, Total) — Note: uses `Application(s) - Permit(s)` not `Applications / Permits`
- `___Patrol` (PeriodDate, Tracked Items, Total)
- `___Traffic` (Date, Tracked Items, Value)
- `___CSB_Monthly` (Date, CSB_Category, Value)
- `___Detectives` (Date, Tracked Items, Value)
- `___Det_case_dispositions_clearance` (Date, Closed Case Dispositions, Value)
- `___STACP_pt_1_2` (Report_End_Date, Tracked Items, Value)
- `ESU_13Month` (MonthKey as date, TrackedItem, Total) — Note: uses `Arrest(s)` not `Arrests`

Summons tables:
- `summons_13month_trend` (ISSUE_DATE, TYPE [M/P], TICKET_COUNT, STATUTE)
- After enrichment: will also have FINE_AMOUNT, VIOLATION_CATEGORY

## Git Status

Branch: `test-dfr-audit` | Latest commit: `af877bd` (v1.19.0)
Many modified files in working tree (see `git status`). OneDrive sync corruption exists.

## Rules

1. Read `CLAUDE.md` first for project conventions
2. One change at a time, test before proceeding
3. Do NOT modify `_classify_violation()` — TYPE must stay as raw Case Type Code
4. Use `path_config.get_onedrive_root()` for all paths
5. Update `CHANGELOG.md` when done
6. Commit with versioned message on `test-dfr-audit` branch

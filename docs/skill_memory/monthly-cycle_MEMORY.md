# monthly-cycle Memory

## Current Status
- Overall status: HARDENED
- Confidence level: High
- Last updated: 2026-03-30
- Current iteration: 1
- Skill type: WRITE-CAPABLE

## Skill Contract
- Expected inputs: YYYY-MM report month (default: previous complete month)
- Expected outputs: Scorecard table with per-ETL status
- Critical rules: Pre_Flight_Validation before any ETL; continue on failure; format conversions YYYY-MM/YYYY_MM; no hardcoded paths
- Safety constraints: autonomous hardening = dry-run or fixture mode only

## Binary Scorecard
| Test | Result | Evidence | Gap | Next Action |
|------|--------|----------|-----|-------------|
| T1 | PASS | All 7 scripts verified via `--help`: Pre_Flight_Validation.py, process_powerbi_exports.py, arrest_python_processor.py, src/main_processor.py, overtime_timeoff_with_backfill.py, process_cad_data_13month_rolling.py, run_summons_etl.py, validate_exports.py. Flags match actual interfaces. | - | - |
| T2 | PASS | No hardcoded OneDrive paths in skill file. Pre_Flight_Validation.py casing correct (PascalCase). Skill references path_config.py. | - | - |
| T3 | PASS | Step 2 (preflight) runs before Step 3 (exports) and Step 4 (ETL). Dry-run documented for exports. | - | - |
| T4 | PASS | `python scripts/Pre_Flight_Validation.py --report-month 2026-02` exits 0 with Gate: GO, 0 failures, 4 warnings. ETL commands documented without execution. | - | - |
| T5 | PASS | Step 6 shows scorecard table with per-script Status and Notes columns. | - | - |
| T6 | PASS | Continue-on-error in Step 4 ("Continue on error but log it") + Critical Rule 4. Preflight-first in Critical Rule 1. Format conversions explicit in Critical Rule 3 with per-script table. | - | - |
| T7 | PASS | Fixed: (1) Community Engagement script changed from `deploy_production.py` to `src/main_processor.py`; (2) process_powerbi_exports.py format corrected from YYYY_MM to YYYY-MM; (3) PYTHONIOENCODING note added; (4) format conversion table added to Critical Rules. | - | - |
| T8 | PASS | This file updated. | - | - |

## Iteration History
### Iteration 1 (2026-03-30)
- **Findings**: 3 issues in original skill file
  1. Community Engagement referenced `deploy_production.py` (a deployment/task-scheduler tool), not the actual ETL script `src/main_processor.py` per `scripts.json`
  2. `process_powerbi_exports.py --report-month` format listed as `{YYYY_MM}` but script takes YYYY-MM (converts internally)
  3. No PYTHONIOENCODING=utf-8 note for Windows execution
- **Fixes applied**: All 3 issues corrected in skill file. Added per-script format conversion table to Critical Rules. Added explicit format notes to Summons and validate_exports steps.
- **Preflight evidence**: Gate: GO, exit 0, 0 failures, 4 warnings (expected for 2026-02 data availability)

## Evidence Log
- 2026-03-30: Pre_Flight_Validation.py --report-month 2026-02 → exit 0, Gate: GO, 4 WARN (summons source, ATS, arrests dir, CE inputs — all data-availability not config issues)
- 2026-03-30: All 8 scripts verified to exist at expected paths
- 2026-03-30: CLI flags verified via --help for all scripts with argparse
- 2026-03-30: `deploy_production.py` confirmed as Task Scheduler deployment tool (not ETL) — attempts to create scheduled tasks, not process data

## Regression Tests
- R1: Community Engagement must reference `src/main_processor.py`, NOT `deploy_production.py`
- R2: `process_powerbi_exports.py --report-month` must use YYYY-MM format (not YYYY_MM)
- R3: `run_summons_etl.py --month` and `validate_exports.py --year-month` must use YYYY_MM format (underscore)
- R4: PYTHONIOENCODING=utf-8 reminder must be present

## Remaining Gaps
- None identified

## Reusable Lessons
- `deploy_production.py` in Community_Engagement is a deployment/task-scheduler tool, not the ETL processor. The actual ETL is `src/main_processor.py` (no CLI args, just run it).
- `process_powerbi_exports.py` accepts YYYY-MM on CLI but converts to YYYY_MM internally — always pass the hyphenated format.
- Two scripts use underscore format (YYYY_MM): `run_summons_etl.py --month` and `validate_exports.py --year-month`. All others use YYYY-MM.

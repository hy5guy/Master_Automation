# Skill Hardening Master Tracker

## Global Status
- Total skills: 6
- Passed: 6
- Failed: 0
- Blocked: 0
- In progress: 0

## Skill Table
| Skill | Type | Iteration | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | Status |
|-------|------|-----------|----|----|----|----|----|----|----|----|----|----|
| validate-window | READ-ONLY | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | PASS |
| preflight | READ-ONLY | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | PASS |
| diagnose-pipeline | READ-ONLY | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | PASS |
| sync-personnel | HYBRID | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | PASS |
| process-exports | WRITE-CAPABLE | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | PASS |
| monthly-cycle | WRITE-CAPABLE | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | PASS |

## Phase 0 Findings (resolved)
- `enforce_13_month_window: true` count = **38** (prompt expected 24 — updated throughout)
- Key name is `enforce_13_month_window` (underscores), not `enforce_13month_window`
- `Pre_Flight_Validation.py` confirmed on disk with correct casing
- `check_traffic_badges_in_master.py` and `find_unknown_badges.py` both confirmed on disk
- Pre_Flight_Validation.py had `Master_Automation` base path → fixed to `06_Workspace_Management`
- Personnel check used wrong file (V3_FINAL.xlsx) → fixed to `Assignment_Master_V2.csv`

## Current Work Queue
(empty — all skills complete)

## Shared Risks
- ~~PowerBI_Data/_DropExports concurrent write collisions~~ — mitigated by dry-run-first enforcement
- ~~Pre_Flight_Validation.py casing on different OS environments~~ — verified correct casing
- ~~AssignmentMasterV2.csv: canonical (09_Reference) vs local copy (06_WM) divergence~~ — skills reference canonical path
- diagnose-pipeline script inventory hardcoded — documented as GAP-1, T7 regression RT-DP1
- YYYY-MM vs YYYYMM vs YYYY_MM format handling — resolved with per-script format table in monthly-cycle

## Shared Reusable Lessons
1. Always set PYTHONIOENCODING=utf-8 on Windows before Python scripts
2. `--report-month` uses YYYY-MM (hyphen) for most scripts; `run_summons_etl.py --month` and `validate_exports.py --year-month` use YYYY_MM (underscore)
3. Always verify actual CSV column names and script `--help` before documenting in skill files
4. Repo was renamed from Master_Automation → 06_Workspace_Management; any lingering references must be updated
5. `deploy_production.py` in Community_Engagement is a Task Scheduler tool, not the ETL processor
6. Visual export enforced count is dynamic (currently 38) — don't hardcode exact numbers
7. Badge numbers in Assignment_Master are strings; NaN entries are expected civilian records
8. Source-data typos (RECODS, ADMINSTIVE) exist in canonical CSV — don't auto-correct

---

## Fixup Pass v3 — 2026-03-30

### Items Resolved
| Item | Description | Status |
|------|-------------|--------|
| 1 | Preflight example: 247→171 rows + column names | Resolved |
| 2A | Export path table: Arrests, Summons, OT, TimeOff, CE corrected | Resolved |
| 2B | OT + TimeOff checks added to Pre_Flight_Validation.py | Resolved — test: exit 0, GO, 0 FAIL |
| 3 | Sync mode safety warning added to sync-personnel.md | Resolved |
| 4 | parse_cad_assignment.py built and tested | Resolved — 12 new, 5 reassign, 1 departure |

### Script Changes
- `Pre_Flight_Validation.py`: fixed eticket path (`month/` not `{MM}_{monthname}`), fixed arrest path (`{YYYY}/month/`), added OT/TimeOff checks, replaced CE `inputs/` with config.json check
- `09_Reference/Personnel/scripts/parse_cad_assignment.py`: new CAD-vs-Master comparison tool
- `sync-personnel.md`: added sync safety warning + `find-unmapped cad` mode
- `preflight.md`: fixed example, corrected all export paths

# preflight Memory

## Current Status
- Overall status: PASS (all T1-T8 = 1)
- Confidence level: High — real execution evidence captured
- Last updated: 2026-03-30
- Current iteration: 3
- Skill type: READ-ONLY

## Skill Contract
- Expected inputs: YYYY-MM report month (default: previous complete month)
- Expected outputs: PASS/FAIL/WARN per check (personnel, config, exports, mapping, _DropExports, arrests, community)
- Critical rules: all checks must run even if one fails; Pre_Flight_Validation.py casing verified on disk
- Safety constraints: read-only — no file modifications

## Binary Scorecard
| Test | Result | Evidence | Gap | Next Action |
|------|--------|----------|-----|-------------|
| T1 | 1 | Skill documents `--report-month YYYY-MM`, script accepts exactly that. Checks match script implementation after fixes. | None | |
| T2 | 1 | Script uses `path_config.get_onedrive_root()`. Skill file `cd /path/to/Master_Automation` removed. Pre_Flight_Validation.py casing correct on disk. | None | |
| T3 | 1 | Script only reads files (path.exists, open for read, csv.reader, json.load). No writes. | None | |
| T4 | 1 | `python scripts/Pre_Flight_Validation.py --report-month 2026-02` → exit 0, Gate: GO, 0 fails, 4 warns, 5 passes. | None | |
| T5 | 1 | Output: Personnel 171 rows, Config 11856B, RT source 1318029B, Visual mapping total=51 enforced=38. Specific paths and sizes reported. | None | |
| T6 | 1 | Row threshold >=50 implemented (GAP-5 addressed). Column validation added (BADGE_NUMBER, LAST_NAME, FIRST_NAME, WG2, RANK). All checks run even on failure (confirmed: 9 checks all reported). | None | |
| T7 | 1 | Regression: Master_Automation→06_Workspace_Management path fix, column name fix, enforced count no longer hardcoded. | None | |
| T8 | 1 | This file updated with evidence. | None | |
| T9 | 1 | All T1-T8 = 1. | None | |

## Iteration History
### Iteration 1 (2026-03-30) — Initial discovery
- Pre_Flight_Validation.py had `Master_Automation` base path (line 158) → 3 false FAILs
- Personnel check used wrong file (V3_FINAL.xlsx instead of V2.csv)
- Visual mapping enforced count hardcoded to 25 (actual: 38)
- Missing Arrest and Community Engagement checks
- No column validation or row threshold on personnel

### Iteration 2 (2026-03-30) — Fixes applied
- Fixed: `Master_Automation` → `06_Workspace_Management`
- Fixed: personnel → `09_Reference/Personnel/Assignment_Master_V2.csv` with column + row validation
- Fixed: visual mapping count no longer hardcoded (reports actual)
- Added: Arrest export and Community Engagement input checks
- Fixed: skill file removed `cd /path/to/Master_Automation`, corrected column names, fixed export paths
- Re-run: exit 0, Gate: GO, 0 fails, 4 warns (data availability, not bugs)

## Evidence Log
### E-1: Pre-run (broken, iteration 1)
- Command: `python scripts/Pre_Flight_Validation.py --report-month 2026-02`
- Exit: 1 (NO-GO)
- Cause: `Master_Automation` path bug → Personnel FAIL, Config FAIL, Visual Mapping FAIL

### E-2: Post-fix (iteration 2)
- Command: `python scripts/Pre_Flight_Validation.py --report-month 2026-02`
- Exit: 0 (GO)
- Output: 5 PASS, 4 WARN, 0 FAIL
- Personnel: 171 rows, all required columns present
- Config: 11856B, parseable
- Visual mapping: total=51, 13-month enforced=38
- Response Time: 1318029B found
- WARNs: E-Ticket, ATS, Arrests, CE inputs — data not present for Feb 2026 (expected)

## Regression Tests
1. **Path base regression**: Pre_Flight_Validation.py must use `06_Workspace_Management` not `Master_Automation`. Check: grep for `Master_Automation` in script.
2. **Personnel file regression**: Must check `Assignment_Master_V2.csv` at `09_Reference/Personnel/`, not `Assignment_Master_V3_FINAL.xlsx`. Check: grep for `V3_FINAL` in script.
3. **Column name regression**: Required columns are BADGE_NUMBER, LAST_NAME, FIRST_NAME, WG2, RANK (CSV headers, not camelCase).

## Remaining Gaps
- GAP-5 (RESOLVED): Row threshold >=50 implemented. Still a relatively low bar vs actual ~171 rows, but serves as corruption check.
- Overtime export check not yet in script (only Summons, Response Time, Arrests, Community covered)

## Iteration History (continued)
### Iteration 3 (2026-03-30) — Fixup pass
- Fixed: stale example "247 rows" → "171 rows, columns: BADGE_NUMBER LAST_NAME FIRST_NAME WG2 RANK"
- Fixed: export path table — Arrests `_Arrest/{YYYY}/month/`, Summons `E_Ticket/{YYYY}/month/`, added OT/TimeOff, CE config-driven
- Added: Overtime + TimeOff export checks to Pre_Flight_Validation.py
- Fixed: Summons eticket path from `{MM}_{month_name}` to `month/` subfolder
- Fixed: CE check from nonexistent `inputs/` to config.json existence
- Test: `python scripts/Pre_Flight_Validation.py --report-month 2026-02` → exit 0, Gate: GO, 0 FAIL, 1 WARN (ATS only)
- All 11 checks pass: Personnel, Config, E-Ticket (2854 rows), RT (1.3MB), Drop folder, Visual mapping (51/38), Arrests (2 files), Overtime (120KB), TimeOff (193KB), CE config (2.4KB)

## Reusable Lessons
1. Always verify actual CSV column names before hardcoding required-column sets
2. Repo was renamed from Master_Automation to 06_Workspace_Management — any script referencing old name needs update
3. Visual export enforced count changes as new visuals are added — don't hardcode exact number
4. OT/TimeOff files are `.xls` not `.xlsx` — use glob `*otactivity.*` to catch both
5. Summons E-Ticket folder structure is `{YYYY}/month/` not `{YYYY}/{MM}_{month_name}/`
6. CE ETL reads from Shared Folder workbooks via config.json, not a local `inputs/` directory

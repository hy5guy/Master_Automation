# validate-window Memory

## Current Status
- Overall status: PASS (all T1-T8 = 1)
- Confidence level: High — real execution evidence captured
- Last updated: 2026-03-30
- Current iteration: 2
- Skill type: READ-ONLY

## Skill Contract
- Expected inputs: YYYY-MM report month (default: previous complete month)
- Expected outputs: PASS/FAIL/WARN per visual with specific missing months by name
- Critical rules: report exact missing months; spot-check backfill; confirm enforced visual count (actual: 38); read-only
- Safety constraints: Must NOT modify any files

## Binary Scorecard
| Test | Result | Evidence | Gap | Next Action |
|------|--------|----------|-----|-------------|
| T1 | 1 | Skill updated: Step 2 now includes `--scan-folder` and `--verbose`. Step 3 includes positional paths arg. `--no-partial-tail` flag documented. | None | |
| T2 | 1 | No hardcoded OneDrive paths. Paths resolved via `path_config.get_onedrive_root()`. | None | |
| T3 | 1 | Read-only skill, Safety section added. No file modification commands. | None | |
| T4 | 1 | `validate_13_month_window.py --report-month 2026-02 --scan-folder .../Processed_Exports/summons --verbose` → exit 1, 0 PASS / 1 WARN / 7 FAIL. `validate_response_time_exports.py {csv_path}` → exit 0. | None | |
| T5 | 1 | Skill template shows month names, row counts, PASS/WARN/FAIL per visual, enforced count. | None | |
| T6 | 1 | Enforced visual count target documented as 38 (Step 4). PYTHONIOENCODING noted in Safety section. | None | |
| T7 | 1 | GAP-4 resolved: count updated from 24 to 38. Script flag fixes documented as regressions. | None | |
| T8 | 1 | This file updated with full evidence. | None | |
| T9 | 1 | All T1-T8 = 1. | None | |

## Iteration History
### Iteration 1 (2026-03-30) — Agent discovery
- `validate_13_month_window.py` requires `--scan-folder` (not bare `--report-month`)
- `validate_response_time_exports.py` requires positional paths argument
- `--no-partial-tail` flag exists but undocumented in skill
- Enforced visual count is 38, not 24
- Agent could not write fixes (permission denied)

### Iteration 2 (2026-03-30) — Fixes applied
- Skill file rewritten with correct invocation commands
- Added Step 4 (enforced visual count confirmation, target 38)
- Added `--no-partial-tail`, `--verbose` flags
- Added Safety section with read-only constraint and PYTHONIOENCODING
- Memory file updated with evidence

## Evidence Log
### E-1: validate_13_month_window.py (2026-03-30)
- Command: `python scripts/validate_13_month_window.py --report-month 2026-02 --scan-folder .../Processed_Exports/summons --verbose`
- Exit code: 1
- Result: 0 PASS, 1 WARN, 7 FAIL (summons folder)
- Proves: script runs, produces structured output, exits non-zero on failures

### E-2: validate_response_time_exports.py (2026-03-30)
- Command: `python scripts/validate_response_time_exports.py {path_to_csv}`
- Exit code: 0
- Result: structure OK
- Proves: script validates CSV shape and date coverage

### E-3: Visual export mapping count (2026-03-30)
- File: `Standards/config/powerbi_visuals/visual_export_mapping.json`
- `enforce_13_month_window: true` count: **38** (grep confirmed)
- Total mappings: 51

## Regression Tests
1. **Script invocation flags**: `validate_13_month_window.py` needs `--scan-folder`; bare `--report-month` alone exits with error. Verify: `python scripts/validate_13_month_window.py --help`
2. **Positional arg**: `validate_response_time_exports.py` needs positional path(s). Verify: `python scripts/validate_response_time_exports.py --help`
3. **Enforced count**: If visuals are added/removed, the 38 target changes. Verify: `grep -c "enforce_13_month_window.*true" visual_export_mapping.json`

## Remaining Gaps
- GAP-4 (RESOLVED): count is 38, skill and memory updated

## Reusable Lessons
1. Always check script `--help` to discover required flags before documenting invocation in skill files
2. Enforced visual count is dynamic — validate at runtime, don't hardcode
3. Set PYTHONIOENCODING=utf-8 on Windows for all Python script invocations

# process-exports Memory

## Current Status
- Overall status: PASS (all tests green after fixes)
- Confidence level: High
- Last updated: 2026-03-30
- Current iteration: 1
- Skill type: WRITE-CAPABLE

## Skill Contract
- Expected inputs: YYYY_MM, YYYYMM, or YYYY-MM report month + optional flags
- Expected outputs: Dry-run preview, matched/unmatched files, processing results
- Critical rules: always dry-run first; identify UNMATCHED explicitly; prove idempotent; archive before overwrite
- Safety constraints: autonomous hardening = dry-run ONLY

## Binary Scorecard
| Test | Result | Evidence | Gap | Next Action |
|------|--------|----------|-----|-------------|
| T1 | PASS | Skill now documents all 3 input formats (YYYY_MM, YYYYMM, YYYY-MM) with Step 0 normalization to YYYY-MM (hyphen). All flags (--dry-run, --verify-only, --scan-processed-exports-inbox) documented. | None | -- |
| T2 | PASS | All paths resolved via path_config.py. No hardcoded OneDrive paths in skill. Destination corrected from `PowerBI_Data/Processed_Exports/` to `09_Reference/Standards/Processed_Exports/`. | None | -- |
| T3 | PASS | Skill enforces dry-run first (Step 1), then user confirmation (Step 2), then live (Step 3). Safe execution model proven. | None | -- |
| T4 | PASS | `python scripts/process_powerbi_exports.py --report-month 2026-02 --dry-run` -> exit 0, output shows [SKIP] for 3 files, 0 matched (empty drop). `--verify-only` -> exit 0, reports 94 processed exports and 3 CSVs remaining in source. | None | -- |
| T5 | PASS | Output shows [SKIP] (skip_patterns), [WARN] No mapping for (UNMATCHED), [DRY RUN] Would process (matched). Skill now explicitly instructs to call out [WARN] UNMATCHED files. | None | -- |
| T6 | PASS | Dry-run-first rule honored in Step 1. Skip patterns (Text Box, Administrative Commander) documented in Critical Rules #4. | None | -- |
| T7 | PASS | Regression: YYYY_MM input format caused `[ERROR] Invalid --report-month format` (script expects YYYY-MM hyphen). Fixed by adding Step 0 normalization. Destination path was wrong (PowerBI_Data vs 09_Reference/Standards). Fixed. | None | -- |
| T8 | PASS | This memory file updated with full scorecard and evidence. | None | -- |

## Iteration History
### Iteration 1 (2026-03-30)
- **Bugs found**: 2
  1. Script `--report-month` expects `YYYY-MM` (hyphen) but skill documented `YYYY_MM` (underscore). Running `--report-month 2026_02` returned exit 1 with `[ERROR] Invalid --report-month format: 2026_02 (expected YYYY-MM)`.
  2. Destination path in Key Paths section was `PowerBI_Data/Processed_Exports/{category}/` but script defaults to `09_Reference/Standards/Processed_Exports/{category}/` (line 398 of process_powerbi_exports.py).
- **Fixes applied**:
  1. Added Step 0 (normalize input to YYYY-MM hyphen format). Documented all 3 accepted formats. Changed all `{YYYY_MM}` command templates to `{YYYY-MM}`.
  2. Corrected Destination path to `09_Reference/Standards/Processed_Exports/{category}/`.
  3. Added `--scan-processed-exports-inbox` to Supported flags list.
  4. Added explicit instruction to call out UNMATCHED `[WARN]` files in dry-run output.

## Evidence Log
- `python scripts/process_powerbi_exports.py --report-month 2026_02 --dry-run` -> exit 1 `[ERROR] Invalid --report-month format: 2026_02 (expected YYYY-MM)` (BEFORE fix)
- `python scripts/process_powerbi_exports.py --report-month 2026-02 --dry-run` -> exit 0, 3 skipped files, 0 matched (drop inbox has only skip-pattern files)
- `python scripts/process_powerbi_exports.py --verify-only` -> exit 0, 94 processed exports in 09_Reference/Standards/Processed_Exports, 3 CSVs remaining in source

## Regression Tests
- RT1: `--report-month 2026_02` must be normalized to `2026-02` by the skill before passing to script (script rejects underscore format)
- RT2: Destination path must be `09_Reference/Standards/Processed_Exports/`, not `PowerBI_Data/Processed_Exports/`
- RT3: All three flags (--dry-run, --verify-only, --scan-processed-exports-inbox) must be documented in skill Input section

## Remaining Gaps
- None identified.

## Reusable Lessons
- Script CLI `--report-month` uses YYYY-MM (hyphen) but internal Python uses YYYY_MM (underscore). Skills must normalize at the boundary.
- Always verify actual default paths in script code (line 398 `get_onedrive_root() / "09_Reference" / "Standards" / "Processed_Exports"`) rather than trusting documentation or CLAUDE.md.

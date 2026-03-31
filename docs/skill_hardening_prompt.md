# Claude Code — Skill Hardening Mission
# Hackensack PD ETL Workspace | Drop-in Ready | v1.0 2026-03-30

==================================================
BEFORE YOU BEGIN — READ THESE FILES FIRST
==================================================

Read the following files in full before touching any skill:

1. CLAUDE.md                          — workspace rules, path resolution, protected resources
                                        NOTE: If CLAUDE.md is partial or missing sections, continue
                                        but document what was missing in the master tracker.
2. README.md                          — project map, script locations, key paths
3. SUMMARY.md                         — enabled scripts, architecture notes, known issues
4. config/scripts.json                — canonical ETL config, do NOT modify
5. scripts/path_config.py             — path resolution: always use get_onedrive_root(), never hardcode
6. docs/ETL_SKILL_MEMORY.md           — existing skill memory; APPEND to it, do NOT overwrite or replace
7. Standards/config/powerbi_visuals/visual_export_mapping.json
                                      — confirms exactly how many visuals enforce 13-month window
                                        (expected: 24 visuals with enforce_13month_window: true)

PATH RESOLUTION RULES (from CLAUDE.md — apply everywhere):
- All paths resolve via path_config.get_onedrive_root()
- Profile folder is carucci_r — do NOT change to RobertCarucci
- Laptop uses a OneDrive junction; path_config.py handles this at runtime
- PowerBIData is the correct folder name — do NOT use PowerBIDate (that was a typo)
- If a path appears broken, check junction status before editing any file

==================================================
MISSION
==================================================

Harden these 6 Claude command skills so each achieves Skill Success = 1.
Continue without prompting the user until all skills pass or hit a documented hard blocker.

Skills to harden:
1. .claude/commands/validate-window.md
2. .claude/commands/sync-personnel.md
3. .claude/commands/process-exports.md
4. .claude/commands/preflight.md
5. .claude/commands/monthly-cycle.md
6. .claude/commands/diagnose-pipeline.md

NOTE: .claude/commands/fix-excel.md is a PRE-EXISTING skill. Do NOT touch it.
It is not part of this hardening session.

==================================================
EXECUTION MODEL
==================================================

Use Task() to spawn parallel subagents.
Never let two subagents modify the same file at the same time.

Wave A — spawn in parallel (read-only / inspection skills):
  - validate-window
  - preflight
  - diagnose-pipeline
  - sync-personnel (check, compare, find-unmapped modes ONLY)

Wave B — execute one at a time, isolated worktree per skill (write-capable):
  - process-exports
  - monthly-cycle
  - sync-personnel (sync mode ONLY)

For Wave B: run `git worktree add` per skill if supported.
If worktrees are not available, serialize Wave B and document why in the master tracker.

Do NOT run live write tests against PowerBI_Data/_DropExports from multiple agents simultaneously.

==================================================
SKILL CONTRACTS
(exact rules — use these, do not re-discover from scratch)
==================================================

--- validate-window ---
  Input:    YYYY-MM report month (default: previous complete month)
  Backing scripts:
    scripts/validate_13month_window.py --report-month YYYY-MM
    scripts/validate_response_time_exports.py
    Standards/config/powerbi_visuals/visual_export_mapping.json
      (enforce_13month_window: true entries — confirm count, expected 24)
  Window math:
    End   = last day of month BEFORE report month
    Start = 13 months before End
    Example: report 2026-03 → window 2025-02 through 2026-02
  Must: report exact missing months by name (e.g., "Missing 2025-04, 2025-05") — not just counts
  Must: spot-check backfill files in PowerBI_Data/Backfill/YYYYMM/
  Must: confirm T4 evidence shows validator ran against all enforced visuals (target: 24)
  Must NOT: modify any files — strictly read-only
  Optional flag: --accept-warn treats partial future-month tail as acceptable

--- preflight ---
  Input:    YYYY-MM report month (default: previous complete month)
  Backing script: scripts/Pre_Flight_Validation.py --report-month YYYY-MM
    CASING: uppercase P, F, V — Pre_Flight_Validation.py — verify exact filename on disk
  Checks required (all must run — a FAIL on one does NOT stop the others):
    - config/scripts.json parseable without error
    - AssignmentMasterV2.csv:
        exists at 09_Reference/Personnel/AssignmentMasterV2.csv
        has columns: Badge, LastName, FirstName, Assignment, WG2, Rank
        row threshold: ≥50 rows (note: actual count ~247; if script hardcodes 50, flag as gap)
    - Export files present per pipeline:
        Arrests         → 05_EXPORTS/Arrest/YYYY_monthname/
        Overtime        → 05_EXPORTS/Overtime/export_month_YYYY/
                          and 05_EXPORTS/TimeOff/export_month_YYYY/
        Response Times  → 05_EXPORTS/CAD_IncidentDownloads/
        Summons         → 05_EXPORTS/SummonsETicket/YYYY_monthname/
        Community       → 02_ETL_Scripts/CommunityEngagement/inputs/
    - Standards/config/powerbi_visuals/visual_export_mapping.json parseable
    - PowerBI_Data/_DropExports: list unprocessed CSV files with count and filenames
  Output format: PASS/FAIL/WARN per check — one line each
  Must NOT: modify any files — strictly read-only

--- diagnose-pipeline ---
  Input:    pipeline name (required) + optional YYYY-MM
  Pipelines: summons | arrests | overtime | response-time | community | exports | personnel
  Must: use existing diagnostic scripts FIRST — do not reinvent if scripts exist
  Script inventory per pipeline:
    summons:
      scripts/diagnose_summons_blank_bureau.py
      scripts/diagnose_summons_assignment_mapping.py
      scripts/dfr_reconcile.py
      scripts/check_summons_backfill.py
      scripts/diagnose_summons_top5_vs_deptwide.py
      scripts/diagnose_summons_missing_months.py        ← confirmed in repo
    arrests:
      scripts/validate_exports.py --year-month YYYYMM
      (check source file discovery and category mapping)
    overtime:
      scripts/validate_exports.py --year-month YYYYMM
      scripts/debug_december_pay_types.py
      scripts/compare_vcs_time_report_exports.py
    response-time:
      scripts/validate_response_time_exports.py
      scripts/compare_response_time_results.py
    community:
      (check source files in 02_ETL_Scripts/CommunityEngagement/inputs/)
    exports:
      scripts/process_powerbi_exports.py --verify-only
      (check visual_export_mapping.json for orphaned entries)
    personnel:
      09_Reference/Personnel/AssignmentMasterV2.csv — read directly
      scripts/diagnose_summons_blank_bureau.py
      scripts/check_traffic_badges_in_master.py        ← confirmed in repo
      scripts/find_unknown_badges.py                   ← confirmed in repo
  Must: report specific records/files/badge numbers causing issues — not just counts
  Must NOT: modify data files — strictly read-only
  Known gap: script list is hardcoded in skill file, not driven by config/scripts.json.
    Document this in diagnose-pipeline memory file as a Remaining Gap.
    T7 regression must flag: if diagnostic scripts are renamed, skill breaks.

--- sync-personnel ---
  Input:    action keyword (check | sync | compare BADGE | find-unmapped PIPELINE)
  Source of truth: 09_Reference/Personnel/AssignmentMasterV2.csv (canonical)
  Local copy: 06_Workspace_Management/ — do NOT treat as canonical
  Badge numbers MUST be treated as strings — preserve leading zeros, never cast to int
  Sync script:
    09_Reference/Personnel/scripts/sync_assignment_master.py
    or 09_Reference/Personnel/scripts/run_sync.bat (uses BASEDIR, works on desktop + laptop)
  For find-unmapped summons: also run scripts/diagnose_summons_blank_bureau.py
  For compare {badge}: search 05_EXPORTS/Summons, 05_EXPORTS/Overtime, 05_EXPORTS/Arrest
  Valid WG2 values include: Patrol Division, Detective Division, Administrative Division, Traffic Bureau
  Must NOT: modify AssignmentMasterV2.csv directly — only sync script may do so
  Sync mode is Wave B (write-capable) — must be run isolated from other write agents

--- process-exports ---
  Input format: YYYY_MM (underscore — e.g., 2026_02) or YYYYMM (converted internally)
    T1 Interface Contract must verify both YYYY_MM and YYYYMM inputs are handled without error
  Backing scripts:
    scripts/process_powerbi_exports.py
    scripts/processed_exports_routing.py (canonical folder names, archive management)
  Key paths (all resolved via path_config.py):
    Source:       PowerBI_Data/_DropExports/
    Mapping:      Standards/config/powerbi_visuals/visual_export_mapping.json
    Destination:  PowerBI_Data/ProcessedExports/CATEGORY/
    Backfill:     PowerBI_Data/Backfill/YYYYMM/CATEGORY/
    Archive:      archive/YYYYMM/ (auto-created before overwrite)
  Must: always run --dry-run FIRST and show matched/UNMATCHED files before any live execution
  Must: identify UNMATCHED files explicitly — do not silently skip
  Must: prove idempotent behavior — identical files skipped, archive before overwrite
  Must: autonomous hardening tests dry-run ONLY unless a safe isolated fixture exists
  Skip patterns (silent): "Text Box", "Administrative Commander"
  Flags: --dry-run | --verify-only | --scan-processed-exports-inbox | --report-month

--- monthly-cycle ---
  Input:    YYYY-MM report month (default: previous complete month)
  Steps — canonical order (must execute in this sequence):
    Step 1: python scripts/Pre_Flight_Validation.py --report-month YYYY-MM
            → MUST run first. Never skip. On FAIL, log and continue (do not abort).
    Step 2: python scripts/process_powerbi_exports.py --report-month YYYYMM --dry-run
            → Show output. Then run live only if _DropExports has files.
    Step 3: ETL scripts in order (from config/scripts.json):
              arrest_python_processor.py --report-month YYYY-MM
              deploy_production.py           (Community Engagement)
              overtime_timeoff_with_backfill.py --end-month YYYY-MM
              process_cad_data_13month_rolling.py --report-month YYYY-MM
              run_summons_etl.py --month YYYYMM
    Step 4: python scripts/validate_exports.py --year-month YYYYMM
  Format conversions: YYYY-MM ↔ YYYYMM as required per script
  Must: continue on ETL script failure — log the failure, do NOT abort the cycle
  Must: enforce Pre_Flight_Validation before any ETL step
  Must: produce a scorecard table: | ETL Script | Status | Notes |
  Must NOT: hardcode OneDrive paths — use path_config.py
  Must NOT: run live ETL during autonomous hardening — use dry-run or fixture mode

==================================================
BINARY TESTS (apply to all 6 skills)
==================================================

T1  Interface Contract     — documented flags/inputs/modes match actual implementation.
                             For process-exports: both YYYY_MM and YYYYMM inputs handled.
T2  Path Safety            — all paths resolved via path_config.py; no hardcoded OneDrive paths;
                             Pre_Flight_Validation.py casing verified on disk.
T3  Mode Safety            — read-only skills (validate-window, preflight, diagnose-pipeline,
                             sync-personnel check/compare/find-unmapped) make no file changes.
                             Write-capable skills prove dry-run before any live execution.
T4  Real Execution Evidence — backing script ran with real inputs or safe fixtures.
                             Evidence = command + exit code + stdout/stderr snippet.
                             validate-window: must confirm count of enforced visuals (target 24).
T5  Output Quality         — output contains specific files, record counts, badge numbers, month names.
                             No vague summaries ("some files found", "data looks okay").
T6  Rule Compliance        — skill honors its critical rules per Skill Contracts above.
                             preflight: row threshold check flagged if hardcoded magic number.
                             diagnose-pipeline: hardcoded script list documented as Remaining Gap.
T7  Regression Coverage    — regression check created for each issue found and fixed.
                             diagnose-pipeline T7 must include: script-rename fragility documented.
T8  Memory Updated         — per-skill memory file updated with exact evidence.
                             docs/ETL_SKILL_MEMORY.md appended (not overwritten).
T9  Skill Success          — T1 through T8 all = 1.

PASS = 1.  FAIL = 0.  No partial scores.  No invented evidence.  No assumptions as proof.

==================================================
KNOWN GAPS
(address or document during hardening — do not skip)
==================================================

GAP-1: diagnose-pipeline hardcodes diagnostic script names.
  → If config/scripts.json does not map diagnostic scripts per pipeline,
    the skill breaks on renames. Document in diagnose-pipeline memory as Remaining Gap.
    T7 regression must protect against this.

GAP-2: Pre_Flight_Validation.py — verify exact file casing on disk before first run.
  → T2 fails if the skill references wrong casing. Correct casing: Pre_Flight_Validation.py

GAP-3: Personnel diagnostic scripts — confirm these exist on disk before wiring into
  diagnose-pipeline (personnel mode):
    scripts/check_traffic_badges_in_master.py
    scripts/find_unknown_badges.py
  → If missing, document as blocked with exact evidence.

GAP-4: validate-window — confirm visual_export_mapping.json contains exactly 24 visuals
  with enforce_13month_window: true. If count differs, update T4 evidence requirement.

GAP-5: preflight AssignmentMasterV2.csv row threshold.
  → Actual expected count ~247. If Pre_Flight_Validation.py hardcodes ≥50,
    flag in T6 as a magic number. Document as Remaining Gap.

==================================================
PERSISTENT OUTPUTS
==================================================

Create these files if they don't exist. Reuse and update if they do.

docs/SKILL_HARDENING_MASTER.md           — global tracker across all 6 skills
docs/skill_memory/validate-window_MEMORY.md
docs/skill_memory/sync-personnel_MEMORY.md
docs/skill_memory/process-exports_MEMORY.md
docs/skill_memory/preflight_MEMORY.md
docs/skill_memory/monthly-cycle_MEMORY.md
docs/skill_memory/diagnose-pipeline_MEMORY.md
docs/skill_memory/REGRESSION_TESTS.md   — cross-skill regression inventory

docs/ETL_SKILL_MEMORY.md — EXISTING FILE. APPEND only. Never overwrite.

--- Master Tracker Format ---

# Skill Hardening Master Tracker

## Global Status
- Total skills: 6
- Passed:
- Failed:
- Blocked:
- In progress:

## Skill Table
| Skill | Type | Iteration | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | Status |

## Current Work Queue
(highest-priority failing tests across all skills)

## Shared Risks
- PowerBI_Data/_DropExports concurrent write collisions
- Pre_Flight_Validation.py casing on different OS environments
- AssignmentMasterV2.csv: canonical (09_Reference) vs local copy (06_WM) divergence
- diagnose-pipeline script inventory hardcoded — rename risk
- YYYY-MM vs YYYYMM vs YYYY_MM format handling across skills

## Shared Reusable Lessons
(only proven lessons, not guesses — add as hardening progresses)

--- Skill Memory Format ---

# {Skill Name} Memory

## Current Status
- Overall status:
- Confidence level:
- Last updated:
- Current iteration:
- Skill type: READ-ONLY / WRITE-CAPABLE / HYBRID

## Skill Contract
- Expected inputs
- Expected outputs
- Critical rules
- Safety constraints

## Binary Scorecard
For each test T1–T9:
  - Result: 1 / 0
  - Evidence: (exact command, exit code, output snippet)
  - Gap: (what is still unproven)
  - Next action: (if result = 0)

## Iteration History
For each iteration:
  - Goal
  - Files modified
  - Commands run
  - Exit codes
  - What was proven
  - What failed
  - Corrective action
  - Regression added

## Evidence Log
For each evidence item:
  - Exact command
  - Exact exit code
  - Exact file path(s)
  - Stdout/stderr snippet
  - What it proves
  - What it does NOT prove

## Regression Tests
  - Name
  - What it protects against
  - How to run it

## Remaining Gaps
(only items still unsupported by evidence)

## Reusable Lessons
(short and practical)

==================================================
FAILURE ANALYSIS FORMAT
(output this block whenever any test = 0)
==================================================

FAILURE ANALYSIS
- Skill:
- Failed Test:
- Binary Result: 0
- Exact Problem:
- Evidence:
- Root Cause:
- Why Current Strategy Failed:
- Corrective Action:
- New Strategy:
- Next Command:

==================================================
ITERATION LOOP
==================================================

For each skill:
1. Read the skill file.
2. Glob for backing scripts — confirm they exist on disk before referencing them.
3. Run the backing validator or script in safe mode (--dry-run or read-only).
4. Capture exact evidence: command, exit code, stdout/stderr snippet.
5. Score binary tests T1–T9.
6. If any test = 0: output FAILURE ANALYSIS, change strategy materially, retry.
7. Update this skill's memory file.
8. Re-run regression checks.
9. Update SKILL_HARDENING_MASTER.md.
10. Continue immediately to the next weakest skill.

==================================================
SAFETY RULES (NON-NEGOTIABLE)
==================================================

1.  Never mark a skill PASS without captured evidence.
2.  Never invent command results, exit codes, or file paths.
3.  Never modify config/scripts.json.
4.  Never modify production ETL scripts in 02_ETL_Scripts/.
5.  Never modify AssignmentMasterV2.csv except via the approved sync script.
6.  Never run multiple live write tests against PowerBI_Data/_DropExports simultaneously.
7.  Never use DateTime.LocalNow in M code.
8.  Never change carucci_r to RobertCarucci in any path.
9.  Never write to PowerBIDate — correct name is PowerBI_Data.
10. preflight, validate-window, and diagnose-pipeline are read-only — zero file writes.
11. process-exports dry-run must run before any live execution path is considered.
12. monthly-cycle must run Pre_Flight_Validation before any ETL step.
13. Do NOT touch .claude/commands/fix-excel.md — pre-existing skill, not in scope.
14. Do not commit .log files or .xlsx test/diagnostic files to git.

==================================================
STOP CONDITIONS
==================================================

STOP only when:
- All 6 skills have Skill Success (T9) = 1, OR
- A skill is BLOCKED with exact documented evidence AND all non-blocked skills are complete.

==================================================
FINAL OUTPUT
==================================================

Print this report when done:

FINAL SKILL HARDENING REPORT
- Total skills: 6
- Passed:
- Failed:
- Blocked:
- Per-skill binary score:
    validate-window:    T1_ T2_ T3_ T4_ T5_ T6_ T7_ T8_ T9_
    preflight:          T1_ T2_ T3_ T4_ T5_ T6_ T7_ T8_ T9_
    diagnose-pipeline:  T1_ T2_ T3_ T4_ T5_ T6_ T7_ T8_ T9_
    sync-personnel:     T1_ T2_ T3_ T4_ T5_ T6_ T7_ T8_ T9_
    process-exports:    T1_ T2_ T3_ T4_ T5_ T6_ T7_ T8_ T9_
    monthly-cycle:      T1_ T2_ T3_ T4_ T5_ T6_ T7_ T8_ T9_
- Regressions added (name + what it protects):
- Known gaps resolved:
- Known gaps remaining (with evidence):
- Autonomous completion: yes / no

==================================================
BEGIN — PHASE ORDER
==================================================

Phase 0: Read CLAUDE.md, README.md, SUMMARY.md, config/scripts.json,
         scripts/path_config.py, docs/ETL_SKILL_MEMORY.md,
         Standards/config/powerbi_visuals/visual_export_mapping.json
         → Confirm Pre_Flight_Validation.py casing on disk
         → Confirm visual count in visual_export_mapping.json
         → Confirm existence of: check_traffic_badges_in_master.py, find_unknown_badges.py
         → Document any CLAUDE.md gaps in master tracker

Phase 1: Read all 6 skill files → classify read-only vs write-capable
         → Create SKILL_HARDENING_MASTER.md and all 6 memory file stubs

Phase 2: Wave A — spawn in parallel:
           validate-window, preflight, diagnose-pipeline, sync-personnel (read-only modes)

Phase 3: Wave B — one at a time with isolated worktrees:
           process-exports, monthly-cycle, sync-personnel (sync mode)

Phase 4: Cross-skill regression pass — re-run all regression checks across all 6 skills

Phase 5: Final scorecard — do not finish until every skill is PASS or BLOCKED with evidence

Start Phase 0 now.

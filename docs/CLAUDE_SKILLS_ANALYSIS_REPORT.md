# Master_Automation Repository Analysis & Claude Skills Report

**Date:** 2026-03-30
**Author:** Claude Code (Lead Automation Architect Analysis)
**Repo Version:** v1.20.2
**Branch:** `claude/analyze-repo-extend-claude-VBBxc`

---

## 1. Repository Overview

**Master_Automation** (aka `06_Workspace_Management`) is the centralized ETL orchestration hub for the **Hackensack Police Department's Compstat reporting pipeline**. It ingests raw data exports from multiple law enforcement systems, transforms them through Python and PowerShell ETL scripts, and outputs Power BI-ready datasets.

### Architecture Summary

```
Raw Exports (05_EXPORTS/)          Personnel (09_Reference/)
     │                                    │
     ▼                                    ▼
┌─────────────────────────────────────────────┐
│           Master_Automation                 │
│  ┌─────────────┐  ┌──────────────────────┐  │
│  │ Pre-Flight   │→│ ETL Scripts (5 active)│  │
│  │ Validation   │  │  • Arrests           │  │
│  └─────────────┘  │  • Community Engage.  │  │
│                    │  • Overtime/TimeOff   │  │
│  ┌─────────────┐  │  • Response Times     │  │
│  │ PBI Visual   │→│  • Summons            │  │
│  │ Export Proc. │  └──────────────────────┘  │
│  └─────────────┘           │                │
│                            ▼                │
│  ┌─────────────────────────────────────┐    │
│  │ Staging (03_Staging/) + Backfill    │    │
│  │ Processed_Exports/ (categorized)    │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────────┘
                     │
                     ▼
           Power BI (.pbix)
         M Code queries load from
         PowerBI_Data/ & Staging/
```

### Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| ETL Orchestrator | `scripts/run_all_etl.ps1` | Sequential execution of all enabled scripts |
| Path Resolution | `scripts/path_config.py` | Portable OneDrive path resolution (desktop/laptop) |
| Visual Export Processing | `scripts/process_powerbi_exports.py` | Route PBI CSV exports to categorized folders |
| Export Routing | `scripts/processed_exports_routing.py` | Canonical folder names, archive management |
| Pre-Flight Validation | `scripts/Pre_Flight_Validation.py` | Gate check before monthly ETL run |
| Summons ETL | `run_summons_etl.py` | 3-tier output: RAW, CLEAN Excel, SLIM CSV |
| Excel Surgery | `scripts/inject_ai_context_reference.py` | Zip-level XML injection into shared workbooks |
| M Code Library | `m_code/` | Version-controlled Power BI queries (30+ tables) |
| TMDL Export | `m_code/tmdl_export/` | Power BI tabular model definitions |
| Visual Mapping | `Standards/config/powerbi_visuals/visual_export_mapping.json` | PBI visual-to-filename routing rules |
| Config | `config/scripts.json` | ETL script registry, paths, timeouts |

### Data Domains (5 Active ETL Pipelines)

1. **Arrests** — Court/arrest records, 13-month rolling window, category distribution
2. **Community Engagement** — Outreach events, attendee tracking
3. **Overtime/TimeOff** — VCS time reports, accrual/usage, sworn officer breakdowns
4. **Response Times** — CAD incident data, dispatch-to-scene calculations, priority filtering
5. **Summons** — E-ticket exports, DFR split, fine/fee enrichment, bureau assignment

---

## 2. Workflow Bottlenecks Identified

### Bottleneck 1: Manual Power BI Visual Exports
**Severity: HIGH** | **Frequency: Monthly**

Power BI visual exports must be manually triggered (`Ctrl+Shift+E` from each report page) and placed into `_DropExports/`. The `run_all_etl.ps1` comments explicitly state: *"Before running this orchestrator each month, ensure Power BI visual exports have been manually exported."*

**Impact:** This is the single largest friction point. Every monthly cycle begins with a manual multi-click export session. If a visual is missed, the entire downstream normalization and backfill chain has gaps.

### Bottleneck 2: No Single-Command Monthly Cycle
**Severity: HIGH** | **Frequency: Monthly**

The monthly cycle requires running multiple commands in sequence: pre-flight validation, export processing, 5 ETL scripts, and post-run validation. While `run_all_etl.ps1` orchestrates the ETL scripts, the pre- and post-steps are separate manual actions.

### Bottleneck 3: Fragmented Diagnostic Scripts
**Severity: MEDIUM** | **Frequency: Ad-hoc**

There are 30+ individual diagnostic scripts in `scripts/` (e.g., `diagnose_summons_blank_bureau.py`, `diagnose_summons_missing_months.py`, `diagnose_summons_top5_vs_deptwide.py`, `diagnose_benchmark_data.py`, `diagnose_traffic_gap.py`). Each requires knowing its exact name and arguments.

### Bottleneck 4: Personnel Master Validation
**Severity: MEDIUM** | **Frequency: When staff changes occur**

When officers transfer between units, the `Assignment_Master_V2.csv` must be updated. Stale data causes blank WG2/bureau assignments in summons and overtime reports. Multiple scripts exist to diagnose this (`diagnose_summons_blank_bureau.py`, `check_traffic_badges_in_master.py`, `find_unknown_badges.py`) but they're not unified.

### Bottleneck 5: 13-Month Window Verification
**Severity: MEDIUM** | **Frequency: Monthly**

24 Power BI visuals enforce a rolling 13-month window. Verifying that all data sources have complete coverage requires running separate validators (`validate_13_month_window.py`, `validate_response_time_exports.py`) and manually cross-checking.

### Bottleneck 6: Backfill Gap Management
**Severity: LOW-MEDIUM** | **Frequency: When gaps discovered**

The backfill system (`summons_backfill_merge.py`, `merge_powerbi_backfill.py`) requires understanding which months are source-of-truth vs. backfilled. There's no quick way to audit backfill completeness across all pipelines.

---

## 3. Recommended Claude Skills

All skills below are implemented as Claude Code custom commands in `.claude/commands/` and are now available via `/skill-name` in any Claude Code session within this repository.

### 3.1 `/monthly-cycle` — Full Monthly ETL Orchestration
**File:** `.claude/commands/monthly-cycle.md`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Eliminate the multi-step monthly cycle by orchestrating pre-flight, export processing, all 5 ETL scripts, and post-run validation in a single guided command |
| **Bottleneck Solved** | #2 (No single-command cycle) |
| **Usage** | `/monthly-cycle 2026-02` |

**What it does:**
1. Resolves report month (defaults to previous month)
2. Runs `Pre_Flight_Validation.py` — stops on FAIL unless user overrides
3. Processes `_DropExports/` CSVs (dry-run first, then execute on confirmation)
4. Runs all 5 enabled ETL scripts in order with error capture
5. Validates outputs post-run
6. Presents a PASS/FAIL scorecard table

### 3.2 `/preflight` — Pre-Flight Validation
**File:** `.claude/commands/preflight.md`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Quick gate-check before committing to a full ETL run — validates source data, config, personnel, and export mapping |
| **Bottleneck Solved** | #2, #4 |
| **Usage** | `/preflight 2026-02` |

**What it does:**
1. Runs `Pre_Flight_Validation.py --report-month YYYY-MM`
2. Checks export file presence per pipeline with file counts and sizes
3. Validates `Assignment_Master_V2.csv` integrity
4. Confirms `visual_export_mapping.json` parses correctly
5. Lists unprocessed CSVs in `_DropExports/`
6. Reports PASS/FAIL/WARN checklist

### 3.3 `/process-exports` — Power BI Visual Export Processing
**File:** `.claude/commands/process-exports.md`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Streamline the most error-prone manual step: routing raw PBI CSV exports to normalized, categorized destinations |
| **Bottleneck Solved** | #1 (Manual PBI exports — post-export processing half) |
| **Usage** | `/process-exports 2026_02` |

**What it does:**
1. Always starts with `--dry-run` to show matched/unmatched files
2. Asks for confirmation before executing
3. Runs the full processing pipeline (rename, normalize, route, backfill copy)
4. Post-run `--verify-only` to confirm all files landed correctly
5. Optional `--scan-processed-exports-inbox` for stray files

### 3.4 `/validate-window` — 13-Month Rolling Window Validation
**File:** `.claude/commands/validate-window.md`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Quickly verify all 24 PBI visuals have complete 13-month data coverage |
| **Bottleneck Solved** | #5 |
| **Usage** | `/validate-window 2026-02` |

**What it does:**
1. Calculates expected 13-month window boundaries
2. Runs `validate_13_month_window.py` for all enforced visuals
3. Runs `validate_response_time_exports.py` for CSV shape checks
4. Spot-checks backfill folder coverage
5. Reports per-visual PASS/WARN/FAIL with missing month names

### 3.5 `/diagnose-pipeline` — Unified Pipeline Diagnostics
**File:** `.claude/commands/diagnose-pipeline.md`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Replace 30+ scattered diagnostic scripts with one entry point that runs the right checks for any pipeline |
| **Bottleneck Solved** | #3 (Fragmented diagnostics) |
| **Usage** | `/diagnose-pipeline summons 2026-02` |

**Supported pipelines:** `summons`, `arrests`, `overtime`, `response-time`, `community`, `exports`, `personnel`

**What it does per pipeline:**
- Runs the relevant subset of diagnostic scripts
- Checks source files, classification mappings, DFR splits, backfill integrity
- Reports specific records/files causing issues (not just counts)
- Provides actionable recommended fixes

### 3.6 `/sync-personnel` — Assignment Master Personnel Management
**File:** `.claude/commands/sync-personnel.md`

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Unified personnel data validation, sync, cross-reference, and gap detection |
| **Bottleneck Solved** | #4 (Personnel validation) |
| **Usage** | `/sync-personnel check` or `/sync-personnel find-unmapped summons` |

**Actions:**
- `check` — Validate Assignment_Master_V2.csv integrity (row count, blank WG2, duplicates, badge format)
- `sync` — Run the sync script to update from source
- `compare {badge}` — Look up a specific badge across all data sources
- `find-unmapped {pipeline}` — Find badges in exports that aren't in the master

### 3.7 `/fix-excel` — Excel Workbook Surgery (Pre-existing)
**File:** `.claude/commands/fix-excel.md` *(already existed)*

This skill was already in place for zip-level XML surgery on shared Excel workbooks. It remains unchanged and handles the critical requirement of modifying `.xlsx/.xlsm` files without destroying Data Validation, Conditional Formatting, or Web Extensions.

---

## 4. Skill Inventory Summary

| # | Skill Command | Status | Bottleneck Addressed |
|---|---------------|--------|----------------------|
| 1 | `/monthly-cycle` | **NEW** | Full monthly cycle automation |
| 2 | `/preflight` | **NEW** | Pre-run validation gate |
| 3 | `/process-exports` | **NEW** | PBI visual export routing |
| 4 | `/validate-window` | **NEW** | 13-month window enforcement |
| 5 | `/diagnose-pipeline` | **NEW** | Unified diagnostics |
| 6 | `/sync-personnel` | **NEW** | Personnel data management |
| 7 | `/fix-excel` | Existing | Excel workbook surgery |

---

## 5. Next Steps: Integration Guide

### Immediate (Ready Now)

All 6 new skills are installed in `.claude/commands/` and are immediately available in any Claude Code session opened within the `Master_Automation` repository. Use them by typing the slash command:

```
/monthly-cycle 2026-02
/preflight 2026-03
/process-exports 2026_03
/validate-window 2026-03
/diagnose-pipeline summons 2026-02
/sync-personnel check
```

### Short-Term Enhancements

1. **Add a `CLAUDE.md`** to the repo root with:
   - Quick reference to available skills
   - Key path conventions (`ONEDRIVE_BASE`, `path_config.py`)
   - Common report-month format reminders (YYYY-MM vs YYYY_MM)

2. **Extend `config/scripts.json`** to include diagnostic script mappings per pipeline, so `/diagnose-pipeline` can discover checks dynamically rather than using hardcoded lists.

3. **Add a `/scorecard` skill** that reads ETL logs from `logs/` and generates a historical pass/fail scorecard across months — useful for tracking pipeline reliability over time.

### Medium-Term Opportunities

4. **Power BI REST API integration** — When/if the Power BI Service exposes export APIs for embedded visuals, create a skill to automate the `Ctrl+Shift+E` export step itself (currently the only remaining manual step).

5. **M Code diff skill** — Create a `/diff-mcode` skill that compares the version-controlled M code in `m_code/` against what's deployed in `m_code/tmdl_export/tables/`, flagging drift between the repo and the live Power BI model.

6. **Backfill audit skill** — A `/audit-backfill` skill that traverses `PowerBI_Data/Backfill/` and reports coverage gaps, duplicate months, and size anomalies across all pipeline categories.

---

## 6. Security Considerations

All skills adhere to these security practices:

- **No hardcoded credentials** — Path resolution uses `ONEDRIVE_BASE` / `ONEDRIVE_HACKENSACK` environment variables via `path_config.py`
- **Read-only by default** — Diagnostic and validation skills never modify source data
- **Dry-run first** — Destructive operations (export processing, file moves) always show a preview and require confirmation
- **Backup before modify** — The `/fix-excel` skill creates timestamped backups before any workbook surgery
- **No secrets in commands** — Skill files contain only procedural instructions, not API keys or connection strings

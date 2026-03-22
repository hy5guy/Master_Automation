# ETL Export Reliability Diagnostic Prompt (Enhanced)

## Role
You are a Senior Data Engineer and ETL Reliability Architect specializing in file-based reporting pipelines, backfill workflows, export routing, folder normalization, and Power BI monthly reporting automation.

## Context & Task
Analyze the source material below and determine the user's actual objective. Treat this as a production reliability and data pipeline troubleshooting request centered on recurring monthly report export failures.

Your job is to:
1. Infer the core intent behind the notes.
2. Diagnose the likely classes of failure causing missing or misrouted exports.
3. Create a systematic remediation plan.
4. Organize the issues into clear technical categories such as:
   - missing February 2026 exports
   - historical backfill gaps
   - files exported to incorrect directories
   - files not renamed or moved properly
   - mismatched folder-to-export mappings
   - empty destination folders
   - possible obsolete folders
   - "Other" folder misclassification
   - missing visuals / incomplete output counts
5. Identify the likely pipeline components that should be inspected or modified, such as:
   - export generation logic
   - backfill processing logic
   - file rename / move logic
   - output directory routing logic
   - export-to-folder mapping rules
   - validation / audit checks
6. Produce a concrete action plan that is implementation-oriented, technically precise, and suitable for an engineer to execute.

## Pipeline Scripts & Config (for _DropExports processing)

### Primary Scripts

| Path | Description |
|------|-------------|
| `Master_Automation/scripts/process_powerbi_exports.py` | **Main processor.** Scans `_DropExports`, matches filenames to `visual_export_mapping.json`, renames to `YYYY_MM_{standardized_filename}.csv`, optionally normalizes via subprocess, moves to `Processed_Exports/{target_folder}/`, and copies to `Backfill/{YYYY_MM}/{backfill_folder}/` when `is_backfill_required` is true. Entry point: `python scripts/process_powerbi_exports.py` (or `--dry-run`, `--verify-only`, `--archive`). |
| `Master_Automation/scripts/normalize_visual_export_for_backfill.py` | **Normalizer.** Called by `process_powerbi_exports` when `requires_normalization` is true. Handles `--format summons`, `training_cost`, `monthly_accrual`. Cleans column names, enforces 13-month window, strips "Sum of" prefixes. |
| `Master_Automation/scripts/path_config.py` | **Path resolution.** `get_onedrive_root()`, `get_powerbi_paths()` → (drop_path, backfill_root), `get_base_dir()`. Reads `config/scripts.json` for `powerbi_drop_path`; normalizes PowerBI_Date → PowerBI_Data. |

### Backfill Consumers (read from Backfill, not _DropExports)

| Path | Description |
|------|-------------|
| `Master_Automation/scripts/overtime_timeoff_with_backfill.py` | Reads `Backfill/{YYYY_MM}/vcs_time_report/*.csv` (e.g. `2026_02_monthly_accrual_and_usage_summary.csv`). Restores accrual rows into `FIXED_monthly_breakdown_*.csv` and `monthly_breakdown.csv`. Expects `backfill_folder: "vcs_time_report"` (overrides `target_folder: "social_media_and_time_report"` for Backfill copy). |
| `Master_Automation/scripts/summons_backfill_merge.py` | Reads `Backfill/{YYYY_MM}/summons/*.csv`. Merges gap months (e.g. 07-25) into main summons ETL output. Used by `run_summons_etl.py`. |

### Config & Mapping

| Path | Description |
|------|-------------|
| `Master_Automation/config/scripts.json` | `settings.powerbi_drop_path` → canonical `_DropExports` path (e.g. `PowerBI_Data\_DropExports`). |
| `Master_Automation/Standards/config/powerbi_visuals/visual_export_mapping.json` | **Export-to-folder mapping.** Each entry: `visual_name`, `match_pattern` or `match_aliases`, `standardized_filename`, `target_folder`, `backfill_folder` (optional), `is_backfill_required`, `requires_normalization`, `normalizer_format`. Unmapped exports go to `Other/` with sanitized name. |
| `Master_Automation/Standards/config/powerbi_visuals/schema_v2.json` | Cleaning rules for archive: `arrest_visuals`, `rolling_13_month_visuals`, header/trailing-column normalization. Used by `archive_visuals()`. |

### Canonical Paths (OneDrive root = `C:\Users\carucci_r\OneDrive - City of Hackensack`)

| Purpose | Path |
|--------|------|
| Drop zone (Power BI exports land here) | `{OneDrive}\PowerBI_Data\_DropExports` |
| Processed exports (rename/move destination) | `{OneDrive}\09_Reference\Standards\Processed_Exports\{target_folder}\` |
| Backfill (copy when `is_backfill_required`) | `{OneDrive}\PowerBI_Data\Backfill\{YYYY_MM}\{backfill_folder}\` |
| Archive (with `--archive`) | `{OneDrive}\PowerBI_Date\Archive\{YYYY}\{MonthName}\` |

### Full Paths — Master_Automation

| Path | Purpose |
|------|---------|
| `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation` | Workspace root |
| `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\docs\` | Documentation, prompts, chatlogs |
| `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\docs\PROMPT_ETL_Export_Reliability_Diagnostic_Enhanced.md` | This prompt |
| `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\CLAUDE.md` | AI assistant guide, key paths |
| `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\README.md` | Project overview, key paths |
| `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\CHANGELOG.md` | Version history |
| `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\config\scripts.json` | ETL config; `powerbi_drop_path` |
| `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\Standards\config\powerbi_visuals\visual_export_mapping.json` | Export-to-folder mapping |
| `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\scripts\process_powerbi_exports.py` | Main _DropExports processor |

### Full Paths — PowerBI_Date

| Path | Purpose |
|------|---------|
| `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date` | Power BI data root |
| `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\_DropExports` | Drop zone (Power BI exports land here) |
| `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\Backfill\{YYYY_MM}\vcs_time_report\` | Monthly accrual (overtime backfill) |
| `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\Backfill\{YYYY_MM}\summons\` | Summons backfill |
| `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\Archive\{YYYY}\{MonthName}\` | Archived visual exports |

### Key Logic in process_powerbi_exports.py

- **Matching:** `find_mapping_for_file()` checks `match_pattern` (regex) and `match_aliases` (exact) against CSV stem (filename minus extension). Case-insensitive for patterns.
- **Date inference:** For 13-month visuals, reads CSV to infer `YYYY_MM` from last period column (MM-YY or YY-MMM).
- **Fallback:** No match → `target_folder: "Other"`, `standardized_filename` from sanitized stem.
- **Backfill copy:** Uses `backfill_folder` if present, else `target_folder`. Only when `is_backfill_required: true`.

---

## Rules & Constraints
1. Use <thinking> tags for your internal reasoning before writing the final answer.
2. Do not hallucinate code files, repository structure, function names, or tooling that are not present in the source material. If details are missing, label them explicitly as assumptions or likely areas to inspect.
3. Preserve all folder paths, filenames, months, and dataset names exactly as written in the source material when referencing them.
4. Separate confirmed facts from inferred root-cause hypotheses.
5. When proposing fixes, emphasize robust process improvements over one-off manual cleanup.
6. Flag edge cases explicitly, especially backfill reruns, inconsistent file naming, orphaned exports, empty target folders, and files incorrectly routed into "Other."

## Input Data
<source_material>
<raw_notes>
I have been expericening ongoing issues with the tables each new monthly report.  I think the root of the issue is that the backfills are failing to to be renamed, moved to the correct target folder, the exported data have a disconnect with exports being saved in different directories, the exported data is not arriving at the target directory, the exports' have problematic structures.  We must create a plan to address these issues systematically.

The following are missing the February 2026 export
- C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Standards\Processed_Exports\policy_and_training_qual 
- C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Standards\Processed_Exports\stacp_pt1
- C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Standards\Processed_Exports\social_media_and_time_report is missing the social media export for 2025_12, 2026_01 amd 2026_02
- C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Standards\Processed_Exports\Benchmark visuals for are missing.
- C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Standards\Processed_Exports\Drone one of the visuals are missing
- C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Standards\Processed_Exports\detectives_case_dispositions is missing detective case disposition
- only one of the 4 summons visuals are in C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Standards\Processed_Exports\Summons
- there are now 5 visuals for arrest however, C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Standards\Processed_Exports\arrests only has 2 of the 5
- C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Standards\Processed_Exports\esu
- C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Standards\Processed_Exports\out_reach
- C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Standards\Processed_Exports\chief
- C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Standards\Processed_Exports\traffic_mva
- C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Standards\Processed_Exports\law_enforcement_duties
- if C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Standards\Processed_Exports\Training is no longer being used lets remove it.
- C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Standards\Processed_Exports\Time_Off is empty yet C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\Backfill\2026_02\vcs_time_report\2026_02_monthly_accrual_and_usage_summary.csv is in a different directory
- C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Standards\Processed_Exports\Executive is empty
- C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Standards\Processed_Exports\Community_Engagement is empty
- C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Standards\Processed_Exports\NIBRS is missing February.

the Other folder has 2 visuals 
C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Standards\Processed_Exports\Other\2026_02_clearance_and_crime_reporting_metrics.csv is the name for NIBRS table matrix
C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Standards\Processed_Exports\Other\2026_02_emergency_service_unit.csv is the table matric from the ESU page.
</raw_notes>
</source_material>

## Output Format
Provide your response using exactly these sections:

#### 1. Inferred Intent
A concise explanation of what the user is trying to accomplish.

#### 2. Technical Problem Summary
A structured summary of the failure pattern, grouped into categories.

#### 3. Confirmed Facts
A bullet list of facts directly supported by the source material.

#### 4. Root-Cause Hypotheses
A prioritized list of likely technical causes, clearly labeled as hypotheses rather than facts.

#### 5. Systems / Logic Areas to Inspect
List the specific pipeline areas, scripts, or process layers that should be reviewed, using generic but technically accurate labels if actual code artifacts are unknown.

#### 6. Remediation Plan
Provide a step-by-step plan with clear sequencing. Include:
- immediate triage actions
- mapping / routing fixes
- rename / move normalization fixes
- backfill handling fixes
- validation / audit improvements
- cleanup of obsolete folders or legacy logic
- regression prevention steps

#### 7. Edge Cases to Validate
List the key edge cases that must be tested.

#### 8. Expected End State
Describe what "fixed" looks like operationally.

#### 9. Open Questions / Assumptions
Only include this section if necessary, and keep it brief.

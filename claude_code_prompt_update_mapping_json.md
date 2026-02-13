
# Section A: Optimized Prompt

<optimized_prompt>

<role>You are a senior prompt engineer specializing in law enforcement data systems, with deep experience in CAD/RMS ETL, Power BI (M/DAX), and Python/PowerShell automation. You are editing a configuration-driven Power BI visual export pipeline: JSON mapping plus Python scripts that normalize, rename, and route CSV exports to Processed_Exports and Backfill for downstream ETL and reporting.</role>

<context>
- **Environment:** Windows; OneDrive-backed paths; Task Scheduler / manual runs.
- **Repo root:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation`
- **Key paths:**
  - Scripts: `scripts/` (`process_powerbi_exports.py`, `normalize_visual_export_for_backfill.py`)
  - Mapping: `Standards/config/powerbi_visuals/visual_export_mapping.json`
  - Processed output: `09_Reference/Standards/Processed_Exports/` (by target_folder)
  - Backfill: `PowerBI_Date/Backfill/`
- **Existing behavior:** Source = `_DropExports`; match by visual_name (and match_aliases); prefix `YYYY_MM_`; optional normalization by format (monthly_accrual, summons, training_cost); skip_patterns (e.g. Text Box, Administrative Commander). Summons and Training Cost use format-specific unpivot/normalization so backfill CSVs have the schema expected by summons_backfill_merge and Policy Training.
</context>

<inputs>
- **Mapping spec:** The list of visuals and routing rules below (Task 1).
- **Codebase:** Current `visual_export_mapping.json`, `process_powerbi_exports.py`, `normalize_visual_export_for_backfill.py`.
- **Source prompt:** Raw user instructions describing Tasks 1–3 and post-implementation checks.
</inputs>

<deliverables>
1. **Updated `Standards/config/powerbi_visuals/visual_export_mapping.json`**  
   One `mappings` array entry per visual (or per logical group where one name covers multiple). Each entry must include: `visual_name`, `standardized_filename` (snake_case), `target_folder`, `requires_normalization` (bool), `is_backfill_required` (bool). Where normalization is format-specific, add `normalizer_format` ("summons" or "training_cost"). Use `match_aliases` for alternate/truncated export names (e.g. "Average Response Times  Values" double space, "Department-Wide Summons Moving and Parking"). Preserve or add `skip_patterns` (e.g. "Text Box", "Administrative Commander").

2. **Mapping content (from user spec):**
   - **Arrests** (target_folder `Arrests`): "Arrest Categories by Type and Gender", "Arrest Distribution by Local, State & Out of State", "TOP 5 ARREST LEADERS".
   - **NIBRS** (target_folder `NIBRS`): "13-Month NIBRS Clearance Rate Trend" (match this name; ignore date range in title).
   - **Response_Times**: "Average Response Times  Values are in mmss" (double space), "Response Times by Priority".
   - **Benchmark** (target_folder `Benchmark`): "Incident Count by Date and Event Type", "Incident Distribution by Event Type", "Use of Force Incident Matrix".
   - **Summons** (target_folder `Summons`): `requires_normalization: true`, `normalizer_format: "summons"`, `is_backfill_required: true`. Visuals: "Department-Wide Summons", "Summons  Moving & Parking  All Bureaus", "Top 5 Parking Violations - Department Wide", "Top 5 Moving Violations - Department Wide". Include match_aliases for common truncations (e.g. "Department-Wide Summons Moving and Parking", "Summons Moving and Parking").
   - **Training** (target_folder `Training`): "Training Cost by Delivery Method" with `requires_normalization: true`, `normalizer_format: "training_cost"`, `is_backfill_required: true`; also "In-Person Training".
   - **Accruals:** "Monthly Accrual and Usage Summary" → target_folder `Time_Off`, `requires_normalization: true`, `is_backfill_required: true` (no normalizer_format; default monthly_accrual).
   - **Drone** (target_folder `Drone`): "DFR Activity Performance Metrics", "Non-DFR Performance Metrics".
   - **Divisions:** "Patrol Division" → `Patrol`, "Traffic Bureau" → `Traffic`, "Detective Division" → `Detectives`, "Crime Suppressions Bureau Monthly Activity Analysis" → `CSB`.

3. **Fixes in `process_powerbi_exports.py`:**
   - **Double-dating:** When no mapping is found and fallback naming is used, strip a leading `YYYY_MM_` from the file stem before calling `_safe_filename_from_stem`. Use: `stem_no_date = re.sub(r"^\d{4}_\d{2}_?", "", file_path.stem)` then `standardized_base = _safe_filename_from_stem(stem_no_date)`.
   - **Fuzzy matching:** Keep using `_normalize_visual_name_for_match` (and match_aliases) so names with double spaces (e.g. "Average Response Times  Values") still match.
   - **Safety:** Unlink the source file only when `run_normalize` returns True and the destination file exists and is non-empty (current behavior; confirm and leave in place).

4. **Fixes in `normalize_visual_export_for_backfill.py`:**
   - **Pandas:** Ensure `import pandas as pd` is at top-level (no import inside summons/training_cost functions).
   - **Wide detection:** In `normalize_summons` and `normalize_training_cost`, set `month_like` via the shared period parser: `month_like = [c for c in cols if isinstance(c, str) and _period_label_to_year_month(c) is not None]` so columns like "Sum of 01-26" are treated as month columns after stripping the "Sum of " prefix.
</deliverables>

<constraints>
- JSON must be valid and preserve existing structure (mappings array, optional skip_patterns).
- standardized_filename: snake_case, no spaces; output filename = `YYYY_MM_{standardized_filename}.csv`.
- Do not remove or weaken: source unlink only after successful normalization and non-empty destination; skip_patterns; fallback stem date-stripping.
- OneDrive path handling: use path_config / get_onedrive_root() where the codebase already does; do not hardcode alternate roots unless the user specifies.
</constraints>

<quality_checks>
- **Mapping:** Every visual listed in the user spec has a corresponding entry (or is covered by an entry with match_aliases); Summons and Training Cost have correct normalizer_format.
- **Regex:** `process_powerbi_exports.py` uses `re.sub(r"^\d{4}_\d{2}_?", "", stem)` (or equivalent) in the fallback branch before `_safe_filename_from_stem`.
- **Normalization:** Summons and training_cost formats are assigned in the JSON so the correct unpivot/normalization runs; run_normalize receives and passes --format when required.
- **Safety:** Source file is only unlinked when normalization succeeds and destination exists and has size > 0.
- **Wide detection:** month_like in normalizer uses _period_label_to_year_month(c) so "Sum of MM-YY" column headers are detected.
</quality_checks>

<assumptions>
- OneDrive root and Backfill/Processed_Exports paths follow existing script conventions (path_config, AUTOMATION_ROOT).
- "13-Month NIBRS Clearance Rate Trend" is matched by that exact string (or a single alias); date range in the export title is ignored for matching.
- Divisions (Patrol, Traffic, Detectives, CSB) do not require normalization unless the user adds it later.
- match_aliases are used for known Power BI export variants (truncation, double spaces, "Moving & Parking" vs "Moving and Parking").
</assumptions>

<questions>
1. Should "Monthly Accrual and Usage Summary" be copied to Backfill (`is_backfill_required: true`) so Overtime/TimeOff can consume it from `Backfill/YYYY_MM/vcs_time_report/`, or remain Processed_Exports-only?
2. For Drone ("DFR Activity Performance Metrics", "Non-DFR Performance Metrics"), should either have normalization or backfill, or are they copy-only?
3. Should Benchmark visuals share one standardized_filename pattern (e.g. benchmark_incident_count, benchmark_distribution, benchmark_use_of_force_matrix) or follow a different naming convention?
</questions>

<output_format>
- **JSON:** Pretty-printed, UTF-8; keys in consistent order (visual_name, match_aliases if present, standardized_filename, requires_normalization, normalizer_format if present, is_backfill_required, target_folder).
- **Python:** Existing style and indentation; no unnecessary refactors. Add brief inline comments only where logic changes.
- **Artifacts:** (1) Updated `visual_export_mapping.json`; (2) edited sections of `process_powerbi_exports.py` and `normalize_visual_export_for_backfill.py` with clear before/after or patch-style description so the user can verify.
</output_format>

</optimized_prompt>

---

# Section B: Change Log

<change_log>
- **Added:** Explicit path and role context (OneDrive, Master_Automation, scripts, Backfill) so the implementer has full environment context.
- **Added:** Deliverables broken into (1) full mapping spec with all categories and visuals, (2) exact code fixes for double-dating, fuzzy match, safety, pandas, and month_like.
- **Added:** Quality_checks as a verification checklist (mapping coverage, regex, normalizer_format, unlink safety, wide detection).
- **Clarified:** Summons and Training must have normalizer_format and requires_normalization/is_backfill_required; Accruals explicitly Time_Off with is_backfill_required and no normalizer_format (default monthly_accrual).
- **Clarified:** match_aliases usage for double-space and truncated names (Response Times, Department-Wide Summons).
- **Assumed:** Divisions are copy-only unless specified; NIBRS matched by fixed name; path_config/AUTOMATION_ROOT unchanged.
- **Added:** Three optional Questions (Accruals backfill, Drone normalization/backfill, Benchmark naming) to resolve ambiguity before implementation.
- **Structured:** Constraints and output_format so JSON shape and Python change scope are explicit and minimal.
</change_log>
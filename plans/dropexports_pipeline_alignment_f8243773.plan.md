# Plan: DropExports Pipeline Alignment

**Plan ID:** dropexports_pipeline_alignment_f8243773
**Created:** 2026-03-22
**Branch:** test-dfr-audit
**Active Report Month:** 2026_02

---

## Phase 1 — Code Fixes (Todos 1-4)

### Todo 1 — Fix verify_processing source_dir default
**Status:** done
**File:** `scripts/process_powerbi_exports.py`
**Issue:** `verify_processing()` line 440 defaults `source_dir` to `AUTOMATION_ROOT / "_DropExports"` (repo-local) instead of `PowerBI_Data/_DropExports` (OneDrive). Also `main()` line 496 passes same wrong default.
**Fix:** Change both to use `get_onedrive_root() / "PowerBI_Data" / "_DropExports"`.
**Verification:** PASS — 0 hits for `AUTOMATION_ROOT.*_DropExports`.

### Todo 2 — Replace hardcoded DEFAULT_BACKFILL_SUMMONS_LABEL
**Status:** done
**File:** `scripts/summons_backfill_merge.py`
**Issue:** `DEFAULT_BACKFILL_SUMMONS_LABEL = "2026_01"` is hardcoded. Should be derived dynamically from report month.
**Fix:** Change to compute from current date (previous month) or accept parameter override.
**Verification:** Grep for hardcoded `"2026_01"` in summons_backfill_merge.py — should be 0 hits.

### Todo 3 — Add --report-month arg to process_powerbi_exports.py
**Status:** done
**File:** `scripts/process_powerbi_exports.py`
**Issue:** No `--report-month` CLI arg; `infer_yyyymm_smart` can't accept an explicit override.
**Fix:** Add `--report-month` argparse option; pass as priority override to `infer_yyyymm_smart`.
**Verification:** `python scripts/process_powerbi_exports.py --help` shows `--report-month`.

### Todo 4 — Fix summons_derived_outputs_simple.py output path
**Status:** done
**File:** `scripts/summons_derived_outputs_simple.py`
**Issue:** Line 34: `output_dir = root / "Master_Automation" / "_DropExports"` — wrong path. Should be `PowerBI_Data/_DropExports`.
**Fix:** Change to `root / "PowerBI_Data" / "_DropExports"`.
**Verification:** Grep for `Master_Automation.*_DropExports` — should return 0 hits.

---

## Phase 2 — Backfill Folder Cleanup (Todos 5-7)

### Todo 5 — Rename non-canonical Backfill/2025_12 subfolders
**Status:** done
**Target:** `PowerBI_Data/Backfill/2025_12/`
**Renames:**
- `arrest` → merge into `arrests`
- `chief_law_enforcement_duties` → merge into `chief`
- `community_engagement` → merge into `community_outreach`
- `crime_suppression` → merge into `csb`
- `detective` → rename to `detectives` (canonical)
- `drones` → merge into `drone`
- `policy_training` → merge into `policy_and_training_qual`
- `records` → merge into `remu`
- `safe_streets` → merge into `ssocc`
- `school` → merge into `stacp`
- `training` → merge into `policy_and_training_qual`
- `uncategorized` → delete (after review)
- `use_of_force` → merge into `benchmark`
**Verification:** List 2025_12 subfolders — only canonical names remain.

### Todo 6 — Delete loose CSVs and dev artifacts from Backfill root
**Status:** done
**Target:** `PowerBI_Data/Backfill/`
**Files to remove:** Loose CSVs at root level, `.premove` files, `manifest.json` in 2025_12, `visual_map.csv`, `data.csv`, `response_time_all_metrics` dir at root.
**Verification:** No loose CSVs or dev artifacts at Backfill root.

### Todo 7 — Add CANONICAL_BACKFILL_FOLDERS constant and validation
**Status:** done
**File:** `scripts/process_powerbi_exports.py`
**Fix:** Add constant with 18 canonical folder names; add validation warning when backfill_folder is not in the list.
**Verification:** Grep for `CANONICAL_BACKFILL_FOLDERS` — 1+ hits.

---

## Phase 3 — Mapping and Normalizer (Todos 8-14)

### Todo 8 — Add skip_patterns for _manifest and ^_ prefix
**Status:** done
**File:** `Standards/config/powerbi_visuals/visual_export_mapping.json`
**Fix:** Add `"_manifest"` and regex-note for underscore-prefixed files to skip_patterns.
**Verification:** `_manifest` appears in skip_patterns array.

### Todo 9 — Add response_time_series normalizer handler
**Status:** done
**File:** `scripts/normalize_visual_export_for_backfill.py`
**Fix:** Add `normalize_response_time_series()` handler for Emergency/Routine/Urgent Total Response exports.
**Verification:** Grep for `response_time_series` in normalizer script.

### Todo 10 — Add response_time_priority_matrix normalizer handler
**Status:** done
**File:** `scripts/normalize_visual_export_for_backfill.py`
**Fix:** Add `normalize_response_time_priority_matrix()` for Response Time Trends by Priority.
**Verification:** Grep for `response_time_priority_matrix` in normalizer script.

### Todo 11 — Add 4 response time mapping entries
**Status:** done
**File:** `Standards/config/powerbi_visuals/visual_export_mapping.json`
**Fix:** Add entries for: Emergency - Total Response, Routine - Total Response, Urgent - Total Response, Response Time Trends by Priority.
**Verification:** Count response_time entries in mapping — should be 10.

### Todo 12 — Fix Officer Summons Activity requires_normalization
**Status:** done
**File:** `Standards/config/powerbi_visuals/visual_export_mapping.json`
**Issue:** `requires_normalization: false` but `normalizer_format: "summons"` — contradictory.
**Fix:** Remove `normalizer_format` since normalization is not required for this snapshot visual.
**Verification:** Officer Summons entry has no `normalizer_format` key.

### Todo 13 — Add DFR Total Fines YTD mapping entry
**Status:** done
**File:** `Standards/config/powerbi_visuals/visual_export_mapping.json`
**Fix:** Add mapping for `DFR Total Fines YTD.csv` → target_folder: drone.
**Verification:** Grep for `DFR Total Fines YTD` in mapping file.

### Todo 14 — Recount total_visuals in mapping metadata
**Status:** done
**File:** `Standards/config/powerbi_visuals/visual_export_mapping.json`
**Fix:** Count actual mappings array length, update `total_visuals`.
**Verification:** `total_visuals` matches actual count.

---

## Phase 4 — Orchestrator and Verification (Todos 15-16)

### Todo 15 — Document manual pre-step in run_all_etl.ps1
**Status:** done
**File:** `scripts/run_all_etl.ps1`
**Fix:** Add comment block documenting that Power BI visual exports must be manually placed in `_DropExports` before running.
**Verification:** Grep for `_DropExports` in orchestrator script header.

### Todo 16 — Fix infer_yyyymm_smart to accept --report-month override
**Status:** done
**File:** `scripts/process_powerbi_exports.py`
**Fix:** Wire `--report-month` arg into `infer_yyyymm_smart` as priority-1 source (before data inference).
**Verification:** `infer_yyyymm_smart` signature includes `report_month` parameter.

---

## Phase 5 — Optional Polish (Todos 17-19)

### Todo 17 — Fix doc drift (PowerBI_Date typo, wrong default source path)
**Status:** done
**Files:** Any docs referencing `PowerBI_Date` (should be `PowerBI_Data`).
**Verification:** Grep for `PowerBI_Date` — 0 hits.

### Todo 18 — Extend .gitignore
**Status:** done
**File:** `.gitignore`
**Fix:** Add patterns for `*.premove`, `_manifest.*`, benchmark diagnostics at root.
**Verification:** `.gitignore` contains `*.premove` pattern.

### Todo 19 — Final recount and dry-run validation
**Status:** done
**Fix:** Run `process_powerbi_exports.py --dry-run` and verify: all _DropExports files mapped or skipped, zero "Other" category, total_visuals correct.
**Verification:** Dry-run log shows 0 Other entries.

---

## Git Commit Plan

| Phase | Commit Message | Files |
|-------|---------------|-------|
| 1 | `fix: Phase 1 — source path, dynamic report-month, derived output alignment` | `scripts/process_powerbi_exports.py`, `scripts/summons_backfill_merge.py`, `scripts/summons_derived_outputs_simple.py` |
| 2 | `fix: Phase 2 — Backfill folder rename/cleanup, canonical validation` | `scripts/process_powerbi_exports.py` |
| 3 | `feat: Phase 3 — mapping entries, normalizer handlers, skip patterns` | `Standards/config/powerbi_visuals/visual_export_mapping.json`, `scripts/normalize_visual_export_for_backfill.py` |
| 4 | `docs: Phase 4 — orchestrator docs, infer_yyyymm_smart override` | `scripts/run_all_etl.ps1`, `scripts/process_powerbi_exports.py` |
| 5 | `chore: Phase 5 — doc drift, .gitignore, final recount` | `.gitignore`, `Standards/config/powerbi_visuals/visual_export_mapping.json`, docs |

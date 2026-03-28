# HUMAN_REVIEW.md -- Aggregated Review Items
## Generated: 2026-03-28

All items requiring human decision-making, aggregated from 6 repository audits.

---

## Benchmark (5 items)

### HIGH
- **Decide PII handling**: `benchmark_preview_table.csv` contains officer names, badge numbers, and incident details. Should it remain in the repo, be gitignored, or be deleted? Currently tracked in git.

### MEDIUM
- **Confirm ___Benchmark_FIXED.m status**: Is the old-path M code still needed or can it be archived?
- **Confirm Benchmark_Queries.m usage**: Is the IR parametrized query still in use in any Power BI model?
- **Verify Power BI Scenario B fix**: Diagnosed Feb 2026 (MonthStart relationships or date types), status unknown.

### LOW
- **Review reorganization_proposal.md**: Approve archival of 3 dead scripts and 5 orphaned files.

---

## Community_Engagment (7 items)

### CRITICAL
- **Directory name typo**: `Community_Engagment` (missing 'e'). Rename requires coordinated update across config.json, task_schedule.xml, M code paths, PBI data sources, and parent workspace references. This is the most impactful single fix across the entire workspace.

### HIGH
- **CSB config inconsistency**: config.json sheet_name `26_01` does not match csb_processor.py default `CSB_CommOut`. Source is disabled so not currently impactful, but should be resolved before re-enabling.
- **Verify task_schedule.xml**: Confirm it is registered in Windows Task Scheduler and functioning.

### MEDIUM
- **Create requirements.txt**: README references `pip install -r requirements.txt` but file does not exist. Decide whether to create it and pin versions.
- **Output retention policy**: 30+ timestamped export pairs in output/. Decide whether to keep all or implement rotation.
- **STACP additional_sheets**: `25_Presentations` and `25_Training Delivered` declared in config but only primary sheet_name is processed. Confirm if these should be processed.

### LOW
- **Review dead scripts**: debug_csb_structure.py, debug_processors.py, sample_office_distribution.py, test_date_parsing.py, project_scaffold.py, deploy_production.py, monitor_etl.py -- confirm safe to archive.

---

## Overtime_TimeOff (6 items)

### HIGH
- **Assignment_Master_V2 file extension**: SUMMARY.md says `.xlsx` but v10.py uses `.csv`. Verify which format is on disk.
- **v11 exec() import**: Decide whether v11.py should be refactored to use proper imports or if v11 is abandoned entirely.
- **Review config.json SMTP exposure**: SMTP password field exists (currently empty) but config.json was committed before .gitignore was added.

### MEDIUM
- **v3/v4 M code hardcoded month**: `12-25` is outdated. Confirm if these M code versions need updating or retirement.
- **Backfill path**: `C:\Dev\PowerBI_Data` is outside OneDrive sync tree. Confirm if still needed or can be removed from docs.

### LOW
- **Review reorganization_proposal.md**: Approve archive of 19 legacy scripts, 12 AI/verification MDs, 11 verification scripts, and deletion of 4 stale files.

---

## Policy_Training_Monthly (7 items)

### HIGH
- **Confirm legacy M code retirement**: 5 legacy M code files (POLICY_TRAINING_ANALYTICS.m, Policy_Training_Summary.m, Policy_Training_Weapons.m, Training_Category_Matrix.m, Training_Delivery_Method.m) -- verify they are not referenced by any active Power BI report before archiving.
- **`.git/Training_Matrix.csv`**: A CSV file appears to be accidentally placed inside the `.git` directory. Review and remove.

### MEDIUM
- **policy_training_rework/ contents**: Confirm working files are not needed for any active workflow before archiving.
- **Generic template disposal**: PYTHON_WORKSPACE_AI_GUIDE.md and PYTHON_WORKSPACE_TEMPLATE.md should move to `08_Templates/` or be deleted.
- **Deduplicate `_to_numeric_frame`**: Function defined twice in policy_training_etl.py (identical definitions).

### LOW
- **Add unit tests**: Zero unit test coverage for normalization.py functions.
- **Extract hardcoded path**: `C:\Dev\Power_BI_Data\tools` in policy_training_etl.py should be moved to config.yaml.

---

## Response_Times (6 items)

### HIGH
- **Confirm production script**: Verify `response_time_batch_all_metrics.py` is the sole production script before archiving alternatives.
- **Review scripts/ directory**: ~80 scripts in `scripts/` -- determine which (if any) are still useful before mass archival.

### MEDIUM
- **Legacy M code files**: Determine if ResponseTimeCalculator.m, monthly_summary_etl_final.m are still referenced by any Power BI report.
- **DAX consolidation**: Three DAX files reference different table names (ResponseTimeCalculator, ResponseTimeData, YourTableName). Decide if they should be consolidated.
- **Verify detached git/ directory**: Confirm it is truly detached and safe to delete.

### LOW
- **Review 8950-line validation doc**: `Response_Time_Backfill_Validation_And_Fixes.md` may contain operational content worth preserving before archiving.

---

## Summons (7 items)

### CRITICAL
- **Dual ETL ambiguity**: `SummonsMaster_Simple.py` and `summons_etl_enhanced.py` both write `summons_powerbi_latest.xlsx`. Determine which is the single authoritative production script.

### HIGH
- **Approve root cleanup**: ~130 files should be archived/deleted (75 dead Python scripts, 22 stale MDs, 5 junk files, 5 OneDrive dupes). See reorganization_proposal.md.
- **Badge override review**: Badge 0388 (LIGGIO) -- is this assignment still current? Badge 2025/0738 FIRE LANES conditionals -- still active?

### MEDIUM
- **config.yaml status**: Not loaded by any active script. References old paths and old Assignment_Master format. Safe to archive?
- **process_monthly_summons.py**: Uses `C:\Dev\PowerBI_Data\Backfill` path. Still in use?
- **Backfill freshness**: When will the `2025_12` backfill be superseded by a `2026_xx` backfill?

### LOW
- **DAX inconsistency**: `Top_5_Moving_Subtitle` uses COUNTROWS instead of SUM(TICKET_COUNT), contradicting documented aggregation rule.

---

## Summary by Priority

| Priority | Count | Repos |
|----------|-------|-------|
| CRITICAL | 2 | Community_Engagment (dir rename), Summons (dual ETL) |
| HIGH | 12 | All 6 repos |
| MEDIUM | 15 | All 6 repos |
| LOW | 9 | All 6 repos |
| **TOTAL** | **38** | |

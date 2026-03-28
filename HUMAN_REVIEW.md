# HUMAN_REVIEW.md -- Aggregated Review Items
## Generated: 2026-03-28

All items requiring human decision-making, aggregated from 6 repository audits.

### Security Remediation Status (2026-03-28)
| Flag | Repo | Action Taken | Status |
|------|------|-------------|--------|
| `benchmark_preview_table.csv` PII | Benchmark | Added to .gitignore; was not tracked in git | **RESOLVED** |
| `production_config.json` credential fields | Community_Engagement | Added to .gitignore; removed from git tracking (`git rm --cached`) | **RESOLVED** |
| `task_schedule.xml` runs as SYSTEM | Community_Engagement | Deployment concern — not a code fix. Document in ops runbook. | **ACCEPTED RISK** |
| `config.json` SMTP password field | Overtime_TimeOff | Field is empty; file excluded by .gitignore (`*.json` pattern). Monitor. | **ACCEPTED RISK** |
| `ASSIGNMENT_OVERRIDES` officer data | Summons | Badge-to-name mappings required for business logic. Cannot be externalized without breaking ETL. | **ACCEPTED RISK** |

---

## Benchmark (5 items)

### HIGH
- ~~**Decide PII handling**: `benchmark_preview_table.csv` contains officer names, badge numbers, and incident details.~~ **RESOLVED** — added to .gitignore, not tracked in git.

### MEDIUM
- **Confirm ___Benchmark_FIXED.m status**: Is the old-path M code still needed or can it be archived?
- **Confirm Benchmark_Queries.m usage**: Is the IR parametrized query still in use in any Power BI model?
- **Verify Power BI Scenario B fix**: Diagnosed Feb 2026 (MonthStart relationships or date types), status unknown.

### LOW
- **Review reorganization_proposal.md**: Approve archival of 3 dead scripts and 5 orphaned files.

---

## Community_Engagement (7 items)

### CRITICAL
- ~~**Directory name typo**: `Community_Engagment` (missing 'e').~~ **RESOLVED 2026-03-28** -- Renamed to `Community_Engagement`. All config, M code, script, and doc references updated. Task Scheduler XML needs manual re-import. See `rename_log_Community_Engagment.md`.

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
- **~~Dual ETL ambiguity~~**: RESOLVED 2026-03-28. Decision: `summons_etl_enhanced.py` is authoritative. Action: `SummonsMaster_Simple.py` moved to `archive/deprecated/SummonsMaster_Simple_DEPRECATED_2026-03-28.py`. Full diff analysis: `02_ETL_Scripts/Summons/docs/etl-diff-analysis.md`. Follow-up needed: port PEO/Class I reclassification rule (`apply_peo_rule()`) to enhanced script.

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
| CRITICAL | 1 | Community_Engagement (dir rename) ~~, Summons (dual ETL -- RESOLVED 2026-03-28)~~ |
| HIGH | 12 | All 6 repos |
| MEDIUM | 15 | All 6 repos |
| LOW | 9 | All 6 repos |
| **TOTAL** | **38** | |

---

## Status Tracking

### Resolved This Session (swarm run 2026-03-28)
- [x] Benchmark PII CSV — added to .gitignore (2026-03-28)
- [x] Community_Engagement production_config.json — removed from git tracking (2026-03-28)
- [x] Community_Engagement directory typo — rename completed (Decision 1, 2026-03-28)
- [x] Summons dual-ETL ambiguity — resolved, summons_etl_enhanced.py is authoritative (Decision 2, 2026-03-28)

### Resolved This Session (post-swarm manual 2026-03-28)
- [x] STOP Flag 1 — Task Scheduler: No scheduled tasks referenced Community_Engagment — confirmed clean (2026-03-28)
- [x] STOP Flag 2 — Power BI .pbix: `___Combined_Outreach_All` OutputFolder typo fixed via Claude Desktop MCP (`Community_Engagment` → `Community_Engagement`). Saved. (2026-03-28)
- [x] STOP Flag 3 — VS Code workspace: `Community_Engagment.code-workspace` renamed to `Community_Engagement.code-workspace` in `02_ETL_Scripts/Community_Engagement/` (2026-03-28)
- [x] Summons: `apply_peo_rule()` ported from SummonsMaster_Simple.py to summons_etl_enhanced.py — PEO/Class I M→P reclassification. Validated with synthetic test (2026-03-28)
- [x] Summons: Power BI column schema verified — WG1, WG2 present; WG3, WG4, WG5, TEAM **missing** from slim CSV and PBI (only existed in deprecated script's ASSIGNMENT_OVERRIDES). Documented in Summons CLAUDE.md (2026-03-28)
- [x] Policy_Training_Monthly: GitHub remote created and pushed to `racmac57/Policy_Training_Monthly` (2026-03-28)

### Pending — Human Confirmation Required
- [ ] **Badge 0388 (LIGGIO)** — was hardcoded in deprecated SummonsMaster_Simple.py (Patrol Bureau / Platoon A / A3). Not in summons_etl_enhanced.py or Assignment_Master_V2.csv. RAC must confirm: is LIGGIO still on this assignment? Should badge be added to Assignment Master?
- [x] ~~**Power BI OutputFolder path**~~ — RESOLVED via Claude Desktop MCP (2026-03-28)
- [ ] **WG3/WG4/WG5/TEAM columns** — missing from enhanced ETL pipeline and Power BI. If sub-bureau granularity is needed, these must be added to summons_etl_normalize.py output and PBI M code.
- [ ] **02_ETL_Scripts parent repo** — needs GitHub remote created (`racmac57/ETL_Scripts` — `gh` CLI not installed, cannot create from CLI). Contains Benchmark and Response_Times commits.

### Queued for Next Session (HIGH)
- [ ] Community_Engagement: CSB config inconsistency (sheet_name mismatch) — QUEUED, see TODO.md in repo
- [ ] Community_Engagement: Verify task_schedule.xml registration — QUEUED, see TODO.md in repo
- [ ] Overtime_TimeOff: Assignment_Master_V2 file extension (.xlsx vs .csv) — QUEUED, see TODO.md in repo
- [ ] Overtime_TimeOff: v11 exec() import refactor decision — QUEUED, see TODO.md in repo
- [ ] Overtime_TimeOff: config.json SMTP exposure review — QUEUED, see TODO.md in repo
- [ ] Policy_Training_Monthly: Legacy M code retirement (5 files) — QUEUED, see TODO.md in repo
- [ ] Policy_Training_Monthly: .git/Training_Matrix.csv removal — QUEUED, see TODO.md in repo
- [ ] Response_Times: Confirm production script — QUEUED, see TODO.md in repo
- [ ] Response_Times: Review ~80 scripts in scripts/ — QUEUED, see TODO.md in repo
- [ ] Summons: Approve root cleanup (~130 files) — QUEUED, see TODO.md in repo

### Backlog (MEDIUM/LOW)
- Benchmark: 3 MEDIUM, 1 LOW
- Community_Engagement: 3 MEDIUM, 1 LOW
- Overtime_TimeOff: 2 MEDIUM, 1 LOW
- Policy_Training_Monthly: 3 MEDIUM, 2 LOW
- Response_Times: 3 MEDIUM, 1 LOW
- Summons: 3 MEDIUM, 1 LOW

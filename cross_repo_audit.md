# Cross-Repository Audit Report
## Run Date: 2026-03-28

## Aggregate Statistics

| Metric | Benchmark | Community_Engagement | Overtime_TimeOff | Policy_Training_Monthly | Response_Times | Summons | TOTAL |
|--------|-----------|---------------------|------------------|-------------------------|----------------|---------|-------|
| Files Created | 7 | 8 | 8 | 10 | 12 | 5 | **50** |
| Files Updated | 4 | 3 | 3 | 1 | 0 | 6 | **17** |
| Dead Scripts | 3 | 7 | 19 | 5 | 91 | 77 | **202** |
| Orphaned Files | 5 | 12 | 30 | 11 | 12 | 15 | **85** |
| Doc Inconsistencies | 4 | 4 | 6 | 6 | 5 | 8 | **33** |
| Reorganization Proposals | 5 | 9 | 7 | 6 | 10 | 9 | **46** |
| Security Flags | 1 | 2 | 2 | 0 | 0 | 0 | **5** |
| Human Review Items | 5 | 7 | 6 | 7 | 6 | 7 | **38** |

### Dead Script Severity
- **Response_Times**: 91 dead scripts (worst offender -- `scripts/` directory alone has ~80 dead files)
- **Summons**: 77 dead scripts (75 dead Python scripts + 2 dead batch files)
- **Overtime_TimeOff**: 19 dead scripts (12 pre-v10 iterations + 7 one-off utilities)
- **Community_Engagement**: 7 dead scripts (debug/scaffold utilities)
- **Policy_Training_Monthly**: 5 dead scripts (legacy M code)
- **Benchmark**: 3 dead scripts (DAX/M referencing defunct tables)

---

## Naming Convention Consistency

### File Naming Patterns

| Pattern | Repos Using It | Notes |
|---------|---------------|-------|
| `YYYY_MM_DD_description.ext` | None consistently | Documented as standard but not uniformly applied |
| `snake_case.py` | All 6 | Python scripts consistently use snake_case |
| `PascalCase.py` | Summons (`SummonsMaster_Simple.py`) | Outlier -- most repos use snake_case |
| `SCREAMING_CASE.md` | All 6 (`CLAUDE.md`, `README.md`, `CHANGELOG.md`) | Standard docs consistently uppercased |
| `mixed_Case.m` | All with M code | M code files vary: `benchmark_r13.m` vs `ResponseTimeCalculator.m` vs `Combined_Outreach_All.m` |

### Config File Naming

| Repo | Config Format | File |
|------|--------------|------|
| Community_Engagement | JSON | `config.json`, `production_config.json` |
| Overtime_TimeOff | JSON | `config.json` |
| Policy_Training_Monthly | YAML | `configs/config.yaml` |
| Summons | YAML (stale) | `config.yaml`, `emergency_config.yaml` (neither loaded by active scripts) |
| Response_Times | JSON (in config/) | Uses `response_time_filters.json` via parent workspace |
| Benchmark | None | No config file |
| 06_Workspace_Management | JSON | `config/scripts.json`, `config.json` |

**Finding:** Mixed JSON/YAML config formats. Policy_Training_Monthly is the only repo actively using YAML. Summons has stale YAML configs that nothing loads.

### Documentation File Naming

| File | All 6 Repos? | Notes |
|------|-------------|-------|
| `CLAUDE.md` | Yes (all UPPERCASE) | Consistent |
| `README.md` | Yes | Consistent |
| `CHANGELOG.md` | Yes | Consistent |
| `SUMMARY.md` | Yes | Consistent |
| `CONTRIBUTING.md` | Yes | All created during this swarm run |
| `reorganization_proposal.md` | Yes | Consistent lowercase |
| `findings.json` | Yes | All created during this swarm run |

### Directory Name Issues

| Issue | Repo | Severity |
|-------|------|----------|
| ~~`Community_Engagment` (missing 'e')~~ | Community_Engagement | ~~CRITICAL~~ RESOLVED 2026-03-28 -- renamed, all refs updated |

---

## CLAUDE.md Completeness Matrix

Required sections: Purpose, File Inventory, ETL Pipeline, Dependencies, Business Logic, Known Issues

| Section | Benchmark | Community_Engagement | Overtime_TimeOff | Policy_Training_Monthly | Response_Times | Summons |
|---------|-----------|---------------------|------------------|-------------------------|----------------|---------|
| Purpose | Yes | Yes (numbered) | Yes | Yes | Yes | Yes |
| File Inventory | Yes | Yes (numbered) | Yes | Yes | Partial (active only) | Yes |
| ETL Pipeline | Yes | Yes (numbered) | Yes | Yes | Yes (as "Data Flow") | Yes |
| Dependencies | Yes | Implicit in pipeline | Yes | Yes | Yes | Yes |
| Business Logic | Yes | Yes (numbered) | Yes | Yes | Yes | Yes |
| Known Issues | Yes (as "Gotchas") | Yes (numbered) | Yes | Yes (split: Gotchas + Tech Debt) | Yes | Yes |
| Path Resolution | Implicit | Yes (numbered) | Implicit (Key Paths table) | Implicit | Implicit | Yes |
| Running Instructions | Yes (Monthly Maintenance) | Yes (numbered) | Implicit (batch files) | Implicit (run_etl.bat) | Missing | Yes |

### Structural Differences

- **Community_Engagement**: Uses numbered sections (1-10), most detailed with Output Schema and Architecture diagram
- **Summons**: Most comprehensive overall -- includes Validation Checklist, Safe Editing Rules, Common User Questions
- **Response_Times**: Leanest -- no explicit dependency section or running instructions
- **Benchmark**: Includes External Documentation section (cross-references 06_Workspace_Management docs)
- **Overtime_TimeOff**: Includes Repository & Remote info and Tech Stack (unique)
- **Policy_Training_Monthly**: Includes Domain Context section (unique)

### Missing Sections by Repo

| Repo | Missing |
|------|---------|
| Response_Times | Running instructions, explicit dependency table |
| Benchmark | Tech stack, path resolution section |
| Overtime_TimeOff | Explicit numbered structure, path resolution rules |
| Policy_Training_Monthly | Path resolution rules (implicit only) |

---

## .gitignore Pattern Comparison

### Coverage Matrix

| Pattern Category | 06_WM | Benchmark | Community_Engagement | Overtime_TimeOff | Policy_Training_Monthly | Response_Times | Summons |
|-----------------|-------|-----------|---------------------|------------------|-------------------------|----------------|---------|
| `__pycache__/` | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| `*.py[cod]` | Yes | Yes | Yes | Yes (codz) | Yes | Yes | Yes (codz) |
| Virtual envs | Yes | Yes | No | Yes | Yes | No | Yes |
| `.vscode/` | Yes | Yes | Yes | No | Yes | No | No |
| `*.code-workspace` | Yes | No | Yes | Yes | No | No | No |
| `Thumbs.db` | Yes | Yes | No | No | Yes | No | No |
| `.DS_Store` | Yes | No | No | No | Yes | No | No |
| Output dirs | Yes | No | Yes | Yes | No | Yes | Yes |
| `*.log` | Yes | No | No | Yes (partial) | Yes (partial) | Yes | Yes |
| Data files (`*.csv`, `*.xlsx`) | Yes (partial) | No | No | Yes | No | Yes (partial) | Yes |
| OneDrive dupes `*(1).*` | No | No | Yes | No | Yes | No | No |
| `nppBackup/` | No | No | No | No | No | Yes | No |
| Config backups | Yes | No | Yes | No | No | No | No |
| Temp files | Yes | No | Yes | No | No | No | No |
| `*.bak` | Yes | No | No | No | No | No | No |
| Dist/packaging | No | Yes | No | Yes | Yes | Yes | Yes |

### Key Gaps

| Gap | Repos Affected | Risk |
|-----|---------------|------|
| No .gitignore at all | None (all have one now) | Resolved by swarm agents |
| Missing output directory ignores | Benchmark | Data files could be committed |
| Missing `*.log` ignores | Benchmark, Community_Engagement | Log files tracked in git |
| Missing OneDrive dupe pattern | Benchmark, Overtime_TimeOff, Response_Times, Summons, 06_WM | `(1)` files not auto-ignored |
| Missing virtual env ignores | Community_Engagement, Response_Times | venv could be committed |
| No data file ignores | Benchmark, Community_Engagement | CSVs/XLSX tracked unnecessarily |
| Overtime_TimeOff uses comprehensive template | Overtime_TimeOff, Summons | Over-broad: may ignore files that should be tracked |

### Recommendations

1. Standardize on a common `.gitignore` base template across all 6 repos
2. All repos should ignore: `__pycache__/`, `*.py[cod]`, `.venv/`, `*.log`, `output/`, `Thumbs.db`, `.DS_Store`, `*.code-workspace`, `*(1).*` (OneDrive dupes)
3. Add repo-specific patterns as needed on top of the base

---

## Python Dependency Analysis

### Declared Dependencies

| Repo | requirements.txt | Declared Deps |
|------|-----------------|---------------|
| Benchmark | Missing | None declared (no Python ETL in this repo) |
| Community_Engagement | Missing | README references it but file does not exist. Needs: pandas, openpyxl, pytz |
| Overtime_TimeOff | Missing | Needs: pandas, openpyxl, python-dateutil |
| Policy_Training_Monthly | Present | pandas>=2.2, openpyxl>=3.1, pyyaml>=6.0, pytest>=8.0 |
| Response_Times | Missing | Needs: pandas, openpyxl |
| Summons | Missing | Needs: pandas, openpyxl; summons_etl_enhanced.py also needs fuzzywuzzy |
| 06_Workspace_Management | Present | pandas, openpyxl, pathlib, pyyaml, watchdog (in root requirements.txt) |

### Common Dependencies Across All Repos

| Package | Used By | Version Pinned? |
|---------|---------|----------------|
| pandas | All 6 | Only Policy_Training_Monthly (>=2.2) |
| openpyxl | All 6 | Only Policy_Training_Monthly (>=3.1) |
| pytz | Community_Engagement | Not pinned anywhere |
| pyyaml | Policy_Training_Monthly, 06_WM | Policy_Training (>=6.0), 06_WM (no version) |
| python-dateutil | Overtime_TimeOff | Not pinned |
| fuzzywuzzy | Summons (optional) | Not pinned, not in any requirements.txt |
| pytest | Policy_Training_Monthly | >=8.0 |
| watchdog | 06_WM | No version pin |

### Issues

1. **5 of 6 repos have no requirements.txt** -- only Policy_Training_Monthly declares dependencies
2. **No version pinning** outside Policy_Training_Monthly
3. **Community_Engagement README references `pip install -r requirements.txt`** but the file does not exist
4. **fuzzywuzzy** in Summons is undeclared and may require `python-Levenshtein` for performance
5. **sys.path.append() hacks** used in Community_Engagement processors instead of proper package structure

---

## Documentation Format Drift

### README.md Structure Comparison

| Element | Benchmark | Community_Engagement | Overtime_TimeOff | Policy_Training_Monthly | Response_Times | Summons |
|---------|-----------|---------------------|------------------|-------------------------|----------------|---------|
| Title style | `# Benchmark ETL` | `Community Engagement ETL` (rst-style underline) | `# Overtime_TimeOff` | `# Policy Training Monthly ETL` | `# Response Times ETL Pipeline` | `# Summons ETL Scripts` |
| Status badge/line | Yes (inline) | No | No | Yes (blockquote) | No | No |
| Quick Start | No | Yes (Overview) | Yes | Yes | Yes | Yes |
| File structure tree | No | Yes | No | Yes | No | No |
| Prerequisites | No | No | No | Yes | No | No |

**Finding:** README title formatting varies -- one uses RST-style underlines (Community_Engagement), rest use ATX-style `#` headers. Content depth varies significantly.

### CHANGELOG.md Format Comparison

| Element | Benchmark | Community_Engagement | Overtime_TimeOff | Policy_Training_Monthly | Response_Times | Summons |
|---------|-----------|---------------------|------------------|-------------------------|----------------|---------|
| KaC reference | Yes | Yes | No | No | No | No |
| Version format | `[1.2.0]` | `[2026-03-28]` | `[2026-03-28]` | `[1.0.0]` | `2026-03-28` | `2026-03-28` |
| Uses semver | Yes | No (date-based) | No (date-based) | Yes | No (date-based) | No (date-based) |

**Finding:** Mixed versioning -- Benchmark and Policy_Training_Monthly use semver; others use date-based entries. Only 2 of 6 reference Keep a Changelog.

### Additional Documentation Files

| File | Present In |
|------|-----------|
| `SUMMARY.md` | All 6 |
| `CONTRIBUTING.md` | All 6 (created by swarm) |
| `reorganization_proposal.md` | All 6 (created by swarm) |
| `DOCUMENTATION_INDEX.md` | Overtime_TimeOff only |
| `docs/etl-pipeline.md` | All 6 (created by swarm) |
| `docs/file-inventory.md` | All 6 (created by swarm) |
| `docs/config-reference.md` | All 6 (created by swarm) |
| `PYTHON_WORKSPACE_AI_GUIDE.md` | Community_Engagement, Overtime_TimeOff, Policy_Training_Monthly |
| `PYTHON_WORKSPACE_TEMPLATE.md` | Community_Engagement, Overtime_TimeOff, Policy_Training_Monthly |

**Finding:** `PYTHON_WORKSPACE_AI_GUIDE.md` and `PYTHON_WORKSPACE_TEMPLATE.md` are generic templates present in 3 repos. These should be moved to `08_Templates/` or deleted.

---

## Shared Resource Dependencies

### Assignment_Master_V2

| Repo | Path Used | Format |
|------|----------|--------|
| Overtime_TimeOff | `09_Reference/Personnel/Assignment_Master_V2.csv` | CSV |
| Summons (primary) | `09_Reference/Personnel/Assignment_Master_V2.csv` | CSV |
| Summons (backfill) | `06_Workspace_Management/Assignment_Master_V2.csv` | CSV |
| 06_Workspace_Management | `./Assignment_Master_V2.csv` (local copy) | CSV |

**Issue:** `summons_backfill_13month.py` references the copy at `06_Workspace_Management/` instead of the canonical `09_Reference/Personnel/` location. Two copies exist, risk of divergence.

### Shared Export Paths

| Path | Used By |
|------|---------|
| `05_EXPORTS/_Benchmark/` | Benchmark |
| `05_EXPORTS/_CAD/timereport/` | Response_Times |
| `05_EXPORTS/_Overtime/` | Overtime_TimeOff |
| `05_EXPORTS/_Time_Off/` | Overtime_TimeOff |
| `05_EXPORTS/_Summons/E_Ticket/` | Summons |
| `03_Staging/Summons/` | Summons output |
| `PowerBI_Data/_DropExports/` | 06_Workspace_Management (process_powerbi_exports.py) |
| `PowerBI_Data/Backfill/` | Overtime_TimeOff, Summons, Response_Times |

### External Path Dependencies (Outside OneDrive)

| Path | Used By | Status |
|------|---------|--------|
| `C:\Dev\PowerBI_Data\Backfill\` | Overtime_TimeOff, Summons (`process_monthly_summons.py`) | May not exist on production machine |
| `C:\Dev\Power_BI_Data\tools\` | Policy_Training_Monthly | Optional (graceful fallback) |

---

## Security Flags (All Repos)

| Repo | Flag | Severity |
|------|------|----------|
| Benchmark | `benchmark_preview_table.csv` contains officer names, badge numbers, incident details (PII/LE sensitive) | HIGH |
| Community_Engagement | `production_config.json` has blank credential fields (SMTP, PBI client_id/secret) | MEDIUM |
| Community_Engagement | `task_schedule.xml` runs as NT AUTHORITY\SYSTEM | LOW |
| Overtime_TimeOff | `config.json` contains SMTP password field (currently empty) | MEDIUM |
| Overtime_TimeOff | `config.json` committed before .gitignore was added | MEDIUM |
| Summons | ASSIGNMENT_OVERRIDES contains officer names/badge numbers (personnel data) | LOW |

### Recommendations

1. Add `benchmark_preview_table.csv` to Benchmark `.gitignore` immediately
2. Add `production_config.json` to Community_Engagement `.gitignore`
3. Ensure no config files with credential fields are committed with real values
4. Consider `.gitignore`-ing all `config.json` files across repos and providing `config.json.example` templates

---

## Recommendations

### Priority 1 -- Critical (Act Now)

1. ~~**Rename `Community_Engagment` to `Community_Engagement`**~~ -- **RESOLVED 2026-03-28**. All downstream refs updated. Task Scheduler needs manual re-import.
2. **Add PII files to .gitignore** -- `benchmark_preview_table.csv` in Benchmark, `production_config.json` in Community_Engagement
3. **Create requirements.txt** for 5 repos missing it (Benchmark exempt -- no Python ETL)

### Priority 2 -- High (This Sprint)

4. **Standardize .gitignore** -- create a base template and apply to all repos
5. **Execute reorganization proposals** -- 202 dead scripts and 85 orphaned files across 6 repos. Response_Times and Summons are the worst.
6. **Consolidate Assignment_Master_V2 references** -- all repos should use `09_Reference/Personnel/Assignment_Master_V2.csv`; remove the copy at `06_Workspace_Management/`
7. **Resolve dual-ETL ambiguity in Summons** -- clarify whether `SummonsMaster_Simple.py` or `summons_etl_enhanced.py` is authoritative

### Priority 3 -- Medium (Next Cycle)

8. **Standardize CHANGELOG format** -- adopt Keep a Changelog + semver across all repos
9. **Standardize README structure** -- all should use ATX-style `#` headers, include Quick Start, Prerequisites, File Structure
10. **Standardize CLAUDE.md sections** -- define required sections: Purpose, File Inventory, ETL Pipeline, Dependencies, Business Logic, Known Issues, Running Instructions, Path Resolution
11. **Remove generic templates** -- move `PYTHON_WORKSPACE_AI_GUIDE.md` and `PYTHON_WORKSPACE_TEMPLATE.md` from individual repos to `08_Templates/`
12. **Add OneDrive dupe pattern to all .gitignore files** -- `*(1).*` pattern

### Priority 4 -- Low (Backlog)

13. **Add unit tests** -- Policy_Training_Monthly has minimal coverage; others have none
14. **Eliminate `sys.path.append()` hacks** in Community_Engagement
15. **Consolidate DAX files** in Response_Times (3 files referencing different table names)
16. **Standardize config format** -- decide JSON vs YAML and stick with it
17. **Remove 0-byte junk files** across repos (`#`, `cd`, `echo`, `python`, `_ul`, `cutoff]`, `10)`, `120`)

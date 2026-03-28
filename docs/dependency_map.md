# Master Dependency Map
## Generated: 2026-03-28

---

## Cross-Repo Dependencies

| Source Repo | File/Variable | Referenced By | Type | Risk if Changed |
|-------------|--------------|---------------|------|-----------------|
| 09_Reference/Personnel | `Assignment_Master_V2.csv` | Summons (`summons_etl_enhanced.py`, `SummonsMaster.py`, `SummonsMaster_Transition.py`, `create_clean_output.py`), Overtime_TimeOff (`v10.py`) | Lookup (badge->name, bureau, sworn/nonsworn) | **HIGH** -- breaks officer display names, bureau assignment, sworn classification in 2 dashboards |
| 09_Reference/Personnel | `Assignment_Master_V2.xlsx` | Overtime_TimeOff (`v10.py` line 26) | Lookup (xlsx variant for sworn/nonsworn) | **HIGH** -- OT pipeline uses xlsx; Summons uses csv; must keep both in sync |
| 06_Workspace_Management | `Assignment_Master_V2.csv` (local copy) | Summons (`summons_backfill_13month.py` line 22) | Fallback lookup | **MEDIUM** -- divergence risk vs canonical 09_Reference copy; `summons_etl_enhanced.py` prefers 09_Reference with fallback to this |
| 09_Reference/Classifications/CallTypes | `CallType_Categories.csv` | Response_Times (`response_time_batch_all_metrics.py`, `response_time_monthly_generator.py`) | Incident-to-ResponseType mapping | **HIGH** -- unmapped incidents cause data gaps in response time dashboard |
| 09_Reference/Classifications/CallTypes | `CallType_Categories.xlsx` | Response_Times M code (`monthly_summary_etl_*.m`) | Same mapping for Power Query | **MEDIUM** -- legacy M code only |
| 09_Reference/LegalCodes/data | legal code files | Summons (`update_dfr_violation_lookup.py` line 25) | Statute-to-violation mapping | **MEDIUM** -- affects DFR violation descriptions |
| 09_Reference/GeographicData/ZipCodes | `uszips.csv` | 06_Workspace_Management M code (`2026_03_09_all_queries.m` line 214) | ZIP code reference for arrest geolocation | **LOW** -- static reference data |
| 06_Workspace_Management/scripts | `path_config.py` | Summons (`summons_etl_enhanced.py` lines 22-28), 06_WM (`etl_orchestrator.py` line 47), 06_WM (`run_summons_etl.py` line 18) | Path resolution (`get_onedrive_root()`) | **HIGH** -- single source of truth for OneDrive root; all path resolution depends on this |
| 06_Workspace_Management/scripts | `summons_etl_normalize.py` | 06_WM (`run_summons_etl.py` line 19) | Summons normalization, DFR split | **HIGH** -- dual entry point: both `02_ETL_Scripts/Summons/summons_etl_enhanced.py` and `06_WM/run_summons_etl.py` process summons |
| 06_Workspace_Management/scripts | `summons_backfill_merge.py` | 06_WM (`run_summons_etl.py` line 64), Summons (`enhanced_monthly_summons_etl.py` sys.path) | Gap-month backfill merge | **MEDIUM** -- used by 06_WM wrapper |
| 06_Workspace_Management/scripts | `dfr_export.py` | 06_WM (`run_summons_etl.py` line 26) | DFR workbook export | **MEDIUM** |
| 06_Workspace_Management/config | `response_time_filters.json` | Response_Times (`response_time_monthly_generator.py` line 59) | JSON filter rules for response time | **MEDIUM** -- hardcoded default path in Response_Times repo |
| 06_Workspace_Management/config | `scripts.json` | 06_WM (`etl_orchestrator.py` line 57), 06_WM/scripts (`path_config.py` line 62) | Master ETL config: paths, scripts, profiles | **CRITICAL** -- orchestrator config for all 5+ pipelines |
| 06_Workspace_Management | `config.json` (root) | 06_WM/scripts (`path_config.py` line 38) | PowerBI folder name override | **LOW** -- optional; defaults to `PowerBI_Data` |

## Shared Output Paths

| Path | Written By | Read By | Collision Risk |
|------|-----------|---------|---------------|
| `03_Staging/Summons/summons_powerbi_latest.xlsx` | Summons (`summons_etl_enhanced.py`), 06_WM (`run_summons_etl.py`) | Power BI M code (6 summons queries in `2026_03_09_all_queries.m`) | **HIGH** -- two scripts write the same file; last-write-wins if both run |
| `03_Staging/Summons/summons_slim_for_powerbi.csv` | 06_WM (`run_summons_etl.py` via `write_three_tier_output`) | Power BI M code (`2026_03_09_all_queries.m` -- 5 queries read this CSV) | **MEDIUM** -- newer M code prefers this slim CSV over the xlsx |
| `PowerBI_Data/response_time_all_metrics/` | Response_Times (`response_time_batch_all_metrics.py`) | Power BI (`Folder.Files()` pattern) | **LOW** -- single writer |
| `PowerBI_Data/Backfill/YYYY_MM/response_time/` | Response_Times (`response_time_monthly_generator.py`) | Power BI (legacy backfill path) | **LOW** -- legacy path |
| `PowerBI_Data/_DropExports/` | Community_Engagement (config output_directory), 06_WM (`process_powerbi_exports.py` reads) | 06_WM (`process_powerbi_exports.py` routes to Processed_Exports) | **MEDIUM** -- shared drop zone; routing logic must recognize all formats |
| `02_ETL_Scripts/Overtime_TimeOff/analytics_output/monthly_breakdown.csv` | Overtime_TimeOff (`v10.py`) | Power BI M code (`overtime_timeoff.m`) | **LOW** -- single writer |
| `02_ETL_Scripts/Overtime_TimeOff/output/FIXED_monthly_breakdown_*.csv` | Overtime_TimeOff (`v10.py`) | Power BI M code (`overtime_timeoff.m`) | **LOW** -- single writer |
| `02_ETL_Scripts/Policy_Training_Monthly/output/policy_training_outputs.xlsx` | Policy_Training_Monthly (`policy_training_etl.py`) | Power BI M code (Training_Log.m, Training_Matrix.m, etc.) | **LOW** -- single writer |
| `05_EXPORTS/_Benchmark/by_time_period/rolling_13month/current_window.csv` | Benchmark (`benchmark_restructure.py` via 06_WM) | Benchmark M code (`benchmark_r13.m`) | **LOW** -- single writer |
| `05_EXPORTS/_Summons/E_Ticket/` | External (manual drop) | Summons (`summons_etl_enhanced.py`), 06_WM (`run_summons_etl.py`) | **LOW** -- read-only by ETL |
| `05_EXPORTS/_Overtime/` | External (manual drop) | Overtime_TimeOff (`v10.py`) | **LOW** -- read-only by ETL |
| `05_EXPORTS/_Time_Off/` | External (manual drop) | Overtime_TimeOff (`v10.py`) | **LOW** -- read-only by ETL |
| `05_EXPORTS/_CAD/timereport/` | External (manual drop) | Response_Times (`response_time_batch_all_metrics.py`, `response_time_monthly_generator.py`) | **LOW** -- read-only by ETL |
| `Shared Folder/Compstat/Contributions/Drone/dfr_directed_patrol_enforcement.xlsx` | Summons (`summons_etl_enhanced.py`), 06_WM (`run_summons_etl.py` via `dfr_export.py`) | Power BI (`DFR_Summons.m`) | **MEDIUM** -- two scripts can write; shared Excel workbook |

## Cross-Repo Script Reads

| Reader Script (Repo) | Reads From (Repo/Path) | Purpose |
|----------------------|----------------------|---------|
| `summons_etl_enhanced.py` (Summons) | `06_Workspace_Management/scripts/path_config.py` | Imports `get_onedrive_root()` for portable path resolution via `sys.path.insert` |
| `summons_etl_enhanced.py` (Summons) | `09_Reference/Personnel/Assignment_Master_V2.csv` (primary), `06_Workspace_Management/Assignment_Master_V2.csv` (fallback) | Officer badge-to-name/bureau lookup |
| `summons_backfill_13month.py` (Summons) | `06_Workspace_Management/Assignment_Master_V2.csv` | Badge lookup (uses 06_WM copy, NOT canonical 09_Reference) |
| `run_summons_etl.py` (06_WM) | `09_Reference/Personnel/Assignment_Master_V2.csv` | Officer assignment lookup |
| `run_summons_etl.py` (06_WM) | `05_EXPORTS/_Summons/E_Ticket/` | E-ticket CSV source data |
| `etl_orchestrator.py` (06_WM) | `02_ETL_Scripts/Overtime_TimeOff/output/` | Checks OT ETL output existence for validation |
| `response_time_monthly_generator.py` (Response_Times) | `06_Workspace_Management/config/response_time_filters.json` | Filter configuration for response time calculations |
| `response_time_batch_all_metrics.py` (Response_Times) | `09_Reference/Classifications/CallTypes/CallType_Categories.csv` | Incident-to-ResponseType mapping |
| `overtime_timeoff_v10.py` (Overtime_TimeOff) | `09_Reference/Personnel/Assignment_Master_V2.xlsx` | Sworn/NonSworn classification |
| `investigate_december_high_values.py` (Overtime_TimeOff) | `06_Workspace_Management/output/2026_01_13_*.csv` | Cross-repo CSV read for investigation |
| `update_dfr_violation_lookup.py` (Summons) | `09_Reference/LegalCodes/data/` | Legal code lookup for DFR violations |
| `SummonsMaster.py` (Summons) | `09_Reference/Personnel/Assignment_Master_V2.csv` | Officer assignment lookup |
| Power BI M code (06_WM `2026_03_09_all_queries.m`) | `03_Staging/Summons/summons_slim_for_powerbi.csv` | Summons ETL output consumed by 5+ Power BI queries |
| Power BI M code (06_WM `2026_03_09_all_queries.m`) | `05_EXPORTS/Benchmark/` | Benchmark AG compliance data |
| Power BI M code (06_WM `2026_03_09_all_queries.m`) | `05_EXPORTS/_CAD/tas/yearly/` | TAS dispatcher incident data |
| Power BI M code (06_WM `2026_03_09_all_queries.m`) | `09_Reference/GeographicData/ZipCodes/uszips.csv` | ZIP code lookups for arrest geolocation |
| Community_Engagement M code (`Combined_Outreach_All.m`) | `02_ETL_Scripts/Community_Engagement/output/` | Latest CSV discovery via `Folder.Files()` pattern |

## Shared Config Variables

| Variable/Key | Repos Using It | Defined Where | Notes |
|-------------|---------------|---------------|-------|
| `ONEDRIVE_BASE` / `ONEDRIVE_HACKENSACK` | Summons (fallback), 06_WM (`path_config.py`), Response_Times (via path_config) | Environment variable (optional) | `path_config.get_onedrive_root()` checks these first; fallback to `C:\Users\carucci_r\OneDrive - City of Hackensack` |
| `pReportMonth` | 06_WM M code (47+ queries), Benchmark M code (via 06_WM), Summons M code (via 06_WM) | Power BI parameter (set per `.pbix`) | Controls rolling 13-month windows in ALL Power Query M code; NOT valid in DAX |
| `powerbi_drop_path` | 06_WM (`scripts.json`), 06_WM (`path_config.py`) | `06_WM/config/scripts.json` `settings.powerbi_drop_path` | Defines `PowerBI_Data/_DropExports` path; used by orchestrator and export processing |
| `PD_BCI_LTP` (profile key) | 06_WM (`etl_orchestrator.py` line 59, `scripts.json` entries) | `06_WM/config/scripts.json` meta | Machine-specific override profile that swaps script paths for laptop vs desktop |
| SMTP settings (`smtp_server`, `smtp_port`) | Overtime_TimeOff (`comprehensive_police_analytics.py`, `refactored_scripts.py`), Community_Engagement (`deploy_production.py`) | Per-repo `config.json` / inline | `smtp.office365.com:587` in Community_Engagement; blank placeholders in OT |
| `carucci_r` base path | ALL repos | Hardcoded in scripts + configs | Canonical form `C:\Users\carucci_r\OneDrive - City of Hackensack`; laptop resolves via junction. NEVER change to `RobertCarucci`. |
| `rolling_months: 13` | Community_Engagement (`config.json`), Policy_Training_Monthly (`config.yaml`), Response_Times (hardcoded), Summons (hardcoded), Overtime_TimeOff (hardcoded) | Per-repo config or constants | Universal 13-month rolling window convention; not centralized |
| `config.json` (per-repo) | Community_Engagement, Summons (`summons_etl_enhanced.py` default arg) | Per-repo root | Different schemas per repo; not interchangeable |
| `config.yaml` | Policy_Training_Monthly, Summons (stale/unused) | Per-repo `configs/` or root | Policy_Training is the only active YAML consumer |

## Fragile Dependencies

### 1. Dual Summons Entry Points (COLLISION RISK)
Both `02_ETL_Scripts/Summons/summons_etl_enhanced.py` and `06_Workspace_Management/run_summons_etl.py` write to `03_Staging/Summons/summons_powerbi_latest.xlsx`. They use different normalization pipelines (inline vs `summons_etl_normalize.py`). Running both produces last-write-wins output with potentially different schemas.

**Recommendation:** Designate one as canonical and disable or redirect the other.

### 2. Assignment Master Copy Divergence
Two copies of `Assignment_Master_V2.csv` exist:
- `09_Reference/Personnel/Assignment_Master_V2.csv` (canonical)
- `06_Workspace_Management/Assignment_Master_V2.csv` (local copy)

`summons_backfill_13month.py` uses the 06_WM copy exclusively (line 22). `summons_etl_enhanced.py` prefers 09_Reference with silent fallback to 06_WM. If the copies diverge, backfill and current-month data will use different officer assignments.

**Recommendation:** Delete the 06_WM copy; update `summons_backfill_13month.py` to point to `09_Reference/Personnel/`.

### 3. Assignment Master Format Split (CSV vs XLSX)
- Summons repos reference `Assignment_Master_V2.csv`
- Overtime_TimeOff `v10.py` references `Assignment_Master_V2.xlsx`

If only one format is updated, the other pipeline gets stale data.

**Recommendation:** Standardize on one format or add a sync check.

### 4. path_config.py -- Single Point of Failure
`06_Workspace_Management/scripts/path_config.py` is the sole source of `get_onedrive_root()`. It is imported by:
- `summons_etl_enhanced.py` (via `sys.path` hack to `06_WM/scripts/`)
- `etl_orchestrator.py`
- `run_summons_etl.py`

If this file is moved, renamed, or broken, both the orchestrator and Summons ETL fail.

### 5. sys.path Cross-Repo Hacks
`summons_etl_enhanced.py` (line 22-24) injects `06_Workspace_Management/scripts/` into `sys.path` at runtime. This creates an undocumented import-time dependency that is invisible to package managers, linters, and IDE tooling. Moving the Summons repo to a different relative position breaks the import.

### 6. Hardcoded Paths Without path_config
Several scripts bypass `path_config.py` entirely:
- `overtime_timeoff_v10.py`: hardcoded `C:\Users\carucci_r\...` for all paths
- `response_time_batch_all_metrics.py`: hardcoded `BASE = Path(r"C:\Users\carucci_r\...")`
- `summons_backfill_13month.py`: hardcoded `BASE = Path(r"C:\Users\carucci_r\...")`

These will fail on any machine without the `carucci_r` junction.

### 7. M Code Path Inconsistency
`all_m_code_26_january_monthly.m` (legacy) uses `RobertCarucci` paths for summons queries while `2026_03_09_all_queries.m` (current) uses `carucci_r` paths. If the legacy M code is loaded into Power BI, it will fail on the desktop machine (which has `carucci_r` natively).

### 8. scripts.json References Nonexistent Paths
`scripts.json` entry "Response Times Fresh Calculator" references `C:\Users\carucci_r\...\Master_Automation\scripts\response_time_fresh_calculator.py` -- the `Master_Automation` folder does not match the current `06_Workspace_Management` folder name.

### 9. Undocumented 06_WM Output Read by Overtime_TimeOff
`investigate_december_high_values.py` in Overtime_TimeOff reads a specific timestamped CSV from `06_Workspace_Management/output/`. This is a one-off debug script but illustrates that ad-hoc cross-repo reads exist without formal documentation.

### 10. pReportMonth Not Centrally Enforced
While all 47+ M code queries use `pReportMonth`, it is set per `.pbix` file, not centrally. Each monthly report requires manually setting this parameter. If one query is loaded from a stale `.m` file that still uses `DateTime.LocalNow()`, it will silently produce different windowing.

---

*Generated by cross-repo dependency scan of 7 repositories. Searched all `.py`, `.m`, `.json`, and `.yaml` files (excluding `archive/`, `.git/`, `__pycache__/` where noted). Last scan: 2026-03-28.*

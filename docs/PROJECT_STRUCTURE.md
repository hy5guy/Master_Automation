# 06_Workspace_Management Project Structure

**Last Updated:** 2026-03-25

---

## Directory Structure

```
06_Workspace_Management/
├── README.md                    # Main project documentation
├── CHANGELOG.md                 # Version history (v1.18.0+)
├── SUMMARY.md                   # Project summary / quick reference
├── etl_orchestrator.py          # Python CLI: list, dry-run, run, parse-logs, validate, scorecard
├── run_summons_etl.py           # Summons ETL entry point (multi-year discovery, 3-tier output)
├── config/
│   ├── scripts.json            # ETL script configuration
│   ├── response_time_filters.json  # Response Time filter config
│   └── scripts.json.bak        # Backup configuration
├── scripts/                     # Python + PowerShell scripts
│   ├── run_all_etl.ps1         # PowerShell orchestrator
│   ├── run_all_etl.bat         # Batch wrapper
│   ├── run_etl_script.ps1      # Single script runner
│   ├── path_config.py          # Centralized get_onedrive_root()
│   ├── summons_etl_normalize.py     # Core summons ETL (badge lookup, TYPE classification)
│   ├── summons_backfill_merge.py    # Summons gap-month merge (07-25 only)
│   ├── summons_derived_outputs_simple.py  # Summons derived outputs
│   ├── Pre_Flight_Validation.py     # Pre-flight GO/NO-GO gate
│   ├── overtime_timeoff_with_backfill.py  # OT/TimeOff monthly wrapper
│   └── (validation, comparison, and diagnostic scripts)
├── m_code/                      # Power BI M code queries (47+ queries, 20 page folders)
│   ├── summons/                # summons_13month_trend, all_bureaus, top5_parking, top5_moving
│   ├── arrests/                # ___Arrest_Categories, ___Arrest_Distro, etc.
│   ├── functions/              # fnGetFiles, fnReadCsv, fnEnsureColumns, etc.
│   ├── ssocc/                # ___SSOCC_Data (legacy MoM), FactServiceLog, DimServiceGroup (Option B), TAS_Dispatcher_Incident
│   └── (benchmark, chief, community, csb, detectives, drone, esu, ...)
├── docs/                        # Project documentation
│   ├── ETL_SKILL_MEMORY.md            # etl_orchestrator.py scorecard evidence
│   ├── SSOCC_Service_Log_Excel_And_Power_BI_Rework_2026_03.md  # SSOCC Option B PQ + DAX
│   ├── SUMMONS_DOC_INDEX.md           # Summons doc suite index
│   ├── SUMMONS_BACKFILL_INJECTION_POINT.md  # Backfill merge details
│   ├── PROMPT_Claude_MCP_*.md         # Claude Desktop MCP prompts
│   ├── response_time/                 # Response Time docs and reports
│   ├── chatlogs/                      # Session transcripts
│   └── (migration guides, verification reports, troubleshooting)
├── verifications/               # ETL verification framework
│   ├── reports/                # Verification markdown reports
│   └── (verifier scripts)
├── outputs/                     # Organized output files
│   ├── arrests/, visual_exports/, summons_validation/, metadata/
│   └── large_exports/
└── logs/                        # ETL execution logs (auto-created)
```

---

## Folder Purposes

### `config/`
**Purpose:** Configuration files for ETL scripts
- `scripts.json` - Main configuration (script paths, settings)
- `scripts.json.bak` - Backup of previous configuration

### `scripts/`
**Purpose:** Python ETL scripts and PowerShell orchestration
- `run_all_etl.ps1` - Main PowerShell orchestrator (runs all ETL scripts)
- `run_all_etl.bat` - Batch file wrapper for easy execution
- `run_etl_script.ps1` - Helper to run individual scripts
- `summons_etl_normalize.py` - Core summons ETL: CSV parsing, badge lookup, TYPE classification (M/P/C), 3-tier output
- `summons_backfill_merge.py` - Injects aggregate totals for gap months (currently 07-25 only)
- `path_config.py` - Centralized `get_onedrive_root()` for portability

### `logs/`
**Purpose:** ETL execution logs (auto-created on first run)
- Created automatically by `run_all_etl.ps1`
- Format: `YYYY-MM-DD_HH-MM-SS_ETL_Run.log`
- Individual script logs: `YYYY-MM-DD_HH-MM-SS_[ScriptName].log`

### `docs/`
**Purpose:** Project documentation
- Migration guides
- Verification reports
- Workflow documentation
- Technical documentation
- `SUMMONS_M_CODE_NOTES.md` — Lessons learned for summons M code (AI assistant ref)

**Note:** `README.md` stays in root for GitHub/visibility

### `chatlogs/`
**Purpose:** AI assistant chat logs and conversation history
- Save important conversations here
- Naming: `YYYY-MM-DD_description.md`
- Examples:
  - `2025-12-11_migration_verification.md`
  - `2025-12-11_backfill_paths_discussion.md`
  - `2025-12-11_script_filename_updates.md`

### `_DropExports/`
**Purpose:** Temporary staging area for ETL outputs
- ETL scripts write CSV files here
- Files are then organized by `organize_backfill_exports.ps1`
- Under OneDrive: `PowerBI_Data\_DropExports\` (folder name from `config.json` / `path_config.get_powerbi_data_dir()`)
- A `_DropExports` folder under this repo (if present) is for local testing/staging only; production drop is **`PowerBI_Data\_DropExports`**

---

## File Organization Guidelines

### Markdown Files
- **Root:** Only `README.md` (main entry point)
- **docs/:** All other documentation files
- **chatlogs/:** AI conversation logs

### Configuration Files
- **config/:** All JSON/YAML configuration files
- Keep backups with `.bak` extension

### Scripts
- **scripts/:** All PowerShell/Batch execution scripts
- Keep helper scripts organized by purpose

### Logs
- **logs/:** Auto-created, don't manually create
- Logs are timestamped and can be archived periodically

---

## Chat Log Naming Convention

**Format:** `YYYY-MM-DD_description.md`

**Examples:**
- `2025-12-11_migration_verification.md`
- `2025-12-11_backfill_column_order.md`
- `2025-12-11_etl_script_updates.md`
- `2025-12-11_path_migration.md`

**Best Practices:**
- Use descriptive names
- Include date for chronological sorting
- Group related conversations
- Archive old logs periodically

---

## PowerBI_Data integration

**Note:** The actual `_DropExports` folder used by ETL scripts is located at:
```
C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\_DropExports\
```

A repo-local `_DropExports/` (if you create one) is optional and can be used for:
- Local testing
- Staging before Power BI organization
- Development/testing purposes

**Processed_Exports** (`09_Reference\Standards\Processed_Exports\`): category subfolders should use **lowercase** canonical names (`benchmark`, `drone`, `nibrs`, `patrol`, `summons`, `traffic`, `detectives`, `stacp`, etc.). New exports are routed by `process_powerbi_exports.py` + `visual_export_mapping.json` + `processed_exports_routing.py`. To reconcile legacy splits or PascalCase folders on disk, run `scripts/canonicalize_processed_exports_layout.py` (see README).

---

## Maintenance

### Regular Tasks
- Archive old logs (move to `logs\archive\`)
- Review and update documentation
- Clean up temporary files in `_DropExports/`
- Organize chatlogs by topic/date

### Backup Recommendations
- Backup `config/` folder regularly
- Archive important chatlogs
- Keep documentation versioned

---

**Maintained by:** R. A. Carucci  
**Last Updated:** 2026-03-25


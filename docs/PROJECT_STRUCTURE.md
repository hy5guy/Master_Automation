# Master_Automation Project Structure

**Last Updated:** 2025-12-11

---

## Directory Structure

```
Master_Automation/
├── README.md                    # Main project documentation (stays in root)
├── config/                      # Configuration files
│   ├── scripts.json            # ETL script configuration
│   └── scripts.json.bak        # Backup configuration
├── scripts/                     # PowerShell execution scripts
│   ├── run_all_etl.ps1         # Main orchestrator
│   ├── run_all_etl.bat         # Batch wrapper
│   └── run_etl_script.ps1      # Single script runner
├── logs/                        # ETL execution logs (auto-created)
│   └── YYYY-MM-DD_HH-MM-SS_*.log
├── docs/                        # Documentation files
│   ├── CHANGELOG.md
│   ├── MIGRATION_VERIFICATION.md
│   ├── VERIFICATION_REPORT.md
│   ├── VERIFICATION_SUMMARY.md
│   ├── QUICK_START.md
│   ├── BACKFILL_*.md
│   └── PROJECT_STRUCTURE.md (this file)
├── chatlogs/                    # AI chat logs and conversations
│   └── YYYY-MM-DD_description.md
├── _DropExports/                # Temporary ETL outputs (before Power BI organization)
│   └── (CSV files from ETL scripts)
└── verify_migration.ps1        # Migration verification script
```

---

## Folder Purposes

### `config/`
**Purpose:** Configuration files for ETL scripts
- `scripts.json` - Main configuration (script paths, settings)
- `scripts.json.bak` - Backup of previous configuration

### `scripts/`
**Purpose:** PowerShell execution scripts
- `run_all_etl.ps1` - Main orchestrator (runs all ETL scripts)
- `run_all_etl.bat` - Batch file wrapper for easy execution
- `run_etl_script.ps1` - Helper to run individual scripts

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
- Located in PowerBI_Date: `PowerBI_Date\_DropExports\`
- This folder in Master_Automation is for local testing/staging if needed

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

## PowerBI_Date Integration

**Note:** The actual `_DropExports` folder used by ETL scripts is located at:
```
C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports\
```

This folder in Master_Automation (`_DropExports/`) is optional and can be used for:
- Local testing
- Staging before Power BI organization
- Development/testing purposes

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
**Last Updated:** 2025-12-11


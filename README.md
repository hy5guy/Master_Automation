# Master ETL Automation

Centralized automation hub for running all Python ETL scripts that feed into Power BI reports.

## Overview

This directory orchestrates all Python data processing scripts from various workspaces and manages their output to the Power BI Date repository.

## Directory Structure

```
Master_Automation/
├── README.md                    # This file
├── CHANGELOG.md                 # Version history and updates
├── VERIFICATION_SUMMARY.md     # Migration verification summary
├── MIGRATION_VERIFICATION.md    # Detailed verification guide
├── CURSOR_AI_PROMPT.md          # AI assistant prompt for verification
├── verify_migration.ps1         # Automated verification script
├── config/
│   ├── scripts.json            # Configuration for all ETL scripts
│   └── scripts.json.bak        # Backup of previous config
├── scripts/
│   ├── run_all_etl.ps1         # PowerShell orchestrator (recommended)
│   ├── run_all_etl.bat         # Batch file orchestrator
│   └── run_etl_script.ps1      # Helper script to run individual scripts
└── logs/
    └── .gitkeep                # ETL execution logs go here (auto-created)
```

## Quick Start

### Run All ETL Scripts

**PowerShell (Recommended):**
```powershell
cd C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation
.\scripts\run_all_etl.ps1
```

**Batch File:**
```batch
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"
scripts\run_all_etl.bat
```

### Run Specific Script

```powershell
.\scripts\run_etl_script.ps1 -ScriptName "Arrests"
```

## Configuration

Edit `config/scripts.json` to add, remove, or modify ETL scripts:

```json
{
  "scripts": [
    {
      "name": "Arrests",
      "path": "C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\02_ETL_Scripts\\Arrests",
      "script": "process_arrests.py",
      "enabled": true,
      "output_to_powerbi": true,
      "order": 1
    },
    {
      "name": "Community Engagement",
      "path": "C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\02_ETL_Scripts\\Community_Engagment",
      "script": "process_engagement.py",
      "enabled": true,
      "output_to_powerbi": true,
      "order": 2
    }
  ]
}
```

## Features

- **Sequential Execution:** Runs scripts in specified order
- **Error Handling:** Continues on errors, logs failures
- **Logging:** Detailed logs for each script execution
- **Power BI Integration:** Automatically copies outputs to Power BI drop folder
- **Selective Execution:** Run all, or specific scripts
- **Status Reporting:** Summary of what succeeded/failed

## Workflow

1. **Configure:** Edit `config/scripts.json` with your script paths
2. **Run:** Execute `run_all_etl.ps1` or `run_all_etl.bat`
3. **Process:** Scripts execute in order, outputs logged
4. **Integrate:** Successful outputs copied to Power BI Date repository
5. **Review:** Check logs for any failures or warnings

## Output Integration

All successful outputs are automatically:
1. Validated (CSV format, proper structure)
2. Copied to `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports\`
3. Ready for `organize_backfill_exports.ps1` processing

## Logging

Logs are saved to:
- `logs/YYYY-MM-DD_HH-MM-SS_ETL_Run.log` - Overall execution log
- `logs/YYYY-MM-DD_HH-MM-SS_[ScriptName].log` - Individual script logs

## Error Handling

- Scripts run independently (failure of one doesn't stop others)
- Errors logged with details
- Summary report shows success/failure status
- Failed scripts can be re-run individually

## Recent Updates (2025-12-11)

### Migration to OneDrive Complete ✅
- **PowerBI_Date** moved from `C:\Dev\PowerBI_Date_Merged` to OneDrive location
- All path references updated in configuration and scripts
- Master_Automation junction created for seamless integration
- Verification scripts and documentation added

### New Files Added
- `verify_migration.ps1` - Automated verification script
- `MIGRATION_VERIFICATION.md` - Detailed verification guide
- `VERIFICATION_SUMMARY.md` - Quick reference summary
- `CHANGELOG.md` - Version history
- `CURSOR_AI_PROMPT.md` - AI assistant prompt for workspace verification

### Configuration Updates
- `powerbi_drop_path` updated to: `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports`
- All script paths verified and updated
- Documentation paths corrected

### Verification
Run `.\verify_migration.ps1` to verify all paths and configurations are correct.

---

**Location:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation`  
**Last Updated:** 2025-12-11  
**Migration Status:** ✅ Complete - Ready for Testing


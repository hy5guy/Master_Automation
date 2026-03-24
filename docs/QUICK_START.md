# Quick Start - Master ETL Automation

## Run All Scripts

**PowerShell:**
```powershell
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\06_Workspace_Management"
.\scripts\run_all_etl.ps1
```

**Batch File (Double-click):**
```
scripts\run_all_etl.bat
```

## Run Specific Script

```powershell
.\scripts\run_etl_script.ps1 -ScriptName "Arrests"
```

## Preview (Dry Run)

```powershell
.\scripts\run_all_etl.ps1 -DryRun
```

## After Running

1. **Check logs:** `logs\YYYY-MM-DD_HH-MM-SS_ETL_Run.log`
2. **Organize Power BI files:**
   ```powershell
   cd "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data"
   .\tools\organize_backfill_exports.ps1
   ```

## Configuration

Edit `config\scripts.json` to:
- Enable/disable scripts
- Change execution order
- Modify timeouts
- Update paths

## Troubleshooting

- **Script not found:** Check path in `config\scripts.json`
- **Python not found:** Set `python_executable` in config
- **Timeout:** Increase `timeout_minutes` for slow scripts


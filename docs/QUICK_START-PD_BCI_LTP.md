# Quick Start - Master ETL Automation

## Run All Scripts

**PowerShell:**
```powershell
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"
.\scripts\run_all_etl.ps1
```

**Batch File (Double-click):**
```
scripts\run_all_etl.bat
```

**Note:** Batch file supports same parameters as PowerShell script (e.g., `run_all_etl.bat -DryRun`)

## Run Specific Script(s)

Run a single script:
```powershell
.\scripts\run_etl_script.ps1 -ScriptName "Arrests"
```

Or run multiple specific scripts:
```powershell
.\scripts\run_all_etl.ps1 -ScriptNames "Arrests", "Summons"
```

## Preview (Dry Run)

Preview what would execute without running scripts:

```powershell
.\scripts\run_all_etl.ps1 -DryRun
```

## Skip Power BI Integration

Run scripts but skip copying outputs to Power BI drop folder:

```powershell
.\scripts\run_all_etl.ps1 -SkipPowerBI
```

## After Running

1. **Check logs:** `logs\YYYY-MM-DD_HH-MM-SS_ETL_Run.log`
2. **Organize Power BI files:**
   ```powershell
   cd C:\Dev\PowerBI_Date
   .\tools\organize_backfill_exports.ps1
   ```

## Configuration

Edit `config\scripts.json` to:
- Enable/disable scripts (`enabled: true/false`)
- Change execution order (`order: 1, 2, 3...`)
- Modify timeouts (`timeout_minutes: 30`)
- Update paths (`path`, `script`)
- Configure output patterns (`output_patterns: ["*.csv"]`)
- Set keywords for categorization (`keywords: ["arrest", "court"]`)
- Configure global settings (`settings` object)

## Troubleshooting

- **Script not found:** Check path in `config\scripts.json`
- **Python not found:** Set `python_executable` in config
- **Timeout:** Increase `timeout_minutes` for slow scripts


# Migration Verification

**Processing Date:** 2026-02-05 00:00:41
**Source File:** MIGRATION_VERIFICATION.md
**Total Chunks:** 1

---

# Master_Automation Migration Verification Guide

## Overview

This guide helps you verify that the Master_Automation workspace is correctly configured after the PowerBI_Date migration to OneDrive. **Migration Date:** 2025-12-11  
**New PowerBI_Date Location:** `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date`  
**Master_Automation Location:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation`

---

## Quick Verification

Run the automated verification script:

```powershell
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"
.\verify_migration.ps1
```

---

## Manual Verification Checklist

### ✅ 1. Configuration File (`config\scripts.json`)

**Check:** `powerbi_drop_path` setting

**Expected Value:**
```json
"powerbi_drop_path": "C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\PowerBI_Date\\_DropExports"
```

**How to Verify:**
```powershell
$config = Get-Content "config\scripts.json" | ConvertFrom-Json
$config.settings.powerbi_drop_path
```

**Should show:** `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports`

---

### ✅ 2. PowerBI_Date Directory Structure

**Check:** Verify all key directories exist in new location

**Expected Location:**
```
C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\
├── Backfill\
├── DAX\
├── etl\
├── mCode\
├── tools\
└── _DropExports\
```

**How to Verify:**
```powershell
$powerBIPath = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date"
Test-Path $powerBIPath
Test-Path "$powerBIPath\_DropExports"
Test-Path "$powerBIPath\Backfill"
Test-Path "$powerBIPath\tools"
```

**All should return:** `True`

---

### ✅ 3. Master_Automation Junction

**Check:** Junction link from PowerBI_Date to Master_Automation

**Expected:**
- Junction exists at: `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Master_Automation`
- Points to: `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation`

**How to Verify:**
```powershell
$junctionPath = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Master_Automation"
$item = Get-Item $junctionPath
$item.Attributes -band [IO.FileAttributes]::ReparsePoint  # Should be True

# Check target
& cmd /c "fsutil reparsepoint query `"$junctionPath`""
```

**Should show:** Junction pointing to Master_Automation directory

---

### ✅ 4. ETL Script Paths

**Check:** All ETL script paths in `config\scripts.json` point to valid locations

**Expected Scripts:**
- Arrests: `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Arrests\main.py`
- Community Engagement: `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Community_Engagment\main.py`
- Overtime TimeOff: `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Overtime_TimeOff\main.py`
- Policy Training Monthly: `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Policy_Training_Monthly\main.py`
- Response Times: `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Response_Times\main.py`
- Summons: `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Summons\main.py`
- Arrest Data Source: `C:\Users\carucci_r\OneDrive - City of Hackensack\01_DataSources\ARREST_DATA\main.py`
- NIBRS: `C:\Users\carucci_r\OneDrive - City of Hackensack\01_DataSources\NIBRS\main.py`

**How to Verify:**
```powershell
$config = Get-Content "config\scripts.json" | ConvertFrom-Json
foreach ($script in $config.scripts) {
    if ($script.enabled) {
        $scriptPath = Join-Path $script.path $script.script
        $exists = Test-Path $scriptPath
        Write-Host "$($script.name): $(if ($exists) { '✅' } else { '❌' }) $scriptPath"
    }
}
```

**Note:** Script files may have different names (e.g., `arrest_python_processor.py` instead of `main.py`). Update `scripts.json` if needed. ---

### ✅ 5. Script File Path References

**Check:** No old `C:\Dev\PowerBI_Date` references in scripts

**Files to Check:**
- `scripts\run_all_etl.ps1`
- `scripts\run_etl_script.ps1`

**How to Verify:**
```powershell
Get-ChildItem scripts\*.ps1 | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    if ($content -match 'C:\\Dev\\PowerBI_Date') {
        Write-Host "❌ Old path found in: $($_.Name)" -ForegroundColor Red
    } else {
        Write-Host "✅ $($_.Name) - No old paths" -ForegroundColor Green
    }
}
```

**Should show:** All files clean (no old paths)

---

### ✅ 6. Documentation Path References

**Check:** Documentation updated with new paths

**Files to Check:**
- `README.md`
- `QUICK_START.md`

**How to Verify:**
```powershell
Get-ChildItem *.md | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    if ($content -match 'C:\\Dev\\PowerBI_Date') {
        Write-Host "❌ Old path found in: $($_.Name)" -ForegroundColor Red
    } else {
        Write-Host "✅ $($_.Name) - Updated" -ForegroundColor Green
    }
}
```

**Should show:** All documentation updated

---

### ✅ 7. Python Executable

**Check:** Python is accessible

**How to Verify:**
```powershell
$config = Get-Content "config\scripts.json" | ConvertFrom-Json
$pythonExe = $config.settings.python_executable
& $pythonExe --version
```

**Should show:** Python version (e.g., `Python 3.13.7`)

---

### ✅ 8. Log Directory

**Check:** Log directory exists (will be created automatically on first run)

**Expected:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\logs`

**How to Verify:**
```powershell
$logDir = "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\logs"
if (Test-Path $logDir) {
    Write-Host "✅ Log directory exists" -ForegroundColor Green
} else {
    Write-Host "⚠️  Log directory will be created on first run" -ForegroundColor Yellow
}
```

---

## Testing the Migration

### Test 1: Dry Run ETL Execution

```powershell
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"
.\scripts\run_all_etl.ps1 -DryRun
```

**Expected:** Scripts list without errors, shows what would execute

---

### Test 2: Verify Drop Folder Access

```powershell
$dropPath = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports"
Test-Path $dropPath
# Should return True

# Try creating a test file
$testFile = Join-Path $dropPath "test_write.txt"
"test" | Set-Content $testFile
Remove-Item $testFile
Write-Host "✅ Drop folder is writable" -ForegroundColor Green
```

---

### Test 3: Verify Junction Access

```powershell
$junctionPath = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Master_Automation"
Get-ChildItem $junctionPath
# Should show contents of Master_Automation directory
```

---

## Common Issues & Solutions

### Issue: Script files not found

**Cause:** Script files may have different names than `main.py`

**Solution:** Update `config\scripts.json` with correct script filenames:
```powershell
# Check actual script files
Get-ChildItem "C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Arrests\*.py"
# Update scripts.json with correct filename
```

---

### Issue: Junction shows wrong target

**Cause:** NTFS junctions may show `\? ?\` prefix in fsutil output

**Solution:** This is normal. The junction is correct if the path after `\? ?\` matches the expected location. ---

### Issue: Drop folder not accessible

**Cause:** OneDrive sync may not have completed

**Solution:**
1. Check OneDrive sync status
2. Ensure files are pinned locally: `attrib +P -U /S /D "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\*"`
3. Wait for sync to complete

---

## Post-Verification Steps

Once verification passes:

1. **Test ETL Execution:**
   ```powershell
   cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"
   .\scripts\run_all_etl.ps1 -DryRun
   ```

2. **Run Single Script Test:**
   ```powershell
   .\scripts\run_etl_script.ps1 -ScriptName "Arrests"
   ```

3. **Verify Output:**
   ```powershell
   Get-ChildItem "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports"
   ```

4. **Organize Exports:**
   ```powershell
   cd "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date"
   .\tools\organize_backfill_exports.ps1
   ```

---

## Summary

**Migration Status:** ✅ Complete  
**Config Updated:** ✅ Yes  
**Path References Fixed:** ✅ Yes  
**Junction Created:** ✅ Yes  
**Ready for Testing:** ✅ Yes

**Next Action:** Run `.\verify_migration.ps1` to see detailed status, then test ETL execution.


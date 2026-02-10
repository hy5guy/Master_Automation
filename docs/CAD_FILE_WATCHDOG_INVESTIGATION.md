# CAD File Watchdog Investigation

**Date:** 2026-01-14  
**File:** `C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_CAD\response_time\2025\2024_12_to_2025_12_ResponseTime_CAD.xlsx`  
**Issue:** User suspects watchdog script may have broken the file when moving it. Previous issues with duplicate data entries when moving files.

---

## Investigation Status

### ✅ File Exists
- **Location:** `C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_CAD\response_time\2025\2024_12_to_2025_12_ResponseTime_CAD.xlsx`
- **Status:** File path exists (verified)

### ⚠️ File Readability Issues

**Issue:** The file cannot be read by pandas - getting error:
```
ValueError: Excel file format cannot be determined, you must specify an engine manually.
```

**Possible Causes:**
1. **OneDrive Cloud-Only Placeholder** (Most Likely)
   - The file is a cloud-only placeholder that hasn't been synced locally
   - This was mentioned in previous Claude Code analysis
   - File exists in OneDrive but data is not available locally
   - Need to sync the file locally to read it

2. **File Corruption**
   - If the watchdog script interrupted file transfer
   - If OneDrive sync was interrupted
   - If file was partially moved

3. **File Format Issue**
   - File might not be a valid Excel file
   - File extension might be incorrect
   - File might be in a different format

---

## Watchdog Script Location

**Script Path:** `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Export_File_Watchdog\watchdog_service.py`

**Status:** Script exists (verified)

**User's Concern:**
- Watchdog script was making duplicate data entries when moving files
- User suspects the watchdog may have broken the CAD file when moving it

---

## Recommended Actions

### 1. Sync the File Locally (IMMEDIATE)

**The file is likely a OneDrive cloud-only placeholder.**

**Steps:**
1. Open File Explorer
2. Navigate to: `C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_CAD\response_time\2025\`
3. Right-click on `2024_12_to_2025_12_ResponseTime_CAD.xlsx`
4. Select "Always keep on this device"
5. Wait for OneDrive to sync the file (watch the OneDrive icon in system tray)
6. Verify the file is fully synced (file icon should show green checkmark)

**After syncing, test if file is readable:**
```powershell
python -c "import pandas as pd; df = pd.read_excel(r'C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_CAD\response_time\2025\2024_12_to_2025_12_ResponseTime_CAD.xlsx', engine='openpyxl', nrows=5); print('File is readable'); print(f'Columns: {list(df.columns)[:5]}'); print(f'Shape: {df.shape}')"
```

### 2. Check File Integrity (After Syncing)

**Check for duplicate entries:**
```powershell
python -c "import pandas as pd; df = pd.read_excel(r'C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_CAD\response_time\2025\2024_12_to_2025_12_ResponseTime_CAD.xlsx', engine='openpyxl'); print(f'Total rows: {len(df)}'); print(f'Duplicate rows: {df.duplicated().sum()}'); print(f'Unique rows: {len(df) - df.duplicated().sum()}')"
```

**Check for duplicate ReportNumberNew values (if column exists):**
```powershell
python -c "import pandas as pd; df = pd.read_excel(r'C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_CAD\response_time\2025\2024_12_to_2025_12_ResponseTime_CAD.xlsx', engine='openpyxl'); print(f'Total rows: {len(df)}'); if 'ReportNumberNew' in df.columns: print(f'Unique ReportNumberNew: {df[\"ReportNumberNew\"].nunique()}'); print(f'Duplicate ReportNumberNew: {len(df) - df[\"ReportNumberNew\"].nunique()}')"
```

### 3. Investigate Watchdog Script (If Issues Found)

**Review the watchdog script:**
- File: `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Export_File_Watchdog\watchdog_service.py`
- Check how it moves files
- Check if it processes Excel files
- Check if it has duplicate entry logic
- Check if it handles OneDrive cloud-only files correctly

**Questions to investigate:**
1. Does the watchdog script move Excel files?
2. Does it read/write Excel files (which could cause duplication)?
3. Does it handle OneDrive cloud-only placeholders?
4. Does it have logic that could create duplicate entries?

### 4. Check File History (If Available)

**If file is corrupted:**
- Check OneDrive file version history (right-click file → Version history)
- Restore previous version if available
- Check if original export file exists elsewhere

---

## Summary

**Current Status:**
- ✅ File exists at expected location
- ⚠️ File is not readable (likely cloud-only placeholder)
- ❓ Unknown if watchdog script affected the file
- ❓ Unknown if file has duplicate entries

**Most Likely Issue:**
The file is a **OneDrive cloud-only placeholder** that needs to be synced locally. This is not necessarily a watchdog script issue - it's a OneDrive sync issue.

**Next Steps:**
1. **Sync the file locally** (see Action #1 above)
2. **Test file readability** after syncing
3. **Check for duplicate entries** if file is readable
4. **Investigate watchdog script** if duplicate entries are found

---

## Watchdog Script Investigation (Future)

If duplicate entries are found after syncing, investigate:
1. Read the watchdog script code
2. Understand how it moves/handles files
3. Check if it modifies Excel files
4. Verify if it has duplicate entry logic
5. Test if moving files causes issues

---

**Note:** The "Excel file format cannot be determined" error is most commonly caused by OneDrive cloud-only placeholders. Sync the file locally first, then investigate further if issues persist.

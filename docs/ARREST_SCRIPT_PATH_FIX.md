# Arrest Script Path Fix - January 5, 2026

## 🔍 Issue Identified

The arrest processing script was not finding the December 2025 file because:
- **Script was looking:** `05_EXPORTS/_Arrest/*.xlsx` (non-recursive)
- **File actually located:** `05_EXPORTS/_Arrest/monthly_export/2025/2025_12_LAWSOFT_ARREST.xlsx`

### Root Cause
The script used `glob("*.xlsx")` which only searches the immediate directory, not subdirectories.

---

## ✅ Fix Applied

### File Updated
`C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Arrests\arrest_python_processor.py`

### Change Made
**Line 404:** Changed from non-recursive to recursive glob search

**Before:**
```python
all_files = sorted(
    self.arrest_folder.glob("*.xlsx"),  # ❌ Only immediate directory
    key=lambda file_path: file_path.stat().st_mtime,
    reverse=True
)
```

**After:**
```python
# Search recursively for .xlsx files in subdirectories (e.g., monthly_export/2025/)
all_files = sorted(
    self.arrest_folder.glob("**/*.xlsx"),  # ✅ Recursive search
    key=lambda file_path: file_path.stat().st_mtime,
    reverse=True
)
```

---

## 📁 Directory Structure

The script now searches recursively and will find files in:

```
05_EXPORTS/_Arrest/
├── *.xlsx                          ✅ (immediate directory)
├── monthly_export/
│   └── 2025/
│       └── 2025_12_LAWSOFT_ARREST.xlsx  ✅ (now found!)
└── full_year/
    └── 2025/
        └── 2025_Lawsoft_Yearly_Arrest.xlsx  ✅ (also found)
```

---

## 🎯 Expected Behavior

After this fix, the script will:
1. ✅ Search recursively in all subdirectories
2. ✅ Find the December 2025 file: `monthly_export/2025/2025_12_LAWSOFT_ARREST.xlsx`
3. ✅ Select the most recent file by modification time
4. ✅ Process it and create `2025_12_Arrests_PowerBI_Ready.xlsx`

---

## 📋 Next Steps

1. **Run the arrest script again:**
   ```powershell
   .\scripts\run_all_etl.ps1 -ScriptNames "Arrests"
   ```

2. **Verify output:**
   - Check for: `2025_12_Arrests_PowerBI_Ready.xlsx` in `01_DataSources/ARREST_DATA/Power_BI/`

3. **Update Power BI queries:**
   - The M code queries are already updated to target December 2025
   - They will automatically load the new PowerBI_Ready file once it's created

---

## ✅ Verification

**Files Found by Recursive Search:**
- ✅ `2025_12_LAWSOFT_ARREST.xlsx` (Modified: 01/02/2026 11:46:24) - **Latest**
- ✅ `2025_Lawsoft_Yearly_Arrest.xlsx` (Modified: 01/02/2026 11:45:34)
- ✅ `2025_11_LAWSOFT_ARREST.xlsx` (Modified: 12/10/2025 13:34:28)

**Status:** ✅ **FIXED - Ready to Process December 2025 Data**

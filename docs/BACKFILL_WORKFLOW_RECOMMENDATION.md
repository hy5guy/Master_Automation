# Backfill Workflow Recommendation

**Date:** 2025-12-11  
**Question:** Should column order be fixed before or after organizing exports?

---

## Current Workflow

### Step 1: Export Visuals from Power BI
- Export CSV files from Power BI visuals
- Save to: `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports\`

### Step 2: Organize Exports
- Run: `organize_backfill_exports.ps1`
- Script:
  - Reads CSV files from `_DropExports` folder
  - Categorizes files based on filename patterns
  - Moves files to: `Backfill\YYYY_MM\category\` folders
  - Renames files with month prefix: `YYYY_MM_Filename.csv`

### Step 3: (Optional) Fix Column Order
- Reorder columns if needed for consistency

---

## Recommendation: **Complete Organization First** ✅

### Why Complete Organization First?

1. **See Full Scope**
   - You'll know which files exist and need fixing
   - Can verify all visuals have been exported
   - Can check which categories have files

2. **Batch Processing**
   - Can fix column order for all files in a category at once
   - More efficient than fixing one-by-one

3. **Verify Organization Script**
   - Ensure `organize_backfill_exports.ps1` is working correctly
   - Files are in correct folders before modifying them

4. **Avoid Duplicate Work**
   - Don't fix files that might get re-exported
   - Fix files in their final location

---

## Recommended Workflow

### Phase 1: Complete Export & Organization ✅ **DO THIS FIRST**

```powershell
# 1. Export all visuals from Power BI to _DropExports folder
# (Manual step in Power BI)

# 2. Verify exports are in _DropExports
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date"
Get-ChildItem "_DropExports\*.csv"

# 3. Organize all exports
.\tools\organize_backfill_exports.ps1

# 4. Verify organization
Get-ChildItem "Backfill\2025_10\*\*.csv" -Recurse
```

**Checklist:**
- [ ] All visuals exported from Power BI
- [ ] Files in `_DropExports` folder
- [ ] `organize_backfill_exports.ps1` run successfully
- [ ] Files moved to correct `Backfill\YYYY_MM\category\` folders
- [ ] Files renamed with month prefix

---

### Phase 2: Fix Column Order (After Organization) ✅ **THEN DO THIS**

**Option A: Fix All Files in a Category**
```powershell
# Fix all files in vcs_time_report category for 2025_10
$categoryPath = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\2025_10\vcs_time_report"
Get-ChildItem "$categoryPath\*.csv" | ForEach-Object {
    # Run column reorder script on each file
    python reorder_csv_columns.py $_.FullName
}
```

**Option B: Fix Specific File**
```powershell
# Fix the Monthly Accrual file
$file = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\2025_10\vcs_time_report\2025_10_Monthly Accrual and Usage Summary.csv"
python reorder_csv_columns.py $file
```

---

## Column Reorder Script (To Create)

**Create:** `reorder_csv_columns.py`

```python
import pandas as pd
import sys
from pathlib import Path

def reorder_csv_columns(csv_path):
    """Reorder CSV columns: Time Category first, then date columns chronologically."""
    csv_path = Path(csv_path)
    
    if not csv_path.exists():
        print(f"❌ File not found: {csv_path}")
        return False
    
    # Read CSV
    df = pd.read_csv(csv_path)
    
    # Find Time Category column (handle both names)
    time_col = None
    for col in df.columns:
        if col.lower() in ['time_category', 'time category']:
            time_col = col
            break
    
    if not time_col:
        print(f"⚠️  No Time Category column found in {csv_path.name}")
        return False
    
    # Get date columns (all columns except Time Category)
    date_cols = [c for c in df.columns if c != time_col]
    
    # Sort date columns chronologically
    def parse_month(col):
        try:
            mm, yy = col.split('-')
            return (int(yy), int(mm))
        except:
            # Handle "Sum of MM-YY" format
            try:
                parts = col.split()
                if len(parts) >= 2:
                    mm, yy = parts[-1].split('-')
                    return (int(yy), int(mm))
            except:
                pass
            return (99, 99)  # Put invalid columns at end
    
    date_cols_sorted = sorted(date_cols, key=parse_month)
    
    # Reorder: Time Category first, then date columns
    new_order = [time_col] + date_cols_sorted
    df_reordered = df[new_order]
    
    # Standardize column name
    if time_col == "Time_Category":
        df_reordered = df_reordered.rename(columns={"Time_Category": "Time Category"})
    
    # Save (backup first)
    backup_path = csv_path.with_suffix('.csv.backup')
    csv_path.rename(backup_path)
    df_reordered.to_csv(csv_path, index=False)
    
    print(f"✅ Reordered: {csv_path.name}")
    print(f"   Columns: {', '.join(new_order[:5])}... ({len(new_order)} total)")
    print(f"   Backup: {backup_path.name}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python reorder_csv_columns.py <csv_file_path>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    reorder_csv_columns(csv_file)
```

---

## Answer to Your Questions

### Q: Will the script change all data exports in different folders?

**A:** No, the script will only change files you explicitly run it on. It won't automatically process all folders. You can:
- Run it on a single file
- Run it on all files in a category folder
- Run it on all files in a month folder
- Run it selectively

### Q: Should I first ensure all visuals have been exported and organized?

**A:** ✅ **YES - Recommended Workflow:**

1. **First:** Export all visuals from Power BI → `_DropExports`
2. **Second:** Run `organize_backfill_exports.ps1` → Moves files to `Backfill\YYYY_MM\category\`
3. **Third:** Verify all files are in correct folders
4. **Fourth:** Fix column order for files that need it

**Why:**
- See the full scope of what needs fixing
- Files are in their final location
- Can batch process by category
- Avoid fixing files that might be re-exported

---

## Current Status Check

### Check What's Already Organized

```powershell
# See what's in Backfill folders
$backfillRoot = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill"
Get-ChildItem $backfillRoot -Directory | ForEach-Object {
    Write-Host "`n$($_.Name):" -ForegroundColor Cyan
    $csvFiles = Get-ChildItem $_.FullName -Recurse -Filter "*.csv"
    Write-Host "  CSV files: $($csvFiles.Count)" -ForegroundColor Yellow
    $csvFiles | Group-Object Directory | ForEach-Object {
        Write-Host "    $($_.Name | Split-Path -Leaf): $($_.Count) file(s)" -ForegroundColor Gray
    }
}
```

### Check What's Still in _DropExports

```powershell
$dropExports = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports"
Get-ChildItem "$dropExports\*.csv" | Select-Object Name, LastWriteTime
```

---

## Summary

**Recommended Order:**
1. ✅ Export all visuals → `_DropExports`
2. ✅ Run `organize_backfill_exports.ps1` → Organize to `Backfill\YYYY_MM\category\`
3. ✅ Verify organization complete
4. ✅ Fix column order for files that need it (can be selective)

**Column Order Fix:**
- Priority: Medium (functional but inconsistent)
- Can be done after organization
- Can be selective (only fix files that need it)
- Script will only change files you run it on

---

**Status:** Complete organization first, then fix column order as needed.


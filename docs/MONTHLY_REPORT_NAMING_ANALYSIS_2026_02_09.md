# Monthly Report Directory Naming Analysis

**Date**: February 9, 2026  
**Current Structure**: `MM_monthname` (e.g., `01_january`)  
**Question**: Should folders be renamed to `YYYY_MM` format?

---

## Current Implementation

### How Save-MonthlyReport Works

From `scripts\run_all_etl.ps1` (lines 46-132):

```powershell
function Save-MonthlyReport {
    # 1. Calculate previous month
    $prevMonth = $now.AddMonths(-1)
    $year = $prevMonth.Year           # e.g., 2026
    $monthNum = $prevMonth.Month.ToString("00")  # e.g., "01"
    $monthName = $prevMonth.ToString("MMMM")     # e.g., "January"
    $monthNameLower = $monthName.ToLower()       # e.g., "january"
    
    # 2. Generate report filename
    # Format: YYYY_MM_Monthly_FINAL_LAP.pbix
    $reportFileName = "${year}_${monthNum}_Monthly_FINAL_LAP.pbix"
    # Example: 2026_01_Monthly_FINAL_LAP.pbix
    
    # 3. Generate target directory
    # Format: YEAR\MM_monthname
    $targetDir = Join-Path $monthlyReportsBase $year
    $targetDir = Join-Path $targetDir "${monthNum}_${monthNameLower}"
    # Example: Monthly Reports\2026\01_january
    
    # 4. Find template (prioritizes files with "Template" in name)
    $sourceFile = Get-ChildItem -Path $templatesDir -Filter "*.pbix"
    
    # 5. Copy template to target directory with new name
    Copy-Item -Path $sourceFile.FullName -Destination $targetFile -Force
}
```

### Current Directory Structure

```
Monthly Reports\
└── 2026\
    ├── 01_january\
    │   └── 2026_01_Monthly_FINAL_LAP.pbix
    ├── 02_february\
    ├── 03_march\
    ├── 04_april\
    ├── 05_may\
    ├── 06_june\
    ├── 07_july\
    ├── 08_august\
    ├── 09_september\
    ├── 10_october\
    ├── 11_november\
    └── 12_december\
```

**Key Points**:
- ✅ Folders: `MM_monthname` (e.g., `01_january`)
- ✅ Files: `YYYY_MM_Monthly_FINAL_LAP.pbix` (e.g., `2026_01_Monthly_FINAL_LAP.pbix`)
- ✅ Script automatically creates this structure
- ✅ Template copied from `15_Templates\Monthly_Report_Template.pbix`

---

## Naming Convention Analysis

### Option 1: Keep Current Format (RECOMMENDED)

**Format**: `MM_monthname` (e.g., `01_january`)

**Advantages**:
- ✅ **Human-readable**: Easy to identify months at a glance
- ✅ **Sortable**: Numeric prefix ensures correct alphabetical order
- ✅ **Descriptive**: Month name immediately recognizable
- ✅ **No changes needed**: Script already implements this
- ✅ **User-friendly**: Non-technical users can navigate easily
- ✅ **Consistent**: Matches script's default behavior

**Disadvantages**:
- ⚠️ Slightly longer folder names
- ⚠️ Month name in English only (not relevant for your use case)

**Example**:
```
Monthly Reports\2026\01_january\2026_01_Monthly_FINAL_LAP.pbix
                     ^^^^^^^^^^^
                     Clear and readable
```

### Option 2: Rename to YYYY_MM Format

**Format**: `YYYY_MM` (e.g., `2026_01`)

**Advantages**:
- ✅ Shorter folder names
- ✅ Matches file naming pattern
- ✅ Year+month in one glance
- ✅ Language-independent

**Disadvantages**:
- ❌ **Less readable**: Need to mentally translate `01` → January
- ❌ **Redundant**: Year already in parent folder (2026\2026_01)
- ❌ **Requires script modification**: Must update run_all_etl.ps1
- ❌ **Inconsistent**: Future months auto-created with old format unless script changed
- ❌ **Manual maintenance**: Must manually rename or update script
- ❌ **Break existing references**: If any other scripts/shortcuts reference folders

**Example**:
```
Monthly Reports\2026\2026_01\2026_01_Monthly_FINAL_LAP.pbix
                     ^^^^^^^^
                     Year redundant (already in 2026\ parent)
```

### Option 3: Rename to MM Only (Alternative)

**Format**: `MM` (e.g., `01`)

**Advantages**:
- ✅ Very short
- ✅ Numeric sorting works
- ✅ Matches file prefix

**Disadvantages**:
- ❌ **Not readable**: What month is 07 again?
- ❌ **Context needed**: Must look at parent folder for year
- ❌ **Requires script modification**
- ❌ **Poor user experience**: Hard to navigate

---

## Recommendation: Keep Current Format

### Why MM_monthname is Best

**For your use case:**
1. **Non-technical users** can easily navigate to "january" reports
2. **Sorting still works** perfectly (01_january comes before 02_february)
3. **No script changes needed** - everything works out of the box
4. **Consistency maintained** - all future months auto-created correctly

### What the Script Does Automatically

When you run `.\scripts\run_all_etl.ps1`:

```
1. Finds template: 15_Templates\Monthly_Report_Template.pbix ✅
2. Calculates previous month: January 2026 ✅
3. Creates folder: Monthly Reports\2026\01_january\ ✅
4. Copies and renames: 2026_01_Monthly_FINAL_LAP.pbix ✅
5. Done! ✅
```

**You don't need to do anything!** It works perfectly as-is.

---

## If You Still Want to Rename (Not Recommended)

If you insist on renaming, here are the steps:

### Step 1: Rename Existing Folders

PowerShell script to rename to `YYYY_MM` format:

```powershell
# Rename 2026 folders from MM_monthname to YYYY_MM
$baseDir = "C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Monthly Reports\2026"

$folderMap = @{
    "01_january"   = "2026_01"
    "02_february"  = "2026_02"
    "03_march"     = "2026_03"
    "04_april"     = "2026_04"
    "05_may"       = "2026_05"
    "06_june"      = "2026_06"
    "07_july"      = "2026_07"
    "08_august"    = "2026_08"
    "09_september" = "2026_09"
    "10_october"   = "2026_10"
    "11_november"  = "2026_11"
    "12_december"  = "2026_12"
}

foreach ($old in $folderMap.Keys) {
    $new = $folderMap[$old]
    $oldPath = Join-Path $baseDir $old
    $newPath = Join-Path $baseDir $new
    
    if (Test-Path $oldPath) {
        Rename-Item -Path $oldPath -NewName $new
        Write-Host "Renamed: $old -> $new"
    }
}

Write-Host "`nRename complete!"
```

### Step 2: Update run_all_etl.ps1

Modify line 69 in `scripts\run_all_etl.ps1`:

**Current** (line 69):
```powershell
$targetDir = Join-Path $targetDir "${monthNum}_${monthNameLower}"
```

**Change to**:
```powershell
# Option A: YYYY_MM format
$targetDir = Join-Path $targetDir "${year}_${monthNum}"

# Option B: MM only format
$targetDir = Join-Path $targetDir "${monthNum}"
```

### Step 3: Test

```powershell
# Test dry-run to verify directory creation
.\scripts\run_all_etl.ps1 -DryRun

# Check what directory would be created
```

---

## Impact Analysis

### If You Keep Current Format (Recommended)

**Impact**: None  
**Action Required**: None  
**Risk**: None  
**User Experience**: ✅ Good

### If You Rename to YYYY_MM

**Impact**: All existing folders renamed  
**Action Required**:  
1. Run rename script (5 minutes)
2. Update run_all_etl.ps1 (2 minutes)
3. Test (5 minutes)
4. Update documentation (5 minutes)

**Risk**: Medium
- Existing references may break
- Future confusion if script not updated
- Manual work for one-time gain

**User Experience**: ⚠️ Worse (less readable)

---

## Decision Matrix

| Factor | Keep MM_monthname | Rename to YYYY_MM |
|--------|------------------|-------------------|
| Readability | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐ Moderate |
| Sortability | ⭐⭐⭐⭐⭐ Perfect | ⭐⭐⭐⭐⭐ Perfect |
| Maintenance | ⭐⭐⭐⭐⭐ Zero work | ⭐⭐ Requires updates |
| User-Friendly | ⭐⭐⭐⭐⭐ Very | ⭐⭐⭐ Moderate |
| Script Compatibility | ⭐⭐⭐⭐⭐ Native | ⭐⭐ Needs modification |
| Consistency | ⭐⭐⭐⭐⭐ Automatic | ⭐⭐⭐ Manual effort |

**Winner**: Keep `MM_monthname` format ✅

---

## Real-World Usage Scenarios

### Scenario 1: Executive Looking for January Report

**With MM_monthname**:
```
1. Open: Monthly Reports\2026\
2. See: 01_january (immediately recognizable)
3. Click: 01_january\
4. Find: 2026_01_Monthly_FINAL_LAP.pbix
Total time: 5 seconds ✅
```

**With YYYY_MM**:
```
1. Open: Monthly Reports\2026\
2. See: 2026_01 (need to remember month number)
3. Think: "Is 01 January or February?"
4. Click: 2026_01\
5. Find: 2026_01_Monthly_FINAL_LAP.pbix
Total time: 10 seconds ⚠️
```

### Scenario 2: Comparing Q1 Reports

**With MM_monthname**:
```
Select: 01_january, 02_february, 03_march
Easy to identify ✅
```

**With YYYY_MM**:
```
Select: 2026_01, 2026_02, 2026_03
Need to mentally map numbers ⚠️
```

---

## Conclusion

### Recommendation: ✅ KEEP CURRENT FORMAT (`MM_monthname`)

**Reasons**:
1. More user-friendly and readable
2. Already implemented in script
3. No work required
4. Better user experience
5. Consistent with script's design

**The current structure is exactly what the script expects and creates automatically. Don't fix what isn't broken!**

---

## If You Disagree...

I've provided the rename script above. But I **strongly recommend** keeping the current format for:
- Better usability
- Zero maintenance
- Automatic consistency

---

**Decision**: Recommend keeping `MM_monthname` format  
**Action Required**: None (already optimal)  
**Script Changes Needed**: None

---

*Last Updated: February 9, 2026*

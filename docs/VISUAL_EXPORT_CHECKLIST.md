# Power BI Visual Export Checklist

**Date:** 2025-12-11  
**Purpose:** Guide for exporting visuals needed for ETL scripts

---

## Visual Categories

### 📊 Backfill Visuals (Multi-Month Historical Data)
**Purpose:** These visuals show data across multiple months and need to be preserved for historical reference and script anchoring.

| Visual Name | Category Folder | ETL Script | Filename Pattern |
|------------|----------------|------------|-----------------|
| **Monthly Accrual and Usage Summary** | `vcs_time_report` | overtime_timeoff | Contains "monthly.*accrual" or "vcs.*time" |
| **Summons Data** (Monthly) | `summons` | Summons | Contains "summon", "moving", "parking", or "violation" |
| **Community Engagement** (Monthly) | `community_outreach` | Community_Engagment | Contains "community", "outreach", or "engagement" |
| **Policy Training Monthly** | `policy_training` | Policy_Training_Monthly | Contains "policy" or "training" |
| **Response Times** | `response_time` | Response_Times | Contains "response.*time" |

### 📁 Archive Visuals (Single Month Snapshots)
**Purpose:** These visuals show only current month data - save for archive/reference, not for backfill.

| Visual Name | Archive Location | Notes |
|------------|-----------------|-------|
| TOP 5 ARREST LEADERS | `Backfill\YYYY_MM\arrest\archive\` | Single month snapshot |
| Arrest Distribution by Local, State & Out of State | `Backfill\YYYY_MM\arrest\archive\` | Single month snapshot |
| Arrest Categories by Type and Gender | `Backfill\YYYY_MM\arrest\archive\` | Single month snapshot |
| Engagement Initiatives by Bureau | `Backfill\YYYY_MM\community_outreach\archive\` | Single month snapshot |
| In-Person Training | `Backfill\YYYY_MM\policy_training\archive\` | Single month snapshot |

---

## Export Instructions

### Step 1: Export from Power BI

**For Each Visual:**

1. Open Power BI report
2. Right-click on the visual
3. Select **"Export data"** → **"Summarized data"**
4. Save to: `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports\`

**Recommended Filenames (for auto-categorization):**

| Visual | Suggested Filename |
|--------|-------------------|
| Monthly Accrual and Usage Summary | `Monthly Accrual and Usage Summary.csv` |
| Summons Data | `summons_monthly_data.csv` or `monthly_summons.csv` |
| Community Engagement | `community_engagement_monthly.csv` or `monthly_engagement.csv` |
| Policy Training Monthly | `policy_training_monthly.csv` or `monthly_training.csv` |
| Response Times | `response_time_monthly.csv` or `monthly_response_times.csv` |

**Archive Visuals (use descriptive names):**
- `TOP_5_Arrest_Leaders.csv`
- `Arrest_Distribution_Local_State_OutOfState.csv`
- `Arrest_Categories_Type_Gender.csv`
- `Engagement_Initiatives_by_Bureau.csv`
- `In_Person_Training.csv`

---

## Step 2: Organize Exports

### Automatic Organization

Run the organization script:
```powershell
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date"
.\tools\organize_backfill_exports.ps1
```

**What it does:**
- Reads CSV files from `_DropExports\`
- Categorizes by filename patterns (see below)
- Moves to `Backfill\YYYY_MM\category\`
- Renames with month prefix: `YYYY_MM_Filename.csv`

**Current Month:** Auto-detected (or specify with `-Month "2025_12"`)

### Filename Pattern Matching

The script automatically categorizes files based on keywords:

| Pattern | Category | Examples |
|---------|----------|----------|
| `summon`, `moving.*parking`, `violation` | `summons` | "summons", "monthly_summons" |
| `vcs.*time`, `monthly.*accrual`, `time.*report` | `vcs_time_report` | "Monthly Accrual", "vcs_time" |
| `community`, `outreach`, `engagement` | `community_outreach` | "community_engagement", "engagement" |
| `policy`, `training` | `policy_training` | "policy_training", "training" |
| `response.*time` | `response_time` | "response_time", "response times" |

---

## Step 3: Manual Archive Organization

For single-month visuals that don't need backfill:

**Create archive folders:**
```powershell
$month = "2025_12"
$basePath = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\$month"

# Create archive folders
New-Item -ItemType Directory -Path "$basePath\arrest\archive" -Force
New-Item -ItemType Directory -Path "$basePath\community_outreach\archive" -Force
New-Item -ItemType Directory -Path "$basePath\policy_training\archive" -Force
```

**Move archive files:**
```powershell
# Example: Move arrest archive visuals
$source = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports\TOP_5_Arrest_Leaders.csv"
$dest = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\2025_12\arrest\archive\2025_12_TOP_5_Arrest_Leaders.csv"
Move-Item -Path $source -Destination $dest
```

---

## Required Visuals Checklist

### ✅ Backfill Visuals (Required for ETL Scripts)

- [ ] **Summons**
  - Visual: Monthly summons data
  - Category: `summons`
  - Script: `Summons\main_orchestrator.py`
  - Location: `Backfill\YYYY_MM\summons\`

- [ ] **Overtime TimeOff**
  - Visual: "Monthly Accrual and Usage Summary"
  - Category: `vcs_time_report`
  - Script: `Overtime_TimeOff\overtime_timeoff_13month_sworn_breakdown_v11.py`
  - Location: `Backfill\YYYY_MM\vcs_time_report\`

- [ ] **Community Engagement**
  - Visual: Monthly community engagement data
  - Category: `community_outreach`
  - Script: `Community_Engagment\deploy_production.py`
  - Location: `Backfill\YYYY_MM\community_outreach\`

- [ ] **Policy Training Monthly**
  - Visual: Monthly training data
  - Category: `policy_training`
  - Script: `Policy_Training_Monthly\` (currently disabled - no Python files)
  - Location: `Backfill\YYYY_MM\policy_training\`

### 📁 Archive Visuals (Optional - for reference)

- [ ] TOP 5 ARREST LEADERS → `arrest\archive\`
- [ ] Arrest Distribution by Local, State & Out of State → `arrest\archive\`
- [ ] Arrest Categories by Type and Gender → `arrest\archive\`
- [ ] Engagement Initiatives by Bureau → `community_outreach\archive\`
- [ ] In-Person Training → `policy_training\archive\`

---

## Current Backfill Status

**2025_12 (Current Month):**
- ✅ summons: 6 files
- ✅ community_outreach: 24 files
- ✅ policy_training: 10 files
- ✅ response_time: 9 files
- ⚠️ uncategorized: 121 files (may need manual review)

**2025_10 (Previous Month):**
- ✅ summons: 4 files
- ✅ vcs_time_report: 3 files
- ✅ community_outreach: 2 files
- ✅ policy_training: 4 files

---

## Verification

### Check Exported Files
```powershell
Get-ChildItem "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports\*.csv"
```

### Check Organized Files
```powershell
$month = "2025_12"
$backfillPath = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\$month"
Get-ChildItem "$backfillPath\*\*.csv" -Recurse | Select-Object FullName
```

### Check Specific Categories
```powershell
# Check summons
Get-ChildItem "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\2025_12\summons\*.csv"

# Check overtime/timeoff
Get-ChildItem "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\2025_12\vcs_time_report\*.csv"

# Check community engagement
Get-ChildItem "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\2025_12\community_outreach\*.csv"

# Check policy training
Get-ChildItem "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\2025_12\policy_training\*.csv"
```

---

## Troubleshooting

### File Not Categorized Correctly

**Solution:** Rename file to match pattern, or manually move:

```powershell
# Example: Manually categorize a file
$source = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports\my_file.csv"
$dest = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\2025_12\summons\2025_12_my_file.csv"
Move-Item -Path $source -Destination $dest
```

### Archive Folder Doesn't Exist

**Solution:** Create archive folders:

```powershell
$month = "2025_12"
$basePath = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\$month"
$categories = @("arrest", "community_outreach", "policy_training")
foreach ($cat in $categories) {
    $archivePath = "$basePath\$cat\archive"
    if (-not (Test-Path $archivePath)) {
        New-Item -ItemType Directory -Path $archivePath -Force
    }
}
```

---

## Summary

**Backfill Visuals (Multi-Month):**
1. Export from Power BI → `_DropExports\`
2. Run `organize_backfill_exports.ps1`
3. Files moved to `Backfill\YYYY_MM\category\`

**Archive Visuals (Single Month):**
1. Export from Power BI → `_DropExports\`
2. Manually move to `Backfill\YYYY_MM\category\archive\`
3. Or create archive structure and organize manually

---

**Last Updated:** 2025-12-11  
**Status:** Ready for visual exports


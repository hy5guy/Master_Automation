# Power BI Visual Export Guide

**Date:** 2025-12-11  
**Purpose:** Guide for exporting and organizing Power BI visual data

---

## Visual Categories

### 📊 Backfill Visuals (Multi-Month Data)
These visuals show historical data across multiple months and need to be preserved in backfill:

| Visual Name | Category Folder | Script |
|------------|----------------|--------|
| Monthly Accrual and Usage Summary | `vcs_time_report` | overtime_timeoff |
| Response Times | `response_time` | Response_Times |
| Summons Data | `summons` | Summons |
| Community Engagement Data | `community_outreach` | Community_Engagment |
| Policy Training Monthly | `policy_training` | Policy_Training_Monthly |

### 📁 Archive Visuals (Single Month Data)
These visuals show only current month data - save for archive, not backfill:

| Visual Name | Archive Location | Notes |
|------------|-----------------|-------|
| TOP 5 ARREST LEADERS | `Backfill\YYYY_MM\arrest\archive\` | Single month snapshot |
| Arrest Distribution by Local, State & Out of State | `Backfill\YYYY_MM\arrest\archive\` | Single month snapshot |
| Arrest Categories by Type and Gender | `Backfill\YYYY_MM\arrest\archive\` | Single month snapshot |
| Engagement Initiatives by Bureau | `Backfill\YYYY_MM\community_outreach\archive\` | Single month snapshot |
| In-Person Training | `Backfill\YYYY_MM\policy_training\archive\` | Single month snapshot |

---

## Export Workflow

### Step 1: Export Visuals from Power BI

**For Backfill Visuals:**
1. Open Power BI report
2. Right-click on visual
3. Select "Export data" → "Summarized data"
4. Save to: `PowerBI_Data\_DropExports\`

**For Archive Visuals:**
1. Same export process
2. Save to: `PowerBI_Data\_DropExports\`
3. Will be moved to `archive\` subfolder

### Step 2: Organize Exports

Run the organization script:
```powershell
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data"
.\tools\organize_backfill_exports.ps1
```

**What it does:**
- Reads CSV files from `_DropExports\`
- Categorizes by filename patterns
- Moves to `Backfill\YYYY_MM\category\`
- Renames with month prefix: `YYYY_MM_Filename.csv`

---

## Visuals Needed for ETL Scripts

### 1. Summons
**Visual Name:** (Check Power BI report)
**Category:** `summons`
**Script:** `02_ETL_Scripts\Summons\main_orchestrator.py`
**Export Location:** `Backfill\YYYY_MM\summons\`
**Filename Pattern:** Contains "summon", "moving", "parking", or "violation"

### 2. Overtime TimeOff
**Visual Name:** "Monthly Accrual and Usage Summary"
**Category:** `vcs_time_report`
**Script:** `02_ETL_Scripts\Overtime_TimeOff\overtime_timeoff_13month_sworn_breakdown_v11.py`
**Export Location:** `Backfill\YYYY_MM\vcs_time_report\`
**Filename Pattern:** Contains "monthly.*accrual", "vcs.*time", or "time.*report"

### 3. Community Engagement
**Visual Name:** (Check Power BI report)
**Category:** `community_outreach`
**Script:** `02_ETL_Scripts\Community_Engagment\deploy_production.py`
**Export Location:** `Backfill\YYYY_MM\community_outreach\`
**Filename Pattern:** Contains "community", "outreach", or "engagement"

### 4. Policy Training Monthly
**Visual Name:** (Check Power BI report - monthly training data)
**Category:** `policy_training`
**Script:** `02_ETL_Scripts\Policy_Training_Monthly\` (currently disabled - no Python files)
**Export Location:** `Backfill\YYYY_MM\policy_training\`
**Filename Pattern:** Contains "policy" or "training"

---

## Export Checklist

### Backfill Visuals (Required)
- [ ] **Summons** - Export monthly summons data
- [ ] **Overtime TimeOff** - Export "Monthly Accrual and Usage Summary"
- [ ] **Community Engagement** - Export community engagement data
- [ ] **Policy Training** - Export monthly training data (if available)
- [ ] **Response Times** - Export response time data (if not already done)

### Archive Visuals (Optional - for reference)
- [ ] TOP 5 ARREST LEADERS
- [ ] Arrest Distribution by Local, State & Out of State
- [ ] Arrest Categories by Type and Gender
- [ ] Engagement Initiatives by Bureau
- [ ] In-Person Training

---

## Filename Patterns (Auto-Detection)

The `organize_backfill_exports.ps1` script automatically categorizes files based on filename:

| Pattern | Category |
|---------|----------|
| `summon`, `moving.*parking`, `violation` | `summons` |
| `vcs.*time`, `monthly.*accrual`, `time.*report` | `vcs_time_report` |
| `community`, `outreach`, `engagement` | `community_outreach` |
| `policy`, `training` | `policy_training` |
| `response.*time` | `response_time` |

**Tip:** When exporting, use descriptive filenames that match these patterns for automatic categorization.

---

## Manual Organization (If Needed)

If automatic categorization fails, manually move files:

```powershell
# Example: Move summons file
$source = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\_DropExports\summons_data.csv"
$dest = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\Backfill\2025_12\summons\2025_12_summons_data.csv"
Move-Item -Path $source -Destination $dest
```

---

## Archive Folder Structure

For single-month visuals that don't need backfill:

```
Backfill\YYYY_MM\
├── category\
│   ├── archive\          # Single-month visuals
│   │   ├── visual1.csv
│   │   └── visual2.csv
│   └── backfill_data.csv # Multi-month data
```

**Note:** Archive folder may need to be created manually if not auto-created by organization script.

---

## Next Steps

1. **Export Visuals:**
   - Open Power BI report
   - Export each visual listed above
   - Save to `_DropExports\` folder

2. **Organize:**
   ```powershell
   cd "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data"
   .\tools\organize_backfill_exports.ps1
   ```

3. **Verify:**
   ```powershell
   Get-ChildItem "Backfill\2025_12\*\*.csv" -Recurse
   ```

4. **Archive Single-Month Visuals:**
   - Manually move to `archive\` subfolders if needed
   - Or create archive structure and move files

---

**Last Updated:** 2025-12-11  
**Status:** Ready for visual exports


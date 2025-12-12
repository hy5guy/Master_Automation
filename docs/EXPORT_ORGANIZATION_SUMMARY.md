# Visual Export Organization Summary

**Date:** 2025-12-11  
**Month:** 2025_12  
**Status:** ✅ Organized (with 3 uncategorized files)

---

## ✅ Successfully Organized

### 📊 Backfill Files (Multi-Month Data)

#### Summons (4 files)
- ✅ `2025_12_Summons  Moving & Parking  All Bureaus.csv`
- ✅ `2025_12_Department-Wide Summons  Moving and Parking.csv`
- ✅ `2025_12_Top 5 Moving Violations - Department Wide.csv`
- ✅ `2025_12_Top 5 Non-Parking Violations - Department Wide.csv`

**Location:** `Backfill\2025_12\summons\`

#### Overtime/TimeOff (1 file)
- ✅ `2025_12_Monthly Accrual and Usage Summary.csv`

**Location:** `Backfill\2025_12\vcs_time_report\`

#### Community Engagement (1 file)
- ✅ `2025_12_Engagement Initiatives by Bureau.csv` (already existed, skipped duplicate)

**Location:** `Backfill\2025_12\community_outreach\`

#### Policy Training (3 files)
- ✅ `2025_12_Training Cost by Delivery Method.csv`
- ✅ `2025_12_Training Metrics Comprehensive Report.csv`
- ✅ `2025_12_In-Person Training.csv` (moved to archive - see below)

**Location:** `Backfill\2025_12\policy_training\`

---

### 📁 Archive Files (Single-Month Snapshots)

#### Arrest Archive (3 files)
- ✅ `2025_12_TOP_5_ARREST_LEADERS.csv`
- ✅ `2025_12_Arrest_Distribution.csv`
- ✅ `2025_12_Arrest_Categories.csv`

**Location:** `Backfill\2025_12\arrest\archive\`

#### Community Outreach Archive (1 file)
- ✅ `2025_12_Engagement_Initiatives_by_Bureau.csv`

**Location:** `Backfill\2025_12\community_outreach\archive\`

#### Policy Training Archive (1 file)
- ✅ `2025_12_In_Person_Training.csv`

**Location:** `Backfill\2025_12\policy_training\archive\`

---

## ⚠️ Uncategorized Files (Need Manual Review)

These files could not be automatically categorized and remain in `_DropExports\`:

1. **Incident Count by Date and Event Type.csv**
   - **Suggested Category:** `detectives` or `patrol`
   - **Action:** Review file content and manually categorize

2. **Incident Distribution by Event Type.csv**
   - **Suggested Category:** `detectives` or `patrol`
   - **Action:** Review file content and manually categorize

3. **Use of Force Incident Matrix.csv**
   - **Suggested Category:** `detectives` or create new category
   - **Action:** Review file content and manually categorize

**To Manually Categorize:**
```powershell
# Example: Move to detectives category
$source = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports\Incident Count by Date and Event Type.csv"
$dest = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\2025_12\detectives\2025_12_Incident_Count_by_Date_and_Event_Type.csv"
Move-Item -Path $source -Destination $dest
```

---

## 📋 Files Organized by Category

| Category | Backfill Files | Archive Files | Total |
|----------|---------------|---------------|-------|
| **summons** | 4 | 0 | 4 |
| **vcs_time_report** | 1 | 0 | 1 |
| **community_outreach** | 1 | 1 | 2 |
| **policy_training** | 2 | 1 | 3 |
| **arrest** | 0 | 3 | 3 |
| **Other categories** | 9 | 0 | 9 |
| **Uncategorized** | 3 | 0 | 3 |
| **TOTAL** | **20** | **5** | **25** |

---

## ✅ Required Visuals Status

### For ETL Scripts

| Visual | Status | Location |
|--------|--------|----------|
| **Summons** | ✅ Organized | `Backfill\2025_12\summons\` (4 files) |
| **Monthly Accrual and Usage Summary** | ✅ Organized | `Backfill\2025_12\vcs_time_report\` |
| **Community Engagement** | ✅ Organized | `Backfill\2025_12\community_outreach\` |
| **Policy Training Monthly** | ✅ Organized | `Backfill\2025_12\policy_training\` |

### Archive Visuals

| Visual | Status | Location |
|--------|--------|----------|
| TOP 5 ARREST LEADERS | ✅ Archived | `Backfill\2025_12\arrest\archive\` |
| Arrest Distribution | ✅ Archived | `Backfill\2025_12\arrest\archive\` |
| Arrest Categories | ✅ Archived | `Backfill\2025_12\arrest\archive\` |
| Engagement Initiatives by Bureau | ✅ Archived | `Backfill\2025_12\community_outreach\archive\` |
| In-Person Training | ✅ Archived | `Backfill\2025_12\policy_training\archive\` |

---

## Next Steps

### Immediate
1. ✅ **Review uncategorized files** - Determine correct categories
2. ✅ **Manually categorize** - Move uncategorized files to appropriate folders
3. ✅ **Verify file locations** - Confirm all required visuals are in correct locations

### Future
- Export visuals monthly following this workflow
- Use archive folders for single-month snapshots
- Keep backfill folders for multi-month historical data

---

## Verification Commands

### Check Backfill Files
```powershell
$month = "2025_12"
$basePath = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\$month"

# Summons
Get-ChildItem "$basePath\summons\*.csv"

# Overtime/TimeOff
Get-ChildItem "$basePath\vcs_time_report\*.csv"

# Community Engagement
Get-ChildItem "$basePath\community_outreach\*.csv" | Where-Object { $_.Name -notlike "*archive*" }

# Policy Training
Get-ChildItem "$basePath\policy_training\*.csv" | Where-Object { $_.Name -notlike "*archive*" }
```

### Check Archive Files
```powershell
Get-ChildItem "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\2025_12\*\archive\*.csv" -Recurse
```

### Check Uncategorized
```powershell
Get-ChildItem "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports\*.csv"
```

---

**Status:** ✅ **Organization Complete**  
**Action Required:** Review and categorize 3 uncategorized files


# Backfill Data Paths - Current Status

**Date:** 2025-12-11  
**Issue:** Some scripts still reference old backfill paths

---

## Current Backfill Directory Location

**✅ New Location (Correct):**
```
C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\
├── _TEMPLATE_YYYY_MM\
├── 2025_09\
│   ├── arrest\
│   ├── chief_law_enforcement_duties\
│   ├── chief_projects\
│   └── vcs_time_report\
├── 2025_10\
├── 2025_11\
└── ...
```

**❌ Old Location (Still Referenced):**
```
C:\Dev\PowerBI_Date\Backfill\  (OLD - Needs Update)
```

---

## Scripts Using Backfill Data

### 1. Response Times Script ⚠️ **NEEDS UPDATE**

**Script:** `02_ETL_Scripts\Response_Times\response_time_diagnostic.py`

**Current Path (Line 32):**
```python
BACKFILL_CSV = Path(r"C:\Dev\PowerBI_Date\Backfill\2025_09\response_time\Average Response Times  Values are in mmss.csv")
```

**Should Be:**
```python
BACKFILL_CSV = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\2025_09\response_time\Average Response Times  Values are in mmss.csv")
```

**Status:** ❌ **Hardcoded old path - needs update**

---

### 2. Overtime TimeOff Script ✅ **Uses Relative Paths**

**Script:** `02_ETL_Scripts\Overtime_TimeOff\overtime_timeoff_13month_sworn_breakdown_v11.py`

**How It Works:**
- Script looks for prior CSV files in its own `analytics_output` directory
- Uses `find_prior_visual_csv()` function to locate previous month's data
- Documentation mentions backfill but script doesn't directly read from Backfill folder

**Backfill Reference in Documentation:**
- README.md mentions: `C:\Dev\PowerBI_Date\Backfill\2025_09\vcs_time_report\Monthly Accrual and Usage Summary.csv`
- This is for manual reference, not used by the script itself

**Status:** ✅ **Script doesn't directly use Backfill path (uses local analytics_output)**

---

### 3. Arrests Script ✅ **No Direct Backfill Path**

**Script:** `02_ETL_Scripts\Arrests\arrest_python_processor.py`

**How It Works:**
- Line 1019 mentions "backfill union" but refers to Power BI union operation
- Script outputs to: `01_DataSources\ARREST_DATA\Power_BI\`
- Uses `write_current_month()` function for standardized output
- No direct backfill file reading

**Status:** ✅ **No backfill path references**

---

### 4. Community Engagement Script ✅ **No Backfill References**

**Script:** `02_ETL_Scripts\Community_Engagment\deploy_production.py`

**Status:** ✅ **No backfill references found**

---

### 5. Summons Script ✅ **No Backfill References**

**Script:** `02_ETL_Scripts\Summons\main_orchestrator.py`

**Status:** ✅ **No backfill references found**

---

## Summary

### Scripts That Need Path Updates

| Script | File | Line | Old Path | Status |
|--------|------|------|----------|--------|
| **Response Times** | `response_time_diagnostic.py` | 32 | `C:\Dev\PowerBI_Date\Backfill\...` | ❌ **NEEDS UPDATE** |

### Scripts That Are OK

| Script | Status | Notes |
|--------|--------|-------|
| **Arrests** | ✅ OK | No direct backfill path |
| **Community Engagement** | ✅ OK | No backfill references |
| **Summons** | ✅ OK | No backfill references |
| **Overtime TimeOff** | ✅ OK | Uses local analytics_output, not Backfill folder |

---

## Action Required

### Update Response Times Script

**File:** `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Response_Times\response_time_diagnostic.py`

**Change Line 32 from:**
```python
BACKFILL_CSV = Path(r"C:\Dev\PowerBI_Date\Backfill\2025_09\response_time\Average Response Times  Values are in mmss.csv")
```

**To:**
```python
BACKFILL_CSV = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\2025_09\response_time\Average Response Times  Values are in mmss.csv")
```

**Note:** Verify the file exists at the new location first:
```powershell
Test-Path "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\2025_09\response_time\Average Response Times  Values are in mmss.csv"
```

---

## Backfill Directory Structure

**Location:** `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\`

**Subdirectories:**
- `2025_09\` - September 2025 backfill data
  - `arrest\` - Arrest data backfill
  - `vcs_time_report\` - Overtime/TimeOff backfill
  - `response_time\` - Response times backfill
  - `chief_law_enforcement_duties\`
  - `chief_projects\`
- `2025_10\` - October 2025 backfill data
- `2025_11\` - November 2025 backfill data
- `_TEMPLATE_YYYY_MM\` - Template structure

---

## How Scripts Use Backfill Data

### Response Times
- **Purpose:** Compare backfill values vs recalculated values
- **Usage:** Loads historical backfill CSV for diagnostic comparison
- **Function:** `load_backfill()` - reads backfill CSV and converts to standard format

### Overtime TimeOff
- **Purpose:** Anchor historical months to preserve backfill values
- **Usage:** Script looks for prior month's output in `analytics_output` directory
- **Note:** Documentation references backfill for manual restoration, but script uses local files

### Arrests
- **Purpose:** Output format compatible with Power BI backfill union
- **Usage:** Uses `write_current_month()` for standardized output format
- **Note:** Doesn't directly read backfill files

---

## Verification Commands

### Check if Backfill Directory Exists
```powershell
Test-Path "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill"
```

### List Backfill Subdirectories
```powershell
Get-ChildItem "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill" -Directory
```

### Check Response Times Backfill File
```powershell
$backfillFile = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\2025_09\response_time\Average Response Times  Values are in mmss.csv"
Test-Path $backfillFile
```

### Find All Old Path References
```powershell
Select-String -Path "02_ETL_Scripts\*\*.py" -Pattern "C:\\Dev\\PowerBI_Date" -Recurse
```

---

**Last Updated:** 2025-12-11  
**Status:** 1 script needs path update (Response Times)


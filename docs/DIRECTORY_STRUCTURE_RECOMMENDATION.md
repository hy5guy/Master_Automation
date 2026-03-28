# Directory Structure Recommendation: Response_Times Project

**Date:** 2025-12-10  
**Question:** Should Response_Times project stay in `02_ETL_Scripts/` or move to `Master_Automation/`?

---

## Current Structure

### Master_Automation (Orchestrator)
```
Master_Automation/
├── config/
│   └── scripts.json           # References external script paths
├── scripts/
│   ├── run_all_etl.ps1        # Orchestrator scripts
│   └── run_all_etl.bat
├── logs/                      # Execution logs
└── documentation files        # System documentation
```

**Purpose:** Centralized orchestrator - references ETL scripts in other locations

### 02_ETL_Scripts (ETL Projects Repository)
```
02_ETL_Scripts/
├── Arrests/                   # ETL project
├── Overtime_TimeOff/          # ETL project
├── Community_Engagement/       # ETL project
├── Policy_Training_Monthly/   # ETL project
├── Response_Times/            # ETL project ⭐
├── Summons/                   # ETL project
└── ...
```

**Purpose:** Repository for all individual ETL script projects

---

## Analysis

### Current Pattern (All Other Scripts):

Looking at `config/scripts.json`, all scripts reference external paths:

| Script | Current Path |
|--------|-------------|
| Arrests | `C:\...\02_ETL_Scripts\Arrests` |
| Community Engagement | `C:\...\02_ETL_Scripts\Community_Engagement` |
| Overtime TimeOff | `C:\...\02_ETL_Scripts\Overtime_TimeOff` |
| Policy Training | `C:\...\02_ETL_Scripts\Policy_Training_Monthly` |
| **Response Times** | `C:\...\02_ETL_Scripts\Response_Times` ⭐ |
| Summons | `C:\...\02_ETL_Scripts\Summons` |

**Pattern:** All ETL projects are in `02_ETL_Scripts/`, Master_Automation references them

---

## Recommendation: **KEEP Response_Times in 02_ETL_Scripts/**

### ✅ Reasons to Keep Current Location:

1. **Consistency with Other Projects**
   - All other ETL scripts are in `02_ETL_Scripts/`
   - Response_Times follows the same pattern
   - Maintains uniform structure

2. **Master_Automation is an Orchestrator, Not Repository**
   - Master_Automation's role: orchestration, configuration, logging
   - It references scripts, doesn't contain them
   - Separates concerns: orchestration vs. script development

3. **Easier Maintenance**
   - Each ETL project is self-contained in its own directory
   - Developers work in `02_ETL_Scripts/Response_Times/`
   - Orchestrator is separate, cleaner separation

4. **Scalability**
   - Easy to add new ETL projects (just add to `02_ETL_Scripts/`)
   - Master_Automation doesn't grow with each project
   - Cleaner Git structure (if using version control)

5. **No Path Changes Needed**
   - Current `scripts.json` already points to correct location
   - No configuration updates required
   - New script (`process_cad_data_13month_rolling.py`) is in correct place

### ❌ Reasons NOT to Move to Master_Automation:

1. **Breaks Existing Pattern**
   - All other scripts are in `02_ETL_Scripts/`
   - Would create inconsistency

2. **Master_Automation Would Become Cluttered**
   - Response_Times has many files (122 Python files, documentation, etc.)
   - Would mix orchestration code with ETL projects
   - Harder to navigate

3. **Requires Configuration Update**
   - Would need to update `scripts.json` path
   - No benefit from the change

4. **Git/Version Control Issues**
   - If using version control, mixing concerns makes history messier
   - Separate repos/directories allow independent versioning

---

## What Needs to Be Updated

### ✅ Update scripts.json Entry

The current entry references the old script:
```json
{
  "name": "Response Times",
  "path": "C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\02_ETL_Scripts\\Response_Times",
  "script": "scripts\\process_cad_data_for_powerbi_FINAL.py",  ← OLD
  ...
}
```

**Should be updated to:**
```json
{
  "name": "Response Times",
  "path": "C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\02_ETL_Scripts\\Response_Times",
  "script": "process_cad_data_13month_rolling.py",  ← NEW (13-month rolling)
  "enabled": true,
  "output_to_powerbi": true,
  "order": 5,
  "timeout_minutes": 15,
  "output_patterns": [
    "output\\*Average_Response_Times*.csv",
    "output\\*Response_Times_Detailed.csv"
  ],
  "keywords": ["response", "time", "rolling", "13-month"],
  "notes": "13-month rolling calculation script. Processes monthly CAD exports with deduplication, 101 admin incident filters, and Self-Initiated filtering. Validated: Emergency 2:59 min (309 calls) for Nov 2025."
}
```

**Note:** Script is in root of `Response_Times/`, not in `scripts/` subdirectory

---

## Final Recommendation

### ✅ **KEEP Response_Times in `02_ETL_Scripts/Response_Times/`**

**Action Items:**
1. ✅ Keep project where it is (no move needed)
2. ✅ Update `Master_Automation/config/scripts.json` to reference new script
3. ✅ Update script name to `process_cad_data_13month_rolling.py`
4. ✅ Update output patterns to match new output files
5. ✅ Update documentation to reflect new script

**No relocation needed - current structure is correct!**

---

## Updated Directory Structure (No Changes)

```
02_ETL_Scripts/
└── Response_Times/                    ← STAYS HERE
    ├── process_cad_data_13month_rolling.py  ← NEW SCRIPT
    ├── scripts/                              ← OLD SCRIPTS (reference)
    ├── output/                               ← OUTPUT FILES
    ├── documentation/                       ← DOCS
    └── ...

Master_Automation/                     ← ORCHESTRATOR ONLY
├── config/
│   └── scripts.json                   ← UPDATE PATH HERE
├── scripts/
│   └── run_all_etl.ps1                ← CALLS EXTERNAL SCRIPTS
└── ...
```

---

## Summary

**Answer: Keep Response_Times in `02_ETL_Scripts/Response_Times/`**

- ✅ Maintains consistency with other ETL projects
- ✅ Master_Automation stays focused on orchestration
- ✅ No relocation needed
- ✅ Just update `scripts.json` configuration


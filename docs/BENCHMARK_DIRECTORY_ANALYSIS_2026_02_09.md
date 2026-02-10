# Benchmark Data Directory Analysis & Recommendation

**Date**: February 9, 2026  
**Issue**: Duplicate Benchmark directories with overly complex structure  
**Status**: Analysis complete, recommendations provided

---

## Current Situation

### Duplicate Directories Found

**Directory 1**: `05_EXPORTS\_Benchmark\` (with underscore)
- **Structure**: Extremely complex nested hierarchy
- **Depth**: Up to 6-7 levels deep
- **Total subdirectories**: 90+ folders
- **Purpose**: Appears to be comprehensive historical archive

**Directory 2**: `05_EXPORTS\Benchmark\` (without underscore)
- **Structure**: Simple 3-folder layout
- **Depth**: 2 levels (root → event type)
- **Total subdirectories**: 3 folders (show_force, use_force, vehicle_pursuit)
- **Purpose**: Appears to be simplified structure

---

## _Benchmark Directory Structure Analysis

### Complexity Level: 🔴 **VERY HIGH**

**Main Categories** (9 top-level folders):
```
_Benchmark/
├── all_events_combined/
├── by_event_type/          (with archives subfolders)
├── by_time_period/         (rolling_13month, ytd_current)
├── show_force/             (complete_report, officer_report)
│   ├── complete_report/
│   │   ├── all_time/
│   │   └── full_year/      (2022-2028 folders!)
│   └── officer_report/
│       └── full_year/      (2022-2028 folders!)
├── use_force/              (complete_report, officer_report, summary)
│   ├── complete_report/
│   │   ├── all_time/
│   │   └── full_year/      (2001, 2020-2028 folders!)
│   ├── officer_report/
│   │   └── full_year/      (2001, 2020-2028 folders!)
│   └── summary/
│       └── full_year/      (2020-2028 folders!)
└── vehicle_pursuit/        (complete_report, officer_report)
    ├── complete_report/
    │   ├── all_time/
    │   └── full_year/      (2019, 2021-2028 folders!)
    └── officer_report/
        └── full_year/      (2019-2028 folders!)
```

**Issues Identified**:
1. ⚠️ **Future years**: Folders for 2027 and 2028 already exist (likely pre-created)
2. ⚠️ **Deep nesting**: 6-7 levels deep makes navigation difficult
3. ⚠️ **Duplication**: Multiple ways to organize same data (by_event_type vs direct event folders)
4. ⚠️ **Complexity**: 90+ total subdirectories

---

## Benchmark Directory Structure (Simple)

### Complexity Level: 🟢 **LOW**

```
Benchmark/
├── show_force/
├── use_force/
└── vehicle_pursuit/
```

**Advantages**:
- ✅ Simple 2-level structure
- ✅ Easy to navigate
- ✅ Clear event type organization
- ✅ Only 3 folders total

---

## Master_Automation Configuration Status

**Checked**: `config\scripts.json`  
**Result**: ❌ **No Benchmark workflow configured**

Benchmark data is **NOT** currently part of the Master_Automation ETL pipeline.

**Implications**:
- Benchmark exports appear to be manual or from another process
- Not automated through Master_Automation scripts
- Directory structure doesn't impact current automation run

---

## Recommendations

### Option 1: Consolidate to Simple Structure (RECOMMENDED)

**Action**: Use `05_EXPORTS\Benchmark\` (simple) as primary location

**Steps**:
1. Identify which January 2026 files you need from `_Benchmark`
2. Copy those specific files to appropriate folders in simple `Benchmark\`
3. Archive or delete `_Benchmark` folder

**Benefits**:
- ✅ Much simpler to navigate
- ✅ Easier to maintain
- ✅ Faster file operations
- ✅ Less confusing

**Simple Structure to Use**:
```
Benchmark/
├── show_force/
│   └── 2026_01_show_force_report.csv
├── use_force/
│   └── 2026_01_use_force_report.csv
└── vehicle_pursuit/
    └── 2026_01_vehicle_pursuit_report.csv
```

### Option 2: Keep _Benchmark for Archives Only

**Action**: Use `_Benchmark` as historical archive, `Benchmark` for active data

**Organization**:
- **05_EXPORTS\Benchmark\** → Current month / active data
- **05_EXPORTS\_Benchmark\** → Historical archive (read-only)

**Benefits**:
- ✅ Preserves historical structure
- ✅ Active data stays simple
- ✅ Clear separation of current vs archive

### Option 3: Standardize on One Structure

**Action**: Pick one directory and delete the other

**If keeping _Benchmark**:
- Simplify the structure (flatten some levels)
- Remove future year folders (2027, 2028)
- Consolidate duplicate organizational schemes

**If keeping Benchmark**:
- Move any January 2026 files from _Benchmark
- Delete _Benchmark entirely

---

## Impact on Master_Automation

### Current Impact: ✅ **NONE**

Benchmark data is not configured in `scripts.json`, so:
- ✅ Doesn't affect today's automation run
- ✅ No validation checks for Benchmark data
- ✅ No ETL scripts processing Benchmark exports

### If Adding Benchmark to Automation (Future)

**Considerations**:
1. Decide on single source directory
2. Define expected file naming pattern
3. Add to `scripts.json` with appropriate order
4. Create validation logic
5. Document expected file structure

**Recommended Pattern** (if adding):
```
05_EXPORTS\Benchmark\
├── use_force\
│   └── YYYY_MM_use_force.csv
├── show_force\
│   └── YYYY_MM_show_force.csv
└── vehicle_pursuit\
    └── YYYY_MM_vehicle_pursuit.csv
```

---

## Decision Guide

### Quick Decision Tree

```
Do you need the complex _Benchmark structure?
│
├─ NO → Delete _Benchmark, use simple Benchmark/ ✅ RECOMMENDED
│
└─ YES → Is it for archives only?
    │
    ├─ YES → Keep _Benchmark as archive, use Benchmark/ for active
    │
    └─ NO → Simplify _Benchmark structure:
            - Remove future year folders
            - Flatten unnecessary nesting
            - Document organizational logic
```

### Questions to Answer

1. **Are January 2026 files in _Benchmark or Benchmark?**
   - Where exactly are they located?

2. **Do you use the complex organizational structure?**
   - By event type AND by time period?
   - Complete reports AND officer reports AND summaries?

3. **Are future year folders (2027, 2028) needed?**
   - Or can they be created as needed?

4. **Is Benchmark data used in Power BI?**
   - If so, which directory does Power BI read from?

5. **Should Benchmark be added to Master_Automation?**
   - Or is it managed separately?

---

## Immediate Action for Today's Run

### ✅ No Action Required

**Reason**: Benchmark is not in automation configuration

**For today's Master_Automation run**:
- ✅ Benchmark directories don't affect execution
- ✅ No validation checks will run for Benchmark
- ✅ No ETL processing of Benchmark data
- ✅ Proceed with automation as planned

**Post-automation cleanup**:
- ⏳ Decide on consolidation strategy
- ⏳ Locate January 2026 Benchmark files
- ⏳ Implement chosen structure
- ⏳ Consider adding to automation (optional)

---

## Consolidation Script (If Needed)

If you decide to consolidate, I can create a PowerShell script to:
1. Find all January 2026 files in _Benchmark
2. Copy to simple Benchmark/ structure
3. Archive or delete _Benchmark
4. Validate file counts

**Would you like me to create this script?**

---

## Summary

**Current Status**:
- ❌ Two Benchmark directories exist
- ⚠️ _Benchmark has 90+ subdirectories (very complex)
- ✅ Benchmark has 3 subdirectories (simple)
- ❌ Not configured in Master_Automation
- ✅ Doesn't affect today's automation run

**Recommendation**:
- ✅ Use simple `Benchmark/` structure going forward
- ⏳ Consolidate or archive `_Benchmark` after automation
- ℹ️ Consider adding to Master_Automation in future (optional)

**Today's Action**:
- ✅ **NONE REQUIRED** - Proceed with automation run
- ⏳ Address Benchmark consolidation post-automation

---

**Last Updated**: February 9, 2026  
**Status**: Analysis complete, no blocking issues  
**Impact on Automation**: None (not configured)

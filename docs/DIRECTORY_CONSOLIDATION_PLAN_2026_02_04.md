# Directory Consolidation Plan

**Date:** 2026-02-04  
**Task:** Merge duplicate directories and organize structure

---

## Current State Analysis

### 1. OUTPUT vs OUTPUTS (Duplicate Directories)
**Problem:** Two similar directories with overlapping content

**`output/` (singular)** - 8 files
- `2025_12_Arrest Categories by Type and Gender.csv`
- `2025_12_Arrest Distribution by Local, State.csv`
- `2025_12_Monthly Accrual and Usage Summary.csv`
- `2025_12_TOP 5 ARREST LEADERS.csv`
- `2026_01_13_18_32_31_Monthly Accrual and Usage Summary.csv`
- `2026_01_13_18_41_43_Monthly Accrual and Usage Summary.csv`
- `cad_data_for_powerbi_final.csv`
- `TimeOffActivity.xls`

**`outputs/` (plural)** - Current structure:
- `community_engagement/` - 6 files
- `large_exports/` - 2 files (37MB total)
- `metadata/` - 6 files
- `misc/` - 7 files
- `summons_validation/` - 11 files
- `visual_exports/` - 21 files
- **PLUS 4 files in root** of outputs/ (duplicates from output/)

**Decision:** ✅ Merge `output/` into `outputs/` and delete `output/`

---

### 2. VERIFICATION_REPORTS vs VERIFICATIONS (Related Directories)
**Problem:** Two directories for verification - one with reports, one with code

**`verification_reports/`** - 2 files (output reports)
- `ARRESTS_MONTHLY_VERIFICATION_REPORT.md`
- `OVERTIME_TIMEOFF_MONTHLY_VERIFICATION_REPORT.md`

**`verifications/`** - Python verification framework (5 Python files + pycache)
- `arrests_verifier.py`
- `etl_verification_framework.py`
- `overtime_timeoff_verifier.py`
- `README.md`
- `run_all_verifications.py`
- `__pycache__/` (3 compiled files)

**Decision:** ✅ Merge reports into verifications folder
- Keep `verifications/` as main directory
- Move reports to `verifications/reports/`
- This groups all verification-related files together

---

### 3. M_CODE Directory (Power BI Query Code)

**`m_code/`** - 13 files + archive subdirectory
- Active M code files (13 .m files)
- `archive/` subdirectory (17 old .m files)

**Purpose:** Contains Power BI M code queries for data transformations

**Decision:** ✅ Keep as standalone in root
**Reasoning:**
1. **Separate concern** - M code is Power BI-specific, not ETL scripts
2. **Frequent access** - Power BI developers need quick access
3. **Version control** - Archive structure already in place
4. **Documentation references** - Already referenced in docs as `m_code/`
5. **Professional standard** - Common to have language-specific code folders in root

**Alternative considered:** Move to `config/m_code/` - ❌ Rejected
- M code is not configuration data
- Would make it harder to find
- Breaking existing documentation references

---

## Consolidation Plan

### Phase 1: Merge OUTPUT → OUTPUTS

1. **Move unique files from `output/` to appropriate `outputs/` subdirectories:**
   - Arrest files → `outputs/arrests/` (new subdirectory)
   - Monthly Accrual files → `outputs/visual_exports/`
   - CAD data file → `outputs/misc/`
   - TimeOffActivity.xls → `outputs/misc/`

2. **Remove duplicate files** (already exist in `outputs/`)

3. **Delete empty `output/` directory**

### Phase 2: Merge VERIFICATION_REPORTS → VERIFICATIONS

1. **Create `verifications/reports/` subdirectory**

2. **Move report files:**
   - `ARRESTS_MONTHLY_VERIFICATION_REPORT.md` → `verifications/reports/`
   - `OVERTIME_TIMEOFF_MONTHLY_VERIFICATION_REPORT.md` → `verifications/reports/`

3. **Update `verifications/README.md`** to document new structure

4. **Delete empty `verification_reports/` directory**

### Phase 3: Organize M_CODE (No Move Required)

1. **Keep in root** - No action needed

2. **Document structure** in main README.md

3. **Consider:** Add `.gitignore` entry for `m_code/archive/*` if not needed in git

---

## Final Directory Structure

```
Master_Automation/
├── config/
├── docs/
├── logs/
├── m_code/                          ← KEEP IN ROOT
│   ├── archive/                     (17 archived .m files)
│   └── (13 active .m files)
├── outputs/                         ← CONSOLIDATED (singular "output" merged here)
│   ├── arrests/                     (new - from output/)
│   ├── community_engagement/
│   ├── large_exports/
│   ├── metadata/
│   ├── misc/
│   ├── summons_validation/
│   └── visual_exports/
├── scripts/
│   └── _testing/
└── verifications/                   ← CONSOLIDATED (reports merged here)
    ├── reports/                     (new - from verification_reports/)
    ├── __pycache__/
    ├── arrests_verifier.py
    ├── etl_verification_framework.py
    ├── overtime_timeoff_verifier.py
    ├── README.md
    └── run_all_verifications.py
```

---

## Benefits

### Organization
- ✅ Single `outputs/` directory for all output files
- ✅ Single `verifications/` directory for all verification code and reports
- ✅ Clear separation: `m_code/` for Power BI, `scripts/` for Python, `verifications/` for testing

### Maintenance
- ✅ Easier to find files (no confusion between output/outputs)
- ✅ Verification framework and reports in one place
- ✅ M code easily accessible in root for Power BI developers

### Professional Structure
- ✅ Follows industry standards
- ✅ Language-specific code in root folders (m_code, scripts)
- ✅ Output/results in dedicated outputs folder
- ✅ Testing/verification grouped together

---

## Execution Steps

### Step 1: Create New Subdirectories
```powershell
New-Item "outputs/arrests" -ItemType Directory
New-Item "verifications/reports" -ItemType Directory
```

### Step 2: Consolidate OUTPUT → OUTPUTS
```powershell
# Move arrest files to new arrests subdirectory
Move-Item "output/2025_12_Arrest*.csv" → "outputs/arrests/"
Move-Item "output/2025_12_TOP 5 ARREST LEADERS.csv" → "outputs/arrests/"

# Move monthly accrual files to visual_exports
Move-Item "output/*Monthly Accrual*.csv" → "outputs/visual_exports/"

# Move misc files
Move-Item "output/cad_data_for_powerbi_final.csv" → "outputs/misc/"
Move-Item "output/TimeOffActivity.xls" → "outputs/misc/"

# Remove duplicate files in outputs root
Remove-Item "outputs/2025_12_*.csv"

# Delete empty output directory
Remove-Item "output" -Recurse
```

### Step 3: Consolidate VERIFICATION_REPORTS → VERIFICATIONS
```powershell
# Move reports to verifications/reports
Move-Item "verification_reports/*.md" → "verifications/reports/"

# Delete empty verification_reports directory
Remove-Item "verification_reports" -Recurse
```

### Step 4: Update Documentation
- Update README.md with final directory structure
- Update verifications/README.md to reference reports/ subdirectory

---

## Impact Assessment

### No Impact On:
- ✅ ETL script execution (no script paths changed)
- ✅ Power BI M code access (staying in root)
- ✅ Verification framework (code stays in place)
- ✅ Project functionality

### Positive Impacts:
- ✅ Clearer directory structure
- ✅ No confusion between output/outputs
- ✅ Verification code and reports together
- ✅ Professional organization

---

**Plan Status:** Ready for execution  
**Estimated Time:** 2-3 minutes  
**Risk Level:** Low (all files preserved, just reorganized)

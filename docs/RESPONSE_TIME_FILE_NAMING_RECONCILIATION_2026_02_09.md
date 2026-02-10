# Response Time File Naming Reconciliation

**Date**: February 9, 2026  
**Status**: File naming pattern mismatch identified  
**Priority**: HIGH - Requires resolution before Response Times can run

---

## Issue Identified

The validation logic expects a different file structure than what exists in the timereport folder.

### What Validation Expects

**Path Pattern**:
```
C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_CAD\timereport\YYYY\YYYY_MM_Monthly_CAD.xlsx
```

**Example** (January 2026):
```
timereport\2026\2026_01_Monthly_CAD.xlsx
```

This follows the same pattern as **Summons E-ticket** exports:
- Year folder: `2026\`
- File naming: `YYYY_MM_descriptor.xlsx`

### What Actually Exists

**Current Structure**:
```
timereport/
├── monthly/
│   └── 2026_01_timereport.xlsx
└── yearly/
    ├── 2017/
    │   └── 2017_full_timereport.xlsx
    ├── 2018/
    │   └── 2018_full_timereport.xlsx
    └── ...
```

---

## Resolution Options

### Option 1: Update Validation to Match Current Structure (RECOMMENDED)

**Pros**:
- Uses existing file organization
- Clean separation between monthly and yearly reports
- Matches the separation pattern recommended for Arrests
- No file reorganization required

**Cons**:
- Different from other export patterns (Summons)
- Requires validation logic update

**Implementation**:

Update `scripts\run_all_etl.ps1` validation:

```powershell
"Response Times Monthly Generator" {
    $cadBase = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_CAD\timereport"
    
    # Check monthly subfolder first
    $monthlyFolder = Join-Path $cadBase "monthly"
    $cadPath = Join-Path $monthlyFolder "$($year)_$($month)_timereport.xlsx"
    
    if (Test-Path $cadPath) {
        Write-Success "  CAD timereport export found: $cadPath"
        $validationResults += [pscustomobject]@{ 
            File = "CAD Timereport Export"
            Path = $cadPath
            Status = "Found" 
        }
    }
    else {
        # Fallback: Try year-based structure
        $cadPath = Join-Path $cadBase "$year\$($year)_$($month)_Monthly_CAD.xlsx"
        
        if (Test-Path $cadPath) {
            Write-Success "  CAD timereport export found: $cadPath"
            $validationResults += [pscustomobject]@{ 
                File = "CAD Timereport Export"
                Path = $cadPath
                Status = "Found" 
            }
        }
        else {
            Write-Fail "  CAD timereport export NOT found"
            Write-Host "    Checked: $monthlyFolder\$($year)_$($month)_timereport.xlsx" -ForegroundColor Gray
            Write-Host "    Checked: $cadBase\$year\$($year)_$($month)_Monthly_CAD.xlsx" -ForegroundColor Gray
            $validationResults += [pscustomobject]@{ 
                File = "CAD Timereport Export"
                Path = "Multiple paths checked"
                Status = "Missing" 
            }
            $allValid = $false
        }
    }
}
```

### Option 2: Reorganize Files to Match Expected Pattern

**Pros**:
- Consistent with other export patterns
- Simpler validation logic
- Easier to maintain

**Cons**:
- Requires file reorganization
- Loses monthly/yearly separation
- Risk of breaking existing integrations

**Required Actions**:
1. Create year-based folder structure: `timereport\2026\`
2. Move/copy files from `monthly\` to appropriate year folders
3. Rename files to match pattern: `YYYY_MM_Monthly_CAD.xlsx`
4. Update any existing scripts that reference the old structure
5. Test thoroughly before committing

---

## Recommendation

**Choose Option 1**: Update validation to match current structure

**Reasoning**:
1. Respects existing file organization decisions
2. Maintains clean monthly/yearly separation (best practice)
3. Less risk of breaking existing workflows
4. No data migration required
5. Aligns with Arrests directory guidance (separate monthly/yearly)

---

## Current File Examples

### Monthly Files
```
timereport/monthly/2026_01_timereport.xlsx
```

**Pattern**: `YYYY_MM_timereport.xlsx`  
**Location**: `timereport/monthly/`

### Yearly Files
```
timereport/yearly/2017/2017_full_timereport.xlsx
timereport/yearly/2018/2018_full_timereport.xlsx
...
timereport/yearly/2025/2025_full_timereport.xlsx
```

**Pattern**: `YYYY_full_timereport.xlsx`  
**Location**: `timereport/yearly/YYYY/`

---

## Implementation Steps (Option 1)

### Step 1: Update Validation Logic

- [ ] Update `scripts\run_all_etl.ps1` (Line ~218-248)
- [ ] Add primary check: `monthly/YYYY_MM_timereport.xlsx`
- [ ] Add fallback check: `YYYY/YYYY_MM_Monthly_CAD.xlsx`
- [ ] Add clear error messages showing both paths checked

### Step 2: Update Python Scripts

- [ ] Update `response_time_monthly_generator.py`
  - Input path: `timereport/monthly/`
  - File pattern: `YYYY_MM_timereport.xlsx`
  - Add logic to handle both patterns (future-proof)

- [ ] Update `response_time_diagnostic.py` (if needed)
  - Match same input path logic
  - Update any hardcoded paths

### Step 3: Test

```powershell
# 1. Run dry-run after validation update
.\scripts\run_all_etl.ps1 -DryRun

# Expected: "CAD timereport export found: [monthly path]"

# 2. Create test file in monthly folder if not present
# Copy existing file or create placeholder

# 3. Re-run validation
.\scripts\run_all_etl.ps1 -DryRun

# 4. Test single script execution (once Python updated)
.\scripts\run_etl_script.ps1 -ScriptName "Response Times Monthly Generator"
```

### Step 4: Document

- [ ] Update Python script docstrings with new paths
- [ ] Update configuration comments
- [ ] Add migration note to CHANGELOG.md
- [ ] Update README.md if needed

---

## Testing Checklist

### Pre-Update Tests
- [ ] Current dry-run shows expected "NOT found" message ✅
- [ ] timereport folder structure documented ✅
- [ ] File naming patterns identified ✅

### Post-Update Tests
- [ ] Dry-run finds monthly file correctly
- [ ] Dry-run handles missing file gracefully
- [ ] Fallback logic works for year-based structure
- [ ] Error messages are clear and helpful
- [ ] Python script reads correct file
- [ ] Output files generated correctly
- [ ] Power BI refresh works
- [ ] Data integrity verified

---

## Related Issues

This file naming pattern issue highlights a broader need:

### Export Standardization Opportunity

Different exports use different patterns:
- **Summons**: `E_Ticket/YYYY/YYYY_MM_eticket_export.csv`
- **Response Times (old)**: `monthly_export/YYYY/YYYY_MM_Monthly_CAD.xlsx`
- **Response Times (new)**: `timereport/monthly/YYYY_MM_timereport.xlsx`

**Future Enhancement**: Standardize export naming conventions across all workflows
- Document pattern choices and rationale
- Create export naming guidelines
- Update scripts to handle common variations
- Add flexible path resolution

---

## Next Actions

1. **Immediate**: Update validation logic (Option 1)
2. **Short-term**: Update Python scripts for new path
3. **Testing**: Verify end-to-end workflow
4. **Long-term**: Consider export standardization

---

**Decision Required**: Confirm Option 1 (update validation) is preferred approach  
**Blocked Until**: Validation update completed  
**Impact**: Response Times Monthly Generator cannot run until resolved

---

**Last Updated**: February 9, 2026  
**Status**: Issue identified, solution proposed, awaiting implementation

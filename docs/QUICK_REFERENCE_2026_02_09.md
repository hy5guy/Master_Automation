# Quick Reference - Automation Timing & Path Updates

**Date**: February 9, 2026  
**Status**: Validation Updated, Scripts Pending Review

---

## 06_Workspace_Management execution model

**Sequential Execution**: Scripts run in order based on `config\scripts.json`  
**Error Handling**: One failure does not stop remaining scripts  
**Parallel Execution**: Future enhancement only (not currently implemented)

### Key Commands

```powershell
# Preview + validate inputs
.\scripts\run_all_etl.ps1 -DryRun

# Run one workflow
.\scripts\run_etl_script.ps1 -ScriptName "Arrests"

# Run full sequence
.\scripts\run_all_etl.ps1
```

---

## Arrests - Directory Layout Guidance

### Recommendation
✅ **Keep monthly and yearly exports in separate subfolders**  
❌ **Do NOT mix monthly and yearly in one root folder**

### Reason
- Prevents overlap and double-count risk
- Reduces duplicate data issues already seen in other pipelines
- Maintains clean data lineage

### Update Checklist (If Required)

When `arrest_python_processor.py` needs folder structure updates:

- [ ] Set single base path (arrest export root)
- [ ] Implement recursive subfolder scanning
- [ ] Filter by filename pattern (monthly vs yearly)
- [ ] Prefer `.xlsx` when multiple formats exist
- [ ] Log selected input file path each run
- [ ] Test: `.\scripts\run_all_etl.ps1 -DryRun`
- [ ] Verify: Check for zero missing-input flags

**Script Location**: `02_ETL_Scripts\Arrests\arrest_python_processor.py`  
**Config**: `config\scripts.json` (Order: 1, Enabled: true)

---

## Response Times - Source Path Updated

### Path Change

**Old**: `05_EXPORTS\_CAD\monthly_export`  
**New**: `05_EXPORTS\_CAD\timereport`

### Directory Structure

```
timereport/
├── monthly/           # Monthly reports
│   └── 2026_01_timereport.xlsx
└── yearly/            # Yearly historical data
    ├── 2017/
    ├── 2018/
    ├── ...
    └── 2025/
```

### What's Updated

✅ **Validation in run_all_etl.ps1**
- Updated for both "Response Times" and "Response Times Monthly Generator"
- Now checks timereport folder instead of monthly_export

### What's Pending

⏳ **Python Scripts** (require review and update)
- `response_time_monthly_generator.py` - Update input path
- `response_time_diagnostic.py` - Update input path (if re-enabled)

⏳ **Power BI M Query** (decision required)
- Option A: Read directly from timereport
- Option B: Continue reading from Backfill (Python transforms)

### Fast Test Sequence

```powershell
# 1. Validate inputs
.\scripts\run_all_etl.ps1 -DryRun

# Expected: "CAD timereport export found: [path]"

# 2. Run Response Times only
.\scripts\run_etl_script.ps1 -ScriptName "Response Times Monthly Generator"

# 3. Verify outputs
Get-ChildItem "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\_DropExports" -Filter "*response*"

# 4. Refresh Power BI and verify data integrity
```

**Script Location**: `02_ETL_Scripts\Response_Times\response_time_monthly_generator.py`  
**Config**: `config\scripts.json` (Order: 5.5, Enabled: true)

---

## File Naming Discrepancy (Requires Clarification)

### Observed in timereport/monthly/
```
2026_01_timereport.xlsx
```

### Expected by validation
```
2026/2026_01_Monthly_CAD.xlsx
```

**Action Required**: Verify which naming pattern is correct and update either:
- The validation logic in `run_all_etl.ps1`, OR
- The Python script to handle the observed naming pattern

---

## Current ETL Workflow Order

From `config\scripts.json`:

1. **Arrests** (Order: 1) ✅ Enabled
2. **Community Engagement** (Order: 2) ✅ Enabled
3. **Overtime TimeOff** (Order: 3) ✅ Enabled
4. **Policy Training Monthly** (Order: 4) ❌ Disabled
5. **Response Times Diagnostic** (Order: 5) ❌ Disabled
6. **Response Times Monthly Generator** (Order: 5.5) ✅ Enabled
7. **Summons** (Order: 6) ✅ Enabled
8. **Summons Derived Outputs** (Order: 6.5) ✅ Enabled
9. **Arrest Data Source** (Order: 7) ❌ Disabled
10. **NIBRS** (Order: 8) ❌ Disabled

**Active Workflows**: 6  
**Disabled Workflows**: 4

---

## Next Actions

### Immediate
1. ✅ ~~Update validation paths in run_all_etl.ps1~~ (COMPLETE)
2. ⏳ Review Python script requirements (PENDING)
3. ⏳ Clarify file naming pattern discrepancy (PENDING)
4. ⏳ Test dry-run validation (READY TO TEST)

### Short Term
1. Update Python scripts for timereport path
2. Test end-to-end Response Times workflow
3. Verify Power BI data accuracy
4. Review Arrests directory structure needs

### Long Term
1. Implement parallel execution capability
2. Enhance error recovery mechanisms
3. Add automated data quality checks

---

## Documentation References

| Document | Purpose |
|----------|---------|
| `docs\IMPLEMENTATION_CHECKLIST_2026_02_09.md` | Complete implementation guide |
| `docs\RESPONSE_TIME_TIMEREPORT_MIGRATION_2026_02_09.md` | Detailed migration documentation |
| `config\scripts.json` | ETL orchestration configuration |
| `scripts\run_all_etl.ps1` | Main orchestrator with validation |
| `README.md` | Project overview and setup |

---

**Last Updated**: February 9, 2026  
**Status**: Validation layer complete, awaiting script review

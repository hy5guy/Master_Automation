# Summons Fix - Production Checklist
## 2026-02-17

## ✅ Completed (Automated)

- [x] **Data Classification Fixed**
  - Statute-based logic applied
  - Moving: 35 → 241 ✅
  - Title 39 violations: 100% classified as Moving ✅

- [x] **YearMonthKey Added**
  - Column created for integer-based sorting
  - Range: 0 to 202601
  - Latest month: 202601 (Jan 2026)

- [x] **Backup Created**
  - File: `summons_powerbi_latest_backup_20260217_062229.xlsx`
  - Location: `03_Staging\Summons\`

- [x] **M Code Created**
  - Top 5 Moving query
  - Top 5 Parking query
  - All Bureaus query

- [x] **ETL Updated**
  - `summons_etl_enhanced.py` classification function
  - Future runs will use correct logic

- [x] **Config Updated**
  - Paths corrected in `scripts.json`

## ⏳ Remaining (Manual - 3 minutes)

### In Power BI Desktop:

- [ ] **Open Report**
  - Open your monthly Power BI report

- [ ] **Update Queries** (2 minutes)
  - Home → Transform Data
  - Update/create 3 queries:
    1. `___Summons_Top5_Moving`
    2. `___Summons_Top5_Parking`
    3. `___Summons_All_Bureaus`
  - Copy code from: `Master_Automation\docs\SUMMONS_POWERBI_QUICKSTART.md`

- [ ] **Close & Apply** (30 seconds)
  - Click: Close & Apply
  - Wait for refresh

- [ ] **Verify Visuals** (30 seconds)
  - Check Top 5 Moving: ~241 total (was ~35)
  - Check Top 5 Parking: ~3,374 total (was ~3,495)
  - Check latest month: January 2026 displayed
  - Check sorting: 01-26 appears last (not first)

- [ ] **Save Report**
  - File → Save

## Verification Tests

### Test 1: Classification Correctness
```
✅ All Title 39 violations = Moving (M)
✅ Parking keywords = Parking (P)
✅ Moving count increased ~7x (35 → 241)
```

### Test 2: Date Sorting
```
✅ YearMonthKey uses integers (202601 > 202512)
✅ January 2026 sorts after December 2025
✅ Latest month identified correctly
```

### Test 3: Power BI Integration
```
⏳ Top 5 Moving query returns data
⏳ Top 5 Parking query returns data
⏳ All Bureaus query returns data
⏳ Counts match data file
```

## Rollback Plan (if needed)

If something goes wrong:

1. **Restore Data File**
   ```powershell
   Copy-Item "C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest_backup_20260217_062229.xlsx" -Destination "C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx" -Force
   ```

2. **Refresh Power BI**
   - Open Power BI
   - Home → Refresh
   - Data reverts to original state

3. **Keep M Code**
   - The new M code queries are still better
   - They use YearMonthKey which is correct pattern
   - Just need to re-apply data fix when ready

## Documentation

All documentation saved in:
- **Full Guide**: `docs/SUMMONS_REMEDIATION_2026_02_17.md`
- **Quick Start**: `docs/SUMMONS_REMEDIATION_QUICKSTART.md`
- **Summary**: `docs/SUMMONS_AUTOMATION_SUMMARY.md`
- **Power BI Guide**: `docs/SUMMONS_POWERBI_QUICKSTART.md`
- **This Checklist**: `docs/SUMMONS_PRODUCTION_CHECKLIST.md`

M Code files:
- `m_code/___Summons_Top5_Moving.m`
- `m_code/___Summons_Top5_Parking.m`
- `m_code/___Summons_All_Bureaus.m`

---

## Quick Command Reference

**Verify current data:**
```powershell
# Check if file exists
Test-Path "C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx"

# Check if backup exists
Test-Path "C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest_backup_20260217_062229.xlsx"
```

**Re-run classification fix:**
```powershell
C:\Users\RobertCarucci\AppData\Local\Microsoft\WindowsApps\python.exe "C:\Users\RobertCarucci\OneDrive - City of Hackensack\Master_Automation\scripts\patch_summons_direct.py"
```

---

**Status**: Data fixed, ready for Power BI refresh
**Est. Time to Complete**: 3 minutes
**Priority**: High (fixes production issue)
**Impact**: ~206 summons correctly reclassified

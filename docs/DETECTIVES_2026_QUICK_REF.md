# Detective Queries - 2026 Update Quick Reference

## What Was Done

Updated Power BI M code queries for restructured Detectives workbook (2026-only data, 12 months: 01-26 through 12-26).

---

## Files Created

1. **`m_code/detectives/___Detectives_2026.m`** - Updated main query
2. **`m_code/detectives/___Det_case_dispositions_clearance_2026.m`** - Updated CCD query
3. **`docs/DETECTIVES_2026_UPDATE_GUIDE.md`** - Complete deployment guide

---

## Key Changes

### Both Queries
- ✅ Added standard project headers (timestamp, author, purpose)
- ✅ Updated comments and structure for clarity
- ✅ Works with 2026-only data (01-26 through 12-26)

### ___Detectives Query
- Default year changed: "25" → "26"
- Rolling 13-month window (adapts to available 2026 data)
- Enhanced date parsing for 2026 format

### ___Det_case_dispositions_clearance Query
- Added `Text.Trim()` for row label matching (handles trailing spaces)
- Added "YTD Bureau Case Clearance %" to RequiredOrder
- Enhanced percentage normalization for decimal storage
- Handles both old ("50%") and new (0.50) formats

---

## Excel Changes (by Claude Add-on)

| Table | Old | New |
|-------|-----|-----|
| _mom_det | Multi-year columns | 01-26 through 12-26 only |
| _CCD_MOM | Multi-year columns | 01-26 through 12-26 only |
| Monthly sheets | N/A | 26_JAN through 26_DEC (12 sheets) |
| Formulas | Manual entry | XLOOKUP to monthly sheets |

---

## Deploy to Power BI

### Quick Steps

1. **Backup Current**
   - Duplicate `___Detectives` → `___Detectives_BACKUP_20260213`
   - Duplicate `___Det_case_dispositions_clearance` → `___Det_case_dispositions_clearance_BACKUP_20260213`

2. **Update ___Detectives**
   - Advanced Editor → Paste from `m_code/detectives/___Detectives_2026.m`

3. **Update ___Det_case_dispositions_clearance**
   - Advanced Editor → Paste from `m_code/detectives/___Det_case_dispositions_clearance_2026.m`

4. **Close & Apply**

5. **Verify**
   - Check visuals show 2026 data
   - Verify MonthsIncluded count
   - Check percentage values display correctly

---

## Verification Checklist

- [ ] No Power Query errors
- [ ] ___Detectives shows 2026 dates
- [ ] ___Det_case_dispositions_clearance shows 9-10 disposition types
- [ ] Percentage rows show decimal values (0.xx)
- [ ] Visuals display correctly
- [ ] Filters work
- [ ] MonthsIncluded = actual available months

---

## Common Issues

**"No data showing"**
- Check if monthly sheets in Excel have data
- Verify date filtering in Power Query

**"Percentage showing as whole numbers"**
- Check `Is_Percent` flag in Power Query
- Verify Excel percentage rows are decimals

**"Missing rows"**
- Check RequiredOrder list matches Excel labels
- Use Text.Trim() (already in updated code)

---

## Full Documentation

See: `docs/DETECTIVES_2026_UPDATE_GUIDE.md`

---

*Quick Reference - 2026-02-13*  
*Git Commit: b25f8f0*

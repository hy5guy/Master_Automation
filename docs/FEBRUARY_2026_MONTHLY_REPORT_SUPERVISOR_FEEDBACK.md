# February 2026 Monthly Report — Supervisor Feedback Action Plan

**Date:** 2026-03-13  
**Source:** Supervisor email review  
**Timing:** Changes can wait until first thing next week or after Cleary report

---

## Summary of Issues

| Page | Issue | Status |
|------|-------|--------|
| 8 | Department-Wide Summons chart missing Feb 2026; 12-25 and 01-26 numbers don't match January report | ✅ Fixed — Full January report backfill; ETL run 2026-03-14 |
| 11 | DFR slide needs NOTE box | Manual Power BI edit |
| 12 | Traffic Bureau parking fees ($115,283.87) not updating total | ✅ Fixed — Excel formulas + ___Traffic `type number` for decimals |
| 20 | REMU NIBRS Entries was 0 | ✅ Already updated by you |

---

## Page 8 — Department-Wide Summons | Moving and Parking

### Issues
1. **Missing February 2026 (02-26)** — Chart ends at 01-26
2. **12-25 and 01-26 mismatch** — Numbers differ from January's monthly report

### January Report Reference (from your comparison table)

| Month | M (Moving) | P (Parking) | Total |
|-------|------------|-------------|-------|
| 12-25 | 436 | 2,874 | 3,310 |
| 01-26 | 241 | 3,368 | 3,609 |

These are the values the February report should match for 12-25 and 01-26.

### Root Cause & Fix

**Data source:** `03_Staging\Summons\summons_slim_for_powerbi.csv`  
**Power BI query:** `summons_13month_trend` (loads from that CSV)  
**Window logic:** 13 months ending at `pReportMonth` (e.g., 02/01/2026 → 02-25 through 02-26)

**Steps:**

1. **Confirm February 2026 data in staging**
   - Open `summons_slim_for_powerbi.csv` and verify rows with `YearMonthKey = 202602`
   - If missing, run Summons ETL for February:
     ```powershell
     cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"
     python run_summons_etl.py --month 2026_02
     ```
   - Ensure February e-ticket export exists at:  
     `00_Raw_Data\Summons\2026_02_eticket_export.csv` (or equivalent path)

2. **Align 12-25 and 01-26 with January report**
   - If staging has different 12-25/01-26 values than January’s report, likely causes:
     - Staging was refreshed with different source/backfill
     - Backfill merge overwrote prior months
   - Compare `summons_slim_for_powerbi.csv` to January’s exported chart values
   - If needed, adjust backfill or re-run ETL so 12-25 and 01-26 match the January report

3. **Refresh Power BI**
   - Set `pReportMonth = #date(2026, 2, 1)` for the February report
   - Refresh all queries
   - Re-export the Department-Wide Summons visual and confirm 02-26 appears and 12-25/01-26 match January

---

## Page 11 — DFR Slide NOTE Box

### Request
Add a NOTE box with:

> "In February 20 Fire Zone summonses were issued utilizing the drone at 500 South River Street"

### Action (Manual in Power BI)

1. Open the February 2026 monthly report `.pbix`
2. Go to Page 11 (DFR / Drone page)
3. Insert → Text box (or Shapes → Rectangle)
4. Type the note text above
5. Style as a NOTE box (e.g., light background, border)
6. Save the report

No code or automation changes required.

---

## Page 12 — Traffic Bureau Parking Fees Total

### Issue
Tina entered **$115,293.90** for Parking Fees Collected (February 2026) in the last box before the total, but the total did not update.

### Source File
`Shared Folder\Compstat\Contributions\Traffic\Traffic_Monthly.xlsx`  
Table: `_mom_traffic`

### Likely Causes

1. **Excel formula range**
   - The “Total” column (or row) may sum a fixed range that doesn’t include the new month (e.g., 02-26)
   - Or the Parking Fees row is excluded from the total formula

2. **Cell format**
   - Value stored as text instead of number, so it’s not included in SUM

3. **Table structure**
   - New column for 02-26 not added to the table, so formulas don’t extend to it

### Action Steps

1. Open `Traffic_Monthly.xlsx`
2. Locate the `_mom_traffic` table
3. Find the “Parking Fees Collected” row and the “Total” or “Grand Total” cell
4. Check the formula:
   - Does it include the 02-26 column?
   - Does it include the Parking Fees row?
5. Update the formula so it:
   - Sums all month columns (including 02-26)
   - Includes the Parking Fees Collected row in any row-wise total
6. Confirm the cell with $115,293.90 is a number, not text (no leading apostrophe, General or Number format)

### Power BI Note (v1.18.7)
The `___Traffic` M code was updated to use `type number` (not `Int64.Type`) for month columns — preserves Parking Fees decimals. See `m_code/traffic/___Traffic.m`.

---

## Page 20 — REMU

Already updated by you (NIBRS Entries was 0). No further action.

---

## Checklist

- [x] Run Summons ETL for February 2026
- [x] Confirm `summons_slim_for_powerbi.csv` has 02-26 data
- [x] Align 12-25 and 01-26 with January report (full backfill)
- [x] Refresh Power BI with `pReportMonth = 02/01/2026`
- [ ] Add DFR NOTE box on Page 11 (manual)
- [x] Fix Traffic Bureau total formula in `Traffic_Monthly.xlsx`
- [ ] Re-publish February 2026 monthly report

---

*Generated from supervisor feedback 2026-03-13; updated 2026-03-14*

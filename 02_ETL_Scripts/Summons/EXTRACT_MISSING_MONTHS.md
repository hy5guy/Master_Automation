# Extract Missing Backfill Months

**Date:** 2026-01-11  
**Missing Months:** 03-25, 07-25

## March 2025 (03-25) Totals

**File:** `2025_03_eticket_export.csv`  
**Totals (Case Type Code):**
- Moving (M): **454**
- Parking (P): **3,097**
- Special (C): 77

**Add to backfill CSV:**
```
TYPE,Month_Year,Count of TICKET_NUMBER
M,03-25,454
P,03-25,3097
```

---

## July 2025 (07-25) Totals

**Status:** Need to check if export file exists  
**File:** `2025_07_eticket_export.csv`

---

## Backfill File Location

**File:** `C:\Dev\PowerBI_Date\Backfill\2025_09\summons\Hackensack Police Department - Summons Dashboard.csv`

**Expected Format:**
- Columns: `TYPE`, `Month_Year`, `Count of TICKET_NUMBER`
- Add rows for missing months in correct position

---

## Steps to Update

1. **Extract totals from e-ticket exports:**
   - ✅ March 2025: M=454, P=3,097 (extracted)
   - ⏳ July 2025: Check if file exists and extract totals

2. **Update backfill CSV:**
   - Open: `C:\Dev\PowerBI_Date\Backfill\2025_09\summons\Hackensack Police Department - Summons Dashboard.csv`
   - Add rows for 03-25 and 07-25
   - Ensure proper format: `TYPE,Month_Year,Count of TICKET_NUMBER`

3. **Re-run ETL script:**
   ```bash
   cd "C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Summons"
   python SummonsMaster_Simple.py
   ```

4. **Verify results:**
   - Check that 03-25 and 07-25 now appear in the output
   - Verify counts match the extracted totals

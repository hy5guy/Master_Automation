# Detective Queries - Excel Structure Mismatch Fix

**Date:** 2026-02-13  
**Status:** ✅ FIXED  
**Queries:** `___Detectives` and `___Det_case_dispositions_clearance`

---

## Problem Summary

Both Detective queries returned **empty preview tables** after the initial 2026 update attempt. Root cause analysis revealed the **actual Excel structure differed significantly from the expected structure** described in the Claude Excel prompt.

---

## Critical Mismatches Found

### 1. Date Format Mismatch

**Expected (per Claude prompt):**
- Column headers: `01-26`, `02-26`, `03-26`, etc. (MM-YY format)
- 2026-only data (12 columns: Jan-Dec 2026)

**Actual (verified via Python analysis):**
- Column headers: `23-Jun`, `23-Jul`, `24-Jan`, `26-Jan`, etc. (YY-MMM format)
- **Historical data from June 2023 to December 2026** (44 columns total!)
- Format examples: `26-Jan`, `26-Feb`, `25-Dec`, `24-Jun`

**Impact:**
- Date parsing logic failed completely (tried to parse `Number.From("Jan")` → error)
- All rows filtered out because no dates could be parsed
- Empty tables resulted

### 2. Data Scope Mismatch

**Expected:**
- 12 columns (01-26 through 12-26 only)
- Rolling 13-month window would need adjustment for limited data

**Actual:**
- 44 columns spanning **3.5 years** (Jun 2023 - Dec 2026)
- Rolling 13-month window logic is actually correct and needed

**Impact:**
- Hardcoded `StartFilterDate = #date(2026, 1, 1)` excluded all valid historical data
- Even if dates parsed correctly, the filter would have removed everything

### 3. Row Label Format Issues (CCD Query)

**Expected:**
- `"Monthly Bureau Case Clearance %"` (single space, no trailing space)
- `"YTD Bureau Case Clearance %"` (no trailing space)

**Actual (from Excel):**
- `"Monthly Bureau Case  Clearance % "` (DOUBLE space before "Clearance", trailing space)
- `"YTD Bureau Case Clearance % "` (trailing space)

**Impact:**
- Row filtering failed to match these percentage rows
- `List.Contains()` with trimmed text didn't match Excel's exact labels

---

## Fixes Applied

### Fix 1: Date Parsing Logic (Both Queries)

**Old logic (broken for YY-MMM format):**

```powerquery
// Tried to parse MM-YY format
MonthPart = Parts{0},  // "26" or "Jan" → fails on "Jan"
YearPart = Parts{1},   // "Jan" or "26"
MonthNum = try Number.From(MonthPart) otherwise null,  // "Jan" → null
YearNum = try Number.From(YearPart) otherwise null,
```

**New logic (handles YY-MMM format):**

```powerquery
// Parts{0} = YY (year), Parts{1} = MMM (month abbrev)
YearPart = if List.Count(Parts) >= 1 then Parts{0} else "26",
MonthPart = if List.Count(Parts) >= 2 then Parts{1} else "Jan",

// Convert month abbreviation to number
MonthNum = if MonthPart = "Jan" then 1
           else if MonthPart = "Feb" then 2
           else if MonthPart = "Mar" then 3
           // ... (all 12 months)
           else null,

// Convert 2-digit year to full year
YearNum = try Number.From(YearPart) otherwise null,
FullYear = if YearNum = null then null
           else if YearNum >= 50 then 1900 + YearNum 
           else 2000 + YearNum,
```

### Fix 2: Rolling Window Logic (Both Queries)

**Old logic (broken for historical data):**

```powerquery
// Hardcoded to 2026 only
StartFilterDate = #date(2026, 1, 1),
EndFilterDate = Date.AddMonths(CurrentMonthStart, -1),
```

**New logic (works with historical data):**

```powerquery
// Dynamic rolling 13-month window
CurrentDate = DateTime.LocalNow(),
CurrentMonthStart = Date.StartOfMonth(Date.From(CurrentDate)),
EndFilterDate = Date.AddMonths(CurrentMonthStart, -1),
StartFilterDate = Date.AddMonths(EndFilterDate, -12),  // 13 months back
```

**Result:**
- As of Feb 2026, window shows: **Jan 2025 through Jan 2026** (13 complete months)
- Automatically adjusts each month (no hardcoding)

### Fix 3: Row Label Matching (CCD Query Only)

**Old logic (trimmed labels):**

```powerquery
RequiredOrder = {
    "Monthly Bureau Case Clearance %",  // ❌ Won't match Excel
    "YTD Bureau Case Clearance %"       // ❌ Won't match Excel
},

KeptRows = Table.SelectRows(CCD_Table, (r) => 
    List.Contains(RequiredOrder, Text.Trim(Record.Field(r, FirstColumnName)))
),
```

**New logic (exact match with spaces):**

```powerquery
RequiredOrder = {
    "Monthly Bureau Case  Clearance % ",  // ✅ Double space + trailing
    "YTD Bureau Case Clearance % "        // ✅ Trailing space
},

KeptRows = Table.SelectRows(CCD_Table, (r) => 
    List.Contains(RequiredOrder, Record.Field(r, FirstColumnName))
),
```

---

## Verification Steps

### Before Fix:
1. `___Detectives`: Empty preview table
2. `___Det_case_dispositions_clearance`: Empty preview table
3. Date column: All `null` values
4. No data passed the filter

### After Fix (Expected):
1. Both queries should show data for **13 months** (Jan 2025 - Jan 2026)
2. Date column populated correctly (e.g., `2025-01-01`, `2025-02-01`, etc.)
3. All 10 disposition rows present in CCD query (including the 2 percentage rows)
4. Preview tables showing ~40 case categories × 13 months in Detectives query

---

## Deployment Instructions

1. **Open Power BI Desktop**
2. **Open the Detective dashboard** (.pbix file)
3. **Go to Power Query Editor** (Transform Data)
4. **Update ___Detectives query:**
   - Right-click → Advanced Editor
   - Copy/paste from `m_code\detectives\___Detectives_2026.m`
   - Click Done → Close & Apply
5. **Update ___Det_case_dispositions_clearance query:**
   - Right-click → Advanced Editor
   - Copy/paste from `m_code\detectives\___Det_case_dispositions_clearance_2026.m`
   - Click Done → Close & Apply
6. **Verify data loads correctly:**
   - Check Date column has valid dates (not all `null`)
   - Check preview shows 13 months of data
   - Check row count is reasonable (not 0)
7. **Refresh all queries** (Home → Refresh)
8. **Save .pbix file**

---

## Why This Happened

The Claude Excel prompt described the **intended restructuring** of the workbook (2026-only data with MM-YY headers), but the **actual Excel file was never restructured** to match that design. The workbook still contains:

- Historical multi-year data (2023-2026)
- YY-MMM format headers (not MM-YY)
- Extra spaces in row labels

The M code was written based on the *plan* (as described in the prompt), not the *reality* (as exists in Excel).

---

## Files Modified

- `m_code\detectives\___Detectives_2026.m` - Date parsing + rolling window logic
- `m_code\detectives\___Det_case_dispositions_clearance_2026.m` - Date parsing + rolling window + label matching
- `docs\DETECTIVES_EXCEL_STRUCTURE_MISMATCH_FIX.md` - This document

---

## Related Documents

- `docs\DETECTIVES_2026_UPDATE_GUIDE.md` - Original deployment guide (now outdated)
- `docs\2026_02_13_claude_excel_prompt_stacp_query.md` - Claude's *intended* restructuring (not implemented)
- `scripts\check_detective_table_data.py` - Python script that revealed actual structure

---

**Next Steps:** User needs to test these fixes in Power BI Desktop and confirm both queries now return data.

# Data Verification Summary - December 2025

**Date:** 2026-01-11  
**Analysis:** Comparison of Raw Export, Excel Output, and Visual Export

---

## Key Findings

### ✅ ChatGPT's Counts Are CORRECT (for Raw Export)

**Raw Export (`2025_12_eticket_export.csv`):**
- Moving (M): **443** ✅
- Parking (P): **2,896** ✅
- Special (C): 44
- **Total: 3,383**

ChatGPT correctly counted the raw export file using `Case Type Code` column.

---

## Data Flow Comparison

### 1. Raw E-Ticket Export
**File:** `2025_12_eticket_export.csv`  
**Source:** Court system export  
**Classification:** Uses `Case Type Code` column

| Type | Count |
|------|-------|
| M (Moving) | 443 |
| P (Parking) | 2,896 |
| C (Special) | 44 |
| **Total** | **3,383** |

### 2. Excel Output (After ETL Processing)
**File:** `summons_powerbi_latest.xlsx`  
**Source:** Processed by `SummonsMaster_Simple.py`  
**Classification:** Uses `classify_violations()` function (reclassifies based on statute numbers and keywords)

| Type | Count | Difference from Raw |
|------|-------|---------------------|
| M (Moving) | 526 | **+83** |
| P (Parking) | 2,835 | **-61** |
| C (Special) | 5 | **-39** |
| **Total** | **3,366** | **-17** |

### 3. Visual Export
**Source:** Power BI visual export  
**Matches:** Excel Output (526 M, 2,835 P)

---

## Why The Difference?

The ETL script's `classify_violations()` function **reclassifies** tickets based on:
1. **Statute numbers:** Title 39 violations → Moving (M)
2. **Keywords in violation description:** Parking keywords → Parking (P)
3. **Default behavior:** Municipal ordinances default to Parking (P)

**This explains:**
- **83 more Moving violations:** Some tickets classified as P or C in raw export are reclassified to M based on statute patterns (e.g., Title 39 violations)
- **61 fewer Parking violations:** Some P tickets reclassified to M
- **39 fewer Special complaints:** Some C tickets reclassified to M or P
- **17 fewer total:** Some records may be filtered out or have invalid dates

---

## December 2024 Data Status

### ✅ 12-24 Data IS in Excel Output

**Excel Output:**
- 2 aggregate records (IS_AGGREGATE = TRUE)
- Moving (M): 452
- Parking (P): 1,778
- Source: HISTORICAL_SUMMARY (backfill data)

**Visual Export:**
- Moving (M): 452 ✅ **MATCHES**
- Parking (P): 1,778 ✅ **MATCHES**

**Conclusion:** 12-24 data is correctly in the Excel file and matches the visual export.

### ⚠️ If 12-24 Not Showing in Visual

If 12-24 data is not appearing in your Power BI visual, check:

1. **Visual Filter:**
   - Ensure no date filters excluding 12-24
   - Check if `Month_Year` filter includes "12-24"

2. **Query Filter:**
   - Verify `summons_13month_trend` query includes `ETL_VERSION = "HISTORICAL_SUMMARY"`
   - Check that `IS_AGGREGATE = true` records are included

3. **Data Type Issues:**
   - Ensure `Month_Year` is text type
   - Verify sorting/grouping isn't excluding 12-24

---

## Summary Table

| Source | 12-24 M | 12-24 P | 12-25 M | 12-25 P | Notes |
|--------|---------|---------|---------|---------|-------|
| **Raw Export** | N/A | N/A | 443 | 2,896 | Original court data |
| **Excel Output** | 452 | 1,778 | 526 | 2,835 | After ETL processing |
| **Visual Export** | 452 | 1,778 | 526 | 2,835 | From Power BI visual |
| **Backfill Data** | 452 | 1,778 | N/A | N/A | Historical aggregate |

---

## Answers to Your Questions

### 1. ✅ Are ChatGPT's totals correct?
**YES** - ChatGPT correctly counted the raw export: M=443, P=2,896

### 2. ✅ Does exported data match backfill data?
**YES** - 12-24 data matches perfectly:
- Backfill: M=452, P=1,778
- Excel Output: M=452, P=1,778
- Visual Export: M=452, P=1,778

### 3. ⚠️ Why is 12-24 not showing in visual?
**12-24 data IS in the Excel file** and matches the visual export. If it's not appearing in your Power BI visual, check:
- Visual-level filters
- Query filters in `summons_13month_trend`
- Data type issues with `Month_Year` column

### 4. ⚠️ Why does 12-25 differ from raw export?
**ETL classification logic** reclassifies tickets based on statute numbers and keywords:
- Raw export uses `Case Type Code` (court system classification)
- Excel output uses `classify_violations()` function (ETL reclassification)
- This is **expected behavior** - the ETL script enforces consistent classification rules

---

## Recommendations

1. **For Visual Accuracy:**
   - Use Excel output counts (526 M, 2,835 P) - these reflect the ETL's classification logic
   - Raw export counts (443 M, 2,896 P) are accurate for the source data but not what's in your visual

2. **If 12-24 Not Showing:**
   - Check Power BI visual filters
   - Verify query includes HISTORICAL_SUMMARY records
   - Ensure no date range filters exclude 12-24

3. **Classification Logic:**
   - If you want to match raw export exactly, you would need to use `Case Type Code` directly
   - Current ETL logic provides more consistent classification based on statute patterns

---

**Analysis Date:** 2026-01-11  
**Files Analyzed:**
- `2025_12_eticket_export.csv` (raw export)
- `summons_powerbi_latest.xlsx` (Excel output)
- `Department-Wide Summons Moving and Parking.csv` (visual export)

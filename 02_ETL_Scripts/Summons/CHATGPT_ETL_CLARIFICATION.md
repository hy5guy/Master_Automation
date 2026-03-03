# Answers to ChatGPT's Clarifying Questions

**Date:** 2026-01-11  
**Purpose:** Clarify ETL processing logic for discrepancy analysis

---

## 1. Scope of Data Inclusion - Filtering

### Case Status Code
**Answer:** **NO** - The ETL does NOT filter based on Case Status Code. All records are processed regardless of status.

**Code Evidence:**
- The `Case Status Code` column is read and stored in the `STATUS` field, but no filtering is applied
- All rows are processed regardless of their Case Status Code value

### Date-Based Filtering
**Answer:** **YES** - The ETL filters records based on **Issue Date only**.

**Filtering Logic:**
- Only records with `Issue Date` falling within the previous month (December 2025) are included
- Records with invalid, missing, or unparseable Issue Date are excluded
- No filtering on Court Date, Pay By Date, or other date fields

**Code Evidence:**
```python
mask = (result["ISSUE_DATE"] >= pd.Timestamp(prev_month_start)) & (
    result["ISSUE_DATE"] <= pd.Timestamp(prev_month_end)
)
result = result.loc[mask].copy()
```

**Impact:**
- From the December 2025 export: 3,383 total records → 3,366 processed (17 records filtered out)
- These 17 records have Issue Dates outside December 2025 or invalid dates

### Agency Id or Jurisdictions
**Answer:** **NO** - The ETL does NOT filter based on Agency Id, jurisdictions, or any other categorical field.

### Test Data, Duplicates, Corrupt Rows
**Answer:** 
- **Corrupt rows:** Excluded via `on_bad_lines='skip'` parameter in `pd.read_csv()`
- **Duplicates:** NOT explicitly removed - all records are kept
- **Test data:** NOT explicitly filtered - relies on date filtering if test data has invalid dates

**Code Evidence:**
```python
df = pd.read_csv(eticket_path, dtype=str, encoding="utf-8", na_filter=False,
                delimiter=delimiter, on_bad_lines='skip')
```

---

## 2. Column Used for Classification

### Case Type Code Usage
**Answer:** **YES** - The ETL uses the `Case Type Code` column directly for classification.

**Recent Change:**
- **As of 2026-01-11:** The ETL now uses `Case Type Code` directly (no reclassification)
- Previously, it used a `classify_violations()` function that reclassified based on statute patterns
- This was changed to match raw export counts exactly

**Code Evidence:**
```python
case_type_raw = df.get("Case Type Code", pd.Series([""] * len(df))).astype(str).str.strip().str.upper()
"TYPE": case_type_raw,  # Use Case Type Code directly from export (M, P, C)
```

### Treatment of Other Codes
**Answer:** 
- **Nulls/Blanks:** Converted to empty string, then uppercase (becomes "")
- **Other types (e.g., "C" for Special Complaint):** Preserved as-is
- **No exclusion:** All Case Type Code values are preserved in the TYPE field

**However, Note the PEO Rule:**
- After classification, a business rule applies: PEO and Class I officers cannot issue Moving violations
- This converts M→P for these officers based on their assignment (WG3 = "PEO" or "CLASS I")
- This happens AFTER Case Type Code assignment and AFTER assignment enrichment

**Code Evidence:**
```python
def apply_peo_rule(df):
    wg3_values = df["WG3"].astype(str).str.strip().str.upper()
    mask = wg3_values.isin(["PEO", "CLASS I"]) & (df["TYPE"] == "M")
    df.loc[mask, "TYPE"] = "P"
```

**Impact:**
- Raw export: M=443, P=2,896
- After Case Type Code (before PEO rule): M=440, P=2,882 (17 records filtered by date)
- After PEO rule: M=449, P=2,891 (9 Moving violations converted to Parking)

---

## 3. Source File Consistency

### File Version
**Answer:** **YES** - The ETL uses the exact same file:
- **File Path:** `C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Summons\E_Ticket\2025\raw\month\2025_12_eticket_export.csv`
- **Version:** This is the same file that ChatGPT analyzed
- **Delimiter Detection:** Automatically detects semicolon (;) vs comma (,) delimiter

### Row Corruption/Malformation
**Answer:** 
- **Partially imported rows:** Handled by `on_bad_lines='skip'` - corrupted rows are skipped
- **Malformed rows:** Skipped during CSV parsing
- **Impact:** Some rows may be excluded if they're corrupted or malformed

**Code Evidence:**
- Uses `on_bad_lines='skip'` parameter
- No explicit validation of row completeness

---

## 4. Transformation Steps

### Classification Transformation
**Answer:** **NO reclassification** (as of 2026-01-11 update)
- Case Type Code is used directly without transformation
- Previously used `classify_violations()` function (removed)

### Renaming/Standardization
**Answer:** **YES** - Column names are standardized:
- `Case Type Code` → `TYPE`
- `Ticket Number` → `TICKET_NUMBER`
- `Officer Id` → `PADDED_BADGE_NUMBER` (with zero-padding)
- `Issue Date` → `ISSUE_DATE` (parsed to datetime)
- Column names are standardized but values are preserved

### Deduplication
**Answer:** **NO** - No explicit deduplication is performed on the e-ticket data.
- All rows from the export file are processed (except those filtered by date or corrupted)
- Duplicates are not removed

### Data Sanitization
**Answer:** **YES** - Limited sanitization:
- **Badge numbers:** Padded to 4 digits (e.g., "123" → "0123")
- **Dates:** Parsed and validated (invalid dates result in NaT, records filtered out)
- **Case Type Code:** Stripped and uppercased (preserves values)
- **No data value changes:** Values are preserved except for formatting (padding, case)

---

## Summary of Filtering/Exclusion Logic

| Filter/Exclusion | Applied? | Impact |
|-----------------|----------|--------|
| Case Status Code filtering | ❌ No | All statuses included |
| Issue Date filtering | ✅ Yes | 17 records excluded (outside Dec 2025) |
| Court Date/Pay By Date filtering | ❌ No | Not used |
| Agency Id/Jurisdiction filtering | ❌ No | Not used |
| Corrupt row exclusion | ✅ Yes | Bad lines skipped |
| Duplicate removal | ❌ No | All records kept |
| Test data filtering | ❌ No (implicit via date) | Only if dates invalid |
| Reclassification | ❌ No (removed 2026-01-11) | Uses Case Type Code directly |
| PEO Rule (M→P conversion) | ✅ Yes | 9 M converted to P |

---

## Expected Differences

### Between Raw Export and ETL Output

1. **Date Filtering:** 
   - Raw export: 3,383 total records
   - ETL output: 3,366 records (17 excluded due to invalid/outside-date-range Issue Dates)

2. **PEO Rule:**
   - Before PEO rule: M=440, P=2,882
   - After PEO rule: M=449, P=2,891 (9 M→P conversions)

3. **Corrupt Row Exclusion:**
   - Some rows may be skipped if they're malformed (count unknown, handled automatically)

---

## File Processing Details

**Source File:**
- Path: `C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Summons\E_Ticket\2025\raw\month\2025_12_eticket_export.csv`
- Delimiter: Automatically detected (semicolon `;` for this file)
- Encoding: UTF-8
- Bad lines: Skipped

**Processing Order:**
1. Load CSV file (skip bad lines)
2. Parse Issue Date
3. Filter to December 2025 date range
4. Assign TYPE from Case Type Code (direct assignment, no reclassification)
5. Enrich with assignment data (officer names, bureaus)
6. Apply PEO rule (convert M→P for PEO/Class I officers)
7. Output to Excel

---

**Last Updated:** 2026-01-11  
**ETL Script:** `SummonsMaster_Simple.py`

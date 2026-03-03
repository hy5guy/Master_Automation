# Summons Classification Fix - Quick Start Guide

## Problem Summary

- **Issue**: State E-Ticket marks Moving violations as Parking ("P")
- **Impact**: Moving count = 35 (should be 211), Parking count = 211 (should be 35)
- **Root Cause**: `Case Type Code` defaults to "P" for Title 39 violations
- **Solution**: Prioritize Statute (Title 39:*) over Case Type Code

---

## Quick Fix (5 minutes)

### Step 1: Update Classification Logic

**File**: `02_ETL_Scripts\Summons\main_orchestrator.py` (or wherever classification happens)

**Find this:**
```python
def classify_violation(row):
    raw_type = str(row.get('Case Type Code', '')).strip().upper()
    # Uses Case Type Code directly
    return raw_type if raw_type in ['M', 'P', 'C'] else 'P'
```

**Replace with:**
```python
def classify_violation(row):
    """Prioritize Statute over Case Type Code"""
    raw_type = str(row.get('Case Type Code', '')).strip().upper()
    statute = str(row.get('Statute', '')).strip().upper()
    description = str(row.get('Violation Description', '')).upper()
    
    # 1. STATUTE CHECK (Primary Authority)
    if statute.startswith("39:"):
        return "M"  # Title 39 = Moving
    
    # 2. PARKING CHECK
    parking_keywords = ["PARK", "METER", "HANDICAP", "NO PARKING", "FIRE HYDRANT"]
    is_parking = statute.startswith("39:4-138") or statute.startswith("39:4-135")
    if is_parking or any(kw in description for kw in parking_keywords):
        return "P"
    
    # 3. FALLBACK
    return raw_type if raw_type in ['M', 'P', 'C'] else 'P'
```

### Step 2: Add YearMonthKey Column (for sorting fix)

**Add after date processing:**
```python
if 'Issue Date' in merged_df.columns:
    merged_df['ISSUE_DATE'] = pd.to_datetime(merged_df['Issue Date'], errors='coerce')
    merged_df['Month_Year'] = merged_df['ISSUE_DATE'].dt.strftime('%m-%y')
    merged_df['Year'] = merged_df['ISSUE_DATE'].dt.year
    merged_df['Month'] = merged_df['ISSUE_DATE'].dt.month
    # Add this line:
    merged_df['YearMonthKey'] = (merged_df['Year'] * 100 + merged_df['Month']).fillna(0).astype(int)
```

### Step 3: Run ETL

```powershell
cd "C:\Users\RobertCarucci\OneDrive - City of Hackensack\Master_Automation"
.\scripts\run_etl_script.ps1 -ScriptName "Summons"
```

### Step 4: Update Power BI M Code (3 queries)

**All three queries need this change:**

**Find this:**
```powerquery
// OLD: Text-based sorting (WRONG!)
LatestMonth = List.Max(#"Filtered Data"[Month_Year])
```

**Replace with:**
```powerquery
// NEW: Integer-based sorting (CORRECT!)
LatestKey = List.Max(#"Filtered Data"[YearMonthKey])
#"Filtered Latest Month" = Table.SelectRows(#"Filtered Data", each [YearMonthKey] = LatestKey)
```

**Files to update:**
- `m_code/summons_top5_moving.m`
- `m_code/summons_top5_parking.m`
- `m_code/summons_all_bureaus.m`

### Step 5: Refresh Power BI

1. Open Power BI Desktop
2. Refresh data source
3. Verify counts:
   - Moving: ~211 (not 35)
   - Parking: ~35 (not 211)
   - Latest month: January 2026 (if data exists)

---

## Verification Checklist

- [ ] Classification function updated (Statute priority)
- [ ] YearMonthKey column added to output
- [ ] ETL runs successfully
- [ ] Moving count is ~211 (was 35)
- [ ] Parking count is ~35 (was 211)
- [ ] Power BI M code updated (3 queries)
- [ ] Power BI refresh shows correct data
- [ ] January 2026 displays (if data exists)
- [ ] Months sorted correctly (202601 > 202512)

---

## Testing

### Test 1: Verify Classification

```python
# In Python console or script
import pandas as pd

df = pd.read_excel(
    r"C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx",
    sheet_name="Summons_Data"
)

# Count by TYPE
print(df['TYPE'].value_counts())
# Expected: M ~211, P ~35

# Check Title 39 violations are Moving
title39 = df[df['VIOLATION_NUMBER'].str.startswith('39:', na=False)]
print(f"Title 39 violations: {len(title39)}")
print(f"Classified as Moving: {(title39['TYPE'] == 'M').sum()}")
# Expected: All Title 39 should be 'M'
```

### Test 2: Verify YearMonthKey

```python
# Check YearMonthKey column exists and is correct
print(df[['ISSUE_DATE', 'Month_Year', 'YearMonthKey']].head())
# Expected format:
# ISSUE_DATE     Month_Year  YearMonthKey
# 2026-01-15     01-26       202601
# 2025-12-20     12-25       202512
```

---

## Rollback Plan (if needed)

1. **Restore original script**:
   ```powershell
   git checkout HEAD -- 02_ETL_Scripts/Summons/main_orchestrator.py
   ```

2. **Restore original M code**:
   ```powershell
   git checkout HEAD -- m_code/summons_*.m
   ```

3. **Re-run ETL**:
   ```powershell
   .\scripts\run_etl_script.ps1 -ScriptName "Summons"
   ```

---

## Full Details

See comprehensive guide: `docs/SUMMONS_REMEDIATION_2026_02_17.md`

---

**Created**: 2026-02-17  
**Est. Time**: 5-10 minutes  
**Impact**: High (fixes data quality issue)

# Response Time ETL Filter Update Plan

**Date:** 2026-01-14  
**Purpose:** Document the planned updates to response_time_monthly_generator.py

---

## Overview

This document outlines the planned updates to the Response Time ETL script to implement enhanced filtering logic using a JSON configuration file.

---

## Changes Required

### 1. JSON Configuration File (✅ COMPLETED)

**File:** `config/response_time_filters.json`

**Purpose:** Centralized configuration for all filtering rules

**Structure:**
- `filters.how_reported.exclude`: List of "How Reported" values to exclude
- `filters.category_types.exclude`: List of Category_Type values to exclude (entire categories)
- `filters.incidents.exclude`: List of specific incidents to exclude
- `filters.inclusion_overrides.include_despite_category_filter`: List of incidents to include even if their Category_Type is filtered

---

### 2. Script Updates Required

#### 2.1. Add JSON Config Loading

**Function:** `load_filter_config(config_path: Path, logger: logging.Logger) -> dict`

**Purpose:** Load the JSON configuration file

**Location:** Add after `load_mapping_file` function

---

#### 2.2. Update Mapping File Loading

**Function:** `load_mapping_file` (UPDATE EXISTING)

**Changes:**
- Return DataFrame instead of dict (or return both dict and DataFrame)
- Include `Category_Type` column in returned data
- Create mapping dict for Response_Type
- Create mapping dict for Category_Type

**Current:** Returns `dict` mapping `Incident_Key` → `Response_Type`

**New:** Returns tuple `(response_type_mapping: dict, category_type_mapping: dict, mapping_df: pd.DataFrame)`

---

#### 2.3. Add "How Reported" Filter

**Location:** After Step 1 (Deduplication), before Step 2 (YearMonth)

**Filter:** Exclude records where `How Reported == "Self-Initiated"`

**Code:**
```python
# Filter out "Self-Initiated" from "How Reported"
if 'How Reported' in df.columns:
    before_how_reported = len(df)
    df = df[df['How Reported'] != 'Self-Initiated'].copy()
    logger.info(f"How Reported filter (exclude Self-Initiated): {before_how_reported:,} -> {len(df):,} records")
```

---

#### 2.4. Add Category_Type to Mapping Merge

**Location:** In Step 6 (Apply Response Type Mapping)

**Changes:**
- Merge `Category_Type` from mapping DataFrame
- Use `Incident_Normalized` as key
- Add `Category_Type` column to dataframe

---

#### 2.5. Add Category_Type Filtering (with Override Logic)

**Location:** After Step 6 (Apply Response Type Mapping)

**Filter:** Exclude records where `Category_Type` is in excluded list

**Override:** Include records where `Incident` is in inclusion_overrides list (even if Category_Type is excluded)

**Code Logic:**
```python
# Apply inclusion overrides first (mark records to keep)
inclusion_overrides_set = {normalize_incident_name(i) for i in config['filters']['inclusion_overrides']['include_despite_category_filter']}
df['_keep_override'] = df['Incident_Normalized'].isin(inclusion_overrides_set)

# Filter by Category_Type (exclude excluded categories)
excluded_categories = set(config['filters']['category_types']['exclude'])
before_category = len(df)
df = df[
    df['_keep_override'] | ~df['Category_Type'].isin(excluded_categories)
].copy()
df = df.drop(columns=['_keep_override'])
logger.info(f"Category_Type filter: {before_category:,} -> {len(df):,} records")
```

---

#### 2.6. Add Specific Incident Filtering

**Location:** After Category_Type filtering

**Filter:** Exclude specific incidents from the exclude list

**Code:**
```python
excluded_incidents = {normalize_incident_name(i) for i in config['filters']['incidents']['exclude']}
before_incident = len(df)
df = df[~df['Incident_Normalized'].isin(excluded_incidents)].copy()
logger.info(f"Incident filter: {before_incident:,} -> {len(df):,} records")
```

---

## Filter Order

1. **Deduplication** (by ReportNumberNew)
2. **How Reported Filter** (exclude "Self-Initiated")
3. **YearMonth Creation** (create YearMonth from cYear/cMonth)
4. **Date Range Filter** (filter to target months)
5. **Admin Incident Filter** (existing - filter out admin incidents)
6. **Response Time Calculation** (calculate response times)
7. **Time Window Filter** (0 < minutes <= 10)
8. **Response Type Mapping** (map Response_Type and Category_Type)
9. **Category_Type Filter** (exclude entire categories, with override logic)
10. **Specific Incident Filter** (exclude specific incidents)
11. **Final Validation** (validate Response_Type, filter to valid types)

---

## Testing Plan

1. **Unit Tests:**
   - Test JSON config loading
   - Test mapping file loading (with Category_Type)
   - Test each filter individually
   - Test override logic

2. **Integration Tests:**
   - Test full pipeline with sample data
   - Verify filter counts match expectations
   - Verify output format matches expected structure

3. **Validation:**
   - Compare filtered counts with expected values
   - Verify Category_Type is correctly assigned
   - Verify inclusion overrides work correctly

---

## Implementation Status

- ✅ JSON Configuration File Created
- ⏳ Script Updates (TO BE IMPLEMENTED)
- ⏳ Documentation Updates (TO BE IMPLEMENTED)
- ⏳ Testing (TO BE IMPLEMENTED)

---

## Notes

- The existing script structure should be maintained
- All existing functionality should be preserved
- New filtering logic should be added incrementally
- Logging should be added for all new filter steps
- Error handling should be maintained

---

**Document Created:** 2026-01-14  
**Status:** Planning Phase

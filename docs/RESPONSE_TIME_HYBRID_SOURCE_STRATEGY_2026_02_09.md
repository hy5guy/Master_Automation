# Response Time Hybrid Source Strategy

**Date**: February 9, 2026  
**Decision**: Use hybrid source strategy (yearly + monthly files)  
**Status**: Implementation design ready

---

## Requirement

Response Times workflow needs a **rolling 13-month dataset** for Power BI.

**Example** (as of Feb 2026):
- Data range: Feb 2025 through Feb 2026 (13 months)
- Output: Monthly CSV files in PowerBI_Date/Backfill structure

---

## Available Data Sources

### Yearly Files
```
timereport/yearly/2025/2025_full_timereport.xlsx
├── Contains: All 12 months of 2025 (Jan-Dec)
├── Updated: Once per year (at year-end)
└── Use case: Historical data for completed years
```

### Monthly Files
```
timereport/monthly/2026_01_timereport.xlsx
timereport/monthly/2026_02_timereport.xlsx (when available)
├── Contains: Single month of data
├── Updated: Monthly as data becomes available
└── Use case: Current and recent month data
```

---

## Recommended Strategy: Hybrid Source

### Concept

**Script intelligently combines data from both sources:**

1. **For historical months** (before current year): Read from yearly file
2. **For current year months**: Read from monthly files
3. **Combine and deduplicate** to create rolling 13-month dataset

### Benefits

✅ **No manual export work** - Uses existing file structure  
✅ **Automatic year transitions** - Script handles logic  
✅ **Efficient storage** - No duplicate monthly exports needed  
✅ **Maintains separation** - Monthly/yearly stay separate (reduces overlap risk)  
✅ **Future-proof** - Works as monthly files accumulate  
✅ **Scalable** - Easy to change window size (13 → 18 months, etc.)

---

## Implementation Design

### High-Level Algorithm

```python
def generate_rolling_13_months():
    """
    Generate 13-month rolling dataset from hybrid sources.
    """
    # 1. Calculate date range
    end_date = datetime.now()
    start_date = end_date - relativedelta(months=12)  # 13 months total
    
    # 2. Build list of months needed
    months_needed = generate_month_list(start_date, end_date)
    
    # 3. Collect data for each month
    all_monthly_data = []
    for month in months_needed:
        data = get_month_data(month)  # Hybrid source logic
        all_monthly_data.append(data)
    
    # 4. Combine and process
    combined_data = combine_all_months(all_monthly_data)
    
    # 5. Calculate response times
    response_times = calculate_response_times(combined_data)
    
    # 6. Output to PowerBI_Date/Backfill structure
    export_monthly_csvs(response_times)
```

### Hybrid Source Logic

```python
def get_month_data(target_month):
    """
    Get data for a specific month from best available source.
    
    Priority:
    1. Monthly file (most current, if exists)
    2. Yearly file (extract specific month)
    3. Error if neither exists
    """
    year = target_month.year
    month = target_month.month
    
    # Option 1: Try monthly file first
    monthly_file = Path(f"timereport/monthly/{year}_{month:02d}_timereport.xlsx")
    
    if monthly_file.exists():
        log(f"Reading {year}-{month:02d} from monthly file: {monthly_file}")
        data = read_excel(monthly_file)
        return filter_by_month(data, target_month)
    
    # Option 2: Fall back to yearly file
    yearly_file = Path(f"timereport/yearly/{year}/{year}_full_timereport.xlsx")
    
    if yearly_file.exists():
        log(f"Reading {year}-{month:02d} from yearly file: {yearly_file}")
        data = read_excel(yearly_file)
        return filter_by_month(data, target_month)
    
    # Option 3: Error - no source available
    raise FileNotFoundError(
        f"No data source found for {year}-{month:02d}. "
        f"Checked: {monthly_file}, {yearly_file}"
    )
```

### Month Filtering Logic

```python
def filter_by_month(df, target_month):
    """
    Extract specific month from dataset.
    
    Assumes date column exists (e.g., 'Incident_Date', 'Report_Date').
    Adjust column name based on actual CAD export structure.
    """
    # Convert to datetime if needed
    df['Incident_Date'] = pd.to_datetime(df['Incident_Date'])
    
    # Filter to target month
    mask = (
        (df['Incident_Date'].dt.year == target_month.year) &
        (df['Incident_Date'].dt.month == target_month.month)
    )
    
    filtered = df[mask].copy()
    
    log(f"  Filtered to {len(filtered)} records for {target_month.strftime('%Y-%m')}")
    
    return filtered
```

---

## Example Scenarios

### Scenario 1: February 2026 (Now)

**13-month window**: Feb 2025 - Feb 2026

**Data sourcing**:
| Month | Source | File |
|-------|--------|------|
| Feb 2025 | Yearly | `yearly/2025/2025_full_timereport.xlsx` → filter Feb |
| Mar 2025 | Yearly | `yearly/2025/2025_full_timereport.xlsx` → filter Mar |
| Apr 2025 | Yearly | `yearly/2025/2025_full_timereport.xlsx` → filter Apr |
| ... | Yearly | ... |
| Dec 2025 | Yearly | `yearly/2025/2025_full_timereport.xlsx` → filter Dec |
| Jan 2026 | Monthly | `monthly/2026_01_timereport.xlsx` ✅ |
| Feb 2026 | Monthly | `monthly/2026_02_timereport.xlsx` (when available) |

**Script reads**:
- 1 yearly file (2025)
- 1-2 monthly files (Jan-Feb 2026)

### Scenario 2: December 2026 (Future)

**13-month window**: Dec 2025 - Dec 2026

**Data sourcing**:
| Month | Source | File |
|-------|--------|------|
| Dec 2025 | Yearly | `yearly/2025/2025_full_timereport.xlsx` → filter Dec |
| Jan 2026 | Either | `monthly/2026_01_timereport.xlsx` OR `yearly/2026/...` |
| Feb 2026 | Either | `monthly/2026_02_timereport.xlsx` OR `yearly/2026/...` |
| ... | Either | ... |
| Dec 2026 | Monthly | `monthly/2026_12_timereport.xlsx` |

**Script reads**:
- 1 yearly file (2025) for Dec 2025 only
- 12 monthly files OR 1 yearly file (2026)

### Scenario 3: January 2027 (Future)

**13-month window**: Jan 2026 - Jan 2027

**Data sourcing**:
| Month | Source | File |
|-------|--------|------|
| Jan 2026 | Yearly | `yearly/2026/2026_full_timereport.xlsx` → filter Jan |
| Feb 2026 | Yearly | `yearly/2026/2026_full_timereport.xlsx` → filter Feb |
| ... | Yearly | ... |
| Dec 2026 | Yearly | `yearly/2026/2026_full_timereport.xlsx` → filter Dec |
| Jan 2027 | Monthly | `monthly/2027_01_timereport.xlsx` ✅ |

**Script reads**:
- 1 yearly file (2026)
- 1 monthly file (Jan 2027)

---

## Output Structure

### PowerBI_Date/Backfill Structure

```
PowerBI_Date/
└── Backfill/
    ├── 2025_02/
    │   └── response_time/
    │       └── 2025_02_Average_Response_Times__Values_are_in_mmss.csv
    ├── 2025_03/
    │   └── response_time/
    │       └── 2025_03_Average_Response_Times__Values_are_in_mmss.csv
    ├── ...
    ├── 2026_01/
    │   └── response_time/
    │       └── 2026_01_Average_Response_Times__Values_are_in_mmss.csv
    └── 2026_02/
        └── response_time/
            └── 2026_02_Average_Response_Times__Values_are_in_mmss.csv
```

**Each monthly CSV contains**:
- Average response times by incident type
- Aggregated statistics for that month
- Formatted as `mm:ss` values

---

## Alternative Approach (NOT Recommended)

### Option B: Export Each Month of 2025 Separately

**Process**:
1. Manually export 12 separate files from CAD system:
   - `2025_01_timereport.xlsx`
   - `2025_02_timereport.xlsx`
   - ... (10 more files)
   - `2025_12_timereport.xlsx`

2. Place all in `timereport/monthly/` folder

3. Script reads only from monthly folder (simpler logic)

**Why NOT recommended**:

❌ **Manual work**: 12 separate exports to create  
❌ **Duplication**: Same data exists in yearly file  
❌ **Maintenance burden**: Keep monthly + yearly in sync  
❌ **Inconsistency risk**: File naming, structure variations  
❌ **Storage waste**: Duplicate data storage  
❌ **Version control**: Which is authoritative source?

**Only advantage**:
✅ Simpler script logic (just loop through monthly files)

**Verdict**: Not worth the tradeoffs. Hybrid approach is superior.

---

## Implementation Checklist

### Phase 1: Script Updates

- [ ] Update `response_time_monthly_generator.py` with hybrid source logic
- [ ] Add `get_month_data()` function with monthly/yearly fallback
- [ ] Add `filter_by_month()` function for yearly file extraction
- [ ] Add date column detection (identify correct date field in CAD export)
- [ ] Add logging for data source tracking
- [ ] Add input validation (verify files exist before processing)

### Phase 2: Configuration

- [ ] Add configuration for rolling window size (default: 13 months)
- [ ] Add configuration for timereport base path
- [ ] Add configuration for output path (PowerBI_Date/Backfill)
- [ ] Update `config/response_time_filters.json` if needed

### Phase 3: Testing

- [ ] Test with current data (Feb 2026 scenario)
- [ ] Verify correct months extracted from yearly file
- [ ] Verify monthly file takes priority when both exist
- [ ] Test error handling (missing files)
- [ ] Verify output structure matches Power BI expectations
- [ ] Compare against previous backfill data for validation

### Phase 4: Documentation

- [ ] Update Python script docstrings
- [ ] Add configuration file comments
- [ ] Update main README with new logic
- [ ] Add troubleshooting guide

### Phase 5: Integration

- [ ] Update validation in `run_all_etl.ps1` (already done ✅)
- [ ] Test with `run_etl_script.ps1`
- [ ] Test with full `run_all_etl.ps1`
- [ ] Verify Power BI refresh works
- [ ] Validate data accuracy in Power BI report

---

## Data Quality Considerations

### Deduplication

If a month exists in both monthly AND yearly files:

**Priority**: Monthly file wins (most current data)

**Dedup logic**:
```python
# Not needed if using priority logic above
# But if combining multiple sources for same month:

def deduplicate_month_data(df):
    """
    Remove duplicate records within a month.
    Assumes CAD exports have unique incident ID.
    """
    return df.drop_duplicates(subset=['Incident_ID'], keep='last')
```

### Date Range Validation

```python
def validate_month_coverage(df, expected_month):
    """
    Ensure filtered data is actually from expected month.
    """
    dates = pd.to_datetime(df['Incident_Date'])
    
    # Check all dates are in expected month
    actual_months = dates.dt.to_period('M').unique()
    expected_period = expected_month.to_period('M')
    
    if len(actual_months) > 1 or actual_months[0] != expected_period:
        log(f"WARNING: Data contains dates outside {expected_month.strftime('%Y-%m')}")
        log(f"  Found periods: {actual_months}")
    
    return df
```

---

## Edge Cases to Handle

### 1. Transition Period (Jan 2026)

**Issue**: When yearly file for 2026 doesn't exist yet, but monthly files do

**Solution**: Script prioritizes monthly files (already in design)

### 2. Missing Monthly File

**Issue**: February 2026 monthly file not yet available

**Solution**: Script falls back to yearly file (if it exists), or errors clearly

### 3. Incomplete Yearly File

**Issue**: Yearly 2025 file missing certain months

**Solution**: Script logs warning, proceeds with available data

### 4. Date Column Variations

**Issue**: CAD exports may have different date column names

**Solution**: Add configuration for date column name, or auto-detect

```python
def detect_date_column(df):
    """
    Find the primary date column in CAD export.
    """
    candidates = ['Incident_Date', 'Report_Date', 'Dispatch_Date', 'Date']
    
    for col in candidates:
        if col in df.columns:
            return col
    
    raise ValueError(f"No date column found. Searched: {candidates}")
```

---

## Performance Considerations

### File Reading Optimization

```python
# Instead of reading full yearly file 12 times,
# read once and cache in memory

class YearlyFileCache:
    def __init__(self):
        self.cache = {}
    
    def get_yearly_data(self, year):
        if year not in self.cache:
            file_path = f"timereport/yearly/{year}/{year}_full_timereport.xlsx"
            self.cache[year] = pd.read_excel(file_path)
        return self.cache[year]
    
    def get_month(self, year, month):
        yearly_data = self.get_yearly_data(year)
        return filter_by_month(yearly_data, datetime(year, month, 1))
```

**Benefits**:
- Read yearly file once (not 12 times)
- Faster processing for 13-month window
- Lower memory footprint than reading all at once

---

## Testing Script

```python
def test_hybrid_source():
    """
    Test hybrid source strategy with current data.
    """
    print("Testing Response Time Hybrid Source Strategy")
    print("=" * 60)
    
    # Test current 13-month window
    months = generate_rolling_13_months()
    
    print(f"\nGenerated {len(months)} months:")
    for month in months:
        print(f"  {month.strftime('%Y-%m')}")
    
    # Test data retrieval for each month
    print("\nTesting data retrieval:")
    cache = YearlyFileCache()
    
    for month in months:
        try:
            data = get_month_data(month, cache)
            print(f"  {month.strftime('%Y-%m')}: {len(data)} records ✅")
        except FileNotFoundError as e:
            print(f"  {month.strftime('%Y-%m')}: MISSING ❌")
            print(f"    {e}")
    
    print("\nTest complete!")
```

---

## Migration from Old System

If transitioning from old `monthly_export` folder:

```python
def migrate_from_old_structure():
    """
    One-time migration helper to understand old structure.
    """
    old_path = "05_EXPORTS/_CAD/monthly_export"
    new_path = "05_EXPORTS/_CAD/timereport"
    
    # List what was in old structure
    print("Old structure files:")
    for file in Path(old_path).rglob("*.xlsx"):
        print(f"  {file}")
    
    # Verify new structure is ready
    print("\nNew structure files:")
    print("  Yearly:")
    for file in Path(new_path, "yearly").rglob("*.xlsx"):
        print(f"    {file}")
    print("  Monthly:")
    for file in Path(new_path, "monthly").rglob("*.xlsx"):
        print(f"    {file}")
```

---

## Conclusion

**Recommendation**: Implement hybrid source strategy (yearly + monthly)

**Why**: Efficient, automated, future-proof, no manual export work

**Next step**: Update `response_time_monthly_generator.py` with hybrid logic

**Timeline**: 2-3 hours implementation + testing

**Risk**: Low (can test alongside existing process)

---

**Decision**: ✅ Use hybrid source strategy  
**Implementation**: Ready to proceed  
**Documentation**: Complete

---

*Last Updated: February 9, 2026*

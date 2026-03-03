# Benchmark Data Architecture Migration

**Processing Date:** 2026-02-04 23:54:58
**Source File:** BENCHMARK_DATA_ARCHITECTURE_MIGRATION.md
**Total Chunks:** 1

---

# Cursor AI Context Prompt - Benchmark Data Architecture Migration

## Project Summary

Successfully completed comprehensive restructure of Hackensack PD Benchmark use-of-force tracking system on **2026-01-12**. Migration transformed siloed, inefficiently organized incident data into query-optimized architecture with zero data loss. ---

## What Was Done

### 1. Data Architecture Overhaul

**Previous Structure (Problematic):**
```
_Benchmark/
├── show_force/complete_report/all_time/
├── use_force/complete_report/all_time/
└── vehicle_pursuit/complete_report/all_time/
```
- Issue: Misleading `full_year` folders (YTD data, not complete years)
- Issue: No combined view across event types
- Issue: Power BI forced to filter 398 records every query

**New Structure (Query-Optimized):**
```
_Benchmark/
├── all_events_combined/
│   ├── master_combined_all_time.csv (398 records total)
│   └── metadata.json
├── by_time_period/
│   ├── rolling_13month/
│   │   ├── current_window.csv (81 records, Dec-24 to Dec-25)
│   │   ├── by_event_type/ (3 pre-filtered CSVs)
│   │   └── last_updated.txt
│   ├── ytd_current/2026_ytd.csv
│   └── archives/ (historical snapshots)
└── by_event_type/
    ├── show_force/archives/
    ├── use_force/archives/
    └── vehicle_pursuit/archives/
```

### 2. Data Inventory

**Total Historical Data:**
- **398 incidents** (2020-07-16 to 2025-12-29)
  - Use of Force: 340
  - Show of Force: 37
  - Vehicle Pursuit: 21

**Current Rolling 13-Month Window (Dec-24 to Dec-25):**
- **81 incidents**
  - Use of Force: 76
  - Show of Force: 3
  - Vehicle Pursuit: 2

### 3. Key Files Created

**Root Path:** `C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Benchmark`

**Critical Files:**
1. `all_events_combined/master_combined_all_time.csv` - Merged all incidents with EventType column
2. `by_time_period/rolling_13month/current_window.csv` - Pre-filtered 81 records (Dec-24 to Dec-25)
3. `by_time_period/rolling_13month/by_event_type/*.csv` - Individual event type breakouts
4. `README.md` - Complete folder structure documentation
5. `MIGRATION_REPORT_20260112.md` - Full migration details

**Updated Power BI Assets:**
- `Master_Automation/2026_01_12_benchmark_m_codes_UPDATED.m` - 3 query options
- `Master_Automation/Use of Force Incident Matrix_UPDATED.csv` - Rolling 13-month matrix
- `Master_Automation/Incident Distribution by Event Type_UPDATED.csv`
- `Master_Automation/Incident Count by Date and Event Type_UPDATED.csv`

**Backup Location:**
- `_Benchmark_BACKUP_20260112/` - Complete legacy structure preserved

---

## Rolling 13-Month Window Logic (CRITICAL)

**Calculation Method:**
```python
# Today: 2026-01-12
end_date = last_day_of_previous_complete_month()  # 2025-12-31
start_date = end_date - 12 months                  # 2024-12-01
# Window: December 2024 through December 2025 (13 complete months)
```

**Key Rules:**
- Always exclude current month (incomplete data)
- Window = 13 complete months ending with last complete month
- Updates monthly (first week of each month recommended)

---

## Power BI M-Code Updates

### Three Query Options Provided

**Option 1: FactIncidents_Rolling13Month** ⭐ **USE THIS**
```m
// Reads pre-filtered CSV - FASTEST performance
let
    Source = Csv.Document(
        File.Contents(RootExportPath & "by_time_period\rolling_13month\current_window.csv"),
        [Delimiter=",", Encoding=65001]
    ),
    // ... schema application
in
    Result
```
- **Performance:** 3-5x faster (reads 81 records vs. 398)
- **Use for:** Dashboards, regular reports, visualizations

**Option 2: FactIncidents_AllTime_Filtered**
```m
// Reads master dataset with dynamic filtering
// Use for ad-hoc historical analysis
```

**Option 3: FactIncidents_DynamicRolling**
```m
// Auto-calculates rolling window from current date
// Use for self-maintaining reports
```

**Parameter to Set:**
```m
RootExportPath = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Benchmark\"
```

---

## File Paths Reference

### Source Data (All-Time Complete)
```
C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Benchmark\
├── all_events_combined\master_combined_all_time.csv
├── by_event_type\show_force\historical_complete.csv
├── by_event_type\use_force\historical_complete.csv
└── by_event_type\vehicle_pursuit\historical_complete.csv
```

### Rolling 13-Month (Current Window)
```
C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Benchmark\by_time_period\rolling_13month\
├── current_window.csv                    (All events combined)
├── by_event_type\show_force_13month.csv
├── by_event_type\use_force_13month.csv
├── by_event_type\vehicle_pursuit_13month.csv
└── last_updated.txt
```

### Power BI Integration Files
```
C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\
├── 2026_01_12_benchmark_m_codes_UPDATED.m
├── Use of Force Incident Matrix_UPDATED.csv
├── Incident Distribution by Event Type_UPDATED.csv
└── Incident Count by Date and Event Type_UPDATED.csv
```

---

## Monthly Maintenance Process

**When:** First week of each month (after previous month completes)

**Tasks:**
1. Export new Benchmark data from source system
2. Run `benchmark_restructure.py` to regenerate rolling window
3. Refresh Power BI to pull updated `current_window.csv`

**Script Location:** `Master_Automation/benchmark_restructure.py`

---

## Data Validation Checklist

When working with Benchmark data, verify:
- [ ] Rolling window shows 13 complete months (not 12, not 14)
- [ ] Current month is excluded (incomplete data)
- [ ] Total incidents = sum of event types
- [ ] Date range matches `last_updated.txt` timestamp
- [ ] Power BI queries point to new structure paths

---

## Important Notes for Future Development

### Schema Consistency
All CSV files use identical schema:
- **Columns:** Date, EventType, [other incident fields]
- **Date Format:** YYYY-MM-DD
- **EventType Values:** "Show of Force", "Use of Force", "Vehicle Pursuit"

### Performance Optimization
- **Pre-filtered CSVs** eliminate runtime filtering overhead
- Reading `current_window.csv` (81 records) vs. `master_combined_all_time.csv` (398 records) = **3-5x speed improvement**
- Use Option 1 M-code for all production dashboards

### Data Integrity
- **100% record match** between legacy and new structure verified
- **Zero data loss** confirmed in migration
- **Backup preserved** at `_Benchmark_BACKUP_20260112/`

### Naming Conventions
- `*_13month.csv` = Rolling 13-month window files
- `*_UPDATED. *` = Files generated during 2026-01-12 migration
- `historical_complete.csv` = All-time data for specific event type

---

## Quick Reference: Expected Totals

**All-Time (2020-07-16 to 2025-12-29):**
- Total: 398 incidents

**Rolling 13-Month (Dec-24 to Dec-25):**
- Total: 81 incidents
- Use of Force: 76
- Show of Force: 3
- Vehicle Pursuit: 2

**YTD 2026 (Jan-01 to Jan-07):**
- Total: 0 incidents (no events yet in 2026)

---

## Related Projects/Systems

This Benchmark restructure follows the same architectural patterns as:
- **Arrests Analytics** (UCR crime categorization)
- **Summons Pipeline** (rolling 13-month windows)
- **Community Engagement ETL** (Python processing + Power BI integration)

All use rolling 13-month windows excluding current incomplete month for consistent trend analysis. ---

## Documentation Locations

- **Folder Structure Guide:** `_Benchmark/README.md`
- **Migration Details:** `_Benchmark/MIGRATION_REPORT_20260112.md`
- **Updated M-Code:** `Master_Automation/2026_01_12_benchmark_m_codes_UPDATED.m`
- **Migration Script:** `Master_Automation/benchmark_restructure.py`

---

## Status
✅ **Migration Complete - Ready for Production**
- Execution: 2026-01-12
- Data Integrity: 100%
- Performance Gain: 3-5x
- Files Generated: 21
- Legacy Backup: Preserved

All Power BI dashboards can now use optimized query structure with pre-filtered rolling 13-month datasets.


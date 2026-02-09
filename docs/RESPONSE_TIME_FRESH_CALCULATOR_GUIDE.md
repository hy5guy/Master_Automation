# Response Time Fresh Calculator v3.0.0 - Implementation Guide

**Date**: February 9, 2026  
**Status**: ✅ Ready for Production  
**Purpose**: Recalculate response times from raw timereport data with consistent methodology

---

## 🎯 Problem Solved

### Issue Identified
- October 2025 visual data doesn't match current backfill exports
- Emergency response times show 10-29 second discrepancies
- Urgent response times have inconsistencies in 3 out of 10 months
- Rolling 13-month averages vs single-month calculations unclear
- **Root Cause**: Different calculation methodologies/data sources

### Solution Implemented
- **Fresh Calculator v3.0.0**: Recalculates ALL months from raw timereport data
- **Consistent Filtering**: Uses `config/response_time_filters.json`
- **Hybrid Data Loading**: Yearly baseline + monthly supplements
- **Single Methodology**: Eliminates calculation discrepancies

---

## 📁 Files Created/Modified

### New Files
1. ✅ **`scripts/response_time_fresh_calculator.py`** (460 lines)
   - Complete ETL script for fresh calculations
   - Hybrid timereport loading (yearly + monthly)
   - Comprehensive filtering and aggregation
   - Outputs monthly CSV files in long format

2. ✅ **`docs/RESPONSE_TIME_FRESH_CALCULATOR_GUIDE.md`** (this file)
   - Implementation instructions
   - Troubleshooting guide
   - Verification procedures

### Modified Files
1. ✅ **`config/scripts.json`**
   - Added "Response Times Fresh Calculator" entry
   - Disabled legacy "Response Times Monthly Generator"
   - Order: 5.6, Timeout: 60 minutes

2. ✅ **`m_code/___ResponseTimeCalculator.m`** (v2.8.1)
   - Updated to prioritize `_DropExports` folder
   - Fresh calculator output now preferred data source
   - Maintains backward compatibility with backfill/visual exports

---

## 🚀 Quick Start

### Prerequisites
- Python 3.7+ with pandas, openpyxl installed
- Raw timereport files exist:
  - `05_EXPORTS\_CAD\timereport\yearly\2025\2025_full_timereport.xlsx`
  - `05_EXPORTS\_CAD\timereport\monthly\2026_01_timereport.xlsx`
- Mapping file exists:
  - `02_ETL_Scripts\Response_Times\input\Response_Type_Mapping.xlsx`
- Filter configuration exists:
  - `config\response_time_filters.json` ✅ (already exists)

### Step 1: Run Fresh Calculator

**Option A: Via Master Automation**
```powershell
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"
.\scripts\run_all_etl.ps1
```

**Option B: Standalone**
```powershell
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"
python scripts\response_time_fresh_calculator.py
```

### Step 2: Verify Output
```powershell
# Check output files created
dir "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports\*Response_Times*.csv"

# Expected files:
# 2025_01_Average_Response_Times__Values_are_in_mmss.csv
# 2025_02_Average_Response_Times__Values_are_in_mmss.csv
# ... (through 2026_01)
```

### Step 3: Refresh Power BI
```
1. Open Power BI report
2. Home tab → Refresh (or Ctrl+R)
3. ___ResponseTimeCalculator query will automatically load fresh data
4. Verify column quality: 100% valid, 0% errors
```

---

## 📊 Expected Output Format

### CSV Structure (Long Format)
```csv
Response_Type,MM-YY,First Response_Time_MMSS
Emergency,01-25,02:59
Emergency,02-25,02:47
Emergency,03-25,03:06
Routine,01-25,01:18
Routine,02-25,01:11
Urgent,01-25,02:52
Urgent,02-25,02:55
```

### Output Statistics
- **Date Range**: 2025-01 through 2026-01 (13 months)
- **Response Types**: Emergency, Routine, Urgent
- **Rows per Month**: 3 (one per response type)
- **Total Rows**: 39 (13 months × 3 types)
- **Format**: MM:SS (e.g., "02:59" for 2 minutes 59 seconds)

---

## 🔍 How It Works

### Data Flow
```
Raw Timereport Files
    ↓
Hybrid Loading (yearly + monthly)
    ↓
Deduplication (by ReportNumberNew)
    ↓
Filter: How Reported (exclude Self-Initiated)
    ↓
Filter: Category_Type (exclude admin categories)
    ↓
Filter: Specific Incidents (exclude admin types)
    ↓
Calculate Response Times (0-10 minute window)
    ↓
Map to Response_Type (Emergency/Routine/Urgent)
    ↓
Aggregate by Month
    ↓
Convert to MM:SS Format
    ↓
Save Monthly CSV Files → _DropExports
    ↓
Power BI M Code Loads → Dashboard
```

### Filtering Logic (from `config/response_time_filters.json`)

1. **How Reported Filter**
   - Excludes: "Self-Initiated"
   - Rationale: Self-initiated calls don't have response times

2. **Category_Type Filter**
   - Excludes: Regulatory, Administrative, Investigations, Community Engagement
   - Overrides: 14 incidents included despite category (Suspicious Person, Missing Person, etc.)

3. **Specific Incident Filter**
   - Excludes: 42 specific administrative incident types
   - Examples: Traffic Detail, TAPS, Patrol Check, etc.

4. **Response Time Window**
   - Valid range: 0-10 minutes
   - Outliers filtered to ensure data quality

---

## 🛠️ Configuration

### Date Range (Edit in script if needed)
```python
# In response_time_fresh_calculator.py (lines 29-33)
START_YEAR = 2025
START_MONTH = 1
END_YEAR = 2026
END_MONTH = 1
```

### File Paths
```python
# Base directories (lines 18-23)
TIMEREPORT_BASE = BASE_DIR / "05_EXPORTS" / "_CAD" / "timereport"
POWERBI_DROP = BASE_DIR / "PowerBI_Date" / "_DropExports"
CONFIG_DIR = MASTER_AUTO_DIR / "config"
```

### Filter Configuration
- File: `config/response_time_filters.json`
- Edit to add/remove excluded incidents
- Restart script after changes (no recompile needed)

---

## ✅ Verification Checklist

### After Running Fresh Calculator

- [ ] **Output Files Created**
  ```powershell
  # Should see 13 files (Jan 2025 - Jan 2026)
  Get-ChildItem "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports\*Response_Times*.csv" | Measure-Object
  ```

- [ ] **Log File Generated**
  ```powershell
  # Check latest log
  Get-ChildItem "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\logs\*response_time_fresh*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  ```

- [ ] **CSV Format Correct**
  ```powershell
  # Open sample file and verify structure
  Get-Content "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports\2025_01_Average_Response_Times__Values_are_in_mmss.csv" | Select-Object -First 10
  ```

- [ ] **Power BI Refresh Success**
  - Open Power BI report
  - Refresh ___ResponseTimeCalculator query
  - Check column quality: 100% valid
  - Verify data loads without errors

- [ ] **Data Consistency Check**
  - Compare October 2025 values to fresh calculations
  - Emergency, Routine, Urgent all populated
  - No missing months in 13-month range

---

## 🐛 Troubleshooting

### Issue: "No timereport files loaded!"

**Cause**: Raw timereport files not found

**Solution**:
```powershell
# Verify files exist
Test-Path "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_CAD\timereport\yearly\2025\2025_full_timereport.xlsx"
Test-Path "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_CAD\timereport\monthly\2026_01_timereport.xlsx"
```

### Issue: "Mapping file not found"

**Cause**: Response_Type_Mapping.xlsx missing

**Solution**:
```powershell
# Verify mapping file
Test-Path "C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Response_Times\input\Response_Type_Mapping.xlsx"

# If missing, check alternate location
Test-Path "C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Response_Times\Response_Type_Mapping.xlsx"
```

### Issue: "High number of unmapped incidents"

**Cause**: New incident types not in mapping file

**Solution**:
1. Check log file for unmapped types
2. Update `Response_Type_Mapping.xlsx` with new types
3. Re-run script

### Issue: "Power BI shows no data after refresh"

**Cause**: M code not finding new files

**Solution**:
```powerquery
// In Power Query Editor, check BackfillBasePath variable
// Should show: C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports
```

---

## 📈 Performance

### Expected Runtime
- **Data Volume**: 120,000-150,000 raw records
- **Processing Time**: 30-90 seconds
- **Output Size**: 13 CSV files (~1-2 KB each)
- **Memory Usage**: <500 MB

### Optimization Tips
1. Run during off-hours if processing large datasets
2. Increase timeout in `scripts.json` if needed (currently 60 min)
3. Monitor log files for performance bottlenecks

---

## 🔄 Integration with Master Automation

### Execution Order
```
1. Arrests (order: 1)
2. Community Engagement (order: 2)
3. Overtime TimeOff (order: 3)
4. Policy Training Monthly (order: 4, disabled)
5. Response Times Diagnostic (order: 5, disabled)
5.5. Response Times Monthly Generator (order: 5.5, disabled - LEGACY)
5.6. Response Times Fresh Calculator (order: 5.6, ENABLED) ← NEW
6. Summons (order: 6)
6.5. Summons Derived Outputs (order: 6.5)
```

### Configuration Entry
```json
{
  "name": "Response Times Fresh Calculator",
  "path": "C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\Master_Automation\\scripts",
  "script": "response_time_fresh_calculator.py",
  "enabled": true,
  "output_to_powerbi": true,
  "order": 5.6,
  "timeout_minutes": 60
}
```

---

## 📝 Comparison: Old vs New

### Old System (Response Times Monthly Generator)
- ❌ Used pre-aggregated CAD exports
- ❌ Required manual export from CAD system
- ❌ Inconsistent calculations across months
- ❌ No clear filtering documentation
- ❌ Generated backfill structure (complex folders)

### New System (Fresh Calculator v3.0.0)
- ✅ Uses raw timereport data (single source of truth)
- ✅ Automated hybrid loading (yearly + monthly)
- ✅ Consistent filtering from JSON configuration
- ✅ Documented methodology
- ✅ Simple output to _DropExports (Power BI ready)

---

## 🎯 Success Criteria

### After Implementation
- ✅ Fresh Calculator runs without errors
- ✅ All 13 monthly files generated
- ✅ Power BI query loads with 0% errors
- ✅ Dashboard visuals display complete data
- ✅ Values match expected methodology
- ✅ October 2025 baseline verified

### Monthly Workflow
1. Raw timereport files updated monthly (automatic)
2. Run Master Automation ETL (`run_all_etl.ps1`)
3. Fresh Calculator recalculates all months
4. Power BI refresh pulls new data
5. Monthly report generated

---

## 📞 Support

**Files to Check**:
- Script: `scripts/response_time_fresh_calculator.py`
- Config: `config/scripts.json`
- Filters: `config/response_time_filters.json`
- M Code: `m_code/___ResponseTimeCalculator.m`
- Log: `logs/*_response_time_fresh_calculator.log`

**Key Directories**:
- Raw Data: `05_EXPORTS\_CAD\timereport\`
- Output: `PowerBI_Date\_DropExports\`
- Mapping: `02_ETL_Scripts\Response_Times\input\`

---

**Implementation Guide Version**: 1.0  
**Fresh Calculator Version**: 3.0.0  
**M Code Version**: 2.8.1  
**Date**: 2026-02-09  
**Status**: ✅ Production Ready

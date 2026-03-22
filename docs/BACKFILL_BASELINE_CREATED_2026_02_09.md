# Backfill Baseline Created - 2026-02-09

## ✅ Successfully Created Backfill Directory Structure

**Date**: 2026-02-09  
**Source**: Current validated visual export data  
**Purpose**: Establish formal baseline for Response Time data  

---

## Directory Structure Created

```
PowerBI_Data\Backfill\
├── 2025_01\response_time\2025_01_Average_Response_Times__Values_are_in_mmss.csv
├── 2025_02\response_time\2025_02_Average_Response_Times__Values_are_in_mmss.csv
├── 2025_03\response_time\2025_03_Average_Response_Times__Values_are_in_mmss.csv
├── 2025_04\response_time\2025_04_Average_Response_Times__Values_are_in_mmss.csv
├── 2025_05\response_time\2025_05_Average_Response_Times__Values_are_in_mmss.csv
├── 2025_06\response_time\2025_06_Average_Response_Times__Values_are_in_mmss.csv
├── 2025_07\response_time\2025_07_Average_Response_Times__Values_are_in_mmss.csv
├── 2025_08\response_time\2025_08_Average_Response_Times__Values_are_in_mmss.csv
├── 2025_09\response_time\2025_09_Average_Response_Times__Values_are_in_mmss.csv
├── 2025_10\response_time\2025_10_Average_Response_Times__Values_are_in_mmss.csv
├── 2025_11\response_time\2025_11_Average_Response_Times__Values_are_in_mmss.csv
├── 2025_12\response_time\2025_12_Average_Response_Times__Values_are_in_mmss.csv
└── 2026_01\response_time\2026_01_Average_Response_Times__Values_are_in_mmss.csv
```

**Total Files**: 13 CSV files (Jan 2025 - Jan 2026)  
**Each File**: 3 rows (Emergency, Routine, Urgent) + header  

---

## Sample Data (October 2025)

```csv
"Response Type","MM-YY","First Response_Time_MMSS"
"Emergency","10-25","02:49"
"Routine","10-25","02:11"
"Urgent","10-25","02:52"
```

---

## M Code Integration

The M code (v2.8.3) will now prioritize loading from this Backfill folder:

### Load Priority:
1. ✅ **Backfill folder** (newly created) ← **Will load from here**
2. visual_export folder (fallback)
3. outputs\visual_exports (fallback)
4. _DropExports (fallback)

### Expected Behavior:
- Power BI will load all 13 monthly files from Backfill
- Data remains stable across refreshes
- New months can be added to this structure

---

## Next Steps

### For February 2026 Data:
When new data arrives for February 2026:

1. **Run ETL** for February data
2. **Refresh Power BI** to include February
3. **Export visual** to CSV
4. **Save to**:
   ```
   PowerBI_Data\Backfill\2026_02\response_time\2026_02_Average_Response_Times__Values_are_in_mmss.csv
   ```

### Monthly Workflow:
```powershell
# Example for adding March 2026:
$month = "2026_03"
$backfillPath = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\Backfill\$month\response_time"
New-Item -ItemType Directory -Path $backfillPath -Force

# Then export your visual to: $backfillPath\${month}_Average_Response_Times__Values_are_in_mmss.csv
```

---

## Verification

To verify the Backfill is working:

1. **Refresh Power BI** (Home → Refresh)
2. **Check source**: Should load from Backfill folder
3. **Data should remain unchanged** (same values as before)
4. **0% errors** in Response_Time_MMSS column

---

## Baseline Values (October 2025)

| Type | Value | Source |
|------|-------|--------|
| Emergency | 02:49 | Validated backfill baseline |
| Routine | 02:11 | Validated backfill baseline |
| Urgent | 02:52 | Validated backfill baseline |

These values represent your current validated data as of 2026-02-09.

---

## Files Created

- 13 monthly CSV files in Backfill structure
- Each file: ~134 bytes (3 data rows + header)
- Format: Standard Power BI visual export format
- Encoding: UTF-8 with quotes

---

## Status

✅ **Backfill baseline established**  
✅ **13 months of data preserved** (Jan 2025 - Jan 2026)  
✅ **M code ready** (v2.8.3 will prioritize Backfill)  
✅ **Structure repeatable** for future months  

**Next Action**: Refresh Power BI to verify it loads from Backfill folder

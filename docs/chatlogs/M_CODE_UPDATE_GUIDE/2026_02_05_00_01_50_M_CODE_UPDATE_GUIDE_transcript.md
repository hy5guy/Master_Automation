# M Code Update Guide

**Processing Date:** 2026-02-05 00:01:50
**Source File:** M_CODE_UPDATE_GUIDE.md
**Total Chunks:** 1

---

# M Code Update Guide for Backfill Data Integration

**Last Updated:** 2025-12-09  
**Purpose:** Guide for updating Power BI M code queries to use backfill data for historical period (November 2024 - October 2025)

---

## Overview

Reports that use M code (Power Query) in Power BI need to be updated to reference backfill directories for the historical period. This guide provides templates and specific instructions for each report. **Backfill Period:** November 2024 - October 2025  
**Live Data Starts:** November 2025 and forward  
**Base Backfill Path:** `C:\Dev\PowerBI_Date\Backfill\2025_10\`

---

## General M Code Pattern

All M code updates should follow this pattern:

```m
let
    // Define date boundaries
    CurrentDate = Date.From(DateTime.LocalNow()),
    BackfillEndDate = #date(2025, 10, 31),
    
    // Determine data source based on date
    Source = if CurrentDate <= BackfillEndDate then
        // Load from backfill directory for historical period
        LoadBackfillData()
    else
        // Load from live source for current period
        LoadLiveData(),
    
    // Continue with data transformations...
    ProcessedData = TransformData(Source)
in
    ProcessedData
```

---

## Response Times - Specific Implementation

**Query Name:** `___ResponseTimeCalculator`  
**Priority:** HIGH - Backfill files ready  
**📁 Final Scripts Available:** See `RESPONSE_TIMES_M_CODE_FINAL.txt` and `RESPONSE_TIMES_M_CODE_SIMPLE.txt`

### Backfill Files:
1. **For Average Response Times Table:**
   - `C:\Dev\PowerBI_Date\Backfill\2025_10\response_time\2025_10_Average Response Times Values are in mmss.csv`
   
2. **For Response Times by Priority Line Graph:**
   - `C:\Dev\PowerBI_Date\Backfill\2025_10\response_time\2025_10_Response Times by Priority.csv`

### November 2025 ETL Output Files:
1. **Average Response Times (November 2025):**
   - `C:\Dev\PowerBI_Date\Backfill\2025_12\response_time\2025_12_Average_Response_Times__Values_are_in_mmss.csv`
   
2. **Response Times by Priority (November 2025):**
   - Check if available in `C:\Dev\PowerBI_Date\Backfill\2025_12\response_time\`

### M Code Template for Response Times:

```m
let
    // Determine if we should use backfill or live data
    CurrentDate = Date.From(DateTime.LocalNow()),
    BackfillEndDate = #date(2025, 10, 31),
    
    // Average Response Times Table
    AverageResponseTimes = if CurrentDate <= BackfillEndDate then
        Csv.Document(
            File.Contents("C:\Dev\PowerBI_Date\Backfill\2025_10\response_time\2025_10_Average Response Times Values are in mmss.csv"),
            [Delimiter=",", Columns=null, Encoding=1252, QuoteStyle=QuoteStyle.None]
        )
    else
        LoadLiveAverageResponseTimes(),
    
    // Response Times by Priority
    ResponseTimesByPriority = if CurrentDate <= BackfillEndDate then
        Csv.Document(
            File.Contents("C:\Dev\PowerBI_Date\Backfill\2025_10\response_time\2025_10_Response Times by Priority.csv"),
            [Delimiter=",", Columns=null, Encoding=1252, QuoteStyle=QuoteStyle.None]
        )
    else
        LoadLiveResponseTimesByPriority(),
    
    // Combine or process data as needed
    Result = ProcessResponseTimeData(AverageResponseTimes, ResponseTimesByPriority)
in
    Result
```

### Implementation Steps:

1. **Locate the `___ResponseTimeCalculator` query** in Power BI Desktop
2. **Identify current data source** (how it currently loads data)
3. **Add date-based conditional logic** to check if data should come from backfill
4. **Update to load from backfill files** for dates ≤ October 31, 2025
5. **Keep existing live data source** for dates > October 31, 2025
6. **Test the query** to ensure both backfill and live data load correctly

### Important Notes:

- **Date Logic:** The condition `CurrentDate <= BackfillEndDate` means:
  - If today's date is before/on Oct 31, 2025 → use backfill
  - If today's date is after Oct 31, 2025 → use live source
  - **Note:** This may need adjustment depending on your refresh schedule and data availability dates

- **Alternative Date Logic** (if you want to use backfill for specific date ranges in the data):
```m
    // Check if the data date falls within backfill period
    DataDate = #date(2024, 11, 1), // Example: start of backfill period
    BackfillStartDate = #date(2024, 11, 1),
    BackfillEndDate = #date(2025, 10, 31),
    
    UseBackfill = DataDate >= BackfillStartDate and DataDate <= BackfillEndDate
```

---

## Other M Code Reports

The following reports also need M code updates. Use the general pattern above with their specific backfill directories:

### SSOCC (Safe Streets Operations Control Center)
- **Backfill Path:** `C:\Dev\PowerBI_Date\Backfill\2025_10\ssocc\`
- Update M code to load all files from this directory for historical period

### STACP
- **Backfill Path:** `C:\Dev\PowerBI_Date\Backfill\2025_10\stacp\`
- Update M code to load all files from this directory for historical period

### Traffic
- **Backfill Path:** `C:\Dev\PowerBI_Date\Backfill\2025_10\traffic\`
- Update M code to load all files from this directory for historical period

### Drone
- **Backfill Path:** `C:\Dev\PowerBI_Date\Backfill\2025_10\drone\`
- Update M code to load all files from this directory for historical period

### Detectives
- **Backfill Path:** `C:\Dev\PowerBI_Date\Backfill\2025_10\detectives\`
- Update M code to load all files from this directory for historical period

### CSB (Community Services Bureau)
- **Backfill Path:** `C:\Dev\PowerBI_Date\Backfill\2025_10\csb\`
- Update M code to load all files from this directory for historical period

### Chief Law Enforcement Duties
- **Backfill Path:** `C:\Dev\PowerBI_Date\Backfill\2025_10\chief_law_enforcement_duties\`
- Update M code to load all files from this directory for historical period

### NIBRS
- **Backfill Path:** `C:\Dev\PowerBI_Date\Backfill\2025_10\nibrs\`
- Update M code to load all files from this directory for historical period (if using M code instead of Python)

---

## Folder.Files Pattern (For Multiple Files)

If your backfill directory contains multiple files that need to be combined:

```m
let
    // Load all files from backfill directory
    BackfillFolder = Folder.Files("C:\Dev\PowerBI_Date\Backfill\2025_10\[category]"),
    
    // Combine all CSV/Excel files
    CombinedData = Table.Combine(
        Table.AddColumn(BackfillFolder, "Data", each 
            if Text.EndsWith([Name], ".csv") then
                Csv.Document([Content])
            else if Text.EndsWith([Name], ".xlsx") then
                Excel.Workbook([Content])[Data]{0}[Data]
            else
                null
        )[Data]
    ),
    
    // Filter out nulls and continue processing
    CleanedData = Table.SelectRows(CombinedData, each [Data] <> null),
    Processed = ProcessData(CleanedData)
in
    Processed
```

---

## Testing Checklist

After updating M code:

- [ ] Verify backfill data loads correctly for dates Nov 2024 - Oct 2025
- [ ] Verify live data loads correctly for dates Nov 2025+
- [ ] Check that date transitions work smoothly (no gaps or overlaps)
- [ ] Test Power BI refresh to ensure no errors
- [ ] Verify data matches expected backfill files
- [ ] Check performance (large backfill files may slow refresh)
- [ ] Validate data quality and completeness

---

## Common Issues and Solutions

### Issue: Date Logic Not Working
**Solution:** Verify date format and timezone. Consider using `DateTimeZone.ToLocal(DateTimeZone.UtcNow())` if timezone issues occur. ### Issue: Files Not Found
**Solution:** 
- Verify exact file paths and names (case-sensitive on some systems)
- Check file permissions
- Ensure files are not locked by another process

### Issue: Data Format Mismatch
**Solution:**
- Compare column structure between backfill and live data
- May need to add data transformation steps to normalize formats
- Consider adding error handling for missing columns

### Issue: Refresh Performance
**Solution:**
- Consider loading backfill data incrementally
- Use query folding where possible
- Optimize data transformations
- Consider using incremental refresh if available

---

## Resources

- **Power Query M Documentation:** https://docs.microsoft.com/en-us/powerquery-m/
- **Backfill Locations:** See `BACKFILL_LOCATIONS.md`
- **Action Items:** See `ACTION_ITEMS.md`
- **Master Automation:** See `README.md`

---

**Next Steps:**
1. Start with Response Times (`___ResponseTimeCalculator`) - files are ready
2. Update remaining 8 reports using the general pattern
3. Test all queries thoroughly before production use
4. Document any report-specific patterns or issues encountered


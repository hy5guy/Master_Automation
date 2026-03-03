# Power BI Monthly Report Information

**Last Updated:** 2025-12-10

## Current Monthly Report

**File:** `25_11_Monthly_FINAL.pbix`  
**Location:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Monthly Reports\2025\11 - November - 2025\`  
**Period:** November 2025  
**Due Date:** Tomorrow (2025-12-11)

---

## M Code Updates Required

### Response Times Query: `___ResponseTimeCalculator`

**Status:** ⏳ Pending Update

**Requirements:**
1. Load backfill data (Nov 2024 - Oct 2025) from:
   - `C:\Dev\PowerBI_Date\Backfill\2025_10\response_time\2025_10_Average Response Times Values are in mmss.csv`
   - `C:\Dev\PowerBI_Date\Backfill\2025_10\response_time\2025_10_Response Times by Priority.csv`

2. Load November 2025 data from ETL output:
   - `C:\Dev\PowerBI_Date\Backfill\2025_12\response_time\Average_Response_Times__Values_are_in_mmss.csv`
   - Other November 2025 response time files as needed

3. Combine datasets with proper date continuity

**Reference:** See `M_CODE_UPDATE_GUIDE.md` for detailed templates and instructions.

---

## Data Sources for November 2025 Report

### ETL Script Outputs
All ETL scripts have been executed successfully (2025-12-10):
- **268 total files** generated and organized
- **Location:** `C:\Dev\PowerBI_Date\Backfill\2025_12\`
- **Organized by category:** arrest, community_outreach, policy_training, response_time, stacp, summons, traffic

### Backfill Data (Nov 2024 - Oct 2025)
- **Location:** `C:\Dev\PowerBI_Date\Backfill\2025_10\`
- **18 backfill directories** documented in `BACKFILL_LOCATIONS.md`
- Used for historical period reporting

---

## Quick Checklist for Report Completion

- [ ] Update Response Times M code query (`___ResponseTimeCalculator`)
- [ ] Verify all other M code queries are up to date (if applicable)
- [ ] Test Power BI refresh - all queries load successfully
- [ ] Verify date ranges and data continuity
- [ ] Check all visualizations display correctly
- [ ] Validate data totals and calculations
- [ ] Final review before submission

---

## Related Documentation

- **[M_CODE_UPDATE_GUIDE.md](M_CODE_UPDATE_GUIDE.md)** - Templates and instructions for M code updates
- **[BACKFILL_LOCATIONS.md](BACKFILL_LOCATIONS.md)** - Complete backfill data locations
- **[ACTION_ITEMS.md](ACTION_ITEMS.md)** - All pending action items
- **[MISSING_DATA_EXPORTS.md](MISSING_DATA_EXPORTS.md)** - ETL execution results

---

**Note:** This file tracks the active monthly report being worked on. Update this file when starting work on a new month's report.


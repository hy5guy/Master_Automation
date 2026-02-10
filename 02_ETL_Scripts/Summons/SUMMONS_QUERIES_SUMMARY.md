# Summons Power BI Queries - Summary

**Updated:** 2026-01-11 01:28:55 EST  
**Status:** Active Queries for Summons Page

---

## Query Names and Purpose

### 1. `summons_13month_trend`
**Replaces:** `___Summons` (previously `___Backfill`)  
**Purpose:** Loads all summons data with complete columns for:
- 13-month trend visual (aggregated in Power BI)
- All bureaus visual (detail view with bureau assignments)

**Columns Included:** All 35 columns from the October preview table:
- Ticket data: `TICKET_NUMBER`, `TICKET_COUNT`, `IS_AGGREGATE`
- Officer data: `PADDED_BADGE_NUMBER`, `OFFICER_DISPLAY_NAME`, `OFFICER_NAME_RAW`
- Assignment data: `TEAM`, `WG1`, `WG2`, `WG3`, `WG4`, `WG5`, `POSS_CONTRACT_TYPE`, `ASSIGNMENT_FOUND`
- Violation data: `VIOLATION_NUMBER`, `VIOLATION_DESCRIPTION`, `VIOLATION_TYPE`, `TYPE`, `STATUS`, `LOCATION`, `WARNING_FLAG`
- Date data: `ISSUE_DATE`, `Year`, `Month`, `YearMonthKey`, `Month_Year`
- Financial data: `TOTAL_PAID_AMOUNT`, `FINE_AMOUNT`, `COST_AMOUNT`, `MISC_AMOUNT`
- Metadata: `SOURCE_FILE`, `ETL_VERSION`, `DATA_QUALITY_SCORE`, `DATA_QUALITY_TIER`, `PROCESSING_TIMESTAMP`

**Data Sources:**
- Historical backfill: `IS_AGGREGATE = true` OR `ETL_VERSION = "HISTORICAL_SUMMARY"`
- Current month: `ETL_VERSION = "ETICKET_CURRENT"`

**Usage in Power BI:**
- 13-month trend visual: Use `SUM(TICKET_COUNT)` measure, group by `Month_Year` and `TYPE`
- All bureaus visual: Use detail columns for filtering and grouping by bureau (`WG2`)

---

### 2. `summons_top5_moving`
**Replaces:** `___Top_5_Moving_Violations`  
**Purpose:** Top 5 officers with most moving violations in the most recent completed month

**Returns:** Rank, Officer, Badge, Bureau, Summons Count

**Filters:**
- `TYPE = "M"` (Moving violations only)
- `IS_AGGREGATE = false` (Individual tickets only)
- Most recent `YearMonthKey` (current completed month)
- Excludes "MULTIPLE OFFICERS (Historical)" records

---

### 3. `summons_top5_parking`
**Replaces:** `___Top_5_Parking_Violations`  
**Purpose:** Top 5 officers with most parking violations in the most recent completed month

**Returns:** Rank, Officer, Badge, Bureau, Summons Count

**Filters:**
- `TYPE = "P"` (Parking violations only)
- `IS_AGGREGATE = false` (Individual tickets only)
- Most recent `YearMonthKey` (current completed month)
- Excludes "MULTIPLE OFFICERS (Historical)" records

---

## Data Source File

All queries read from:
```
C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx
```

Sheet: `Summons_Data`

---

## Assignment Data

Officer assignments come from:
```
C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Personnel\Assignment_Master_V2.csv
```

The ETL script (`SummonsMaster_Simple.py`) enriches the data with assignment information by joining on `PADDED_BADGE_NUMBER`.

---

## Important Notes

1. **13-Month Trend Visual:**
   - Must use `SUM(TICKET_COUNT)` measure (not `COUNTROWS`)
   - Group by `Month_Year` and `TYPE`
   - Sort by `Month_Year` or create a `SortKey` column in a calculated table/column if needed

2. **All Bureaus Visual:**
   - Uses all detail columns from `summons_13month_trend`
   - Filter by `WG2` for bureau breakdown
   - Can filter by current month using `YearMonthKey = MAX(YearMonthKey)`

3. **Top 5 Visuals:**
   - Automatically filter to most recent completed month
   - Only show individual tickets (not aggregate records)
   - Ranked by total summons count

---

## Query File Locations

All M code files are in:
```
C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Summons\
```

Files:
- `summons_13month_trend.m`
- `summons_top5_moving.m`
- `summons_top5_parking.m`

---

## Migration from Old Query Names

| Old Name | New Name | Status |
|----------|----------|--------|
| `___Backfill` | `summons_13month_trend` | ✅ Updated (now includes all columns) |
| `___Summons` | `summons_13month_trend` | ✅ Merged into summons_13month_trend |
| `___Top_5_Moving_Violations` | `summons_top5_moving` | ✅ Updated |
| `___Top_5_Parking_Violations` | `summons_top5_parking` | ✅ Updated |

---

## Troubleshooting

### Issue: 13-month trend visual shows incorrect totals
**Solution:** Ensure the visual uses `SUM(TICKET_COUNT)` measure, not `COUNTROWS()`.

### Issue: All bureaus visual missing assignment columns
**Solution:** Verify `summons_13month_trend` query includes all columns (WG1, WG2, WG3, WG4, WG5, TEAM).

### Issue: Top 5 visuals not showing current month
**Solution:** Check that the Excel file has been updated with the latest month's data. The query automatically uses `MAX(YearMonthKey)`.

---

**Last Updated:** 2026-01-11 01:28:55 EST

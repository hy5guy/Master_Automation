# Prompt for Claude (Power BI MCP) — Summons Month Fix

**Use this prompt with Claude Code or Claude Desktop when the Power BI MCP server is connected and your Power BI file (e.g. TEST_2026_02_Monthly_Report_TEST.pbix) is open.**

---

## Context

All four Summons visuals show January 2026 data (or no 02-26 column) when the report is for February 2026. Root cause: M code uses "previous month" or `List.Max(YearMonthKey)` instead of the report month (`pReportMonth`).

**Affected visuals:**
1. **Department-Wide Summons | Moving and Parking** — columns stop at 01-26, no 02-26
2. **Summons | Moving & Parking | All Bureaus** — shows January data
3. **Top 5 Moving Violations** — uses List.Max, inconsistent
4. **Top 5 Parking Violations** — uses List.Max, inconsistent

---

## Your Task

Use your Power BI MCP tools to update the M code for these four partitions. Connect to the local Power BI instance, then apply the changes below.

**Partitions to update:**
- `summons_13month_trend`
- `summons_all_bureaus`
- `summons_top5_moving`
- `summons_top5_parking`

---

## Fix 1: summons_13month_trend

**Change:** End the 13-month window at the **report month**, not the previous month.

Replace lines 5–6 (header comment) and lines 10–12 (EndDate/StartDate) with:

```m
// # Rolling 13-month window driven by pReportMonth: EndDate = pReportMonth (report month),
// #   StartDate = 12 months before EndDate. E.g. pReportMonth=02/01/2026 → 02-25 through 02-26.
```

And replace:
```m
    // 13-month window ending at previous complete month
    EndDate   = Date.AddMonths(DateTime.Date(pReportMonth), -1),
    StartDate = Date.AddMonths(EndDate, -12),
```

With:
```m
    // 13-month window ending at report month (e.g. pReportMonth=02/01/2026 → 02-25 through 02-26)
    EndDate   = DateTime.Date(pReportMonth),
    StartDate = Date.AddMonths(EndDate, -12),
```

---

## Fix 2: summons_all_bureaus

**Change:** Filter to the **report month**, not the previous month.

Replace lines 4–6 (header) and lines 9–11 and 19 with:

Header:
```m
// # Purpose: Aggregate summons counts by bureau for moving and parking violations (report month).
// # Note: pReportMonth is a Date type (#date(YYYY,M,1)); filter to report month so visual matches subtitle.
```

Logic:
```m
    // Report month (e.g. pReportMonth=02/01/2026 -> Feb 2026 -> ReportMonthKey=202602)
    ReportMonthKey = Date.Year(DateTime.Date(pReportMonth)) * 100 + Date.Month(DateTime.Date(pReportMonth)),
```

And change line 19 from:
```m
    FilteredLatestMonth = Table.SelectRows(WG2Mapped, each [YearMonthKey] = PreviousMonthKey),
```
To:
```m
    FilteredLatestMonth = Table.SelectRows(WG2Mapped, each [YearMonthKey] = ReportMonthKey),
```

---

## Fix 3: summons_top5_moving

**Change:** Use `pReportMonth` instead of `List.Max(YearMonthKey)`.

Replace lines 26–30:
```m
    // Find LATEST month using YearMonthKey (integer sorting, not text!)
    LatestKey = List.Max(FilteredMovingNoPEO[YearMonthKey]),
    
    // Filter to latest month only
    FilteredLatestMonth = Table.SelectRows(FilteredMovingNoPEO, each [YearMonthKey] = LatestKey),
```

With:
```m
    // Filter to report month (pReportMonth-driven, not List.Max)
    ReportMonthKey = Date.Year(DateTime.Date(pReportMonth)) * 100 + Date.Month(DateTime.Date(pReportMonth)),
    FilteredLatestMonth = Table.SelectRows(FilteredMovingNoPEO, each [YearMonthKey] = ReportMonthKey),
```

---

## Fix 4: summons_top5_parking

**Change:** Use `pReportMonth` instead of `List.Max(YearMonthKey)`.

Replace lines 17–21:
```m
    // Find LATEST month using YearMonthKey (integer sorting, not text!)
    LatestKey = List.Max(FilteredParking[YearMonthKey]),
    
    // Filter to latest month only
    FilteredLatestMonth = Table.SelectRows(FilteredParking, each [YearMonthKey] = LatestKey),
```

With:
```m
    // Filter to report month (pReportMonth-driven, not List.Max)
    ReportMonthKey = Date.Year(DateTime.Date(pReportMonth)) * 100 + Date.Month(DateTime.Date(pReportMonth)),
    FilteredLatestMonth = Table.SelectRows(FilteredParking, each [YearMonthKey] = ReportMonthKey),
```

---

## MCP Workflow

1. **Connect:** Use `model_operations` or equivalent to list local instances and connect to the open Power BI model.
2. **Get partitions:** Use `partition_operations` with action `Get` (or `List` then `Get`) for each partition to retrieve the current M code.
3. **Update partitions:** Use `partition_operations` with action `Update` (or equivalent) to replace the partition M code with the corrected version. Apply the text replacements above to the retrieved M code, then write back.
4. **Refresh:** After all four partitions are updated, instruct the user to refresh the model in Power BI Desktop (or use refresh tools if available).

---

## Verification

After applying and refreshing:
- **Department-Wide:** Columns should include 02-26; M, P, Total for February 2026.
- **All Bureaus:** Subtitle "Summons issued during February 2026" should match bureau totals.
- **Top 5 Moving / Parking:** Subtitles "February 2026" should match officer counts.

**Prerequisite:** Ensure `summons_slim_for_powerbi.csv` contains rows with `YearMonthKey = 202602`. If the trend table still maxes at 202601 after the M fix, run:

```powershell
cd C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation
python run_summons_etl.py --month 2026_02
```

This regenerates the slim CSV with proper `YearMonthKey = 202602` on all February rows. Then refresh all four summons tables in Power BI.

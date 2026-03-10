# Summons Round 3 Fix — Claude MCP Execution Prompt

> **Purpose:** Fix 3 issues found after post-ETL refresh: Feb 2025 missing from trend, dept-wide totals undercounting (WG2 filter), and July 2025 hidden.
>
> **Model:** `2026_02_Monthly_Report` (currently open in Power BI Desktop)
>
> **Parameter:** `pReportMonth` should already be `#date(2026, 3, 1)` — verify, do NOT change.
>
> **Date:** 2026-03-10

---

## What You Are Fixing

| Bug | Query | Symptom | Fix |
|-----|-------|---------|-----|
| 13-month window uses `pReportMonth` as EndDate, but all_bureaus uses `pReportMonth - 1`. With pReportMonth=March 2026, window starts at March 2025, excluding Feb 2025 | `summons_13month_trend` | 02-25 missing from trend | Change EndDate to `Date.AddMonths(pReportMonth, -1)` |
| WG2 filter (`[WG2] <> null and <> ""`) in dept-wide trend excludes officers with no bureau (K. Peralta, 30 tickets) | `summons_13month_trend` | Dept-wide M=419 instead of 421, P=2326 instead of 2354 | Remove WG2 filter entirely (dept-wide counts all officers) |
| BackfillMonths = {"07-25"} filters out 17 straggler records (IS_AGGREGATE=False) but no backfill file exists | `summons_13month_trend` | July 2025 completely missing | Clear BackfillMonths to {} |
| Total column returns null when C column is null (try catches errors, not nulls) | `summons_all_bureaus` | SSOCC, DETECTIVE rows show blank Total | Use `[C] ?? 0` null coalesce |

---

## Pre-Flight

Verify connection and parameter:

```
connection_operations -> ListLocalInstances
connection_operations -> Connect (use the returned connection string)
```

```
named_expression_operations -> Get -> references: [{ "name": "pReportMonth" }]
```

Confirm it's `#date(2026, 3, 1)`. If not, update it before proceeding.

---

## Update 1: summons_13month_trend (FULL REPLACEMENT)

This is a complete replacement of the partition M code. Apply it exactly:

```
partition_operations -> Update
definitions: [{
  "tableName": "summons_13month_trend",
  "expression": "let\n    // 13-month window ending at previous complete month (pReportMonth - 1), spanning 12 months back.\n    // e.g. pReportMonth=03/01/2026 → EndDate=Feb 2026, StartDate=Feb 2025 → 02-25 through 02-26\n    EndDate = Date.AddMonths(DateTime.Date(pReportMonth), -1),\n    StartDate = Date.AddMonths(EndDate, -12),\n    EndYM = Date.Year(EndDate) * 100 + Date.Month(EndDate),\n    StartYM = Date.Year(StartDate) * 100 + Date.Month(StartDate),\n\n    Source = Csv.Document(File.Contents(\"C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\03_Staging\\Summons\\summons_slim_for_powerbi.csv\"), [Delimiter=\",\", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n    ExistingCols = Table.ColumnNames(PromotedHeaders),\n    TypeMap = {\n        {\"PADDED_BADGE_NUMBER\", type text},\n        {\"OFFICER_DISPLAY_NAME\", type text},\n        {\"OFFICER_NAME_RAW\", type text},\n        {\"ISSUE_DATE\", type datetime},\n        {\"TYPE\", type text},\n        {\"ETL_VERSION\", type text},\n        {\"IS_AGGREGATE\", type text},\n        {\"Year\", Int64.Type},\n        {\"Month\", Int64.Type},\n        {\"YearMonthKey\", Int64.Type},\n        {\"Month_Year\", type text},\n        {\"WG2\", type text},\n        {\"DATA_QUALITY_SCORE\", Int64.Type}\n    },\n    FilteredTypes = List.Select(TypeMap, each List.Contains(ExistingCols, _{0})),\n    ChangedType = Table.TransformColumnTypes(PromotedHeaders, FilteredTypes),\n    // No WG2 filter — this is department-wide; all officers count regardless of bureau assignment.\n    FilteredMonthYear = Table.SelectRows(ChangedType, each\n        [YearMonthKey] <> null and [YearMonthKey] >= StartYM and [YearMonthKey] <= EndYM\n    ),\n    BackfillMonths = {},\n    FilteredPreferBackfill = Table.SelectRows(FilteredMonthYear, each\n        if List.Contains(BackfillMonths, [Month_Year])\n        then Text.Upper(Text.From([IS_AGGREGATE] ?? \"false\")) = \"TRUE\"\n        else true\n    ),\n    WithTicketCount = if Table.HasColumns(FilteredPreferBackfill, \"TICKET_COUNT\")\n        then Table.TransformColumnTypes(FilteredPreferBackfill, {{\"TICKET_COUNT\", Int64.Type}})\n        else Table.AddColumn(FilteredPreferBackfill, \"TICKET_COUNT\", each 1, Int64.Type),\n    AddConsolidatedBureau = Table.AddColumn(WithTicketCount, \"Bureau_Consolidated\", each if [WG2] = \"HOUSING\" or [WG2] = \"OFFICE OF SPECIAL OPERATIONS\" or [WG2] = \"PATROL BUREAU\" then \"PATROL DIVISION\" else [WG2], type text)\nin\n    AddConsolidatedBureau"
}]
```

---

## Update 2: summons_all_bureaus (Total formula fix only)

```
partition_operations -> Update
definitions: [{
  "tableName": "summons_all_bureaus",
  "expression": "let\n    PrevDate = Date.AddMonths(DateTime.Date(pReportMonth), -1),\n    PreviousMonthKey = Date.Year(PrevDate) * 100 + Date.Month(PrevDate),\n\n    Source = Csv.Document(File.Contents(\"C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\03_Staging\\Summons\\summons_slim_for_powerbi.csv\"), [Delimiter=\",\", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {{\"YearMonthKey\", Int64.Type}, {\"TICKET_COUNT\", Int64.Type}, {\"TYPE\", type text}, {\"WG2\", type text}}),\n\n    FilteredClean = Table.SelectRows(ChangedType, each [WG2] <> \"UNKNOWN\" and [WG2] <> \"nan\" and [WG2] <> null and [WG2] <> \"\"),\n    FilteredLatestMonth = Table.SelectRows(FilteredClean, each [YearMonthKey] = PreviousMonthKey),\n\n    GroupedRows = Table.Group(\n        FilteredLatestMonth,\n        {\"WG2\", \"TYPE\"},\n        {{\"Count\", each List.Sum([TICKET_COUNT]), type number}}\n    ),\n\n    ConsolidatedBureaus = Table.TransformColumns(\n        GroupedRows,\n        {\"WG2\", each if _ = \"HOUSING\" or _ = \"OFFICE OF SPECIAL OPERATIONS\" or _ = \"PATROL BUREAU\"\n            then \"PATROL DIVISION\" else _}\n    ),\n\n    RegroupedRows = Table.Group(\n        ConsolidatedBureaus,\n        {\"WG2\", \"TYPE\"},\n        {{\"Count\", each List.Sum([Count]), type number}}\n    ),\n\n    PivotedColumn = Table.Pivot(\n        RegroupedRows,\n        List.Distinct(RegroupedRows[TYPE]),\n        \"TYPE\",\n        \"Count\",\n        List.Sum\n    ),\n\n    AddM = if Table.HasColumns(PivotedColumn, \"M\") then PivotedColumn\n        else Table.AddColumn(PivotedColumn, \"M\", each 0, Int64.Type),\n    AddP = if Table.HasColumns(AddM, \"P\") then AddM\n        else Table.AddColumn(AddM, \"P\", each 0, Int64.Type),\n\n    ReplacedValue = Table.ReplaceValue(AddP, null, 0, Replacer.ReplaceValue, {\"M\", \"P\"}),\n\n    AddedTotal = Table.AddColumn(\n        ReplacedValue,\n        \"Total\",\n        each [M] + [P] + (try ([C] ?? 0) otherwise 0),\n        type number\n    ),\n\n    RenamedColumns = Table.RenameColumns(AddedTotal, {{\"WG2\", \"Bureau\"}})\nin\n    RenamedColumns"
}]
```

---

## Refresh

```
table_operations -> Refresh -> references: [{ "name": "summons_13month_trend" }]
table_operations -> Refresh -> references: [{ "name": "summons_all_bureaus" }]
```

(top5 queries unchanged — no need to refresh them unless you want to verify.)

---

## Mandatory Validation

### Check 1: 13-month trend has 13 months including 02-25 and 07-25

```
dax_query_operations -> Execute
query:
  EVALUATE
  SUMMARIZECOLUMNS(
    'summons_13month_trend'[Month_Year],
    'summons_13month_trend'[TYPE],
    "Tickets", SUM('summons_13month_trend'[TICKET_COUNT])
  )
```

**Show me the full result table.** I expect:

- **13 months**: 02-25, 03-25, 04-25, 05-25, 06-25, **07-25**, 08-25, 09-25, 10-25, 11-25, 12-25, 01-26, 02-26
- **02-25 MUST be present**: M ~324, P ~2,368
- **07-25 MUST be present**: small numbers (17 total straggler records)
- **02-26**: M=421, P=2,354 (includes Peralta's 2 M + 28 P that were previously filtered)
- All C values < 100

### Check 2: All Bureaus — SSOCC present, no nan row, Totals populated

```
dax_query_operations -> Execute
query: EVALUATE 'summons_all_bureaus'
```

I expect:
- SSOCC: M=0, P=4, **Total=4** (not blank)
- DETECTIVE BUREAU: M=1, P=0, **Total=1** (not blank)
- No row labeled "nan"
- TRAFFIC BUREAU Total should equal M + P (e.g. 230 + 2022 = 2252 + C)

### Check 3: Dept-wide Feb 2026 totals now include Peralta

From the Check 1 results, confirm 02-26 shows:
- **M = 421** (not 419)
- **P = 2,354** (not 2,326)

If M=419 and P=2,326, the WG2 filter was NOT removed — re-apply Update 1.

---

## Summary

| Check | Status | Detail |
|-------|--------|--------|
| 02-25 in trend | PASS/FAIL | Present? M=? P=? |
| 07-25 in trend | PASS/FAIL | Present? Ticket count? |
| 02-26 dept-wide M | PASS/FAIL | 421 or 419? |
| 02-26 dept-wide P | PASS/FAIL | 2,354 or 2,326? |
| All bureaus Total column | PASS/FAIL | SSOCC/DETECTIVE Total populated? |
| No nan row | PASS/FAIL | nan row absent? |
| Total months | PASS/FAIL | 13 months? |

---

## About the Image Tickets (E26005828–E26006719)

Those 19 tickets are from **M. RAMIREZ-DRAKEFORD #2025** (Traffic Bureau), all Parking (88-6D(2) Fire Lanes), all Feb 2026. They ARE included in the data — they're part of TRAFFIC BUREAU's P=2,022 count in all_bureaus. These are not Polson's tickets (Polson's are E26005452, E26005461, E26005467, E26006376).

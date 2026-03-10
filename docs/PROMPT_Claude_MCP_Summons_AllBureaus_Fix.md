# Claude MCP Prompt: Update summons_all_bureaus Partition

**Copy-paste this into a new Claude Desktop conversation (with Power BI MCP enabled) to apply the summons_all_bureaus M code fix.**

---

## Task

Connect to Power BI Desktop and update the `summons_all_bureaus` partition with the M code below. Then refresh the table.

**Context:** The All Bureaus M total is 2 less than department-wide because records with UNKNOWN/nan/null/blank WG2 were being filtered out. The fix maps those to "UNASSIGNED" so the sum matches.

---

## Steps

1. **Connect** to Power BI Desktop (use `mcp_powerbi-modeling-mcp_connection_operations` with operation `Connect` if not already connected).

2. **Update** the `summons_all_bureaus` partition with the M expression below. Use `mcp_powerbi-modeling-mcp_partition_operations` with operation `Update`, or `mcp_powerbi-modeling-mcp_table_operations` if the partition expression is set at the table level. The partition/table sources from `summons_slim_for_powerbi.csv`.

3. **Refresh** the `summons_all_bureaus` table using the appropriate refresh operation.

4. **Verify** that All Bureaus now shows an UNASSIGNED row and that the M total matches department-wide (421 for Feb 2026).

---

## M Code to Apply

```powerquery
let
    // Previous complete month (e.g. pReportMonth=02/01/2026 -> Jan 2026 -> PreviousMonthKey=202601)
    PrevDate = Date.AddMonths(DateTime.Date(pReportMonth), -1),
    PreviousMonthKey = Date.Year(PrevDate) * 100 + Date.Month(PrevDate),

    Source = Csv.Document(File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_slim_for_powerbi.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {{"YearMonthKey", Int64.Type}, {"TICKET_COUNT", Int64.Type}, {"TYPE", type text}, {"WG2", type text}}),

    // Map UNKNOWN / blank / "nan" WG2 to UNASSIGNED so sum of bureaus = department-wide
    WG2Mapped = Table.TransformColumns(ChangedType, {"WG2", each if _ = null or _ = "" or _ = "UNKNOWN" or _ = "nan" then "UNASSIGNED" else _, type text}),
    FilteredLatestMonth = Table.SelectRows(WG2Mapped, each [YearMonthKey] = PreviousMonthKey),

    // Group by Bureau (WG2) and Type
    GroupedRows = Table.Group(
        FilteredLatestMonth,
        {"WG2", "TYPE"},
        {{"Count", each List.Sum([TICKET_COUNT]), type number}}
    ),

    // Consolidate HOUSING, OSO, and PATROL BUREAU into PATROL DIVISION
    ConsolidatedBureaus = Table.TransformColumns(
        GroupedRows,
        {"WG2", each if _ = "HOUSING" or _ = "OFFICE OF SPECIAL OPERATIONS" or _ = "PATROL BUREAU"
            then "PATROL DIVISION" else _}
    ),

    // Re-group after consolidation to merge any combined rows
    RegroupedRows = Table.Group(
        ConsolidatedBureaus,
        {"WG2", "TYPE"},
        {{"Count", each List.Sum([Count]), type number}}
    ),

    // Pivot by TYPE to get M, P columns
    PivotedColumn = Table.Pivot(
        RegroupedRows,
        List.Distinct(RegroupedRows[TYPE]),
        "TYPE",
        "Count",
        List.Sum
    ),

    AddM = if Table.HasColumns(PivotedColumn, "M") then PivotedColumn
        else Table.AddColumn(PivotedColumn, "M", each 0, Int64.Type),
    AddP = if Table.HasColumns(AddM, "P") then AddM
        else Table.AddColumn(AddM, "P", each 0, Int64.Type),

    ReplacedValue = Table.ReplaceValue(AddP, null, 0, Replacer.ReplaceValue, {"M", "P"}),

    AddedTotal = Table.AddColumn(
        ReplacedValue,
        "Total",
        each [M] + [P] + (try ([C] ?? 0) otherwise 0),
        type number
    ),

    // Rename WG2 to Bureau for cleaner visual display
    RenamedColumns = Table.RenameColumns(AddedTotal, {{"WG2", "Bureau"}})
in
    RenamedColumns
```

---

## Notes

- Ensure Power BI Desktop has the report open (e.g. `2026_02_Monthly_Report.pbix`).
- The partition may be named `summons_all_bureaus` or the table may have a single partition. Use List operations to find the correct target.
- After refresh, run the ETL (`python run_summons_etl.py --month 2026_02`) to regenerate the CSV with Ramirez SSOCC overrides, then refresh again in Power BI.

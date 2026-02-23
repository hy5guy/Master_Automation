// 🕒 2026-02-20-23-48-50
// # chief/___Chief2.m
// # Author: R. A. Carucci
// # Purpose: Load Chief of Police monthly activity metrics with YoY comparison and unpivoted periods.

let
    // === Load Chief Excel File ===
    Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Chief\chief_monthly.xlsx"), 
        null, true
    ),
    ChiefTable = Source{[Item="MoM_Chief", Kind="Table"]}[Data],

    // === Set Column Types Dynamically ===
    ColumnNames = Table.ColumnNames(ChiefTable),
    MonthColumns = List.Select(ColumnNames, each Text.Contains(_, "-") and Text.Length(_) >= 4),
    TrackedItemsType = {{"Tracked Items", type text}},
    MonthTypes       = List.Transform(MonthColumns, each {_, Int64.Type}),
    AllTypes         = List.Combine({TrackedItemsType, MonthTypes}),
    ChangedTypes     = Table.TransformColumnTypes(ChiefTable, AllTypes),

    // === Clean Text Data ===
    CleanedText  = Table.TransformColumns(ChangedTypes, {{"Tracked Items", Text.Clean, type text}}),
    TrimmedText  = Table.TransformColumns(CleanedText, {{"Tracked Items", Text.Trim, type text}}),
    FilteredRows = Table.SelectRows(TrimmedText, each [Tracked Items] <> ""),

    // === Classifications ===
    AddedCategory = Table.AddColumn(FilteredRows, "Category", each
        let item = Text.Upper([Tracked Items]) in
        if Text.Contains(item,"MEETING") then "Meetings & Conferences"
        else if Text.Contains(item,"TRAINING") then "Training & Development"
        else "Executive Administration"
    , type text),

    AddedDivision = Table.AddColumn(AddedCategory, "Division/Bureau", each "Chief of Police - Executive Office", type text),

    AddedActivityLevel = Table.AddColumn(AddedDivision, "Activity_Level", each
        let
          cols = MonthColumns,
          recent = List.LastN(cols,3),
          vals = List.Transform(recent, each try Record.Field(_,_) otherwise 0),
          avg3 = if List.Count(vals)>0 then List.Average(vals) else 0
        in
          if avg3>=10 then "High Activity"
          else if avg3>=5 then "Moderate Activity"
          else if avg3>0 then "Low Activity"
          else "No Recent Activity"
    , type text),

    AddedRecentTotal = Table.AddColumn(AddedActivityLevel, "Recent 3 Month Avg", each
        let
          cols = MonthColumns,
          recent = List.LastN(cols,3),
          vals = List.Transform(recent, each try Record.Field(_,_) otherwise 0),
          clean = List.Select(vals, each _<>null),
          a = if List.Count(clean)>0 then List.Average(clean) else 0
        in Number.Round(a,1)
    , type number),

    AddedYoYComparison = Table.AddColumn(AddedRecentTotal, "YoY Change %", each
        let
          cols = MonthColumns,
          sorted = List.Sort(cols),
          curr  = List.Last(sorted),
          parts = Text.Split(curr,"-"),
          mm    = parts{0},
          yy    = Number.From(parts{1}),
          prev  = mm & "-" & Text.From(yy-1),
          cVal  = Record.Field(_,curr),
          pVal  = try Record.Field(_,prev) otherwise 0,
          pct   = if pVal>0 then (cVal - pVal)/pVal*100 else 0
        in Number.Round(pct,1)
    , type number),

    // === NEW: Unpivot + Date + Type + Index ===
    Unpivoted     = Table.Unpivot(AddedYoYComparison, MonthColumns, "Month", "Total"),
    AddDate       = Table.AddColumn(Unpivoted, "PeriodDate", each Date.FromText("01-" & [Month]), type date),
    ChangeType2   = Table.TransformColumnTypes(AddDate, {{"Total", Int64.Type}}),
    AddMonthIndex = Table.AddColumn(ChangeType2, "MonthIndex", each Date.Year([PeriodDate])*100 + Date.Month([PeriodDate]), Int64.Type),

    // === Final columns ===
    Final = Table.SelectColumns(
      AddMonthIndex,
      {
        "Tracked Items",
        "Category",
        "Division/Bureau",
        "Activity_Level",
        "Recent 3 Month Avg",
        "YoY Change %",
        "Month",
        "PeriodDate",
        "Total",
        "MonthIndex"
      }
    )
in
    Final

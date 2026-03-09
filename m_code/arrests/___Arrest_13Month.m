// 🕒 2026-03-09-20-00-00
// # arrests/___Arrest_13Month.m
// # Author: R. A. Carucci
// # Purpose: Rolling 13-month arrest data from raw Lawsoft monthly exports.
// #          Dynamic file discovery, pReportMonth-driven window, charge and home enrichment.
// # Source:  05_EXPORTS\_Arrest\monthly\YYYY\*.xlsx

let
    // ═══ 1) Rolling 13-month window boundaries (pReportMonth-driven) ═══════
    EndOfWindow   = Date.EndOfMonth(pReportMonth),
    StartOfWindow = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12)),

    // ═══ 2) Dynamic file discovery ═════════════════════════════════════════
    BasePath = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Arrest\monthly",
    AllFiles = Folder.Files(BasePath),

    // Case-insensitive filter: .xlsx files containing "lawsoft" and "arrest"
    ArrestFiles = Table.SelectRows(
        AllFiles,
        each [Extension] = ".xlsx"
             and Text.Contains(Text.Lower([Name]), "lawsoft")
             and Text.Contains(Text.Lower([Name]), "arrest")
    ),

    // ═══ 3) Load each file, promote headers, tag with source ═══════════════
    WithData = Table.AddColumn(
        ArrestFiles,
        "TableData",
        each
            let
                wb = Excel.Workbook([Content], null, true),
                firstSheet = wb{0}[Data],
                promoted = Table.PromoteHeaders(firstSheet, [PromoteAllScalars = true])
            in
                promoted
    ),

    WithFileName = Table.SelectColumns(WithData, {"Name", "TableData"}),

    // Tag each row with its source file before combining
    Tagged = Table.AddColumn(
        WithFileName,
        "TaggedTable",
        each
            let
                src = [Name],
                tbl = [TableData]
            in
                Table.AddColumn(tbl, "SourceFile", each src, type text)
    ),

    Combined = Table.Combine(Tagged[TaggedTable]),

    // ═══ 4) Normalize column names ═════════════════════════════════════════
    // Handle variations: "Arrest Date" vs "Arrest_Date", "Officer of Record" vs "Officer_of_Record"
    ColNames = Table.ColumnNames(Combined),

    NormalizedDate =
        if List.Contains(ColNames, "Arrest Date") then Combined
        else if List.Contains(ColNames, "Arrest_Date") then
            Table.RenameColumns(Combined, {{"Arrest_Date", "Arrest Date"}})
        else Combined,

    NormalizedOfficer =
        if List.Contains(Table.ColumnNames(NormalizedDate), "Officer of Record") then NormalizedDate
        else if List.Contains(Table.ColumnNames(NormalizedDate), "Officer_of_Record") then
            Table.RenameColumns(NormalizedDate, {{"Officer_of_Record", "Officer of Record"}})
        else NormalizedDate,

    // ═══ 5) Parse Arrest Date and filter to window ═════════════════════════
    ToDate = (x) => try Date.From(x) otherwise null,

    WithParsedDate = Table.TransformColumns(
        NormalizedOfficer,
        {{"Arrest Date", ToDate, type nullable date}}
    ),

    ValidDates = Table.SelectRows(
        WithParsedDate,
        each [#"Arrest Date"] <> null
    ),

    Windowed = Table.SelectRows(
        ValidDates,
        each [#"Arrest Date"] >= StartOfWindow and [#"Arrest Date"] <= EndOfWindow
    ),

    // ═══ 6) Charge categorization (mirrors ___Arrest_Categories logic) ═════
    WithChargeCategory = Table.AddColumn(
        Windowed,
        "ChargeCategory",
        each
            let
                charge = Text.Upper([Charge] ?? "")
            in
                if Text.Contains(charge, "ASSAULT") then "Assault"
                else if Text.Contains(charge, "SHOPLIFTING") or Text.Contains(charge, "THEFT") then "Theft"
                else if Text.Contains(charge, "BURGLARY") then "Burglary"
                else if Text.Contains(charge, "ROBBERY") then "Robbery"
                else if Text.Contains(charge, "WARRANT") then "Warrant"
                else if Text.Contains(charge, "DWI") or Text.Contains(charge, "DUI") then "DWI"
                else if Text.Contains(charge, "DRUG") or Text.Contains(charge, "CDS") or Text.Contains(charge, "NARCOTIC") then "Drug Related"
                else if Text.Contains(charge, "WEAPON") or Text.Contains(charge, "FIREARM") or Text.Contains(charge, "GUN") then "Weapons"
                else "Other",
        type text
    ),

    // ═══ 7) Simplified home categorization (address-based) ═════════════════
    WithHomeCategory = Table.AddColumn(
        WithChargeCategory,
        "Home_Category",
        each
            let
                addr = Text.Upper(Text.Trim([Address] ?? ""))
            in
                if addr = "" or addr = "HOMELESS" or addr = "NONE" or addr = "UNKNOWN"
                    or Text.Contains(addr, "HACKENSACK")
                    or Text.StartsWith(addr, "07601")
                    or Text.StartsWith(addr, "07602")
                then "Local"
                else "Out-of-Town",
        type text
    ),

    // ═══ 8) Period columns for visuals ═════════════════════════════════════
    WithArrestMonth = Table.AddColumn(
        WithHomeCategory,
        "ArrestMonth",
        each Date.StartOfMonth([#"Arrest Date"]),
        type date
    ),

    WithMMYY = Table.AddColumn(
        WithArrestMonth,
        "MM_YY",
        each Text.PadStart(Text.From(Date.Month([#"Arrest Date"])), 2, "0")
             & "-"
             & Text.End(Text.From(Date.Year([#"Arrest Date"])), 2),
        type text
    ),

    WithMonthSort = Table.AddColumn(
        WithMMYY,
        "MonthSort",
        each Date.Year([#"Arrest Date"]) * 100 + Date.Month([#"Arrest Date"]),
        Int64.Type
    ),

    WithMonthLabel = Table.AddColumn(
        WithMonthSort,
        "MonthLabel",
        each Date.MonthName([#"Arrest Date"]) & " " & Text.From(Date.Year([#"Arrest Date"])),
        type text
    ),

    // ═══ 9) Select and type final columns ══════════════════════════════════
    KeepCols = {"Name", "Age", "Address", "Charge", "Arrest Date",
                "Officer of Record", "ChargeCategory", "Home_Category",
                "MM_YY", "MonthSort", "MonthLabel", "ArrestMonth", "SourceFile"},

    AvailableCols = List.Intersect({KeepCols, Table.ColumnNames(WithMonthLabel)}),

    Selected = Table.SelectColumns(WithMonthLabel, AvailableCols, MissingField.Ignore),

    Typed = Table.TransformColumnTypes(
        Selected,
        {
            {"Arrest Date", type date},
            {"ArrestMonth", type date},
            {"ChargeCategory", type text},
            {"Home_Category", type text},
            {"MM_YY", type text},
            {"MonthSort", Int64.Type},
            {"MonthLabel", type text},
            {"SourceFile", type text}
        }
    ),

    // ═══ 10) Sort by date for clean output ═════════════════════════════════
    Sorted = Table.Sort(Typed, {{"Arrest Date", Order.Ascending}})

in
    Sorted

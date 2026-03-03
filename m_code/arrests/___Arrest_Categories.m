// 🕒 2026-02-21-01-00-00 (EST)
// Project: Arrest_Analysis/Arrest_Categories
// Author: R. A. Carucci
// Purpose: Simplified M Code that relies on Python preprocessing for geographic
// data

let
    ReportMonth = pReportMonth,

    // ═══ A) Load latest Power BI ready file ═══════════════════════
    FolderFiles = Folder.Files(
        "C:\Users\carucci_r\OneDrive - City of Hackensack\01_DataSources\ARREST_DATA\Power_BI"
    ),
    PowerBIFiles = Table.SelectRows(
        FolderFiles,
        each [Extension] = ".xlsx" and 
             Text.Contains([Name], "PowerBI_Ready")
    ),
    Sorted = Table.Sort(PowerBIFiles, {{"Date modified", Order.Descending}}),
    
    // Load the latest file
    Source = if Table.RowCount(Sorted) > 0 then
        Excel.Workbook(Sorted{0}[Content], null, true){0}[Data]
    else
        error "No Power BI ready files found",

    // ═══ B) Basic data cleaning ═══════════════════════════════════
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    
    // Filter to previous month
    ToDate = (x) => try Date.From(x) otherwise null,
    Prev = Date.AddMonths(ReportMonth, -1),
    PrevY = Date.Year(Prev),
    PrevM = Date.Month(Prev),
    
    DateFiltered = Table.SelectRows(
        Headers,
        each let d = ToDate([#"Arrest Date"]) in
            d <> null and Date.Year(d) = PrevY and Date.Month(d) = PrevM
    ),

    // ═══ C) Use Python-processed geographic data directly ═══════════
    // Since Python already did the heavy lifting, just use the results
    WithHomeCategory = Table.AddColumn(
        DateFiltered,
        "Home_Category_Final",
        each 
            // Use Python's Home_Category if available, otherwise fallback
            if Table.HasColumns(DateFiltered, "Home_Category") then 
                [Home_Category]
            else if Text.Contains(Text.Upper([Address] ?? ""), "HACKENSACK") then 
                "Local"
            else 
                "Check Data",
        type text
    ),

    // ═══ D) Simple charge categorization ═══════════════════════════
    AddChargeCategory = Table.AddColumn(
        WithHomeCategory,
        "ChargeCategory",
        each 
            let charge = Text.Upper([Charge] ?? "") in
            if Text.Contains(charge, "ASSAULT") then "Assault"
            else if Text.Contains(charge, "SHOPLIFTING") then "Theft"
            else if Text.Contains(charge, "BURGLARY") then "Burglary"
            else if Text.Contains(charge, "ROBBERY") then "Robbery" 
            else if Text.Contains(charge, "WARRANT") then "Warrant"
            else if Text.Contains(charge, "DWI") then "DWI"
            else if Text.Contains(charge, "DRUG") then "Drug Related"
            else if Text.Contains(charge, "WEAPON") then "Weapons"
            else "Other",
        type text
    ),

    // ═══ E) Data quality indicators ═══════════════════════════════
    AddDataQuality = Table.AddColumn(
        AddChargeCategory,
        "DataQualityScore", 
        each 
            (if [Name] <> null and [Name] <> "" then 1 else 0) +
            (if [Age] <> null and Number.From([Age] ?? 0) > 0 then 1 else 0) +
            (if [Address] <> null and [Address] <> "" then 1 else 0) +
            (if [Charge] <> null and [Charge] <> "" then 1 else 0) +
            (if Table.HasColumns(AddChargeCategory, "ZIP") and [ZIP] <> null then 1 else 0),
        type number
    ),

    // ═══ F) Final type enforcement ═══════════════════════════════
    TypedData = Table.TransformColumnTypes(
        AddDataQuality,
        {
            {"Age", type number},
            {"DataQualityScore", type number},
            {"Arrest Date", type date}
        }
    ),

    // ═══ G) Add source tracking ═══════════════════════════════════
    WithSourceInfo = Table.AddColumn(
        TypedData,
        "SourceFile",
        each if Table.RowCount(Sorted) > 0 then Sorted{0}[Name] else "Unknown",
        type text
    )

in
    WithSourceInfo
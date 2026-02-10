// ___Arrest_Categories
// 🕒 2025-01-05-15-15-00
// Project: Arrest_Analysis/Arrest_Categories
// Author: R. A. Carucci
// Purpose: Simplified M Code with defensive type handling to avoid Culture
// errors

let
    // ═══ A) Load latest Power BI ready file ═══════════════════════
    FolderFiles = Folder.Files("C:\Users\carucci_r\OneDrive - City of Hackensack\01_DataSources\ARREST_DATA\Power_BI"),
    
    PowerBIFiles = Table.SelectRows(
        FolderFiles,
        each [Extension] = ".xlsx" and Text.Contains([Name], "PowerBI_Ready")
    ),
    
    Sorted = Table.Sort(PowerBIFiles, {{"Date modified", Order.Descending}}),
    
    // Load the latest file
    Source = if Table.RowCount(Sorted) > 0 then
        Excel.Workbook(Sorted{0}[Content], null, true){0}[Data]
    else
        error "No Power BI ready files found",

    // ═══ B) Basic data cleaning ═══════════════════════════════════
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    
    // Filter to previous month - handle multiple date column name variations
    // Handle Excel serial dates, actual dates, and text dates
    ToDate = (x) => 
        if x = null or x = "" then
            null
        else
            // Try Date.From first (handles Excel serial numbers and dates)
            try Date.From(x) otherwise
            // Try converting number to Excel serial date
            try if Number.From(x) > 0 and Number.From(x) < 1000000 then
                Date.From(Number.From(x))
            else
                null
            otherwise
            // Try Date.FromText for text dates
            try Date.FromText(Text.From(x)) otherwise null,
    
    // December 2025 data is now available
    Prev = Date.AddMonths(Date.From(DateTime.LocalNow()), -1),
    PrevY = Date.Year(Prev),
    PrevM = Date.Month(Prev),
    
    // Find the date column (handle variations)
    DateColumnName = if Table.HasColumns(Headers, "Arrest Date") then
        "Arrest Date"
    else if Table.HasColumns(Headers, "Arrest_Date") then
        "Arrest_Date"
    else if Table.HasColumns(Headers, "ArrestDate") then
        "ArrestDate"
    else if Table.HasColumns(Headers, "Date") then
        "Date"
    else
        null,
    
    DateFiltered = if DateColumnName = null then
#table({"Name", "Age", "Address", "Charge", "Arrest Date"}, {})
    else
        Table.SelectRows(
            Headers,
            each let d = ToDate(Record.Field(_, DateColumnName)) in d <> null and Date.Year(d) = PrevY and Date.Month(d) = PrevM
        ),

    // ═══ C) Handle empty results gracefully ═══════════════════════
    HasData = Table.RowCount(DateFiltered) > 0,
    
    // Use Python-processed geographic data directly
    WithHomeCategory = if not HasData then
#table({"Name", "Age", "Address", "Charge", "Arrest Date",                     \
        "Home_Category_Final"},                                                \
       {})
    else
        Table.AddColumn(
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
    AddChargeCategory = if not HasData then
        WithHomeCategory
    else
        Table.AddColumn(
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
    AddDataQuality = if not HasData then
        Table.AddColumn(AddChargeCategory, "DataQualityScore", each 0, type number)
    else if Table.HasColumns(AddChargeCategory, "DataQualityScore") then
        AddChargeCategory
    else
        Table.AddColumn(
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

    // ═══ F) NO TYPE CONVERSION - Avoid Culture errors ═════════════
    // Skip all type conversions to prevent Culture errors
    // Power BI will auto-detect types from the Excel source
    TypedData = AddDataQuality,

    // ═══ G) Add source tracking ═══════════════════════════════════
    WithSourceInfo = Table.AddColumn(
        TypedData,
        "SourceFile",
        each if Table.RowCount(Sorted) > 0 then Sorted{0}[Name] else "Unknown",
        type text
    )

in
    WithSourceInfo

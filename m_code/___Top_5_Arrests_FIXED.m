// ___Top_5_Arrests
// 🕒 2025-01-05-14-30-00
// Project: Arrest_Analysis/Top_5_Arrest
// Author: R. A. Carucci
// Purpose: Fixed Top 5 Officers analysis with dynamic file loading and better error handling

let
    // ═══ A) Dynamic file discovery ═══════════════════════════════
    FolderFiles = Folder.Files("C:\Users\carucci_r\OneDrive - City of Hackensack\01_DataSources\ARREST_DATA\Power_BI"),
    
    PowerBIFiles = Table.SelectRows(
        FolderFiles,
        each [Extension] = ".xlsx" and Text.Contains([Name], "PowerBI_Ready")
    ),
    
    Sorted = Table.Sort(PowerBIFiles, {{"Date modified", Order.Descending}}),

    // Load the latest file
    Source = if Table.RowCount(Sorted) > 0 then
        let
            LatestFile = Sorted{0}[Content],
            ExcelData = Excel.Workbook(LatestFile, null, true),
            FirstSheet = ExcelData{0}[Data]
        in
            FirstSheet
    else
        error "No Power BI ready files found",

    // ═══ B) Promote headers and handle column names ═══════════════
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    // Check if columns exist and rename safely
    SafeRename = if Table.HasColumns(Headers, "Officer of Record") then
        Table.RenameColumns(Headers, {{"Officer of Record", "OfficerOfRecord"}})
    else if Table.HasColumns(Headers, "Officer_of_Record") then
        Table.RenameColumns(Headers, {{"Officer_of_Record", "OfficerOfRecord"}})
    else if Table.HasColumns(Headers, "OfficerOfRecord") then
        Headers
    else
        error "Officer column not found in data",

    SafeRename2 = if Table.HasColumns(SafeRename, "Arrest Date") then
        Table.RenameColumns(SafeRename, {{"Arrest Date", "ArrestDate"}})
    else if Table.HasColumns(SafeRename, "Arrest_Date") then
        Table.RenameColumns(SafeRename, {{"Arrest_Date", "ArrestDate"}})
    else if Table.HasColumns(SafeRename, "ArrestDate") then
        SafeRename
    else
        error "Arrest Date column not found in data",

    // ═══ C) Calculate previous month with better date handling ════
    // December 2025 data is now available at:
    // C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Arrest\monthly_export\2025\2025_12_LAWSOFT_ARREST.xlsx
    Current = Date.From(DateTime.LocalNow()),
    PreviousMonth = Date.AddMonths(Current, -1),
    TargetYear = Date.Year(PreviousMonth),
    TargetMonth = Date.Month(PreviousMonth),
    MonthYearDisplay = Date.MonthName(PreviousMonth) & " " & Text.From(TargetYear),

    // ═══ D) Filter to previous month with better error handling ═══
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

    PreviousMonthOnly = Table.SelectRows(
        SafeRename2,
        each let d = ToDate([ArrestDate]) in d <> null and Date.Year(d) = TargetYear and Date.Month(d) = TargetMonth
    ),

    // ═══ E) Handle empty results gracefully ═══════════════════════
    HasData = Table.RowCount(PreviousMonthOnly) > 0,

    VerifyData = if not HasData then
        #table({"OfficerOfRecord", "ArrestDate", "Officer_Name_Clean", "Arrest_Count", "Month_Year", "Rank", "Source_File"}, {})
    else
        PreviousMonthOnly,

    // ═══ F) Clean officer names with simplified logic ═════════════
    CleanOfficerNames = if not HasData then
        VerifyData
    else
        Table.TransformColumns(
            VerifyData,
            {{"OfficerOfRecord", each
                if _ = null or _ = "" then
                    "UNKNOWN OFFICER"
                else
                    let
                        original = Text.Upper(Text.Trim(Text.From(_))),
                        // Remove common prefixes
                        step1 = Text.Replace(
                            Text.Replace(
                                Text.Replace(
                                    Text.Replace(original, "P.O. ", ""),
                                    "PO ", ""
                                ),
                                "DET. ", ""
                            ),
                            "DETECTIVE ", ""
                        ),
                        // Clean up whitespace and special characters
                        step2 = Text.Replace(
                            Text.Replace(
                                Text.Replace(
                                    Text.Replace(
                                        Text.Replace(step1, "  ", " "),
                                        " - ", " "
                                    ),
                                    "(", ""
                                ),
                                ")", ""
                            ),
                            "#", ""
                        ),
                        // Simple badge number removal - remove trailing 1-4 digit numbers
                        step3 = Text.Trim(
                            if Text.Length(step2) > 0 then
                                let
                                    words = Text.Split(step2, " "),
                                    lastWord = if List.Count(words) > 1 then List.Last(words) else "",
                                    isNumber = try Number.From(lastWord) >= 0 otherwise false,
                                    isBadgeNumber = Text.Length(lastWord) <= 4 and isNumber,
                                    cleanWords = if isBadgeNumber then List.RemoveLastN(words, 1) else words
                                in
                                    Text.Combine(cleanWords, " ")
                            else
                                step2
                        )
                    in
                        if Text.Length(step3) > 0 then step3 else "UNKNOWN OFFICER",
                type text
            }}
        ),

    // ═══ G) Group by officer and count arrests ════════════════════
    GroupedByOfficer = if not HasData then
        #table({"OfficerOfRecord", "Arrest_Count"}, {})
    else
        Table.Group(
            CleanOfficerNames,
            {"OfficerOfRecord"},
            {{"Arrest_Count", each Table.RowCount(_), Int64.Type}}
        ),

    // ═══ H) Sort and get top 5 ════════════════════════════════════
    SortedByCount = if not HasData then
        GroupedByOfficer
    else
        Table.Sort(GroupedByOfficer, {{"Arrest_Count", Order.Descending}}),

    Top5Officers = if not HasData then
        GroupedByOfficer
    else
        Table.FirstN(SortedByCount, 5),

    // ═══ I) Add metadata and formatting ═══════════════════════════
    WithMonthYear = Table.AddColumn(Top5Officers, "Month_Year", each MonthYearDisplay, type text),

    WithRanking = Table.AddIndexColumn(WithMonthYear, "Rank", 1, 1, Int64.Type),

    // Rename for final output
    FinalRenamed = Table.RenameColumns(WithRanking, {{"OfficerOfRecord", "Officer_Name_Clean"}}),

    // ═══ J) Final type enforcement ════════════════════════════════
    TypedData = Table.TransformColumnTypes(
        FinalRenamed,
        {
            {"Officer_Name_Clean", type text},
            {"Arrest_Count", Int64.Type},
            {"Month_Year", type text},
            {"Rank", Int64.Type}
        }
    ),

    // ═══ K) Add source file info for debugging ════════════════════
    WithSourceInfo = if Table.RowCount(Sorted) > 0 then
        Table.AddColumn(TypedData, "Source_File", each Sorted{0}[Name], type text)
    else
        TypedData

in
    WithSourceInfo

// 🕒 2026-02-17-14-30-00
// # Master_Automation/m_code/___Top_5_Arrests_ALL_TIME.m
// # Author: R. A. Carucci
// # Purpose: Top 5 arrests without date filter to verify query logic.

let
    // Load the latest Power BI ready file
    FolderFiles = Folder.Files("C:\Users\carucci_r\OneDrive - City of Hackensack\01_DataSources\ARREST_DATA\Power_BI"),
    
    PowerBIFiles = Table.SelectRows(
        FolderFiles,
        each [Extension] = ".xlsx" and Text.Contains([Name], "PowerBI_Ready")
    ),
    
    Sorted = Table.Sort(PowerBIFiles, {{"Date modified", Order.Descending}}),

    Source = if Table.RowCount(Sorted) > 0 then
        let
            LatestFile = Sorted{0}[Content],
            ExcelData = Excel.Workbook(LatestFile, null, true),
            FirstSheet = ExcelData{0}[Data]
        in
            FirstSheet
    else
        error "No Power BI ready files found",

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

    // *** NO DATE FILTERING - Use all data ***
    AllData = SafeRename,

    // Handle empty results gracefully
    HasData = Table.RowCount(AllData) > 0,

    VerifyData = if not HasData then
        #table({"OfficerOfRecord", "Officer_Name_Clean", "Arrest_Count", "Rank", "Source_File"}, {})
    else
        AllData,

    // Clean officer names
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
                        // Simple badge number removal
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

    // Group by officer and count arrests
    GroupedByOfficer = if not HasData then
        #table({"OfficerOfRecord", "Arrest_Count"}, {})
    else
        Table.Group(
            CleanOfficerNames,
            {"OfficerOfRecord"},
            {{"Arrest_Count", each Table.RowCount(_), Int64.Type}}
        ),

    // Sort and get top 5
    SortedByCount = if not HasData then
        GroupedByOfficer
    else
        Table.Sort(GroupedByOfficer, {{"Arrest_Count", Order.Descending}}),

    Top5Officers = if not HasData then
        GroupedByOfficer
    else
        Table.FirstN(SortedByCount, 5),

    // Add metadata
    WithRanking = Table.AddIndexColumn(Top5Officers, "Rank", 1, 1, Int64.Type),

    // Rename for final output
    FinalRenamed = Table.RenameColumns(WithRanking, {{"OfficerOfRecord", "Officer_Name_Clean"}}),

    // Final type enforcement
    TypedData = Table.TransformColumnTypes(
        FinalRenamed,
        {
            {"Officer_Name_Clean", type text},
            {"Arrest_Count", Int64.Type},
            {"Rank", Int64.Type}
        }
    ),

    // Add source file info
    WithSourceInfo = if Table.RowCount(Sorted) > 0 then
        Table.AddColumn(TypedData, "Source_File", each Sorted{0}[Name], type text)
    else
        TypedData

in
    WithSourceInfo

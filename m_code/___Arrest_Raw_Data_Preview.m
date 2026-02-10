// ___Arrest_Raw_Data_Preview
// 🕒 2025-01-05-14-45-00
// Project: Arrest_Analysis/Raw_Data_Preview
// Author: R. A. Carucci
// Purpose: Show first 100 rows of raw arrest data to verify source file contents

let
    // Load the latest Power BI ready file
    FolderFiles = Folder.Files("C:\Users\carucci_r\OneDrive - City of Hackensack\01_DataSources\ARREST_DATA\Power_BI"),
    
    PowerBIFiles = Table.SelectRows(
        FolderFiles,
        each [Extension] = ".xlsx" and Text.Contains([Name], "PowerBI_Ready")
    ),
    
    Sorted = Table.Sort(PowerBIFiles, {{"Date modified", Order.Descending}}),
    
    Source = if Table.RowCount(Sorted) > 0 then
        Excel.Workbook(Sorted{0}[Content], null, true){0}[Data]
    else
        error "No Power BI ready files found",

    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    
    // Add source file info
    WithSourceFile = Table.AddColumn(
        Headers,
        "Source_File",
        each if Table.RowCount(Sorted) > 0 then Sorted{0}[Name] else "Unknown",
        type text
    ),
    
    // Take first 100 rows for preview
    Preview = Table.FirstN(WithSourceFile, 100)

in
    Preview

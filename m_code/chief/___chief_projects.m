// 🕒 2026-02-20-23-48-50
// # chief/___chief_projects.m
// # Author: R. A. Carucci
// # Purpose: Load Chief's Projects and Initiatives event data from contribution workbook.

let
    Source = Excel.Workbook(File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Chief\chief_monthly.xlsx"), null, true),
    Table8_Table = Source{[Item="Table8",Kind="Table"]}[Data],
    #"Changed Type" = Table.TransformColumnTypes(Table8_Table,
        {{"Date", type date},
         {"Event", type text},
         {"Notes", type any},
         {"Duration", type any},
         {"Location", type any}}),

// Remove parentheses and numbers from Event column
#"Replaced Value" = Table.ReplaceValue(#"Changed Type", each[Event], each 
        if Text.Contains([Event], " (") then 
            Text.BeforeDelimiter([Event], " (")
        else 
            [Event]
    , Replacer.ReplaceValue, {"Event"})
in
#"Replaced Value"

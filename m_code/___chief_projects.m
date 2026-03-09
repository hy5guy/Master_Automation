// 🕒 2026-03-04-23-45-00
// # PowerBI_ChiefMonthly/___chief_projects.m
// # Author: R. A. Carucci
// # Purpose: Load chief project/event data from Table8, clean event names, and
// enrich with category lookup from Categories table.

let Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\Shared "
                      "Folder\Compstat\Contributions\Chief\chief_monthly.xlsx"),
        null, true),

    // Load the Raw_Input data (table name in Excel Table Design must be Raw_Input)
    Raw_Input_Table = Source{[Item = "Raw_Input", Kind = "Table"]}[Data],

#"Changed Type" = Table.TransformColumnTypes(Raw_Input_Table, {
    {"Date", type date}, {"Event", type text}, {"Notes", type text},
    {"Duration", type text}, {
  "Location", type text
}
}),

// Remove parentheses and trailing numbers from Event column
// e.g., "Meeting (3)" → "Meeting"
#"Cleaned Events" = Table.TransformColumns(#"Changed Type", {
        {
  "Event",
      each if Text.Contains(_, " (") then Text.BeforeDelimiter(_, " (") else _,
      type text
}
}),

// Remove blank rows (rows with no Date)
#"Removed Blanks" = Table.SelectRows(#"Cleaned Events", each[Date]<> null),
    
    // Load Categories lookup table
    Categories_Table = Source{[Item="Categories",Kind="Table"]}[Data],
#"Categories Typed" = Table.TransformColumnTypes(Categories_Table, {
        {"Event", type text}, 
        {"Category", type text}, 
        {
  "Subcategory", type text
}
}),

// Merge with Categories to enrich events
#"Merged Categories" = Table.NestedJoin(
#"Removed Blanks", {"Event" },
#"Categories Typed", {"Event" }, 
        "CatLookup", JoinKind.LeftOuter
    ),

// Expand Category and Subcategory columns
#"Expanded Categories" = Table.ExpandTableColumn(
#"Merged Categories", "CatLookup", 
        {"Category", "Subcategory"}, {"Category", "Subcategory"}
    )
in
#"Expanded Categories"
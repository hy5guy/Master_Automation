// 🕒 2026-02-21-01-00-00 (EST)
// # traffic/___Traffic.m
// # Author: R. A. Carucci
// # Purpose: Load Traffic Bureau monthly activity metrics from contribution workbook.

let
    ReportMonth = pReportMonth,
    Source = Excel.Workbook(File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Traffic\Traffic_Monthly.xlsx"), null, true),
    _mom_traffic_Table = Source{[Item="_mom_traffic",Kind="Table"]}[Data],
#"Changed Type" = Table.TransformColumnTypes(                                  \
    _mom_traffic_Table, {{"Tracked Items", type text },                        \
                          {"06-23", Int64.Type },                              \
                           {"07-23", Int64.Type },                             \
                            {"08-23", Int64.Type },                            \
                             {"09-23", Int64.Type },                           \
                              {"10-23", Int64.Type },                          \
                               {"11-23", Int64.Type },                         \
                                {"12-23", Int64.Type },                        \
                                 {"01-24", Int64.Type },                       \
                                  {"02-24", Int64.Type },                      \
                                   {"03-24", Int64.Type },                     \
                                    {"04-24", Int64.Type },                    \
                                     {"05-24", Int64.Type },                   \
                                      {"06-24", Int64.Type },                  \
                                       {"07-24", Int64.Type },                 \
                                        {"08-24", Int64.Type },                \
                                         {"09-24", Int64.Type },               \
                                          {"10-24", Int64.Type },              \
                                           {"11-24", Int64.Type },             \
                                            {"12-24", Int64.Type },            \
                                             {"01-25", Int64.Type },           \
                                              {"02-25", Int64.Type },          \
                                               {"03-25", Int64.Type },         \
                                                {"04-25", Int64.Type },        \
                                                 {"05-25", Int64.Type },       \
                                                  {"06-25", Int64.Type },      \
                                                   {"07-25", Int64.Type },     \
                                                    {"08-25", Int64.Type },    \
                                                     {"09-25", Int64.Type },   \
                                                      {"10-25", Int64.Type },  \
                                                       {"11-25", Int64.Type }, \
                                                        {"12-25",              \
                                                         Int64.Type } }),
#"Filtered Rows" = Table.SelectRows(#"Changed Type",                           \
                                    each([Tracked Items]<> "Grand Total")),
    
    // Rolling 13-Month Logic Implementation
    CurrentDate = DateTime.From(ReportMonth),
    EndDate = Date.AddMonths(Date.StartOfMonth(DateTime.Date(CurrentDate)), -1),
    StartDate = Date.AddMonths(EndDate, -12),
    
    // Unpivot all date columns
    DateColumns = List.RemoveItems(Table.ColumnNames(#"Filtered Rows"), {"Tracked Items"}),
#"Unpivoted Columns" = Table.UnpivotOtherColumns(#"Filtered Rows",             \
                                                 {"Tracked Items" }, "Period", \
                                                  "Value"),

// Convert Period to proper date for filtering
#"Added Date Column" = Table.AddColumn(#"Unpivoted Columns", "Date", each
        let
            monthPart = Text.Start([Period], 2),
            yearPart = "20" & Text.End([Period], 2),
            fullDate = monthPart & "/01/" & yearPart
        in
            Date.From(fullDate)),

// Apply Rolling 13-Month Filter
#"Filtered Rolling Window" = Table.SelectRows(#"Added Date Column", 
        each [Date] >= StartDate and [Date] <= EndDate),

// Separate arrest details from totals for recalculation
#"Arrest Details Only" = Table.SelectRows(#"Filtered Rolling Window", 
        each [Tracked Items] <> "Total - Arrest(s)"),

// Calculate correct arrest totals by period
#"Arrest Components" = Table.SelectRows(#"Arrest Details Only", each
        [Tracked Items] = "Criminal Warrant Arrest" or
        [Tracked Items] = "DUI Arrest" or 
        [Tracked Items] = "Self-Initiated Arrest" or
        [Tracked Items] = "Motor Vehicle Warrant"),

#"Grouped Arrest Totals" = Table.Group(#"Arrest Components", {"Period" }, 
        {{"Calculated Total", each List.Sum([Value]), type number}}),

#"Added Corrected Totals" = Table.AddColumn(#"Grouped Arrest Totals",          \
                                            "Tracked Items", 
        each "Total - Arrest(s)"),

#"Renamed Total Value" = Table.RenameColumns(#"Added Corrected Totals", 
        {{"Calculated Total", "Value"}}),

#"Reordered Total Columns" = Table.ReorderColumns(#"Renamed Total Value", 
        {"Tracked Items", "Period", "Value"}),

// Add Date column to corrected totals
#"Added Date to Totals" = Table.AddColumn(#"Reordered Total Columns", "Date",  \
                                          each
        let
            monthPart = Text.Start([Period], 2),
            yearPart = "20" & Text.End([Period], 2),
            fullDate = monthPart & "/01/" & yearPart
        in
            Date.From(fullDate)),

// Combine corrected totals with other data
#"Combined Data" = Table.Combine({#"Arrest Details Only",                      \
                                  #"Added Date to Totals" }),

// Add currency flag and other columns
#"Added Currency Flag" = Table.AddColumn(#"Combined Data", "Is Currency", each 
        if [Tracked Items] = "Parking Fees Collected" then "Yes" else "No"),

#"Added Window Info" = Table.AddColumn(#"Added Currency Flag", "Window Info",  \
                                       each
        "Rolling 13-Month Window: " & 
        Date.ToText(StartDate, "MMM yyyy") & " to " & 
        Date.ToText(EndDate, "MMM yyyy")),

#"Added Sort Order" = Table.AddColumn(#"Added Window Info", "Sort Order", each
        Date.Year([Date]) * 100 + Date.Month([Date])),

#"Added Period Label" = Table.AddColumn(#"Added Sort Order", "Period Label",   \
                                        each
        Date.ToText([Date], "MMM yyyy")),

#"Added Rolling Month" = Table.AddColumn(#"Added Period Label",                \
                                         "Rolling Month", each
        let
            MonthDiff = ((Date.Year([Date]) - Date.Year(StartDate)) * 12) + 
                       (Date.Month([Date]) - Date.Month(StartDate)) + 1
        in
            MonthDiff),

// Fix values: whole numbers for non-parking, keep precision for parking
#"Updated Values" = Table.AddColumn(#"Added Rolling Month", "Final Value", each
        if [Tracked Items] = "Parking Fees Collected" then 
            [Value]
        else 
            Number.RoundUp([Value], 0)),

#"Removed Original" = Table.RemoveColumns(#"Updated Values", {"Value" }),
#"Renamed Value" = Table.RenameColumns(#"Removed Original", {{"Final Value",   \
                                                              "Value" } })
in
#"Renamed Value"

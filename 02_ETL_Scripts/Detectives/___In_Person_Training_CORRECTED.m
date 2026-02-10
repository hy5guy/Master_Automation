// 🕒 2026-01-12-17-45-00
// Project: Policy_Training / In_Person_Training
// Author: R. A. Carucci
// Purpose: Load In-Person training list from ETL output with proper date filtering
// to exclude incomplete current month and future dates

let
    // Load ETL workbook/sheet
    Source = Excel.Workbook(
        File.Contents("C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\02_ETL_Scripts\\Policy_Training_Monthly\\output\\policy_training_outputs.xlsx"),
        null, true),
    Tbl = Source{[Item = "InPerson_Prior_Month_List", Kind = "Sheet"]}[Data],
    Promoted = Table.PromoteHeaders(Tbl, [PromoteAllScalars = true]),

    // Handle either naming convention (with/without spaces)
    Aliases = {{"CourseDuration", "Course Duration"},
               {"TotalCost", "Total Cost"},
               {"AttendeesCount", "Attendees Count"}},
    Standardized = List.Accumulate(
        Aliases, Promoted,
        (state, pair) =>
            if Table.HasColumns(state, {pair{0}}) and
            not Table.HasColumns(state, {pair{1}})
                    then Table.RenameColumns(state, {pair}) else state),

    // Keep expected columns (now includes dates to preserve individual events)
    Kept = Table.SelectColumns(Standardized,
                               {"Start date", "End date", "Course Name",
                                "Course Duration", "Total Cost",
                                "Attendees Count"},
                               MissingField.Ignore),

    // Strong typing + safe numeric coercion (ensures totals will sum)
    Coerced = Table.TransformColumns(
        Kept,
        {{"Start date", each try DateTime.From(_) otherwise null,
          type nullable datetime},
         {"End date", each try DateTime.From(_) otherwise null,
          type nullable datetime},
         {"Course Name", each if _ = null then "" else Text.From(_), type text},
         {"Course Duration",
          each try Number.RoundDown(Number.From(_)) otherwise 0, Int64.Type},
         {"Total Cost", each try Number.From(_) otherwise 0, type number},
         {"Attendees Count",
          each try Number.RoundDown(Number.From(_)) otherwise 0, Int64.Type}}),

    // *** NEW: Calculate cutoff date (end of prior complete month) ***
    Today = DateTime.Date(DateTime.LocalNow()),
    FirstOfCurrentMonth = Date.StartOfMonth(Today),
    LastDayOfPriorMonth = Date.AddDays(FirstOfCurrentMonth, -1),
    CutoffDate = Date.From(LastDayOfPriorMonth),

    // *** NEW: Filter to only training events that started on or before last complete month ***
    FilteredByDate = Table.SelectRows(Coerced, each 
        [Start date] <> null and 
        Date.From([Start date]) <= CutoffDate),

    // Sort by Start date to match visual expectations
    Sorted = Table.Sort(FilteredByDate, {{"Start date", Order.Ascending}}),

    // Create deterministic event identifier to keep duplicate course names distinct in visuals
    WithEventId = Table.AddColumn(
        Sorted, "Event Id",
        each Text.Combine(
            {
              if [Start date]<> null 
                then DateTime.ToText([Start date], "yyyy-MM-ddTHH:mm:ss") 
                else "",
              Text.Trim([Course Name]), 
              Text.From([Course Duration]),
              Text.From([Attendees Count]),
              Text.From(Number.From([Total Cost]))
            },
            "|"),
        type text),

    // Final type conversion for date columns
    ChangedType = Table.TransformColumnTypes(
        WithEventId,
        {{"End date", type date}, 
         {"Start date", type date}})
in
    ChangedType

// ========================================
// DEPLOYMENT INSTRUCTIONS
// ========================================
// 1. Open: C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Policy_Training\Policy_Training_Monthly.xlsx
// 2. Navigate to: Data > Queries & Connections
// 3. Right-click query: "___In_Person_Training"
// 4. Select: "Edit" to open Advanced Editor
// 5. Replace ALL existing code with this entire script
// 6. Click: "Done" > "Close & Load"
// 7. Verify results show only data through December 2025 (or latest complete month)

// ========================================
// VALIDATION CHECKLIST
// ========================================
// ✓ No dates after last complete month appear
// ✓ January 2026 data is excluded (current incomplete month)
// ✓ All training events have valid Start dates
// ✓ Event counts match ETL output for valid date range
// ✓ Power BI visuals update correctly with filtered data

// ========================================
// IMPORTANT NOTE
// ========================================
// This query uses the "InPerson_Prior_Month_List" sheet which only contains
// the prior month's data. To see December 2025 data, the ETL script must be run:
// C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Policy_Training_Monthly\src\policy_training_etl.py

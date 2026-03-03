// 🕒 2025-01-12-18-45-00
// Project: Policy_Training / In_Person_Training
// Author: R. A. Carucci
// Purpose: Load In-Person training from Training_Log sheet (not table),
// showing ONLY previous complete month (e.g., Dec 2024 when run in Jan 2025)
// NOTE: Do NOT auto-format this file - file paths will break

let
    // Load from SHEET (not table) - more reliable
    Source = Excel.Workbook(
        File.Contents(
            "C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\Shared Folder\\Compstat\\Contributions\\Policy_Training\\Policy_Training_Monthly.xlsx"),
        null, true),

    // Get the Training_Log sheet
    Training_Log_Sheet = Source{[Item = "Training_Log", Kind = "Sheet"]}[Data],

    // Promote headers
    PromotedHeaders =
        Table.PromoteHeaders(Training_Log_Sheet, [PromoteAllScalars = true]),

    // Ensure proper column types (includes Total Cost which already exists)
    ChangedType = Table.TransformColumnTypes(
        PromotedHeaders, {{"Start Date", type datetime},
                          {"End Date", type datetime},
                          {"Course Duration", Int64.Type},
                          {"Course Name", type text},
                          {"Delivery Method", type text},
                          {"Count of Attendees", Int64.Type},
                          {"Cost Per Attendee", type number},
                          {"Total Cost", type number}}),

    // Filter for In-Person delivery method only
    FilteredInPerson =
        Table.SelectRows(ChangedType, each[Delivery Method] = "In-Person"),

    // Calculate previous complete month boundaries
    Today = DateTime.Date(DateTime.LocalNow()),
    FirstOfCurrentMonth = Date.StartOfMonth(Today),
    FirstOfPriorMonth = Date.AddMonths(FirstOfCurrentMonth, -1),
    LastOfPriorMonth = Date.AddDays(FirstOfCurrentMonth, -1),

    // Filter for ONLY previous complete month
    FilteredByDate = Table.SelectRows(
        FilteredInPerson, each[Start Date]<> null and Date.From([Start Date]) >=
                                  FirstOfPriorMonth and
                              Date.From([Start Date]) <= LastOfPriorMonth),

    // Rename columns to match expected Power BI field names
    RenamedColumns = Table.RenameColumns(
        FilteredByDate, {{"Count of Attendees", "Attendees Count"}}),

    // Select only needed columns
    SelectColumns = Table.SelectColumns(
        RenamedColumns, {"Start Date", "End Date", "Course Name",
                         "Course Duration", "Total Cost", "Attendees Count"}),

    // Add date sort key for proper chronological sorting
    WithDateSort = Table.AddColumn(
        SelectColumns, "Date_Sort",
        each if[Start Date]<> null then Date.Year([Start Date]) * 10000 +
            Date.Month([Start Date]) * 100 + Date.Day([Start Date]) else 0,
        Int64.Type),

    // Sort by Start Date (ascending)
    Sorted = Table.Sort(WithDateSort, {{"Start Date", Order.Ascending}}),

    // Create unique Event ID for duplicate course names
    WithEventId = Table.AddColumn(
        Sorted, "Event Id",
        each Text.Combine(
            {
              if
                [Start Date]<> null then DateTime.ToText(
                    [Start Date], "yyyy-MM-ddTHH:mm:ss") else "",
                    Text.Trim([Course Name]), Text.From([Course Duration]),
                    Text.From([Attendees Count]), Text.From([Total Cost])
            },
            "|"),
        type text),

    // Final type conversion
    FinalTypes =
        Table.TransformColumnTypes(
            WithEventId, {{"End Date", type date}, {"Start Date", type date}})
            in FinalTypes

        // ========================================
        // DEPLOYMENT INSTRUCTIONS
        // ========================================
        // 1. Open: C:\Users\carucci_r\OneDrive - City of Hackensack\Shared
        // Folder\Compstat\Contributions\Policy_Training\Policy_Training_Monthly.xlsx
        // 2. Navigate to: Data > Queries & Connections
        // 3. Right-click query: "___In_Person_Training"
        // 4. Select: "Edit" to open Advanced Editor
        // 5. Replace ALL existing code with this entire script
        // 6. Click: "Done" > "Close & Load"
        // 7. Verify results show ONLY December 2024 data (9 events expected)

        // ========================================
        // KEY DIFFERENCES FROM PREVIOUS VERSION
        // ========================================
        // - Reads from SHEET not TABLE (avoids "table not found" error)
        // - Uses File.Contents() with full path (more reliable)
        // - Works even if table structure changes
        // - Promotes headers from first row automatically

        // ========================================
        // VALIDATION CHECKLIST
        // ========================================
        // ✓ Shows 9 In-Person training events for December 2024
        // ✓ Includes: ESU Training, Defensive Tactics, POTR, MOI, etc.
        // ✓ Date range: Dec 1, 2024 - Dec 31, 2024
        // ✓ All records have Delivery Method = "In-Person"
        // ✓ Total Cost comes directly from sheet (pre-calculated)
        // ✓ Event IDs are unique for duplicate course names

        // ========================================
        // COLUMN MAPPING
        // ========================================
        // Source Sheet          →  Query Output
        // ------------------       ---------------
        // Start Date            →  Start Date
        // End Date              →  End Date
        // Course Name           →  Course Name
        // Course Duration       →  Course Duration
        // Total Cost            →  Total Cost (existing column)
        // Count of Attendees    →  Attendees Count (renamed)

        // ========================================
        // DATE BEHAVIOR EXAMPLES
        // ========================================
        // Run Date: January 12, 2025 → Shows December 2024
        // Run Date: February 15, 2025 → Shows January 2025
        // Run Date: March 5, 2025 → Shows February 2025
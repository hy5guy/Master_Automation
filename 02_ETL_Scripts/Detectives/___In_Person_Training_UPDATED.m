// 🕒 2026-01-12
// Project: Policy_Training / In_Person_Training
// Author: R. A. Carucci (updated by Auto)
// Purpose: Load In-Person training list from ETL output
// Updated: Changed to use Training_Log_Clean sheet (all data) instead of InPerson_Prior_Month_List (prior month only)
//          Added filter for "In-Person" delivery type

let
    // Load ETL workbook/sheet - using Training_Log_Clean which has all data
    Source = Excel.Workbook(
        File.Contents("C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\02_ETL_Scripts\\Policy_Training_Monthly\\output\\policy_training_outputs.xlsx"),
        null, true),
    Tbl = Source{[Item = "Training_Log_Clean", Kind = "Sheet"]}[Data],
    Promoted = Table.PromoteHeaders(Tbl, [PromoteAllScalars = true]),

    // Filter for In-Person training only
    FilteredInPerson = Table.SelectRows(Promoted, each [Delivery_Type] = "In-Person"),

    // Rename "Course Attendees" to "Attendees Count" to match expected column name
    RenamedColumns = Table.RenameColumns(
        FilteredInPerson,
        {{"Course Attendees", "Attendees Count"}},
        MissingField.Ignore
    ),

    // Keep expected columns
    Kept = Table.SelectColumns(RenamedColumns,
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

    // Sort by Start date to match visual expectations
    Sorted = Table.Sort(Coerced, {{"Start date", Order.Ascending}}),

    // Create deterministic event identifier to keep duplicate course names
    // distinct in visuals
    WithEventId = Table.AddColumn(
        Sorted, "Event Id",
        each Text.Combine(
            {
              if
                [Start date]<> null then DateTime.ToText(
                    [Start date], "yyyy-MM-ddTHH:mm:ss") else "",
                    Text.Trim([Course Name]), Text.From([Course Duration]),
                    Text.From([Attendees Count]),
                    Text.From(Number.From([Total Cost]))
            },
            "|"),
        type text),
    #"Changed Type" = Table.TransformColumnTypes(WithEventId,{{"End date", type date}, {"Start date", type date}})
in
    #"Changed Type"

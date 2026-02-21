// 🕒 2026-02-20-23-48-50
// # training/___In_Person_Training.m
// # Author: R. A. Carucci
// # Purpose: Load in-person training attendance and cost data from Policy Training workbook.

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
        (state, pair) => // <--- ERROR WAS HERE
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

    // Sort by Start date to match visual expectations
    Sorted = Table.Sort(Coerced, {{"Start date", Order.Ascending}}),

    // Create deterministic event identifier to keep duplicate course names
    // distinct in visuals
    WithEventId = Table.AddColumn(
        Sorted, "Event Id",
        each Text.Combine(
            {
                if                 [Start date]<> null then DateTime.ToText(
                    [Start date], "yyyy-MM-ddTHH:mm:ss") else "",
                    Text.Trim([Course Name]), Text.From([Course Duration]),
                    Text.From([Attendees Count]),
                    Text.From(Number.From([Total Cost]))
            },
            "|"),
        type text),
#"Changed Type" = Table.TransformColumnTypes(WithEventId,                      \
                                             {{"End date", type date },        \
                                               {"Start date", type date } })
in
    #"Changed Type"

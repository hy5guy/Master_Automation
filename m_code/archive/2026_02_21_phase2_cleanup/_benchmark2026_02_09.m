// 🕒 2026-02-17-14-30-00
// # Master_Automation/m_code/_benchmark2026_02_09.m
// # Author: R. A. Carucci
// # Purpose: Load Benchmark event data from 05_EXPORTS with required column schema.

let
    // Required columns
    RequiredColumns = {
        "Officer Name","Badge Number","Rank","Organization","Incident Number","Report Number",
        "Incident Date","Location","Initial Contact","# of Officers Involved","# of Subjects",
        "Subject type","Report Key","SourceFile","SourceModified","EventType"
    },

    // Read one subfolder
    ReadFolder = (subfolder as text, eventType as text) as table =>
        let
            path = RootExportPath & "\" & subfolder,
            allFiles = Folder.Files(path),
            csvFiles = Table.Buffer(
                Table.SelectRows(allFiles, each Text.Lower([Extension]) = ".csv")
            ),
            perFile = List.Transform(
                Table.ToRecords(csvFiles),
                (r) =>
                    let
                        src     = Csv.Document(r[Content],[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
                        header  = Table.PromoteHeaders(src, [PromoteAllScalars=true]),
                        withSF  = Table.AddColumn(header, "SourceFile", each r[Name], type text),
                        withSM  = Table.AddColumn(withSF, "SourceModified", each r[Date modified], type datetime),
                        withET  = Table.AddColumn(withSM, "EventType", each eventType, type text),
                        selected = Table.SelectColumns(withET, RequiredColumns, MissingField.UseNull),
                        typed    = Table.TransformColumnTypes(
                            selected,
                            {
                                {"Badge Number", Int64.Type},
                                {"# of Officers Involved", Int64.Type},
                                {"# of Subjects", Int64.Type},
                                {"Incident Date", type datetime},
                                {"Officer Name", type text},
                                {"Rank", type text},
                                {"Organization", type text},
                                {"Incident Number", type text},
                                {"Report Number", type text},
                                {"Location", type text},
                                {"Initial Contact", type text},
                                {"Subject type", type text},
                                {"Report Key", type text},
                                {"SourceFile", type text},
                                {"SourceModified", type datetime},
                                {"EventType", type text}
                            },
                            "en-US"
                        )
                    in
                        typed
            ),
            combined =
                if List.Count(perFile) = 0
                then #table(RequiredColumns,{})
                else Table.Combine(perFile)
        in
            combined,

    // Read all event types
    UseOfForce     = ReadFolder("use_force", "Use of Force"),
    ShowOfForce    = ReadFolder("show_force", "Show of Force"),
    VehiclePursuit = ReadFolder("vehicle_pursuit", "Vehicle Pursuit"),

    AllRows = Table.Combine({UseOfForce, ShowOfForce, VehiclePursuit}),

    // Sort and dedupe
    Sorted  = Table.Sort(AllRows, {{"Report Key", Order.Ascending},{"SourceModified", Order.Descending}}),
    Deduped = Table.Distinct(Sorted, {"Report Key"}),

    // Date filter
    FactIncidents_IR =
        Table.SelectRows(
            Deduped,
            each [Incident Date] <> null and [Incident Date] >= RangeStart and [Incident Date] < RangeEnd
        ),

    // Month fields
    AddMonthStart = Table.AddColumn(FactIncidents_IR, "MonthStart", each Date.StartOfMonth(Date.From([Incident Date])), type date),
    AddMonthLabel = Table.AddColumn(AddMonthStart, "MonthLabel", each Date.ToText([MonthStart], "MM-yy"), type text),
    AddMonthSort  = Table.AddColumn(AddMonthLabel, "MonthSort", each Date.Year([MonthStart]) * 100 + Date.Month([MonthStart]), Int64.Type),

    // Replace nulls with 0 in numeric columns
    ReplaceNullNumeric =
        Table.ReplaceValue(
            AddMonthSort,
            null,
            0,
            Replacer.ReplaceValue,
            {"Badge Number", "# of Officers Involved", "# of Subjects"}
        ),

    // Final filter
    Filtered = Table.SelectRows(ReplaceNullNumeric, each [MonthStart] <> null)
in
    Filtered
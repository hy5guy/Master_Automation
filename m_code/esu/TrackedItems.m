// 🕒 2026-02-17-14-30-00
// # Master_Automation/m_code/esu/TrackedItems.m
// # Author: R. A. Carucci
// # Purpose: Load ESU tracked items dimension from _mom_hacsoc; add SortKey 1..22 for visual order.

let
    ESUPath = "C:\Users\RobertCarucci\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\ESU\ESU.xlsx",

    Source = Excel.Workbook(
        File.Contents(ESUPath),
        null,
        true
    ),

    MoMRow =
        try Source{[Name="_mom_hacsoc", Kind="Table"]}
        otherwise Source{[Item="_mom_hacsoc", Kind="Table"]},

    MoM = MoMRow[Data],

    // Find column whose trimmed text equals "Tracked Items" (handles trailing space and non-breaking space Chr 160)
    TrackedColName =
        let
            cols = Table.ColumnNames(MoM),
            matches = List.Select(
                cols,
                each Text.Trim(Text.Replace(_, Character.FromNumber(160), " ")) = "Tracked Items"
            )
        in
            if List.Count(matches) = 0 then
                error "Tracked Items column not found. Check the _mom_hacsoc table header."
            else
                matches{0},

    AddTrackedItem = Table.AddColumn(
        MoM,
        "TrackedItem",
        each fnCleanText(Text.From(Record.Field(_, TrackedColName))),
        type text
    ),

    Keep = Table.SelectColumns(
        AddTrackedItem,
        {"TrackedItem", "Status", "ItemKey", "StartMonth", "EndMonth"}
    ),

    // Parse ISO datetime strings (e.g. 2023-11-01T04:00:00.000Z) to Date; blank/null -> null
    ParseStartEnd = Table.TransformColumns(
        Keep,
        {
            {"StartMonth", each if _ = null or _ = "" then null else Date.FromText(Text.Start(Text.From(_), 10), [Format = "yyyy-MM-dd"]), type date},
            {"EndMonth", each if _ = null or _ = "" then null else Date.FromText(Text.Start(Text.From(_), 10), [Format = "yyyy-MM-dd"]), type date}
        }
    ),

    Types = Table.TransformColumnTypes(
        ParseStartEnd,
        {{"Status", type text}, {"ItemKey", type text}}
    ),

    // SortKey: 1..22 for visual order (matches ESU tracked items list); items not in list = 99
    SortKeyOrder = {
        "Arrest(s)", "Assist Other Bureau", "Assist Outside Agency", "BWC Review(s)",
        "CDS Seized", "Community Outreach", "Dignitary Protection", "ESU OOS",
        "ESU Single Operator", "Forcible Entries", "ICS Functions (IAPs/AARs)",
        "Instructor For Hpd Training", "Moving Summonses", "MV Lock Outs", "MV Stops",
        "Parking Summonses", "School Drills", "Tabletop Exercises", "Targeted Area Patrols",
        "Threat Assessments Received", "Warrants Executed", "Weapons Recovered"
    },
    SortKeyList = List.Zip({SortKeyOrder, List.Generate(() => 1, each _ <= 22, each _ + 1)}),
    SortKeyTable = Table.FromRows(SortKeyList, {"TrackedItem", "SortKey"}),
    Merged = Table.NestedJoin(
        Types,
        {"TrackedItem"},
        SortKeyTable,
        {"TrackedItem"},
        "SortRow",
        JoinKind.LeftOuter
    ),
    ExpandSort = Table.ExpandTableColumn(Merged, "SortRow", {"SortKey"}, {"SortKey"}),
    SortKeyDefault = Table.TransformColumnTypes(
        Table.ReplaceValue(ExpandSort, null, 99, Replacer.ReplaceValue, {"SortKey"}),
        {{"SortKey", Int64.Type}}
    )
in
    SortKeyDefault

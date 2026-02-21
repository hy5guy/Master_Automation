// 🕒 2026-02-20-23-48-50
// # stacp/___Social_Media.m
// # Author: R. A. Carucci
// # Purpose: Load social media engagement metrics with rolling 13-month window.

let
    // === SOURCE ===
    Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\STACP\STACP.xlsm"),
        null,
        true
    ),
    _stacp_mom_sm_Table = Source{[Item="_stacp_mom_sm", Kind="Table"]}[Data],

    // === DYNAMIC TYPES: Platform = text; everything else = Int64 ===
    ColumnNames = Table.ColumnNames(_stacp_mom_sm_Table),
    TypeList =
        List.Transform(
            ColumnNames,
            (c) => if c = "Platform" then {
  c, type text} else {c, Int64.Type}
        ),
#"Changed Type" = Table.TransformColumnTypes(_stacp_mom_sm_Table, TypeList),

    // === ROLLING 13-MONTH WINDOW (full months only) ===
    // Today
    Today = Date.From(DateTime.LocalNow()),

    // End of window = start of last complete month (exclude current month)
    // Example: if Today = 2025-10-02, EndMonth = 2025-09-01
    EndMonth = Date.StartOfMonth(Date.AddMonths(Today, -1)),

    // Start of window = 12 months before EndMonth (inclusive, total = 13 months)
    // Example: StartMonth = 2024-09-01  → months: Sep-2024 ... Sep-2025
    StartMonth = Date.StartOfMonth(Date.AddMonths(EndMonth, -12)),

    // Build ordered list of the 13 month keys in "MM-yy" format to match your columns
    MonthDates = List.Transform({0..12}, each Date.AddMonths(StartMonth, _)),
    MonthKeys  = List.Transform(MonthDates, each Date.ToText(_, "MM-yy")),

    // Desired column order: Platform, [13 month keys], Total (if present)
    DesiredOrder = {"Platform"} & MonthKeys & {"Total"},

    // Some workbooks may be missing a month or Total—keep only columns that actually exist
    ExistingInOrder = List.Select(DesiredOrder, each List.Contains(ColumnNames, _)),

// Select (and order) the rolling 13-month columns
#"Selected Columns" = Table.SelectColumns(#"Changed Type", ExistingInOrder,    \
                                          MissingField.Ignore)

in
#"Selected Columns"

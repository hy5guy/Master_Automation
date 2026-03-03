// 🕒 2026-02-20-23-48-50
// # functions/fnLoadRaw.m
// # Author: R. A. Carucci
// # Purpose: Helper function to load, rename, align, and deduplicate benchmark event data.

(eventFolder as text, eventTypeName as text, renameMap as list) as table =>
let
    files    = fnGetFiles(eventFolder),
    rows     = List.Transform(Table.ToRecords(files), each fnReadCsv([Content],[Name],[Date modified])),
    combined = if List.Count(rows) = 0 then #table({}, {}) else Table.Combine(rows),
    renamed  = fnApplyRenameMap(combined, renameMap),
    withType = if Table.HasColumns(renamed, {"EventType"}) then renamed else Table.AddColumn(renamed, "EventType", each eventTypeName, type text),
    aligned  = fnEnsureColumns(withType, RequiredTypes),
    sorted   = Table.Sort(aligned, {{"Report Key", Order.Ascending}, {"SourceModified", Order.Descending}}),
    deduped  = Table.Distinct(sorted, {"Report Key"})
in
    deduped

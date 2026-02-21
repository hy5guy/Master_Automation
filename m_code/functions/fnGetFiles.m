// 🕒 2026-02-20-23-48-50
// # functions/fnGetFiles.m
// # Author: R. A. Carucci
// # Purpose: Helper function to discover CSV files in a benchmark event subfolder.

(eventFolder as text) as table =>
let
    folderPath = RootExportPath & "\" & eventFolder,
    files = Folder.Files(folderPath),
    csv   = Table.SelectRows(files, each Text.Lower([Extension]) = ".csv"),
    keep  = Table.SelectColumns(csv, {"Content","Name","Date modified"})
in
    keep

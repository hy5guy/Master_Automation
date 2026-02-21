// 🕒 2026-02-20-23-48-50
// # functions/fnApplyRenameMap.m
// # Author: R. A. Carucci
// # Purpose: Helper function to apply column rename mappings with missing field tolerance.

(tbl as table, renameMap as list) as table =>
let
    renamed = if List.Count(renameMap)=0 then tbl else Table.RenameColumns(tbl, renameMap, MissingField.Ignore)
in
    renamed

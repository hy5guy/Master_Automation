// 🕒 2026-02-20-23-48-50
// # functions/fnEnsureColumns.m
// # Author: R. A. Carucci
// # Purpose: Helper function to ensure all required columns exist with correct types.

(tbl as table, required as type) as table =>
let
    flds    = Type.RecordFields(required),
    names   = Record.FieldNames(flds),
    ensure  = List.Accumulate(names, tbl, (state, col) =>
                if Table.HasColumns(state, {col})
                then state
                else Table.AddColumn(state, col, each null, Value.Type(Record.Field(flds, col)[Type]))),
    casted  = Table.TransformColumnTypes(
                ensure,
                List.Transform(names, each {_, Value.Type(Record.Field(flds, _)[Type])}),
                "en-US")
in
    casted

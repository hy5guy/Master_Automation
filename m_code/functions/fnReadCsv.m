// 🕒 2026-02-20-23-48-50
// # functions/fnReadCsv.m
// # Author: R. A. Carucci
// # Purpose: Helper function to read and type a single benchmark CSV with source metadata.

(content as binary, fileName as text, fileModified as datetime) as table =>
let
    src     = Csv.Document(content, [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    headers = Table.PromoteHeaders(src, [PromoteAllScalars=true]),
    typed   = Table.TransformColumnTypes(headers, {
                {"Badge Number", Int64.Type},
                {"# of Officers Involved", Int64.Type},
                {"# of Subjects", Int64.Type},
                {"Incident Date", type datetime}
             }, "en-US"),
    withSF  = Table.AddColumn(typed, "SourceFile", each fileName, type text),
    withSM  = Table.AddColumn(withSF, "SourceModified", each fileModified, type datetime)
in
    withSM

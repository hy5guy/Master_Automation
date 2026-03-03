// 🕒 2026-02-20-23-48-50
// # shared/Parameters_Check.m
// # Author: R. A. Carucci
// # Purpose: Diagnostic table displaying current values of all Power BI parameters.

#table(
    {"Parameter","Value"},
    {
        {"RootExportPath", RootExportPath},
        {"EtlRootPath",    EtlRootPath},
        {"SourceMode",     SourceMode},
        {"RangeStart",     DateTime.ToText(RangeStart)},
        {"RangeEnd",       DateTime.ToText(RangeEnd)}
    }
)

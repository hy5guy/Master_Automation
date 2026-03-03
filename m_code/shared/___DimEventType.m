// 🕒 2026-02-20-23-48-50
// # shared/___DimEventType.m
// # Author: R. A. Carucci
// # Purpose: Generate event type dimension lookup for benchmark reporting.

let
    Source = #table(
        {"EventType"},
        {
            {"Show of Force"},
            {"Use of Force"},
            {"Vehicle Pursuit"}
        }
    ),
    Typed = Table.TransformColumnTypes(Source, {{"EventType", type text}})
in
    Typed

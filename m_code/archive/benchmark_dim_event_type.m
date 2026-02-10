// DimEventType - Event type dimension table
// QUERY NAME: benchmark_dim_event_type
//
let Source = #table(
        {"EventType", "EventTypeSort"},
        {{"Show of Force", 1}, {"Use of Force", 2}, {"Vehicle Pursuit", 3}}),

    Typed = Table.TransformColumnTypes(
        Source, {{"EventType", type text}, {"EventTypeSort", Int64.Type}})
                in Typed
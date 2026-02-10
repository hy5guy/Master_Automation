// DimEventType - Event Type Dimension Table for Benchmark Dashboard
// Created: 2026-02-09
// Purpose: Dimension table for three Benchmark event types
//
// Columns:
// - EventType: Event type name (text)
//
// Usage:
// - Create relationship: ___Benchmark[EventType] -> ___DimEventType[EventType] (many-to-one)
// - Use in slicers, filters, and visual breakdowns
// - Ensures all three event types appear in visuals even if no data for a specific month

let
    // Define the three event types
    Source = #table(
        {"EventType"},
        {
            {"Show of Force"},
            {"Use of Force"},
            {"Vehicle Pursuit"}
        }
    ),
    
    // Set column type
    Typed = Table.TransformColumnTypes(Source, {{"EventType", type text}})
in
    Typed

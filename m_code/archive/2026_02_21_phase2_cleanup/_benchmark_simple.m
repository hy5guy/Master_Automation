// Benchmark Data Query - SIMPLE VERSION
// Updated: 2026-02-09
// Source: 05_EXPORTS\Benchmark\
//
// This is a simplified version that combines all three event types
// from the cleaned-up Benchmark directory structure.

let
    // Base path
    BasePath = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\Benchmark\",
    
    // === USE OF FORCE ===
    UseOfForcePath = BasePath & "use_force\",
    UseOfForceFiles = Folder.Files(UseOfForcePath),
    UseOfForceLatest = Table.Sort(UseOfForceFiles, {{"Date modified", Order.Descending}}){0}[Content],
    UseOfForceData = Csv.Document(UseOfForceLatest, [Delimiter=",", Encoding=65001]),
    UseOfForceHeaders = Table.PromoteHeaders(UseOfForceData),
    UseOfForceTyped = Table.AddColumn(UseOfForceHeaders, "Event Type", each "Use of Force"),
    
    // === SHOW OF FORCE ===
    ShowOfForcePath = BasePath & "show_force\",
    ShowOfForceFiles = Folder.Files(ShowOfForcePath),
    ShowOfForceLatest = Table.Sort(ShowOfForceFiles, {{"Date modified", Order.Descending}}){0}[Content],
    ShowOfForceData = Csv.Document(ShowOfForceLatest, [Delimiter=",", Encoding=65001]),
    ShowOfForceHeaders = Table.PromoteHeaders(ShowOfForceData),
    ShowOfForceTyped = Table.AddColumn(ShowOfForceHeaders, "Event Type", each "Show of Force"),
    
    // === VEHICLE PURSUIT ===
    VehiclePursuitPath = BasePath & "vehicle_pursuit\",
    VehiclePursuitFiles = Folder.Files(VehiclePursuitPath),
    VehiclePursuitLatest = Table.Sort(VehiclePursuitFiles, {{"Date modified", Order.Descending}}){0}[Content],
    VehiclePursuitData = Csv.Document(VehiclePursuitLatest, [Delimiter=",", Encoding=65001]),
    VehiclePursuitHeaders = Table.PromoteHeaders(VehiclePursuitData),
    VehiclePursuitTyped = Table.AddColumn(VehiclePursuitHeaders, "Event Type", each "Vehicle Pursuit"),
    
    // === COMBINE ALL ===
    Combined = Table.Combine({UseOfForceTyped, ShowOfForceTyped, VehiclePursuitTyped})
in
    Combined

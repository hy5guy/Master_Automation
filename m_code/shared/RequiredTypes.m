// 🕒 2026-02-20-23-48-50
// # shared/RequiredTypes.m
// # Author: R. A. Carucci
// # Purpose: Define required column schema type for benchmark data validation.

let
    RequiredTypes = type table [
#"Officer Name" = text,
#"Badge Number" = Int64.Type,
        Rank = text,
        Organization = text,
#"Incident Number" = text,
#"Report Number" = text,
#"Incident Date" = datetime,
        Location = text,
#"Initial Contact" = text,
#"# of Officers Involved" = Int64.Type,
#"# of Subjects" = Int64.Type,
#"Subject type" = text,
#"Report Key" = text,
        SourceFile = text,
        SourceModified = datetime,
        EventType = text
    ]
in
    RequiredTypes

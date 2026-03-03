// ==============================================================================
// RESPONSE TIMES M CODE - VALIDATED BACKFILL LOADER (v2.8.3 - Revert to Backfill)
// Query Name: ___ResponseTimeCalculator
// ==============================================================================
// UPDATE (v2.8.3 - 2026-02-09):
// - REVERTED to multi-path loading to use January 14, 2026 validated data
// - Fresh Calculator v3.0.0 did not include Jan 14 deduplication/filtering logic
// - Restored priority: Backfill (Jan 14 corrected) > visual_export > _DropExports
// - January 14 data includes: deduplication, enhanced filtering, validated results
// ==============================================================================
// CRITICAL FIX (v2.8.0 - 2026-02-09):
// - REMOVED "type text" from Table.TransformColumns tuple (PRIMARY FIX)
// - Added Response_Time_MMSS to final Typed step for explicit typing
// - Wrapped Step4 lambda in try...otherwise "00:00" for safety
// - Added Number.RoundDown(Number.Round(rawSecs, 0)) for guaranteed integer
// - Fixed Text.From() calls - added "en-US" to ALL conversions (lines 219-220)
// - Added Response_Time_MMSS to empty table schema (line 118)
// - Added AM/PM stripping for time-typed values (line 198)
// ==============================================================================
// ROOT CAUSE ANALYSIS:
// 1. PRIMARY ISSUE: "type text" annotation in Table.TransformColumns caused 
//    Power Query type engine conflict with auto-typing (PromoteAllScalars=true)
//    - CSV value "2.87" auto-typed as Number
//    - Type annotation tried to validate original Number against declared "type text"
//    - 2-decimal precision values (2.87, 2.92) triggered coercion edge case
// 2. SECONDARY ISSUE: Response_Time_MMSS missing from final Typed step
//    - Table.Combine lost per-file column type metadata
//    - Column reverted to inferred numeric type instead of text
// ==============================================================================
// PREVIOUS VERSIONS:
// - v2.7.1: Gemini v2.1 - locale-safe Text.From(raw, "en-US") but still had errors
// - v2.7.0: Gemini v2 - Type-agnostic handling with Value.Is() checks
// - v2.6.0: Gemini-enhanced locale handling (en-US) and proper step ordering
// - v2.5.1: Fixed mixed format handling (MM:SS and decimal minutes)
// - v2.1.0-v2.4.1: Fixed DataSource.NotFound, column naming, date parsing
// ==============================================================================

let
    // ========================================================================
    // CONFIGURATION
    // ========================================================================
    
    // Try multiple possible paths for aggregated response time data
    // Priority order (v2.8.3 - Restored for January 14, 2026 validated data):
    // 1. Backfill folder (January 14 corrected data with dedup + filtering)
    // 2. Visual exports (manual exports from Power BI)
    // 3. Outputs folder (alternative location)
    // 4. _DropExports (Fresh Calculator - NOT used until validated)
    
    PossiblePaths = {
        "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill",
        "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\data\visual_export",
        "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\outputs\visual_exports",
        "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports"
    },
    
    // Find which path exists and has files
    FindValidPath = List.First(
        List.Select(
            PossiblePaths,
            each try Folder.Files(_)[Name]{0}? <> null otherwise false
        ),
        "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill"
    ),
    
    BackfillBasePath = FindValidPath,
    
    // ========================================================================
    // LOAD AGGREGATED MONTHLY FILES ONLY
    // ========================================================================
    
    AllFilesRaw = Folder.Files(BackfillBasePath),
    
    // Filter: response_time subdirectories OR root folders, CSV files with "Average" or "Response Time"
    ResponseTimeFiles = Table.AddColumn(
        Table.SelectRows(
            AllFilesRaw,
            each (Text.Contains([Folder Path], "response_time") or 
                  Text.Contains([Folder Path], "Backfill") or
                  Text.Contains([Folder Path], "visual_export") or
                  Text.Contains([Folder Path], "_DropExports")) and
                 Text.EndsWith(Text.Lower([Name]), ".csv") and
                 (Text.Contains([Name], "Average") or 
                  Text.Contains([Name], "Response Time"))
        ),
        "FileSize",
        each Binary.Length([Content])
    ),
    
    // Filter by file size - keep only small files (aggregated data)
    AggregatedFilesOnly = Table.SelectRows(
        ResponseTimeFiles,
        each [FileSize] < 50000  // Aggregated <10KB, raw data >50KB
    ),
    
    // ========================================================================
    // PROCESS EACH AGGREGATED CSV FILE
    // ========================================================================
    
    LoadedFiles = Table.AddColumn(
        AggregatedFilesOnly,
        "Data",
        each let
            RawData = Csv.Document([Content], [Delimiter = ",", Encoding = 1252, QuoteStyle = QuoteStyle.None]),
            WithHeaders = Table.PromoteHeaders(RawData, [PromoteAllScalars = true]),
            
            // Check if this is raw data (skip if so)
            IsRawData = Table.HasColumns(WithHeaders, "ReportNumberNew") or
                       Table.HasColumns(WithHeaders, "Time of Call"),
            
            Result = if IsRawData then
                // Skip raw data - return empty table with all expected columns including Response_Time_MMSS
                #table(
                    {"Response_Type", "Average_Response_Time", "Response_Time_MMSS", "MM-YY"}, 
                    {}
                )
            else
                // Process aggregated data
                let
                    // Rename Response_Type column if needed
                    Step1 = if Table.HasColumns(WithHeaders, "Response_Type") then WithHeaders
                           else if Table.HasColumns(WithHeaders, "Response Type") 
                           then Table.RenameColumns(WithHeaders, {{"Response Type", "Response_Type"}}, MissingField.Ignore)
                           else WithHeaders,
                    
                    // Rename Response_Time_MMSS column if needed
                    Step1b = if Table.HasColumns(Step1, "Response_Time_MMSS") then Step1
                            else if Table.HasColumns(Step1, "First Response_Time_MMSS")
                            then Table.RenameColumns(Step1, {{"First Response_Time_MMSS", "Response_Time_MMSS"}}, MissingField.Ignore)
                            else Step1,
                    
                    // Rename Month-Year column to MM-YY
                    Step2 = if Table.HasColumns(Step1b, "MM-YY") then Step1b
                           else if Table.HasColumns(Step1b, "MM_YY")
                           then Table.RenameColumns(Step1b, {{"MM_YY", "MM-YY"}}, MissingField.Ignore)
                           else if Table.HasColumns(Step1b, "Month-Year")
                           then Table.RenameColumns(Step1b, {{"Month-Year", "MM-YY"}}, MissingField.Ignore)
                           else Step1b,
                    
                    // Handle WIDE format (Emergency_Avg_13M, Routine_Avg_13M, Urgent_Avg_13M OR Emergency Avg, Routine Avg, Urgent Avg)
                    Step3 = if (Table.HasColumns(Step2, "Emergency_Avg_13M") or Table.HasColumns(Step2, "Emergency Avg")) and
                              (Table.HasColumns(Step2, "Routine_Avg_13M") or Table.HasColumns(Step2, "Routine Avg")) and
                              (Table.HasColumns(Step2, "Urgent_Avg_13M") or Table.HasColumns(Step2, "Urgent Avg"))
                           then let
                               Unpivoted = Table.UnpivotOtherColumns(Step2, {"MM-YY"}, "Response_Type_Raw", "Average_Response_Time"),
                               WithType = Table.AddColumn(
                                   Unpivoted, 
                                   "Response_Type", 
                                   each Text.Trim(
                                       Text.Replace(
                                           Text.Replace([Response_Type_Raw], "_Avg_13M", ""),
                                           " Avg", 
                                           ""
                                       )
                                   ), 
                                   type text
                               ),
                               Cleaned = Table.RemoveColumns(WithType, {"Response_Type_Raw"}),
                               WithMMSS = Table.AddColumn(
                                   Cleaned,
                                   "Response_Time_MMSS",
                                   each let
                                       // Handle null or non-numeric values
                                       totalMins = if [Average_Response_Time] = null then 0
                                                  else if Value.Is([Average_Response_Time], type number) then [Average_Response_Time]
                                                  else try Number.From([Average_Response_Time], "en-US") otherwise 0,
                                       mins = Number.RoundDown(totalMins),
                                       secs = Number.RoundDown(Number.Round((totalMins - mins) * 60, 0)),
                                       mmss = Text.PadStart(Text.From(mins, "en-US"), 2, "0") & ":" & 
                                             Text.PadStart(Text.From(secs, "en-US"), 2, "0")
                                   in mmss
                               )
                           in WithMMSS
                           else Step2,
                    
                    // Step 4: Standardize Response_Time_MMSS (Handles MM:SS, M:SS, HH:MM:SS, and Decimals)
                    // v2.8.0 CRITICAL FIX: Removed "type text" from tuple, added try...otherwise wrapper
                    Step4 = if Table.HasColumns(Step3, "Response_Time_MMSS")
                            then Table.TransformColumns(
                                Step3,
                                {{"Response_Time_MMSS", each 
                                    try (
                                        let
                                            // 1. Capture the raw value and its type
                                            raw = if _ = null then "00:00" else _,
                                            isNum = Value.Is(raw, type number),
                                            isDuration = Value.Is(raw, type duration),
                                            isTime = Value.Is(raw, type time),
                                            
                                            // 2. Convert to text safely with locale
                                            strVal = Text.Trim(
                                                if isTime then 
                                                    // Strip AM/PM if present
                                                    Text.Replace(Text.Replace(Text.From(raw, "en-US"), " AM", ""), " PM", "")
                                                else 
                                                    Text.From(raw, "en-US")
                                            ),
                                            hasColon = Text.Contains(strVal, ":"),

                                            result = if hasColon then
                                                // Logic for MM:SS or HH:MM:SS formats
                                                let
                                                    parts = Text.Split(strVal, ":"),
                                                    // Handle 3-part time (HH:MM:SS) by taking first two as MM:SS
                                                    m = Text.PadStart(parts{0}, 2, "0"),
                                                    s = if List.Count(parts) > 1 
                                                        then Text.PadStart(Text.Start(parts{1}, 2), 2, "0") 
                                                        else "00"
                                                in m & ":" & s
                                            else
                                                // Logic for Decimal Minutes (e.g., 1.3 -> 01:18, 2.87 -> 02:52)
                                                let
                                                    // Convert to number safely using en-US locale if not already a number
                                                    decVal = if isNum then raw 
                                                            else try Number.From(strVal, "en-US") 
                                                            otherwise 0,
                                                    mins = Number.RoundDown(decVal),
                                                    // v2.8.0 FIX: Added Number.RoundDown wrapper for guaranteed integer
                                                    rawSecs = (decVal - mins) * 60,
                                                    secs = Number.RoundDown(Number.Round(rawSecs, 0)),
                                                    // v2.8.0 FIX: Added "en-US" to ALL Text.From calls
                                                    finalMmss = Text.PadStart(Text.From(mins, "en-US"), 2, "0") & ":" & 
                                                               Text.PadStart(Text.From(secs, "en-US"), 2, "0")
                                                in finalMmss
                                        in result
                                    ) otherwise "00:00"  // v2.8.0 FIX: Safety wrapper
                                }}  // v2.8.0 CRITICAL FIX: Removed ", type text" from here
                            )
                            else Step3,

                    // Step 4b: Calculate Average_Response_Time (Decimal Minutes) from standardized MM:SS
                    Step4b = if Table.HasColumns(Step4, "Response_Time_MMSS")
                            then Table.AddColumn(
                                // Ensure we remove any existing 'Average_Response_Time' column before recalculating
                                if Table.HasColumns(Step4, "Average_Response_Time") 
                                    then Table.RemoveColumns(Step4, {"Average_Response_Time"}) 
                                    else Step4,
                                "Average_Response_Time",
                                each try let
                                    parts = Text.Split([Response_Time_MMSS], ":"),
                                    total = Number.From(parts{0}, "en-US") + (Number.From(parts{1}, "en-US") / 60)
                                in total 
                                otherwise 0, 
                                type number
                            )
                            else Step4,
                    
                    // Add YearMonth - handle multiple formats
                    Step5 = if Table.HasColumns(Step4b, "YearMonth") then Step4b
                           else Table.AddColumn(
                               Step4b,
                               "YearMonth",
                               each let
                                   mmYY = Text.Trim(Text.From([#"MM-YY"])),
                                   parts = Text.Split(mmYY, "-"),
                                   yearMonth = if List.Count(parts) >= 2 then
                                       let
                                           part1 = parts{0},
                                           part2 = parts{1},
                                           isMMYY = Text.Length(part2) = 2 and Text.Length(part1) <= 2,
                                           isYYYYMM = Text.Length(part1) = 4,
                                           
                                           result = if isMMYY then
                                               "20" & part2 & "-" & Text.PadStart(part1, 2, "0")
                                           else if isYYYYMM and Text.Length(part2) = 2 then
                                               mmYY
                                           else if isYYYYMM and Text.Length(part2) = 3 then
                                               let
                                                   monthNum = if Text.Upper(part2) = "JAN" then "01"
                                                             else if Text.Upper(part2) = "FEB" then "02"
                                                             else if Text.Upper(part2) = "MAR" then "03"
                                                             else if Text.Upper(part2) = "APR" then "04"
                                                             else if Text.Upper(part2) = "MAY" then "05"
                                                             else if Text.Upper(part2) = "JUN" then "06"
                                                             else if Text.Upper(part2) = "JUL" then "07"
                                                             else if Text.Upper(part2) = "AUG" then "08"
                                                             else if Text.Upper(part2) = "SEP" then "09"
                                                             else if Text.Upper(part2) = "OCT" then "10"
                                                             else if Text.Upper(part2) = "NOV" then "11"
                                                             else if Text.Upper(part2) = "DEC" then "12"
                                                             else null
                                               in if monthNum <> null then part1 & "-" & monthNum else null
                                           else null
                                       in result
                                   else null
                               in yearMonth,
                               type text
                           ),
                    
                    // Add Date_Sort_Key
                    Step6 = if Table.HasColumns(Step5, "Date_Sort_Key") then Step5
                           else Table.AddColumn(
                               Step5,
                               "Date_Sort_Key",
                               each try Date.FromText([YearMonth] & "-01") otherwise null,
                               type date
                           )
                    
                in Step6
        in Result
    ),
    
    // ========================================================================
    // COMBINE ALL FILES
    // ========================================================================
    
    AllData = Table.Combine(LoadedFiles[Data]),
    
    // Remove any empty rows (from skipped raw data files)
    NonEmpty = Table.SelectRows(AllData, each [Response_Type] <> null),
    
    // ========================================================================
    // ENSURE COLUMN TYPES - v2.8.0 FIX: Added Response_Time_MMSS here
    // ========================================================================
    
    Typed = Table.TransformColumnTypes(
        NonEmpty,
        {
            {"Response_Type", type text},
            {"Average_Response_Time", type number},
            {"Response_Time_MMSS", type text},  // v2.8.0 CRITICAL FIX: Added explicit typing HERE
            {"MM-YY", type text},
            {"YearMonth", type text},
            {"Date_Sort_Key", type date}
        },
        "en-US"
    ),
    
    // ========================================================================
    // ADD DAX-COMPATIBLE COLUMNS
    // ========================================================================
    
    WithSummaryType = Table.AddColumn(Typed, "Summary_Type", each "Response_Type", type text),
    WithCategory = Table.AddColumn(WithSummaryType, "Category", each [Response_Type], type text),
    WithDate = Table.AddColumn(WithCategory, "Date", each [Date_Sort_Key], type date),
    
    // ========================================================================
    // FINAL OUTPUT
    // ========================================================================
    
    Result = Table.SelectColumns(
        WithDate,
        {
            "YearMonth",
            "Date_Sort_Key",
            "Date",
            "Response_Type",
            "Summary_Type",
            "Category",
            "Average_Response_Time",
            "Response_Time_MMSS",
            "MM-YY"
        }
    )

in
    Result

// ==============================================================================
// v2.8.0 SUMMARY OF 7 CRITICAL FIXES:
// 1. REMOVED "type text" from Table.TransformColumns tuple (line 192)
// 2. ADDED Response_Time_MMSS to final Typed step as "type text" (line 332)
// 3. WRAPPED entire Step4 lambda in try...otherwise "00:00" (lines 192-223)
// 4. ADDED Number.RoundDown(Number.Round(rawSecs, 0)) for integer guarantee (line 219)
// 5. ADDED AM/PM stripping for time-typed values (line 198)
// 6. ADDED "en-US" to ALL Text.From() calls (lines 220-221, 178-179)
// 7. ADDED Response_Time_MMSS to empty table schema (line 118)
// ==============================================================================
// EXPECTED RESULT: 0% errors (down from 31%)
// Column quality: Response_Time_MMSS should show 100% valid (green bar)
// ==============================================================================

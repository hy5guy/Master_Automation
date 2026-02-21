"""Split consolidated M code file into individual .m files with standardized headers."""
import re
from pathlib import Path
from datetime import datetime, timezone, timedelta

EST = timezone(timedelta(hours=-5))
TIMESTAMP = datetime.now(EST).strftime("%Y-%m-%d-%H-%M-%S")

SRC = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\m_code\all_m_code_26_january_monthly.m")
BASE = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\m_code")

QUERY_MAP = {
    "___Arrest_Distro":                    ("arrests",       "___Arrest_Distro.m",                    "Process arrest data with enhanced null handling, ZIP lookup, and home category classification."),
    "___Top_5_Arrests":                    ("arrests",       "___Top_5_Arrests.m",                    "Compute top 5 arresting officers for the previous month with dynamic file loading."),
    "___ComprehensiveDateTable":           ("shared",        "___ComprehensiveDateTable.m",           "Generate date dimension table with fiscal year, sort keys, and multiple display formats."),
    "___Chief2":                           ("patrol",        "___Chief2.m",                           "Load Chief of Police monthly activity metrics with YoY comparison and unpivoted periods."),
    "___Drone":                            ("drone",         "___Drone.m",                            "Process DFR and Non-DFR drone metrics with duration-based value handling."),
    "___Combined_Outreach_All":            ("community",     "___Combined_Outreach_All.m",            "Load community engagement data from Python ETL CSV output for Power BI."),
    "___CSB_Monthly":                      ("csb",           "___CSB_Monthly.m",                      "Load Crime Suppression Bureau monthly tracked items with rolling 13-month window."),
    "___Detectives":                       ("detectives",    "___Detectives.m",                       "Load Detective Division monthly activity from workbook with rolling 13-month window."),
    "___Det_case_dispositions_clearance":  ("detectives",    "___Det_case_dispositions_clearance.m",  "Load case disposition and clearance rates for Detective Division with 13-month window."),
    "___STACP_pt_1_2":                     ("stacp",         "___STACP_pt_1_2.m",                     "Load STACP monthly tracked items with rolling 13-month window and dynamic column detection."),
    "___Patrol":                           ("patrol",        "___Patrol.m",                           "Load Patrol Division monthly activity metrics with wide-format month columns."),
    "___REMU":                             ("patrol",        "___REMU.m",                             "Load REMU monthly activity metrics from contribution workbook."),
    "___Benchmark":                        ("benchmark",     "___Benchmark.m",                        "Load use-of-force benchmark data with event type classification and month dimensions."),
    "___DimMonth":                         ("shared",        "___DimMonth.m",                         "Generate month dimension lookup table for benchmark date relationships."),
    "___DimEventType":                     ("shared",        "___DimEventType.m",                     "Generate event type dimension lookup for benchmark reporting."),
    "___Overtime_Timeoff_v3":              ("overtime",      "___Overtime_Timeoff_v3.m",              "Load Overtime and TimeOff monthly accrual data with personnel merge and 13-month window."),
    "___ResponseTimeCalculator":           ("response_time", "___ResponseTimeCalculator.m",           "Calculate average response times from backfill CSVs with mm:ss conversion and 13-month window."),
    "___Traffic":                          ("traffic",       "___Traffic.m",                          "Load Traffic Bureau monthly activity metrics from contribution workbook."),
    "___Social_Media":                     ("stacp",         "___Social_Media.m",                     "Load social media engagement metrics with rolling 13-month window."),
    "___SSOCC_Data":                       ("ssocc",         "___SSOCC_Data.m",                       "Load SSOCC dispatch and alert data with multi-sheet workbook handling."),
    "___NIBRS_Monthly_Report":             ("nibrs",         "___NIBRS_Monthly_Report.m",             "Load NIBRS monthly crime statistics with clearance rate calculations."),
    "___In_Person_Training":               ("training",      "___In_Person_Training.m",               "Load in-person training attendance and cost data from Policy Training workbook."),
    "___Cost_of_Training":                 ("training",      "___Cost_of_Training.m",                 "Calculate training cost by delivery method with rolling 13-month window."),
    "___chief_projects":                   ("community",     "___chief_projects.m",                   "Load Chief's Projects and Initiatives event data from contribution workbook."),
    "RootExportPath":                      ("parameters",    "RootExportPath.m",                      "Power BI parameter for benchmark export root folder path."),
    "EtlRootPath":                         ("parameters",    "EtlRootPath.m",                         "Power BI parameter for benchmark ETL script root folder path."),
    "SourceMode":                          ("parameters",    "SourceMode.m",                          "Power BI parameter to select data source mode (Excel or Folder)."),
    "RangeStart":                          ("parameters",    "RangeStart.m",                          "Power BI parameter for benchmark date range start boundary."),
    "RangeEnd":                            ("parameters",    "RangeEnd.m",                            "Power BI parameter for benchmark date range end boundary."),
    "RequiredTypes":                       ("shared",        "RequiredTypes.m",                       "Define required column schema type for benchmark data validation."),
    "fnGetFiles":                          ("functions",     "fnGetFiles.m",                          "Helper function to discover CSV files in a benchmark event subfolder."),
    "fnReadCsv":                           ("functions",     "fnReadCsv.m",                           "Helper function to read and type a single benchmark CSV with source metadata."),
    "fnEnsureColumns":                     ("functions",     "fnEnsureColumns.m",                     "Helper function to ensure all required columns exist with correct types."),
    "fnApplyRenameMap":                    ("functions",     "fnApplyRenameMap.m",                    "Helper function to apply column rename mappings with missing field tolerance."),
    "fnLoadRaw":                           ("functions",     "fnLoadRaw.m",                           "Helper function to load, rename, align, and deduplicate benchmark event data."),
    "Parameters_Check":                    ("shared",        "Parameters_Check.m",                    "Diagnostic table displaying current values of all Power BI parameters."),
    "summons_13month_trend":               ("summons",       "summons_13month_trend.m",               "Load summons data from staging workbook for 13-month trend analysis."),
    "summons_top5_parking":                ("summons",       "summons_top5_parking.m",                "Compute top 5 parking violation officers for the latest month."),
    "summons_all_bureaus":                 ("summons",       "summons_all_bureaus.m",                 "Aggregate summons counts by bureau for moving and parking violations."),
    "___Summons_Diagnostic":               ("summons",       "___Summons_Diagnostic.m",               "Diagnostic query to validate summons data quality and column structure."),
    "summons_top5_moving":                 ("summons",       "summons_top5_moving.m",                 "Compute top 5 moving violation officers for the latest month."),
    "STACP_DIAGNOSTIC":                    ("stacp",         "STACP_DIAGNOSTIC.m",                    "Diagnostic query to verify STACP column detection and 13-month window logic."),
    "TAS_Dispatcher_Incident":             ("ssocc",         "TAS_Dispatcher_Incident.m",             "Load TAS dispatcher incident summary data from SSOCC workbook."),
    "ESU_13Month":                         ("esu",           "ESU_13Month.m",                         "Load ESU monthly activity with tracked item lookup and rolling 13-month window."),
}

SKIP_SUBHEADERS = {
    "REQUIRED ROW ORDER (EXACT LABELS)",
    "___Benchmark - FIXED for DAX compatibility",
    "Required by DAX measures: EventType (no space), MonthStart, MonthLabel",
    "___Summons_Top5_Parking (Standalone)",
    "___Summons_All_Bureaus (Standalone)",
    "___Summons_Top5_Moving (Standalone)",
}

def make_header(folder, filename, purpose):
    return (
        f"// \U0001f552 {TIMESTAMP}\n"
        f"// # {folder}/{filename}\n"
        f"// # Author: R. A. Carucci\n"
        f"// # Purpose: {purpose}\n"
    )

def split_file():
    lines = SRC.read_text(encoding="utf-8").splitlines()
    queries = []
    current_name = None
    current_lines = []

    header_re = re.compile(r"^//\s*(_{2,3}[A-Za-z]\w*|fn[A-Z]\w*|summons_\w+|STACP_DIAGNOSTIC|TAS_Dispatcher_Incident|ESU_13Month|RootExportPath|EtlRootPath|SourceMode|RangeStart|RangeEnd|RequiredTypes|Parameters_Check)\s*$")

    for line in lines:
        m = header_re.match(line)
        if m:
            candidate = m.group(1).strip()
            if candidate in SKIP_SUBHEADERS:
                current_lines.append(line)
                continue
            if candidate in QUERY_MAP:
                if current_name:
                    queries.append((current_name, current_lines))
                current_name = candidate
                current_lines = []
                continue
        current_lines.append(line)

    if current_name:
        queries.append((current_name, current_lines))

    print(f"Parsed {len(queries)} queries from consolidated file")

    written = 0
    for name, body_lines in queries:
        while body_lines and body_lines[0].strip() == "":
            body_lines = body_lines[1:]
        while body_lines and body_lines[-1].strip() == "":
            body_lines = body_lines[:-1]

        # Strip old headers (lines starting with // before the first non-comment, non-blank line)
        code_start = 0
        for i, ln in enumerate(body_lines):
            stripped = ln.strip()
            if stripped == "" or stripped.startswith("//"):
                continue
            code_start = i
            break
        code_lines = body_lines[code_start:]

        folder, filename, purpose = QUERY_MAP[name]
        header = make_header(folder, filename, purpose)
        content = header + "\n" + "\n".join(code_lines) + "\n"

        out_path = BASE / folder / filename
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        size = out_path.stat().st_size
        print(f"  {folder}/{filename} ({size:,} B, {len(code_lines)} lines)")
        written += 1

    print(f"\nWritten: {written} files")
    print(f"Missing from consolidated: ___Arrest_Categories (export manually from Power Query)")

if __name__ == "__main__":
    split_file()

"""
inject_ai_context_reference.py — Inject AI_Context_Reference worksheet into HPD shared workbooks.

Usage:
    python scripts/inject_ai_context_reference.py                # All Tier 1 workbooks
    python scripts/inject_ai_context_reference.py --tier2        # Include Tier 2
    python scripts/inject_ai_context_reference.py --dry-run      # Preview only
    python scripts/inject_ai_context_reference.py --workbook CSB  # Single workbook
    python scripts/inject_ai_context_reference.py --verbose       # Detailed logging
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------
ONEDRIVE_ROOT = Path(os.path.expanduser("~")) / "OneDrive - City of Hackensack"
CONTRIBUTIONS_DIR = ONEDRIVE_ROOT / "Shared Folder" / "Compstat" / "Contributions"
REPO_ROOT = ONEDRIVE_ROOT / "06_Workspace_Management"

# ---------------------------------------------------------------------------
# HPD color palette
# ---------------------------------------------------------------------------
NAVY = "1A2744"
GOLD = "C8A84B"
LIGHT_GOLD = "F5F0E0"
LIGHT_BLUE = "D6E4F0"
GRAY_ALT = "F2F2F2"
GRAY_TEXT = "666666"
LINK_BLUE = "0563C1"
WHITE = "FFFFFF"
BLACK = "000000"

# ---------------------------------------------------------------------------
# Workbook inventory
# ---------------------------------------------------------------------------
TIER1_WORKBOOKS = [
    {"id": 1, "name": "csb_monthly.xlsm", "subfolder": "CSB",
     "purpose": "Crime Suppression Bureau monthly metrics", "tier": 1},
    {"id": 2, "name": "STACP.xlsm", "subfolder": "STACP",
     "purpose": "Strategic Tackling Armed Crime Plan data", "tier": 1},
    {"id": 3, "name": "patrol_monthly.xlsm", "subfolder": "Patrol",
     "purpose": "Patrol Division monthly activity metrics", "tier": 1},
    {"id": 4, "name": "Policy_Training_Monthly.xlsx", "subfolder": "Policy_Training",
     "purpose": "Training course attendance and cost tracking", "tier": 1},
    {"id": 5, "name": "detectives_monthly.xlsx", "subfolder": "Detectives",
     "purpose": "Detective case dispositions and clearance rates", "tier": 1},
    {"id": 6, "name": "ESU.xlsx", "subfolder": "ESU",
     "purpose": "Emergency Services Unit monthly activity", "tier": 1},
    {"id": 7, "name": "Traffic_Monthly.xlsx", "subfolder": "Traffic",
     "purpose": "Traffic Bureau enforcement and citations", "tier": 1},
    {"id": 8, "name": "chief_monthly.xlsx", "subfolder": "Chief",
     "purpose": "Chief's Projects and Initiatives tracking", "tier": 1},
    {"id": 9, "name": "Drone_Monthly.xlsx", "subfolder": "",
     "purpose": "Drone operations metrics (DFR vs Non-DFR)", "tier": 1},
    {"id": 10, "name": "dfr_directed_patrol_enforcement.xlsx", "subfolder": "Drone",
     "purpose": "DFR Summons Log (Claude in Excel workbook; ETL-fed via dfr_export.py)", "tier": 1},
]

TIER2_WORKBOOKS = [
    {"id": 11, "name": "policy_training_outputs.xlsx",
     "path": ONEDRIVE_ROOT / "02_ETL_Scripts" / "Policy_Training_Monthly" / "output" / "policy_training_outputs.xlsx",
     "purpose": "Aggregated training delivery costs (ETL output)", "tier": 2},
    {"id": 12, "name": "Assignment_Master_V3_FINAL.xlsx",
     "path": ONEDRIVE_ROOT / "09_Reference" / "Personnel" / "Assignment_Master_V3_FINAL.xlsx",
     "purpose": "Personnel roster — 25 columns, 166 records", "tier": 2},
    {"id": 13, "name": "NIBRS_Monthly_Report.xlsx",
     "path": ONEDRIVE_ROOT / "01_DataSources" / "NIBRS" / "NIBRS_Monthly_Report.xlsx",
     "purpose": "NIBRS monthly incident classification", "tier": 2},
    {"id": 14, "name": "_SSOCC - Service Log.xlsx",
     "path": ONEDRIVE_ROOT / "KB_Shared" / "04_output" / "ssocc_claude_in_excel_rework" / "_SSOCC - Service Log.xlsx",
     "purpose": "SSOCC dispatch and alert data", "tier": 2},
]

# ---------------------------------------------------------------------------
# Known M-code → workbook mappings
# ---------------------------------------------------------------------------
M_CODE_MAP = {
    "csb_monthly.xlsm": {
        "m_code": ["m_code/csb/___CSB_Monthly.m"],
        "sheet_target": "MoM sheet",
        "month_format": "MM-YY",
        "pages": ["CSB"],
    },
    "STACP.xlsm": {
        "m_code": ["m_code/stacp/___STACP_pt_1_2.m"],
        "sheet_target": "Multiple sheets (month columns MM-YY)",
        "month_format": "MM-YY",
        "pages": ["STACP"],
    },
    "patrol_monthly.xlsm": {
        "m_code": ["m_code/patrol/___Patrol.m"],
        "sheet_target": "_mom_patrol table",
        "month_format": "MM-YY",
        "pages": ["Patrol"],
    },
    "Policy_Training_Monthly.xlsx": {
        "m_code": ["m_code/training/___In_Person_Training.m"],
        "sheet_target": "Training_Log sheet (fallback Training_Log_Clean)",
        "month_format": "Date column (Start date)",
        "pages": ["Policy & Training Qual"],
    },
    "detectives_monthly.xlsx": {
        "m_code": ["m_code/detectives/___Detectives.m", "m_code/detectives/___Det_case_dispositions_clearance.m"],
        "sheet_target": "Case data tables / Disposition tables",
        "month_format": "MM-YY",
        "pages": ["Detectives"],
    },
    "ESU.xlsx": {
        "m_code": ["m_code/esu/ESU_13Month.m"],
        "sheet_target": "_YY_MMM named tables + _mom_hacsoc dimension",
        "month_format": "_YY_MMM (e.g., _25_JAN)",
        "pages": ["ESU"],
    },
    "Traffic_Monthly.xlsx": {
        "m_code": ["m_code/traffic/___Traffic.m"],
        "sheet_target": "_mom_traffic table",
        "month_format": "MM-YY",
        "pages": ["Traffic"],
    },
    "chief_monthly.xlsx": {
        "m_code": ["m_code/chief/___Chief2.m", "m_code/chief/___chief_projects.m"],
        "sheet_target": "Table8 (events) / Projects table",
        "month_format": "Date column",
        "pages": ["Chief"],
    },
    "Drone_Monthly.xlsx": {
        "m_code": ["m_code/drone/___Drone.m"],
        "sheet_target": "DFR Activity sheet, Non-DFR sheet",
        "month_format": "Date column",
        "pages": ["Drone"],
    },
    "dfr_directed_patrol_enforcement.xlsx": {
        "m_code": ["m_code/drone/DFR_Summons.m"],
        "sheet_target": "DFR_Summons table (fallback: DFR Summons Log sheet)",
        "month_format": "Date column + MM-YY derived",
        "pages": ["DFR Summons"],
        "python_etl": "scripts/dfr_export.py",
    },
    "policy_training_outputs.xlsx": {
        "m_code": ["m_code/training/___In_Person_Training.m", "m_code/training/___Cost_of_Training.m"],
        "sheet_target": "InPerson_Prior_Month_List / Delivery_Cost_By_Month",
        "month_format": "Date column / MM-YY",
        "pages": ["Policy & Training Qual"],
    },
    "NIBRS_Monthly_Report.xlsx": {
        "m_code": ["m_code/nibrs/___NIBRS_Monthly_Report.m"],
        "sheet_target": "NIBRS data tables",
        "month_format": "MM-YY",
        "pages": ["NIBRS"],
    },
    "_SSOCC - Service Log.xlsx": {
        "m_code": ["m_code/ssocc/___SSOCC_Data.m"],
        "sheet_target": "Service log tables",
        "month_format": "Date column",
        "pages": ["SSOCC"],
    },
    "Assignment_Master_V3_FINAL.xlsx": {
        "m_code": [],
        "sheet_target": "Personnel roster",
        "month_format": "N/A",
        "pages": ["(Reference — not directly visualized)"],
    },
}

# Related docs mapping
RELATED_DOCS = {
    "csb_monthly.xlsm": [],
    "STACP.xlsm": ["docs/stacp_standardization_prompt_claude_in_excel.md"],
    "patrol_monthly.xlsm": [],
    "Policy_Training_Monthly.xlsx": ["docs/POLICY_TRAINING_AUTOMATION_AND_COST_VISUAL.md", "docs/POWER_BI_YTD_MEASURES_AND_PAGE_INSTRUCTIONS.md"],
    "detectives_monthly.xlsx": [],
    "ESU.xlsx": ["docs/ESU_POWER_BI_LOAD_AND_PUBLISH.md"],
    "Traffic_Monthly.xlsx": [],
    "chief_monthly.xlsx": [],
    "Drone_Monthly.xlsx": [],
    "dfr_directed_patrol_enforcement.xlsx": ["docs/DFR_Summons_Claude_Excel_Development_Log.md", "docs/PROMPT_Claude_In_Excel_DFR_Directed_Patrol_Summons_MCode.md"],
    "policy_training_outputs.xlsx": ["docs/POLICY_TRAINING_AUTOMATION_AND_COST_VISUAL.md"],
    "Assignment_Master_V3_FINAL.xlsx": ["09_Reference/Personnel/Assignment_Master_SCHEMA.md"],
    "NIBRS_Monthly_Report.xlsx": [],
    "_SSOCC - Service Log.xlsx": ["docs/SSOCC_Service_Log_Excel_And_Power_BI_Rework_2026_03.md"],
}


# ---------------------------------------------------------------------------
# Config loaders
# ---------------------------------------------------------------------------
def load_scripts_json():
    p = REPO_ROOT / "config" / "scripts.json"
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_visual_export_mapping():
    p = REPO_ROOT / "Standards" / "config" / "powerbi_visuals" / "visual_export_mapping.json"
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def find_etl_scripts_for_workbook(wb_name, scripts_json):
    """Cross-reference scripts.json to find ETL scripts related to a workbook."""
    results = []
    keywords_map = {
        "csb_monthly.xlsm": ["csb"],
        "STACP.xlsm": ["stacp"],
        "patrol_monthly.xlsm": ["patrol"],
        "Policy_Training_Monthly.xlsx": ["policy", "training"],
        "detectives_monthly.xlsx": ["detective"],
        "ESU.xlsx": ["esu"],
        "Traffic_Monthly.xlsx": ["traffic"],
        "chief_monthly.xlsx": ["chief"],
        "Drone_Monthly.xlsx": ["drone"],
        "dfr_directed_patrol_enforcement.xlsx": ["summon", "dfr"],
        "policy_training_outputs.xlsx": ["policy", "training"],
        "NIBRS_Monthly_Report.xlsx": ["nibrs"],
        "_SSOCC - Service Log.xlsx": ["ssocc"],
        "Assignment_Master_V3_FINAL.xlsx": ["personnel", "assignment"],
    }
    kws = keywords_map.get(wb_name, [])
    for script in scripts_json.get("scripts", []):
        script_kws = [k.lower() for k in script.get("keywords", [])]
        if any(k in script_kws for k in kws):
            results.append(script)
    # Special: DFR always maps to dfr_export.py
    if wb_name == "dfr_directed_patrol_enforcement.xlsx":
        results.append({"name": "DFR Export", "script": "scripts/dfr_export.py", "enabled": True})
    return results


def find_visuals_for_workbook(wb_name, visual_mapping):
    """Find visual export mappings related to a workbook's domain."""
    domain_map = {
        "csb_monthly.xlsm": ["csb"],
        "STACP.xlsm": ["stacp"],
        "patrol_monthly.xlsm": ["patrol"],
        "Policy_Training_Monthly.xlsx": ["training", "policy"],
        "detectives_monthly.xlsx": ["detective"],
        "ESU.xlsx": ["esu"],
        "Traffic_Monthly.xlsx": ["traffic"],
        "chief_monthly.xlsx": ["chief"],
        "Drone_Monthly.xlsx": ["drone"],
        "dfr_directed_patrol_enforcement.xlsx": ["dfr", "drone"],
        "policy_training_outputs.xlsx": ["training"],
        "NIBRS_Monthly_Report.xlsx": ["nibrs"],
        "_SSOCC - Service Log.xlsx": ["ssocc"],
        "Assignment_Master_V3_FINAL.xlsx": [],
    }
    domains = domain_map.get(wb_name, [])
    results = []
    for m in visual_mapping.get("mappings", []):
        folder = m.get("normalized_folder", "").lower()
        page = m.get("page_name", "").lower()
        if any(d in folder or d in page for d in domains):
            results.append(m)
    return results


# ---------------------------------------------------------------------------
# Workbook analysis
# ---------------------------------------------------------------------------
def analyze_workbook(wb_path, wb):
    """Analyze workbook structure: sheets, tables, columns, validations."""
    info = {
        "sheets": [],
        "tables": [],
        "columns": {},
        "named_ranges": [],
        "has_vba": wb_path.suffix.lower() == ".xlsm",
        "protected_sheets": [],
    }

    for ws_name in wb.sheetnames:
        ws = wb[ws_name]
        visibility = "Visible"
        if ws.sheet_state == "hidden":
            visibility = "Hidden"
        elif ws.sheet_state == "veryHidden":
            visibility = "Very Hidden"

        table_names = []
        for tbl in ws.tables.values():
            table_names.append(tbl.name)
            ref = tbl.ref
            # Parse ref like A1:Z100
            info["tables"].append({
                "name": tbl.name,
                "sheet": ws_name,
                "ref": ref,
            })

        # Row/col counts
        row_count = ws.max_row or 0
        col_count = ws.max_column or 0

        # Check protection
        if ws.protection.sheet:
            info["protected_sheets"].append(ws_name)

        info["sheets"].append({
            "name": ws_name,
            "visibility": visibility,
            "tables": table_names,
            "rows": row_count,
            "cols": col_count,
        })

        # Extract column headers from first non-empty row (for visible data sheets)
        if visibility == "Visible" and row_count > 0 and ws_name != "AI_Context_Reference":
            headers = []
            for col_idx in range(1, min(col_count + 1, 51)):  # up to 50 cols
                cell = ws.cell(row=1, column=col_idx)
                if cell.value is not None:
                    hdr = str(cell.value)
                    # Check for non-breaking spaces
                    has_nbsp = "\xa0" in hdr
                    dtype = infer_dtype(ws, col_idx, row_count)
                    sample = get_sample_value(ws, col_idx)
                    # Check for data validation
                    validation_info = ""
                    dropdown_source = ""
                    headers.append({
                        "name": hdr,
                        "dtype": dtype,
                        "sample": sample,
                        "has_nbsp": has_nbsp,
                        "validation": validation_info,
                        "dropdown_source": dropdown_source,
                    })
            if headers:
                info["columns"][ws_name] = headers

    # Named ranges
    try:
        for name in wb.defined_names:
            info["named_ranges"].append(name)
    except Exception:
        pass

    return info


def infer_dtype(ws, col_idx, max_row):
    """Infer column data type from first few non-empty data cells."""
    types_seen = set()
    for r in range(2, min(max_row + 1, 12)):  # sample up to 10 rows
        cell = ws.cell(row=r, column=col_idx)
        v = cell.value
        if v is None:
            continue
        if isinstance(v, datetime):
            types_seen.add("Date")
        elif isinstance(v, bool):
            types_seen.add("Boolean")
        elif isinstance(v, (int,)):
            types_seen.add("Integer")
        elif isinstance(v, float):
            types_seen.add("Decimal")
        elif isinstance(v, str):
            # Check if it looks like a date string
            if re.match(r"^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}$", v):
                types_seen.add("Date")
            elif re.match(r"^\d{1,2}-\d{2}$", v):
                types_seen.add("Text (MM-YY)")
            else:
                types_seen.add("Text")
        # Check if cell has formula
        if cell.data_type == "f":
            types_seen.add("Formula")
    if not types_seen:
        return "Empty"
    if "Formula" in types_seen:
        return "Formula/Calculated"
    if len(types_seen) == 1:
        return types_seen.pop()
    return " / ".join(sorted(types_seen))


def get_sample_value(ws, col_idx):
    """Get first non-empty sample value from a column."""
    for r in range(2, min((ws.max_row or 1) + 1, 7)):
        v = ws.cell(row=r, column=col_idx).value
        if v is not None:
            s = str(v)
            return s[:60] if len(s) > 60 else s
    return ""


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------
FONT_TITLE = Font(name="Calibri", size=16, bold=True, color=NAVY)
FONT_SUBTITLE = Font(name="Calibri", size=10, italic=True, color=GRAY_TEXT)
FONT_SECTION = Font(name="Calibri", size=12, bold=True, color=WHITE)
FONT_COL_HDR = Font(name="Calibri", size=10, bold=True, color=NAVY)
FONT_DATA = Font(name="Calibri", size=10, color=BLACK)
FONT_LINK = Font(name="Calibri", size=10, color=LINK_BLUE, underline="single")

FILL_TITLE = PatternFill(start_color=LIGHT_GOLD, end_color=LIGHT_GOLD, fill_type="solid")
FILL_SECTION = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")
FILL_COL_HDR = PatternFill(start_color=LIGHT_BLUE, end_color=LIGHT_BLUE, fill_type="solid")
FILL_ALT = PatternFill(start_color=GRAY_ALT, end_color=GRAY_ALT, fill_type="solid")
FILL_WHITE = PatternFill(start_color=WHITE, end_color=WHITE, fill_type="solid")

BORDER_BOTTOM = Border(bottom=Side(style="thin"))
ALIGN_WRAP = Alignment(wrap_text=True, vertical="top")
ALIGN_LEFT = Alignment(horizontal="left", vertical="top", wrap_text=True)


def write_title(ws, row, text, max_col=7):
    """Write title row with merge and formatting."""
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=max_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = FONT_TITLE
    cell.fill = FILL_TITLE
    cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[row].height = 30
    return row + 1


def write_subtitle(ws, row, text, max_col=7):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=max_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = FONT_SUBTITLE
    cell.alignment = Alignment(horizontal="left", vertical="center")
    return row + 1


def write_section_header(ws, row, text, max_col=7):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=max_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = FONT_SECTION
    cell.fill = FILL_SECTION
    cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[row].height = 22
    return row + 1


def write_col_headers(ws, row, headers):
    for i, h in enumerate(headers, 1):
        cell = ws.cell(row=row, column=i, value=h)
        cell.font = FONT_COL_HDR
        cell.fill = FILL_COL_HDR
        cell.border = BORDER_BOTTOM
        cell.alignment = ALIGN_WRAP
    return row + 1


def write_kv_row(ws, row, label, value, is_alt=False):
    c1 = ws.cell(row=row, column=1, value=label)
    c1.font = Font(name="Calibri", size=10, bold=True, color=NAVY)
    c1.alignment = ALIGN_LEFT
    ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=7)
    c2 = ws.cell(row=row, column=2, value=value)
    c2.font = FONT_DATA
    c2.alignment = ALIGN_LEFT
    if is_alt:
        for col in range(1, 8):
            ws.cell(row=row, column=col).fill = FILL_ALT
    return row + 1


def write_data_row(ws, row, values, is_alt=False):
    for i, v in enumerate(values, 1):
        cell = ws.cell(row=row, column=i, value=v)
        cell.font = FONT_DATA
        cell.alignment = ALIGN_WRAP
        if is_alt:
            cell.fill = FILL_ALT
        else:
            cell.fill = FILL_WHITE
    return row + 1


def auto_fit_columns(ws, min_width=15, max_width=80):
    for col_idx in range(1, (ws.max_column or 1) + 1):
        max_len = min_width
        col_letter = get_column_letter(col_idx)
        for row_idx in range(1, min((ws.max_row or 1) + 1, 200)):
            cell = ws.cell(row=row_idx, column=col_idx)
            if cell.value:
                max_len = max(max_len, min(len(str(cell.value)), max_width))
        ws.column_dimensions[col_letter].width = min(max_len + 2, max_width)


# ---------------------------------------------------------------------------
# Main injection logic
# ---------------------------------------------------------------------------
def inject_ai_context_sheet(wb_path, wb_entry, scripts_json, visual_mapping, dry_run=False, verbose=False):
    """Inject AI_Context_Reference into a single workbook. Returns result dict."""
    result = {
        "workbook": wb_entry["name"],
        "status": "❌ Error",
        "sheets": 0,
        "tables": 0,
        "vba_modules": "N/A",
        "m_code": "",
        "reason": "",
    }

    if not wb_path.exists():
        result["status"] = "⚠️ Skipped"
        result["reason"] = f"File not found: {wb_path}"
        return result

    is_xlsm = wb_path.suffix.lower() == ".xlsm"

    try:
        wb = openpyxl.load_workbook(str(wb_path), keep_vba=is_xlsm, data_only=False)
    except Exception as e:
        result["status"] = "❌ Error"
        result["reason"] = f"Cannot open: {e}"
        return result

    # Analyze
    try:
        info = analyze_workbook(wb_path, wb)
    except Exception as e:
        result["status"] = "❌ Error"
        result["reason"] = f"Analysis failed: {e}"
        wb.close()
        return result

    result["sheets"] = len(info["sheets"])
    result["tables"] = len(info["tables"])
    if is_xlsm:
        result["vba_modules"] = "VBA present (inspection requires xlwings/COM)"

    # M code mapping
    mc = M_CODE_MAP.get(wb_entry["name"], {})
    m_code_files = mc.get("m_code", [])
    result["m_code"] = ", ".join(m_code_files) if m_code_files else "None"

    # ETL scripts
    etl_scripts = find_etl_scripts_for_workbook(wb_entry["name"], scripts_json)
    python_etl = mc.get("python_etl", "")
    if not python_etl and etl_scripts:
        python_etl = "; ".join(f"{s['name']} ({s.get('script','')})" for s in etl_scripts[:3])
    if not python_etl:
        python_etl = "None — direct Power Query load"

    # Visuals
    visuals = find_visuals_for_workbook(wb_entry["name"], visual_mapping)
    visual_names = [v["visual_name"] for v in visuals]

    if dry_run:
        result["status"] = "🔍 Dry Run"
        result["reason"] = "Would inject AI_Context_Reference"
        if verbose:
            print(f"  Sheets: {[s['name'] for s in info['sheets']]}")
            print(f"  Tables: {[t['name'] for t in info['tables']]}")
            print(f"  M Code: {m_code_files}")
            print(f"  ETL: {python_etl}")
            print(f"  Visuals: {visual_names[:5]}")
            for ws_name, cols in info["columns"].items():
                nbsp_cols = [c["name"] for c in cols if c.get("has_nbsp")]
                if nbsp_cols:
                    print(f"  ⚠ Non-breaking spaces in '{ws_name}': {nbsp_cols}")
        wb.close()
        return result

    # Remove existing AI_Context_Reference if present
    if "AI_Context_Reference" in wb.sheetnames:
        del wb["AI_Context_Reference"]

    # Create new sheet
    ws = wb.create_sheet("AI_Context_Reference")
    ws.sheet_properties.tabColor = GOLD
    MAX_COL = 7

    # --- SECTION: Title ---
    row = 1
    row = write_title(ws, row, f"{wb_entry['name']} — AI & ETL Context Architecture", MAX_COL)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    row = write_subtitle(ws, row, f"Generated: {timestamp} | Hackensack PD Compstat Pipeline", MAX_COL)
    row += 1  # blank separator

    # --- SECTION 1: OVERVIEW ---
    row = write_section_header(ws, row, "1. OVERVIEW", MAX_COL)
    tier_label = f"Tier {wb_entry['tier']}"
    role = f"{tier_label} — {'Staff Data Entry → Power BI via M Code' if wb_entry['tier'] == 1 else 'ETL Output / Reference'}"

    overview_items = [
        ("Purpose", wb_entry["purpose"]),
        ("File Format", wb_path.suffix + (" (macro-enabled)" if is_xlsm else "")),
        ("Pipeline Role", role),
        ("OneDrive Path", str(wb_path)),
        ("Consuming M Code", ", ".join(m_code_files) if m_code_files else "None"),
        ("Python ETL", python_etl),
        ("Power BI Page(s)", ", ".join(mc.get("pages", ["(Unknown)"]))),
        ("13-Month Window", "Yes — pReportMonth driven | Standard pattern" if m_code_files else "N/A"),
    ]
    for i, (label, value) in enumerate(overview_items):
        row = write_kv_row(ws, row, label, value, is_alt=(i % 2 == 1))
    row += 1

    # --- SECTION 2: SHEET & TABLE DIRECTORY ---
    row = write_section_header(ws, row, "2. SHEET & TABLE DIRECTORY", MAX_COL)
    row = write_col_headers(ws, row, ["Sheet Name", "Visibility", "Table Name(s)", "Row Count", "Column Count", "Notes", ""])

    for i, sh in enumerate(info["sheets"]):
        notes = ""
        if sh["name"] in info["protected_sheets"]:
            notes = "Protected"
        if any(c.get("has_nbsp") for c in info["columns"].get(sh["name"], [])):
            notes += (" | " if notes else "") + "Has \\xa0 in headers"
        table_str = ", ".join(sh["tables"]) if sh["tables"] else "—"
        row = write_data_row(ws, row, [
            sh["name"], sh["visibility"], table_str,
            sh["rows"], sh["cols"], notes, ""
        ], is_alt=(i % 2 == 1))
    row += 1

    # --- SECTION 3: DATA DICTIONARY ---
    row = write_section_header(ws, row, "3. DATA DICTIONARY & VALIDATION", MAX_COL)
    row = write_col_headers(ws, row, ["Column Name", "Data Type", "Sample Value", "Validation/Dropdown", "Dropdown Source", "Formula Dependencies", "Notes"])

    data_row_idx = 0
    for ws_name, cols in info["columns"].items():
        # Sub-header for each sheet
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=MAX_COL)
        cell = ws.cell(row=row, column=1, value=f"— {ws_name} —")
        cell.font = Font(name="Calibri", size=10, bold=True, italic=True, color=NAVY)
        row += 1
        for col_info in cols:
            notes = ""
            if col_info.get("has_nbsp"):
                notes = "Contains non-breaking space (\\xa0)"
            row = write_data_row(ws, row, [
                col_info["name"],
                col_info["dtype"],
                col_info["sample"],
                col_info.get("validation", ""),
                col_info.get("dropdown_source", ""),
                "",
                notes,
            ], is_alt=(data_row_idx % 2 == 1))
            data_row_idx += 1
    row += 1

    # --- SECTION 4: ETL & INTEGRATION MAP ---
    row = write_section_header(ws, row, "4. ETL & INTEGRATION MAP", MAX_COL)
    etl_items = [
        ("M Code Query", ", ".join(m_code_files) if m_code_files else "None"),
        ("M Code Source Pattern", f'Excel.Workbook(File.Contents("{wb_path}"), null, true)' if m_code_files else "N/A"),
        ("Target Sheet/Table", mc.get("sheet_target", "Unknown")),
        ("Month Column Format", mc.get("month_format", "Unknown")),
        ("Rolling Window", "pReportMonth → EndOfMonth(pReportMonth) back 12 months" if m_code_files else "N/A"),
        ("Python ETL Script", python_etl),
        ("Output CSV Pattern", "; ".join(s.get("output_patterns", ["N/A"])[0] for s in etl_scripts[:3]) if etl_scripts else "N/A"),
        ("Downstream Power BI Visuals", "; ".join(visual_names[:5]) if visual_names else "None mapped"),
    ]
    for i, (label, value) in enumerate(etl_items):
        row = write_kv_row(ws, row, label, value, is_alt=(i % 2 == 1))
    row += 1

    # --- SECTION 5: VBA & MACROS (only for .xlsm) ---
    if is_xlsm:
        row = write_section_header(ws, row, "5. VBA & MACROS", MAX_COL)
        row = write_col_headers(ws, row, ["Module Name", "Type", "Purpose", "Triggers", "", "", ""])
        row = write_data_row(ws, row, [
            "(VBA project present)", "Standard/Class/UserForm",
            "Inspection requires xlwings or COM automation",
            "—", "", "", ""
        ])
        row += 1

    # --- SECTION 6: CLAUDE IN EXCEL QUICK START ---
    row = write_section_header(ws, row, "6. CLAUDE IN EXCEL — QUICK START", MAX_COL)
    table_names = [t["name"] for t in info["tables"]]
    gotchas = []
    for ws_name, cols in info["columns"].items():
        nbsp_cols = [c["name"] for c in cols if c.get("has_nbsp")]
        if nbsp_cols:
            gotchas.append(f"Non-breaking spaces in headers on '{ws_name}': {nbsp_cols}")
    if info["protected_sheets"]:
        gotchas.append(f"Protected sheets: {info['protected_sheets']}")
    if is_xlsm:
        gotchas.append("Macro-enabled workbook — use keep_vba=True when saving with openpyxl")

    related = RELATED_DOCS.get(wb_entry["name"], [])

    qs_items = [
        ("Workbook Purpose", wb_entry["purpose"]),
        ("Key Tables", ", ".join(table_names) if table_names else "No structured tables found"),
        ("Month Key Format", mc.get("month_format", "Unknown")),
        ("Common Formulas", "Check individual sheets for XLOOKUP / VLOOKUP / INDEX-MATCH patterns"),
        ("Protected Ranges", ", ".join(info["protected_sheets"]) if info["protected_sheets"] else "None detected"),
        ("Validation Rules", "See Data Dictionary section above for per-column details"),
        ("Gotchas", "; ".join(gotchas) if gotchas else "None detected"),
        ("Related Docs", "; ".join(related) if related else "See docs/ in 06_Workspace_Management"),
    ]
    for i, (label, value) in enumerate(qs_items):
        row = write_kv_row(ws, row, label, value, is_alt=(i % 2 == 1))

    # --- Final formatting ---
    ws.freeze_panes = "A4"
    ws.sheet_view.showGridLines = False
    auto_fit_columns(ws)

    # Save
    try:
        wb.save(str(wb_path))
        result["status"] = "✅ Injected"
    except PermissionError:
        result["status"] = "⚠️ Skipped"
        result["reason"] = "File is open in another application or permission denied"
    except Exception as e:
        result["status"] = "❌ Error"
        result["reason"] = str(e)
    finally:
        wb.close()

    return result


# ---------------------------------------------------------------------------
# Resolve workbook paths
# ---------------------------------------------------------------------------
def resolve_path(entry):
    if "path" in entry:
        return Path(entry["path"])
    subfolder = entry.get("subfolder", "")
    if subfolder:
        return CONTRIBUTIONS_DIR / subfolder / entry["name"]
    return CONTRIBUTIONS_DIR / entry["name"]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Inject AI_Context_Reference into HPD shared workbooks")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--tier2", action="store_true", help="Include Tier 2 workbooks")
    parser.add_argument("--workbook", type=str, help="Filter to a single workbook (substring match)")
    parser.add_argument("--verbose", action="store_true", help="Detailed logging")
    args = parser.parse_args()

    print("=" * 72)
    print("  AI_Context_Reference Sheet Injector — Hackensack PD Compstat")
    print(f"  {'DRY RUN MODE' if args.dry_run else 'LIVE MODE'}")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 72)

    # Load configs
    scripts_json = load_scripts_json()
    visual_mapping = load_visual_export_mapping()
    if scripts_json:
        print(f"  Loaded scripts.json: {len(scripts_json.get('scripts', []))} scripts")
    if visual_mapping:
        print(f"  Loaded visual_export_mapping.json: {len(visual_mapping.get('mappings', []))} mappings")
    print()

    # Build workbook list
    workbooks = list(TIER1_WORKBOOKS)
    if args.tier2:
        workbooks.extend(TIER2_WORKBOOKS)

    if args.workbook:
        pattern = args.workbook.lower()
        workbooks = [w for w in workbooks if pattern in w["name"].lower()]
        if not workbooks:
            print(f"  No workbooks matched filter '{args.workbook}'")
            sys.exit(1)

    print(f"  Target workbooks: {len(workbooks)}")
    print(f"  Contributions dir: {CONTRIBUTIONS_DIR}")
    print()

    results = []
    for entry in workbooks:
        wb_path = resolve_path(entry)
        label = f"[{entry['id']:>2}] {entry['name']}"
        print(f"  Processing {label} ...")
        if args.verbose:
            print(f"      Path: {wb_path}")

        r = inject_ai_context_sheet(wb_path, entry, scripts_json, visual_mapping,
                                    dry_run=args.dry_run, verbose=args.verbose)
        results.append(r)
        status = r["status"]
        print(f"      → {status}" + (f" ({r['reason']})" if r["reason"] else ""))
        print()

    # Summary table
    print()
    print("=" * 110)
    print(f"  {'Workbook':<42} {'Status':<16} {'Sheets':>6} {'Tables':>7} {'VBA':>10} {'M Code':<30}")
    print("-" * 110)
    for r in results:
        print(f"  {r['workbook']:<42} {r['status']:<16} {r['sheets']:>6} {r['tables']:>7} {str(r['vba_modules'])[:10]:>10} {r['m_code'][:30]:<30}")
    print("=" * 110)

    ok = sum(1 for r in results if "Injected" in r["status"] or "Dry Run" in r["status"])
    skip = sum(1 for r in results if "Skipped" in r["status"])
    err = sum(1 for r in results if "Error" in r["status"])
    print(f"\n  Total: {len(results)} | Success: {ok} | Skipped: {skip} | Errors: {err}")

    if any(r["reason"] for r in results):
        print("\n  Notes:")
        for r in results:
            if r["reason"]:
                print(f"    {r['workbook']}: {r['reason']}")


if __name__ == "__main__":
    main()

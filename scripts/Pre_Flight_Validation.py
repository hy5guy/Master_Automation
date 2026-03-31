#!/usr/bin/env python3
# 2026-02-21-00-38-24 (EST)
# Project Name: Hackensack PD | Data Ops & ETL Remediation
# File Name: scripts/Pre_Flight_Validation.py
# Author: R. A. Carucci
# Purpose: Pre-flight validation gate for monthly ETL cycle — checks source data, config, personnel, and visual export mapping before orchestrator run.

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from path_config import get_onedrive_root

MONTH_NAMES = {
    1: "january", 2: "february", 3: "march", 4: "april",
    5: "may", 6: "june", 7: "july", 8: "august",
    9: "september", 10: "october", 11: "november", 12: "december",
}

MIN_CSV_BYTES = 100
MIN_EXCEL_BYTES = 1024


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pre-flight validation for monthly ETL cycle")
    parser.add_argument(
        "--report-month",
        required=True,
        help="Report month in YYYY-MM format (e.g. 2026-01)",
    )
    args = parser.parse_args()
    parts = args.report_month.split("-")
    if len(parts) != 2:
        parser.error("--report-month must be YYYY-MM")
    try:
        args.year = int(parts[0])
        args.month = int(parts[1])
    except ValueError:
        parser.error("--report-month must be YYYY-MM with numeric values")
    if not 1 <= args.month <= 12:
        parser.error("Month must be between 01 and 12")
    return args


def file_evidence(path: Path) -> dict:
    """Return size and row-count evidence for a file."""
    info: dict = {"size_bytes": 0, "data_rows": None}
    if not path.is_file():
        return info
    info["size_bytes"] = path.stat().st_size
    if path.suffix.lower() == ".csv":
        try:
            with open(path, newline="", encoding="utf-8-sig") as fh:
                reader = csv.reader(fh)
                row_count = sum(1 for _ in reader)
                info["data_rows"] = max(row_count - 1, 0)
        except Exception:
            pass
    return info


def check_file(path: Path, name: str, severity: str = "FAIL") -> dict:
    """Check existence and size of a single file. severity is FAIL or WARN."""
    result = {"name": name, "status": "PASS", "path": str(path), "detail": ""}

    if not path.exists():
        result["status"] = severity
        result["detail"] = "MISSING"
        return result

    evidence = file_evidence(path)
    size = evidence["size_bytes"]
    suffix = path.suffix.lower()

    if path.is_file():
        threshold = MIN_EXCEL_BYTES if suffix in (".xlsx", ".xls") else MIN_CSV_BYTES
        if size < threshold:
            result["status"] = severity
            result["detail"] = f"File too small ({size} bytes, minimum {threshold})"
            return result

    detail_parts = [f"size={size}B"]
    if evidence["data_rows"] is not None:
        detail_parts.append(f"data_rows={evidence['data_rows']}")
        if evidence["data_rows"] < 1:
            result["status"] = severity
            result["detail"] = "CSV has no data rows"
            return result

    result["detail"] = ", ".join(detail_parts)
    return result


def check_eticket(root: Path, year: int, month: int) -> dict:
    """E-Ticket: WARN if both .csv and .xlsx are missing."""
    yyyy_mm = f"{year}_{month:02d}"
    base = root / "05_EXPORTS" / "_Summons" / "E_Ticket" / str(year) / "month"

    csv_path = base / f"{yyyy_mm}_eticket_export.csv"
    xlsx_path = base / f"{yyyy_mm}_eticket_export.xlsx"

    for p in (csv_path, xlsx_path):
        if p.exists():
            return check_file(p, "E-Ticket Summons Source", severity="WARN")

    return {
        "name": "E-Ticket Summons Source",
        "status": "WARN",
        "path": str(base),
        "detail": f"Neither .csv nor .xlsx found for {yyyy_mm}",
    }


def check_visual_export_mapping(master_path: Path) -> dict:
    mapping_path = master_path / "Standards" / "config" / "powerbi_visuals" / "visual_export_mapping.json"
    result = {"name": "Visual Export Mapping", "status": "PASS", "path": str(mapping_path), "detail": ""}

    if not mapping_path.is_file():
        result["status"] = "FAIL"
        result["detail"] = "MISSING"
        return result

    try:
        with open(mapping_path, encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as exc:
        result["status"] = "FAIL"
        result["detail"] = f"JSON parse error: {exc}"
        return result

    mappings = data.get("mappings", [])
    total = len(mappings)
    enforced = sum(1 for m in mappings if m.get("enforce_13_month_window") is True)

    detail_parts = [f"total={total}", f"13-month enforced={enforced}"]

    if total < 30:
        result["status"] = "WARN"
        detail_parts.append(f"total mappings {total} seems low")

    result["detail"] = ", ".join(detail_parts)

    return result


def check_personnel(root: Path) -> dict:
    """Validate Assignment_Master_V2.csv: existence, columns, row count."""
    personnel_path = root / "09_Reference" / "Personnel" / "Assignment_Master_V2.csv"
    result = {"name": "Personnel File (Assignment_Master_V2.csv)", "status": "PASS",
              "path": str(personnel_path), "detail": ""}

    if not personnel_path.is_file():
        result["status"] = "FAIL"
        result["detail"] = "MISSING"
        return result

    required_cols = {"BADGE_NUMBER", "LAST_NAME", "FIRST_NAME", "WG2", "RANK"}
    try:
        with open(personnel_path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.reader(fh)
            header = next(reader, None)
            if header is None:
                result["status"] = "FAIL"
                result["detail"] = "Empty file (no header)"
                return result
            data_rows = sum(1 for _ in reader)
    except Exception as exc:
        result["status"] = "FAIL"
        result["detail"] = f"Read error: {exc}"
        return result

    header_set = {h.strip() for h in header}
    missing_cols = required_cols - header_set
    detail_parts = [f"data_rows={data_rows}"]

    if missing_cols:
        result["status"] = "FAIL"
        detail_parts.append(f"missing columns: {', '.join(sorted(missing_cols))}")
    if data_rows < 50:
        result["status"] = "FAIL"
        detail_parts.append(f"row count {data_rows} below minimum 50")

    result["detail"] = ", ".join(detail_parts)
    return result


def validate_system(year: int, month: int) -> bool:
    root = get_onedrive_root()
    workspace_path = root / "06_Workspace_Management"
    drop_folder = root / "PowerBI_Data" / "_DropExports"
    yyyy_mm = f"{year}_{month:02d}"
    month_name = MONTH_NAMES[month]

    print(f"--- PRE-FLIGHT AUDIT: 06_Workspace_Management ---")
    print(f"Report Month : {year}-{month:02d}")
    print(f"Target Root  : {root}\n")

    results: list[dict] = []

    results.append(check_personnel(root))

    results.append(check_file(
        workspace_path / "config" / "scripts.json",
        "ETL Orchestrator Config",
    ))

    results.append(check_eticket(root, year, month))

    results.append(check_file(
        root / "05_EXPORTS" / "_CAD" / "timereport" / "monthly" / f"{yyyy_mm}_timereport.xlsx",
        "Response Time Source (CAD timereport)",
    ))

    # ATS file — advisory only
    results.append(check_file(
        root / "05_EXPORTS" / "_ATS" / f"{yyyy_mm}_ats_export.csv",
        "ATS Export",
        severity="WARN",
    ))

    results.append(check_file(drop_folder, "Power BI Drop Folder Access"))

    results.append(check_visual_export_mapping(workspace_path))

    # Arrest exports: 05_EXPORTS/_Arrest/{YYYY}/month/{YYYY}_{MM}_*.xlsx
    arrest_base = root / "05_EXPORTS" / "_Arrest" / str(year) / "month"
    if arrest_base.is_dir():
        arrest_files = list(arrest_base.glob(f"{yyyy_mm}_*.xlsx")) + list(arrest_base.glob(f"{yyyy_mm}_*.csv"))
        results.append({
            "name": "Arrest Exports",
            "status": "PASS" if arrest_files else "WARN",
            "path": str(arrest_base),
            "detail": f"{len(arrest_files)} files found" if arrest_files else f"No {yyyy_mm}_* files",
        })
    else:
        results.append({
            "name": "Arrest Exports",
            "status": "WARN",
            "path": str(arrest_base),
            "detail": f"Directory not found: {arrest_base}",
        })

    # Overtime exports: 05_EXPORTS/_Overtime/export/month/{YYYY}/{YYYY}_{MM}_otactivity.*
    ot_base = root / "05_EXPORTS" / "_Overtime" / "export" / "month" / str(year)
    ot_files = list(ot_base.glob(f"{yyyy_mm}_otactivity.*")) if ot_base.is_dir() else []
    if ot_files:
        results.append({
            "name": "Overtime Export",
            "status": "PASS",
            "path": str(ot_files[0]),
            "detail": f"size={ot_files[0].stat().st_size}B",
        })
    elif ot_base.is_dir():
        results.append({
            "name": "Overtime Export",
            "status": "WARN",
            "path": str(ot_base),
            "detail": f"No {yyyy_mm}_otactivity.* found",
        })
    else:
        results.append({
            "name": "Overtime Export",
            "status": "WARN",
            "path": str(ot_base),
            "detail": f"Year directory not found",
        })

    # TimeOff exports: 05_EXPORTS/_Time_Off/export/month/{YYYY}/{YYYY}_{MM}_timeoffactivity.*
    to_base = root / "05_EXPORTS" / "_Time_Off" / "export" / "month" / str(year)
    to_files = list(to_base.glob(f"{yyyy_mm}_timeoffactivity.*")) if to_base.is_dir() else []
    if to_files:
        results.append({
            "name": "TimeOff Export",
            "status": "PASS",
            "path": str(to_files[0]),
            "detail": f"size={to_files[0].stat().st_size}B",
        })
    elif to_base.is_dir():
        results.append({
            "name": "TimeOff Export",
            "status": "WARN",
            "path": str(to_base),
            "detail": f"No {yyyy_mm}_timeoffactivity.* found",
        })
    else:
        results.append({
            "name": "TimeOff Export",
            "status": "WARN",
            "path": str(to_base),
            "detail": f"Year directory not found",
        })

    # Community Engagement — config-driven from Shared Folder workbooks (not file-based exports)
    ce_config = root / "02_ETL_Scripts" / "Community_Engagement" / "config.json"
    if ce_config.is_file():
        results.append({
            "name": "Community Engagement Config",
            "status": "PASS",
            "path": str(ce_config),
            "detail": f"size={ce_config.stat().st_size}B",
        })
    else:
        results.append({
            "name": "Community Engagement Config",
            "status": "WARN",
            "path": str(ce_config),
            "detail": "config.json not found",
        })

    fails = sum(1 for r in results if r["status"] == "FAIL")
    warnings = sum(1 for r in results if r["status"] == "WARN")

    for r in results:
        tag = r["status"].ljust(4)
        detail = f" — {r['detail']}" if r["detail"] else ""
        print(f"[{tag}] {r['name']}{detail}")

    gate = "GO" if fails == 0 else "NO-GO"

    print(f"\n--- Audit Summary ---")
    print(f"Gate     : {gate}")
    print(f"Failures : {fails}")
    print(f"Warnings : {warnings}")

    summary = {
        "gate": gate,
        "fails": fails,
        "warnings": warnings,
        "checks": results,
    }
    print("\n" + json.dumps(summary, indent=2))

    return fails == 0


if __name__ == "__main__":
    args = parse_args()
    if not validate_system(args.year, args.month):
        sys.exit(1)

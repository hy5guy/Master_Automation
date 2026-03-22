#!/usr/bin/env python3
"""
Visual Data Verifier

Validates that every Power BI visual defined in visual_export_mapping.json
has a corresponding, non-empty source data file. Also checks 13-month window
compliance for visuals that enforce it.

Used as Phase 3 of the powerbi_visual_validator orchestrator.

Version: 1.0.0
Created: 2026-03-14
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

# Resolve paths
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
MAPPING_PATH = REPO_ROOT / "Standards" / "config" / "powerbi_visuals" / "visual_export_mapping.json"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
try:
    from path_config import get_onedrive_root
except ImportError:
    def get_onedrive_root() -> Path:
        return Path.home() / "OneDrive - City of Hackensack"

try:
    from validate_13_month_window import validate_file as validate_13m_window
except ImportError:
    validate_13m_window = None


MIN_FILE_BYTES = 50  # Minimum file size to consider non-empty


def load_visual_mapping() -> List[Dict]:
    """Load visual export mapping configuration."""
    if not MAPPING_PATH.exists():
        raise FileNotFoundError(f"Visual mapping not found: {MAPPING_PATH}")
    with open(MAPPING_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("mappings", [])


def find_visual_source_file(
    mapping: Dict,
    backfill_root: Path,
    drop_exports: Path,
    report_month: str,
) -> Tuple[str, Path | None]:
    """
    Locate the source data file for a visual using the backfill priority chain:
    Backfill > _DropExports.

    Args:
        mapping: Single visual mapping entry from visual_export_mapping.json
        backfill_root: Path to PowerBI_Date/Backfill/
        drop_exports: Path to PowerBI_Date/_DropExports/
        report_month: Report month in YYYY_MM format

    Returns:
        (source_location, file_path) — source_location is "backfill", "drop_exports", or "NOT_FOUND"
    """
    std_name = mapping.get("standardized_filename", "")
    target_folder = mapping.get("target_folder", mapping.get("normalized_folder", ""))
    backfill_folder = mapping.get("backfill_folder", target_folder)

    if not std_name:
        return ("NOT_FOUND", None)

    # Priority 1: Backfill folder for the report month
    backfill_dir = backfill_root / report_month / backfill_folder
    if backfill_dir.exists():
        # Try exact match and prefix match
        for pattern in [f"*{std_name}*", f"{report_month}_{std_name}*"]:
            matches = list(backfill_dir.glob(pattern))
            csv_matches = [m for m in matches if m.suffix.lower() == ".csv"]
            if csv_matches:
                return ("backfill", csv_matches[0])

    # Priority 2: _DropExports
    if drop_exports.exists():
        for pattern in [f"*{std_name}*"]:
            matches = list(drop_exports.glob(pattern))
            csv_matches = [m for m in matches if m.suffix.lower() == ".csv"]
            if csv_matches:
                return ("drop_exports", csv_matches[0])

    return ("NOT_FOUND", None)


def check_file_health(file_path: Path) -> Dict:
    """
    Run basic health checks on a data file.

    Returns:
        Dict with keys: is_healthy, size_bytes, row_count, issues
    """
    result = {
        "is_healthy": False,
        "size_bytes": 0,
        "row_count": 0,
        "issues": [],
    }

    if not file_path.exists():
        result["issues"].append("File does not exist")
        return result

    result["size_bytes"] = file_path.stat().st_size

    if result["size_bytes"] < MIN_FILE_BYTES:
        result["issues"].append(f"File too small ({result['size_bytes']} bytes)")
        return result

    try:
        df = pd.read_csv(file_path, encoding="utf-8-sig", nrows=5)
        if df.empty:
            result["issues"].append("File has no data rows")
            return result

        # Count all rows
        df_full = pd.read_csv(file_path, encoding="utf-8-sig")
        result["row_count"] = len(df_full)

        if result["row_count"] == 0:
            result["issues"].append("File has 0 data rows")
            return result

        result["is_healthy"] = True

    except Exception as e:
        result["issues"].append(f"Failed to read CSV: {e}")

    return result


def verify_all_visuals(
    report_month: str,
) -> Dict:
    """
    Verify all mapped visuals have valid source data files.

    Args:
        report_month: Report month in YYYY_MM format (e.g. "2026_02")

    Returns:
        Dict with keys: status, total, found, missing, window_pass, window_fail,
                        details, issues
    """
    mappings = load_visual_mapping()
    onedrive_root = get_onedrive_root()

    # Resolve key directories
    powerbi_date = onedrive_root / "00_dev" / "projects" / "PowerBI_Date"
    if not powerbi_date.exists():
        # Try alternate location
        powerbi_date = onedrive_root / "PowerBI_Date"

    backfill_root = powerbi_date / "Backfill"
    drop_exports = powerbi_date / "_DropExports"

    results = {
        "status": "PENDING",
        "total": len(mappings),
        "found": 0,
        "missing": 0,
        "window_pass": 0,
        "window_fail": 0,
        "window_skipped": 0,
        "details": [],
        "issues": [],
    }

    for mapping in mappings:
        visual_name = mapping.get("visual_name", "Unknown")
        page_name = mapping.get("page_name", "Unknown")
        enforce_window = mapping.get("enforce_13_month_window", False)
        is_backfill_required = mapping.get("is_backfill_required", False)

        # Find the source file
        source_location, file_path = find_visual_source_file(
            mapping, backfill_root, drop_exports, report_month
        )

        detail = {
            "visual_name": visual_name,
            "page_name": page_name,
            "source_location": source_location,
            "file_path": str(file_path) if file_path else None,
            "file_healthy": False,
            "window_status": "N/A",
            "issues": [],
        }

        if source_location == "NOT_FOUND":
            if is_backfill_required:
                detail["issues"].append("Required backfill file not found")
                results["missing"] += 1
            else:
                # Non-backfill visuals may not have files yet
                detail["issues"].append("Source file not found (non-critical)")
                results["missing"] += 1
        else:
            results["found"] += 1

            # Check file health
            health = check_file_health(file_path)
            detail["file_healthy"] = health["is_healthy"]
            detail["row_count"] = health["row_count"]
            detail["size_bytes"] = health["size_bytes"]
            if health["issues"]:
                detail["issues"].extend(health["issues"])

            # Check 13-month window if required
            if enforce_window and validate_13m_window and file_path:
                try:
                    window_status, window_msg = validate_13m_window(file_path)
                    detail["window_status"] = window_status
                    detail["window_message"] = window_msg
                    if window_status == "PASS":
                        results["window_pass"] += 1
                    else:
                        results["window_fail"] += 1
                        detail["issues"].append(f"13-month window: {window_msg}")
                except Exception as e:
                    detail["window_status"] = "ERROR"
                    detail["issues"].append(f"Window validation error: {e}")
                    results["window_fail"] += 1
            elif enforce_window:
                results["window_skipped"] += 1
                detail["window_status"] = "SKIPPED"

        results["details"].append(detail)

    # Determine overall status
    critical_missing = sum(
        1 for d in results["details"]
        if d["source_location"] == "NOT_FOUND"
        and any("Required" in i for i in d["issues"])
    )

    unhealthy = sum(
        1 for d in results["details"]
        if d["source_location"] != "NOT_FOUND" and not d["file_healthy"]
    )

    if critical_missing > 0 or unhealthy > 0:
        results["status"] = "FAIL"
        if critical_missing:
            results["issues"].append(f"{critical_missing} required visual(s) missing source data")
        if unhealthy:
            results["issues"].append(f"{unhealthy} visual source file(s) are unhealthy")
    elif results["window_fail"] > 0:
        results["status"] = "FAIL"
        results["issues"].append(f"{results['window_fail']} visual(s) failed 13-month window check")
    else:
        results["status"] = "PASS"

    return results


def print_summary(results: Dict) -> None:
    """Print a human-readable summary of verification results."""
    print(f"\n  Visual-Data Mapping Verification")
    print(f"  {'='*50}")
    print(f"  Total visuals mapped:    {results['total']}")
    print(f"  Source files found:      {results['found']}")
    print(f"  Source files missing:    {results['missing']}")

    window_checked = results["window_pass"] + results["window_fail"]
    if window_checked > 0:
        print(f"  13-month window PASS:    {results['window_pass']}")
        print(f"  13-month window FAIL:    {results['window_fail']}")

    print(f"  Status:                  {results['status']}")

    if results["issues"]:
        print(f"\n  Issues:")
        for issue in results["issues"]:
            print(f"    - {issue}")


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Verify Power BI visual-to-data mappings")
    parser.add_argument(
        "--report-month",
        required=True,
        help="Report month in YYYY_MM format (e.g. 2026_02)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Show per-visual details")
    args = parser.parse_args()

    # Normalize month format
    report_month = args.report_month.replace("-", "_")

    try:
        results = verify_all_visuals(report_month)
    except (FileNotFoundError, ValueError) as e:
        print(f"[ERROR] {e}")
        return 1

    print_summary(results)

    if args.verbose:
        print(f"\n  Per-Visual Details:")
        print(f"  {'-'*70}")
        for d in results["details"]:
            status_icon = "OK" if d["file_healthy"] else "!!"
            print(f"  [{status_icon}] {d['visual_name']} ({d['page_name']})")
            print(f"       Source: {d['source_location']} -> {d['file_path'] or 'N/A'}")
            if d["issues"]:
                for issue in d["issues"]:
                    print(f"       Issue: {issue}")

    return 0 if results["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())

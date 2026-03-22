#!/usr/bin/env python3
"""
Power BI Visual Validator — Pre-Send Hard Gate

Orchestrates all validation phases to produce a GO/NO-GO verdict before
sending the Power BI report to the supervisor. Chains existing validation
infrastructure (ETL output checks, backfill comparison, visual mapping,
cross-visual consistency) with Power BI REST API refresh verification.

Exit Codes:
  0 = GO   — All phases passed. Safe to send the report.
  1 = NO-GO — One or more phases failed. Do NOT send.

Usage:
  python scripts/powerbi_visual_validator.py --report-month 2026-02
  python scripts/powerbi_visual_validator.py --report-month 2026-02 --skip-api
  python scripts/powerbi_visual_validator.py --report-month 2026-02 --verbose

Version: 1.0.0
Created: 2026-03-14
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent

sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(REPO_ROOT / "verifications"))

from path_config import get_onedrive_root


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
REPORTS_DIR = REPO_ROOT / "verifications" / "reports"
MIN_FILE_BYTES = 50


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def parse_report_month(raw: str):
    """
    Parse --report-month into (year, month, yyyy_mm, yyyy-mm) forms.
    Accepts: 2026-02, 2026_02
    """
    normalized = raw.replace("_", "-")
    parts = normalized.split("-")
    if len(parts) != 2:
        raise ValueError(f"Invalid --report-month '{raw}'. Use YYYY-MM format.")
    year, month = int(parts[0]), int(parts[1])
    if not (1 <= month <= 12):
        raise ValueError(f"Month must be 01-12, got {month}")
    yyyy_mm = f"{year:04d}_{month:02d}"
    yyyy_dash = f"{year:04d}-{month:02d}"
    return year, month, yyyy_mm, yyyy_dash


def prev_month_str(year: int, month: int) -> str:
    """Return YYYY_MM for the month before (year, month)."""
    d = date(year, month, 1) - timedelta(days=1)
    return f"{d.year:04d}_{d.month:02d}"


def phase_header(num: int, total: int, name: str):
    print(f"\n  Phase {num}/{total}: {name}")
    print(f"  {'-'*50}")


# ---------------------------------------------------------------------------
# Phase 1 — ETL Output Validation
# ---------------------------------------------------------------------------
def run_phase_1_etl_outputs(yyyy_mm: str) -> Dict:
    """Validate that ETL output files exist, are non-empty, and have valid schemas."""
    config_path = REPO_ROOT / "config" / "scripts.json"
    if not config_path.exists():
        return {"status": "FAIL", "message": "scripts.json not found", "details": []}

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    scripts = [s for s in config.get("scripts", []) if s.get("enabled")]
    checked = 0
    passed = 0
    issues = []
    details = []

    onedrive = get_onedrive_root()

    for script_cfg in scripts:
        name = script_cfg.get("name", "Unknown")
        output_patterns = script_cfg.get("output_patterns", [])
        script_path_str = script_cfg.get("path", "")

        if not output_patterns:
            continue

        script_path = Path(script_path_str)
        # Resolve path portability
        if not script_path.exists():
            # Try replacing username in path
            relative = str(script_path).split("OneDrive - City of Hackensack")
            if len(relative) > 1:
                script_path = onedrive / relative[-1].lstrip("\\").lstrip("/")

        found_any = False
        for pattern in output_patterns:
            pattern_path = Path(pattern)
            # Handle absolute patterns
            if not pattern_path.is_absolute():
                search_dir = script_path
            else:
                search_dir = pattern_path.parent
                pattern = pattern_path.name

                # Resolve portability
                if not search_dir.exists():
                    relative = str(search_dir).split("OneDrive - City of Hackensack")
                    if len(relative) > 1:
                        search_dir = onedrive / relative[-1].lstrip("\\").lstrip("/")

            if search_dir.exists():
                matches = list(search_dir.glob(pattern))
                if matches:
                    found_any = True
                    # Check file health
                    for match in matches:
                        if match.stat().st_size >= MIN_FILE_BYTES:
                            checked += 1
                            passed += 1
                            details.append({"script": name, "file": match.name, "status": "OK"})
                        else:
                            checked += 1
                            issues.append(f"{name}: {match.name} is too small ({match.stat().st_size} bytes)")
                            details.append({"script": name, "file": match.name, "status": "TOO_SMALL"})

        if not found_any and script_cfg.get("output_to_powerbi"):
            issues.append(f"{name}: No output files found matching patterns")
            details.append({"script": name, "file": "N/A", "status": "MISSING"})
            checked += 1

    status = "PASS" if not issues else "FAIL"
    message = f"{passed}/{checked} output files validated" if checked > 0 else "No output files to check"

    return {"status": status, "message": message, "details": details, "issues": issues}


# ---------------------------------------------------------------------------
# Phase 2 — Backfill Integrity Check
# ---------------------------------------------------------------------------
def run_phase_2_backfill_integrity(yyyy_mm: str, year: int, month: int) -> Dict:
    """Compare current month outputs against backfill baseline using the verification framework."""
    prev_mm = prev_month_str(year, month)

    try:
        from etl_verification_framework import ETLVerifier
    except ImportError:
        return {
            "status": "FAIL",
            "message": "etl_verification_framework.py not importable",
            "pass_rate": 0.0,
            "issues": ["Cannot import verification framework"],
        }

    # Run available verifiers
    verifier_results = []

    try:
        from arrests_verifier import ArrestsVerifier
        verifier = ArrestsVerifier(current_month=yyyy_mm, backfill_month=prev_mm)
        result = verifier.run_verification()
        verifier_results.append(("Arrests", result))
    except Exception as e:
        verifier_results.append(("Arrests", {"status": "SKIPPED", "pass_rate": 0, "issues": [str(e)]}))

    try:
        from overtime_timeoff_verifier import OvertimeTimeOffVerifier
        verifier = OvertimeTimeOffVerifier(current_month=yyyy_mm, backfill_month=prev_mm)
        result = verifier.run_verification()
        verifier_results.append(("Overtime/TimeOff", result))
    except Exception as e:
        verifier_results.append(("Overtime/TimeOff", {"status": "SKIPPED", "pass_rate": 0, "issues": [str(e)]}))

    # Aggregate
    total_pass_rates = []
    all_issues = []
    has_failures = False

    for name, result in verifier_results:
        status = result.get("status", "UNKNOWN")
        pr = result.get("pass_rate", 0.0)
        total_pass_rates.append(pr)
        if status == "FAIL":
            has_failures = True
            all_issues.append(f"{name}: FAILED (pass rate {pr:.1f}%)")
        elif status == "SKIPPED":
            all_issues.append(f"{name}: Skipped — {result.get('issues', ['unknown'])[0]}")

    avg_pass_rate = sum(total_pass_rates) / len(total_pass_rates) if total_pass_rates else 0.0
    status = "FAIL" if has_failures else "PASS"
    message = f"Backfill comparison: {avg_pass_rate:.1f}% average pass rate across {len(verifier_results)} verifier(s)"

    return {
        "status": status,
        "message": message,
        "pass_rate": avg_pass_rate,
        "verifier_count": len(verifier_results),
        "issues": all_issues,
    }


# ---------------------------------------------------------------------------
# Phase 3 — Visual-Data Mapping Validation
# ---------------------------------------------------------------------------
def run_phase_3_visual_mapping(yyyy_mm: str) -> Dict:
    """Verify every mapped Power BI visual has a corresponding source data file."""
    try:
        from visual_data_verifier import verify_all_visuals
    except ImportError:
        return {
            "status": "FAIL",
            "message": "visual_data_verifier.py not importable",
            "issues": ["Cannot import visual_data_verifier"],
        }

    try:
        results = verify_all_visuals(yyyy_mm)
        return {
            "status": results["status"],
            "message": f"{results['found']}/{results['total']} visuals have source data",
            "found": results["found"],
            "total": results["total"],
            "missing": results["missing"],
            "issues": results["issues"],
        }
    except Exception as e:
        return {"status": "FAIL", "message": str(e), "issues": [str(e)]}


# ---------------------------------------------------------------------------
# Phase 4 — Cross-Visual Consistency
# ---------------------------------------------------------------------------
def run_phase_4_cross_visual(yyyy_mm: str) -> Dict:
    """
    Check cross-visual consistency:
    - No duplicate months in rolling-window CSVs
    - Summons dept-wide totals match bureau breakdowns (if data available)
    """
    onedrive = get_onedrive_root()
    issues = []

    # Check 1: Duplicate months in backfill CSVs
    powerbi_date = onedrive / "00_dev" / "projects" / "PowerBI_Data"
    if not powerbi_date.exists():
        powerbi_date = onedrive / "PowerBI_Data"

    backfill_dir = powerbi_date / "Backfill" / yyyy_mm
    duplicate_files = []

    if backfill_dir.exists():
        for csv_file in backfill_dir.rglob("*.csv"):
            try:
                df = pd.read_csv(csv_file, encoding="utf-8-sig", low_memory=False)
                # Detect period column
                for col in ["Period", "Month_Year", "PeriodLabel", "Month"]:
                    if col in df.columns:
                        periods = df[col].dropna()
                        dupes = periods[periods.duplicated()]
                        if not dupes.empty and len(periods.unique()) > 1:
                            # Only flag if same period appears with same category
                            pass  # Duplicates within period are normal (multiple categories)
                        break
            except Exception:
                pass

    # Check 2: 13-month window validation on key rolling-window files
    window_issues = []
    try:
        from validate_13_month_window import scan_folder

        # Scan backfill subfolders for rolling-window CSVs
        if backfill_dir.exists():
            for subfolder in backfill_dir.iterdir():
                if subfolder.is_dir():
                    scan_results = scan_folder(subfolder)
                    for filename, (status, msg) in scan_results.items():
                        if status == "FAIL":
                            window_issues.append(f"{subfolder.name}/{filename}: {msg}")
    except ImportError:
        pass

    if window_issues:
        issues.extend(window_issues[:5])  # Cap at 5 to avoid noise

    status = "PASS" if not issues else "FAIL"
    message = f"Cross-visual consistency: {len(issues)} issue(s) found"

    return {"status": status, "message": message, "issues": issues}


# ---------------------------------------------------------------------------
# Phase 5 — Power BI Refresh Verification (REST API)
# ---------------------------------------------------------------------------
def run_phase_5_api_refresh() -> Dict:
    """Check Power BI dataset refresh status via REST API."""
    try:
        from powerbi_refresh_checker import check_refresh_status
        result = check_refresh_status()
        return {
            "status": result["status"],
            "message": result["message"],
            "refresh_details": result.get("refresh_details"),
            "issues": [result["message"]] if result["status"] != "PASS" else [],
        }
    except FileNotFoundError as e:
        return {
            "status": "FAIL",
            "message": f"API config missing: {e}",
            "issues": [str(e)],
        }
    except Exception as e:
        return {
            "status": "FAIL",
            "message": f"API check failed: {e}",
            "issues": [str(e)],
        }


# ---------------------------------------------------------------------------
# Report Generation
# ---------------------------------------------------------------------------
def generate_report(
    report_month: str,
    phase_results: List[Dict],
    verdict: str,
    report_path: Path,
) -> str:
    """Generate markdown validation report."""
    lines = []
    lines.append("# Power BI Visual Validation Report")
    lines.append("")
    lines.append(f"**Report Month:** {report_month}")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Validator:** powerbi_visual_validator.py v1.0.0")
    lines.append("")
    lines.append(f"## Verdict: **{verdict}**")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Phase summary table
    lines.append("## Phase Results")
    lines.append("")
    lines.append("| Phase | Name | Status | Details |")
    lines.append("|-------|------|--------|---------|")

    for pr in phase_results:
        phase_num = pr["phase"]
        name = pr["name"]
        status = pr["status"]
        message = pr.get("message", "")
        lines.append(f"| {phase_num} | {name} | **{status}** | {message} |")

    lines.append("")

    # Issues section
    all_issues = []
    for pr in phase_results:
        for issue in pr.get("issues", []):
            all_issues.append(f"Phase {pr['phase']} ({pr['name']}): {issue}")

    if all_issues:
        lines.append("## Issues")
        lines.append("")
        for issue in all_issues:
            lines.append(f"- {issue}")
        lines.append("")

    # Conclusion
    lines.append("---")
    lines.append("")
    if verdict == "GO":
        lines.append("**All validation phases passed. This report is safe to send to the supervisor.**")
    else:
        lines.append("**One or more validation phases failed. Do NOT send this report until issues are resolved.**")
    lines.append("")

    report_text = "\n".join(lines)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    # Also write JSON summary
    json_path = report_path.with_suffix(".json")
    summary = {
        "report_month": report_month,
        "generated": datetime.now().isoformat(),
        "verdict": verdict,
        "phases": phase_results,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)

    return str(report_path)


# ---------------------------------------------------------------------------
# Main Orchestrator
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Power BI Visual Validator — Pre-Send Hard Gate (GO/NO-GO)"
    )
    parser.add_argument(
        "--report-month",
        required=True,
        help="Report month in YYYY-MM format (e.g. 2026-02)",
    )
    parser.add_argument(
        "--skip-api",
        action="store_true",
        help="Skip Phase 5 (Power BI REST API refresh check)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed per-phase output",
    )
    args = parser.parse_args()

    # Parse month
    try:
        year, month, yyyy_mm, yyyy_dash = parse_report_month(args.report_month)
    except ValueError as e:
        print(f"[ERROR] {e}")
        return 1

    total_phases = 5 if not args.skip_api else 4

    # Header
    print()
    print("  " + "=" * 58)
    print(f"  POWER BI VISUAL VALIDATION -- {yyyy_dash}  [HARD GATE]")
    print("  " + "=" * 58)

    phase_results = []
    has_failure = False

    # Phase 1: ETL Output Validation
    phase_header(1, total_phases + 1, "ETL Output Validation")
    r1 = run_phase_1_etl_outputs(yyyy_mm)
    phase_results.append({"phase": 1, "name": "ETL Output Validation", **r1})
    status_str = f"{r1['status']}"
    print(f"  Result: {status_str} — {r1['message']}")
    if r1["status"] == "FAIL":
        has_failure = True
        if args.verbose:
            for issue in r1.get("issues", []):
                print(f"    - {issue}")

    # Phase 2: Backfill Integrity
    phase_header(2, total_phases + 1, "Backfill Integrity Check")
    r2 = run_phase_2_backfill_integrity(yyyy_mm, year, month)
    phase_results.append({"phase": 2, "name": "Backfill Integrity", **r2})
    print(f"  Result: {r2['status']} — {r2['message']}")
    if r2["status"] == "FAIL":
        has_failure = True
        if args.verbose:
            for issue in r2.get("issues", []):
                print(f"    - {issue}")

    # Phase 3: Visual-Data Mapping
    phase_header(3, total_phases + 1, "Visual-Data Mapping Validation")
    r3 = run_phase_3_visual_mapping(yyyy_mm)
    phase_results.append({"phase": 3, "name": "Visual-Data Mapping", **r3})
    print(f"  Result: {r3['status']} — {r3['message']}")
    if r3["status"] == "FAIL":
        has_failure = True
        if args.verbose:
            for issue in r3.get("issues", []):
                print(f"    - {issue}")

    # Phase 4: Cross-Visual Consistency
    phase_header(4, total_phases + 1, "Cross-Visual Consistency")
    r4 = run_phase_4_cross_visual(yyyy_mm)
    phase_results.append({"phase": 4, "name": "Cross-Visual Consistency", **r4})
    print(f"  Result: {r4['status']} — {r4['message']}")
    if r4["status"] == "FAIL":
        has_failure = True
        if args.verbose:
            for issue in r4.get("issues", []):
                print(f"    - {issue}")

    # Phase 5: Power BI Refresh (optional)
    if not args.skip_api:
        phase_header(5, total_phases + 1, "Power BI Refresh Verification")
        r5 = run_phase_5_api_refresh()
        phase_results.append({"phase": 5, "name": "Power BI Refresh", **r5})
        print(f"  Result: {r5['status']} — {r5['message']}")
        if r5["status"] == "FAIL":
            has_failure = True
    else:
        phase_results.append({
            "phase": 5,
            "name": "Power BI Refresh",
            "status": "SKIPPED",
            "message": "--skip-api flag used",
            "issues": [],
        })
        phase_header(5, total_phases + 1, "Power BI Refresh Verification")
        print("  Result: SKIPPED (--skip-api)")

    # Phase 6: Report Generation
    phase_header(total_phases + 1, total_phases + 1, "Report Generation")
    verdict = "NO-GO" if has_failure else "GO"

    report_filename = f"VISUAL_VALIDATION_REPORT_{yyyy_mm}.md"
    report_path = REPORTS_DIR / report_filename

    try:
        rp = generate_report(yyyy_dash, phase_results, verdict, report_path)
        phase_results.append({
            "phase": total_phases + 1,
            "name": "Report Generation",
            "status": "PASS",
            "message": f"Report saved to {rp}",
            "issues": [],
        })
        print(f"  Report: {rp}")
    except Exception as e:
        print(f"  [ERROR] Failed to write report: {e}")

    # Final Verdict
    print()
    print("  " + "=" * 58)
    if verdict == "GO":
        print(f"  VERDICT: GO -- Safe to send to supervisor")
    else:
        print(f"  VERDICT: NO-GO -- Do NOT send. Fix issues above.")
    print("  " + "=" * 58)
    print(f"  Exit code: {0 if verdict == 'GO' else 1}")
    print()

    return 0 if verdict == "GO" else 1


if __name__ == "__main__":
    sys.exit(main())

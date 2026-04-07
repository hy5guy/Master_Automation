#!/usr/bin/env python3
"""
Check source file freshness for all ETL pipelines against a target report month.

Read-only: does not modify any file. Discovers paths from path_config.py and
config/scripts.json — no hardcoded OneDrive paths.

Usage:
  python scripts/check_source_freshness.py --report-month 2026-03
  python scripts/check_source_freshness.py                         # defaults to previous month
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Callable, NamedTuple

try:
    from path_config import get_onedrive_root, get_powerbi_data_dir
except ImportError:
    # Fallback when running outside scripts/ directory
    _here = Path(__file__).resolve().parent
    sys.path.insert(0, str(_here))
    from path_config import get_onedrive_root, get_powerbi_data_dir


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

class FreshnessResult(NamedTuple):
    pipeline: str
    file_path: str
    expected_month: str
    latest_month: str
    status: str          # READY | STALE | UNKNOWN
    evidence_type: str   # content | tab-name | file-timestamp | not-found
    notes: str


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"


def setup_logging(report_month_label: str) -> Path:
    """Configure logging to both console and log file. Returns log file path."""
    LOG_DIR.mkdir(exist_ok=True)
    log_file = LOG_DIR / f"stale_sources_{report_month_label}.log"

    logger = logging.getLogger("source_freshness")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    fmt = logging.Formatter("[%(asctime)s] %(levelname)s  %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    fh = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    return log_file


log = logging.getLogger("source_freshness")


# ---------------------------------------------------------------------------
# Path helpers (runtime-resolved, never hardcoded)
# ---------------------------------------------------------------------------

def _onedrive() -> Path:
    return get_onedrive_root()


def _exports_base() -> Path:
    return _onedrive() / "05_EXPORTS"


def _shared_contributions() -> Path:
    return _onedrive() / "Shared Folder" / "Compstat" / "Contributions"


def _staging() -> Path:
    return _onedrive() / "03_Staging"


def _load_scripts_json() -> dict:
    """Load config/scripts.json from repo root."""
    repo_root = Path(__file__).resolve().parent.parent
    cfg = repo_root / "config" / "scripts.json"
    if not cfg.exists():
        log.warning("config/scripts.json not found at %s", cfg)
        return {}
    with open(cfg, encoding="utf-8") as f:
        return json.load(f)


def _load_ce_config() -> dict:
    """Load Community Engagement config.json for source workbook paths."""
    ce_dir = _onedrive() / "02_ETL_Scripts" / "Community_Engagement"
    cfg = ce_dir / "config.json"
    if not cfg.exists():
        log.warning("CE config.json not found at %s", cfg)
        return {}
    with open(cfg, encoding="utf-8") as f:
        return json.load(f)


def _load_pt_config() -> dict:
    """Load Policy Training config.yaml for source workbook path."""
    pt_dir = _onedrive() / "02_ETL_Scripts" / "Policy_Training_Monthly" / "configs"
    cfg = pt_dir / "config.yaml"
    if not cfg.exists():
        log.warning("PT config.yaml not found at %s", cfg)
        return {}
    try:
        import yaml
    except ImportError:
        # Fallback: parse the source_workbook line manually
        with open(cfg, encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("source_workbook:"):
                    return {"source_workbook": line.split(":", 1)[1].strip()}
        return {}
    with open(cfg, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


# ---------------------------------------------------------------------------
# Truncation helper
# ---------------------------------------------------------------------------

def _truncate_path(p: Path, segments: int = 3) -> str:
    """Show last N path segments for compact display."""
    parts = p.parts
    if len(parts) <= segments:
        return str(p)
    return str(Path(*parts[-segments:]))


# ---------------------------------------------------------------------------
# Evidence helpers
# ---------------------------------------------------------------------------

def _file_mod_month(p: Path) -> tuple[str, str]:
    """Return (YYYY-MM, evidence_type) from file modification timestamp."""
    mtime = datetime.fromtimestamp(p.stat().st_mtime)
    return mtime.strftime("%Y-%m"), "file-timestamp"


def _check_excel_date_column(path: Path, sheet: str | None, date_cols: list[str]) -> tuple[str | None, str]:
    """Open workbook read-only, find the max date across candidate columns.

    Returns (YYYY-MM or None, evidence_type).
    """
    try:
        import pandas as pd
    except ImportError:
        return None, "content"

    try:
        kwargs: dict = {"engine": "openpyxl"}
        if sheet:
            kwargs["sheet_name"] = sheet
        df = pd.read_excel(path, nrows=500, **kwargs)
    except ValueError:
        # Sheet not found — try without specifying sheet
        try:
            df = pd.read_excel(path, nrows=500, engine="openpyxl")
        except Exception:
            return None, "content"
    except Exception:
        return None, "content"

    for col in date_cols:
        matches = [c for c in df.columns if str(c).strip().lower() == col.lower()]
        if not matches:
            continue
        series = pd.to_datetime(df[matches[0]], errors="coerce").dropna()
        if series.empty:
            continue
        max_dt = series.max()
        return max_dt.strftime("%Y-%m"), "content"

    return None, "content"


def _check_excel_tab_names(path: Path, target_year: int, target_month: int) -> tuple[str | None, str]:
    """Look for tab names containing a month/year pattern. Returns (YYYY-MM, evidence_type) or (None, ...)."""
    try:
        import openpyxl
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        sheets = wb.sheetnames
        wb.close()
    except Exception:
        return None, "tab-name"

    import re
    target_label = f"{target_month:02d}-{target_year % 100:02d}"  # e.g. 03-26
    target_label2 = f"{target_year}_{target_month:02d}"            # e.g. 2026_03
    target_label3 = f"{target_month:02d}_{target_year % 100:02d}"  # e.g. 03_26

    best_ym: str | None = None
    for s in sheets:
        if target_label in s or target_label2 in s or target_label3 in s:
            return f"{target_year}-{target_month:02d}", "tab-name"
        # Try to extract any MM-YY or YYYY_MM pattern
        m = re.search(r"(\d{4})_(\d{2})", s)
        if m:
            ym = f"{m.group(1)}-{m.group(2)}"
            if best_ym is None or ym > best_ym:
                best_ym = ym
        m2 = re.search(r"(\d{2})[-_](\d{2})", s)
        if m2:
            mm, yy = int(m2.group(1)), int(m2.group(2))
            if 1 <= mm <= 12 and 20 <= yy <= 30:
                ym = f"20{yy}-{mm:02d}"
                if best_ym is None or ym > best_ym:
                    best_ym = ym

    return best_ym, "tab-name"


# ---------------------------------------------------------------------------
# Per-pipeline checkers
# ---------------------------------------------------------------------------

def _check_export_file_exists(
    pipeline: str,
    base_dir: Path,
    year: int,
    month: int,
    pattern: str,
    notes_prefix: str = "",
) -> FreshnessResult:
    """Check for a monthly export file matching a glob pattern."""
    target_ym = f"{year}-{month:02d}"
    yyyy_mm = f"{year}_{month:02d}"

    search_dir = base_dir
    if not search_dir.exists():
        return FreshnessResult(
            pipeline=pipeline,
            file_path=_truncate_path(search_dir),
            expected_month=target_ym,
            latest_month="—",
            status="UNKNOWN",
            evidence_type="not-found",
            notes=f"{notes_prefix}Directory not found: {_truncate_path(search_dir)}",
        )

    matches = sorted(search_dir.glob(pattern))
    if matches:
        latest = matches[-1]
        mod_ym, _ = _file_mod_month(latest)
        return FreshnessResult(
            pipeline=pipeline,
            file_path=_truncate_path(latest),
            expected_month=target_ym,
            latest_month=target_ym,
            status="READY",
            evidence_type="file-timestamp",
            notes=f"{notes_prefix}Found {len(matches)} file(s); newest: {latest.name}",
        )

    # No match for target month — find the latest file of any month
    all_files = sorted(search_dir.glob("*"), key=lambda p: p.stat().st_mtime if p.is_file() else 0)
    all_files = [f for f in all_files if f.is_file()]
    if all_files:
        latest = all_files[-1]
        mod_ym, _ = _file_mod_month(latest)
        return FreshnessResult(
            pipeline=pipeline,
            file_path=_truncate_path(search_dir),
            expected_month=target_ym,
            latest_month=mod_ym,
            status="STALE",
            evidence_type="file-timestamp",
            notes=f"{notes_prefix}No {yyyy_mm} file; latest is {latest.name} ({mod_ym})",
        )

    return FreshnessResult(
        pipeline=pipeline,
        file_path=_truncate_path(search_dir),
        expected_month=target_ym,
        latest_month="—",
        status="UNKNOWN",
        evidence_type="not-found",
        notes=f"{notes_prefix}Directory exists but is empty",
    )


def check_arrests(year: int, month: int) -> FreshnessResult:
    base = _exports_base() / "_Arrest" / str(year) / "month"
    pattern = f"{year}_{month:02d}_*.*"
    return _check_export_file_exists("Arrests", base, year, month, pattern)


def check_overtime(year: int, month: int) -> FreshnessResult:
    base = _exports_base() / "_Overtime" / "export" / "month" / str(year)
    pattern = f"{year}_{month:02d}_otactivity.*"
    return _check_export_file_exists("Overtime", base, year, month, pattern)


def check_timeoff(year: int, month: int) -> FreshnessResult:
    base = _exports_base() / "_Time_Off" / "export" / "month" / str(year)
    pattern = f"{year}_{month:02d}_timeoffactivity.*"
    return _check_export_file_exists("TimeOff", base, year, month, pattern)


def check_response_times(year: int, month: int) -> FreshnessResult:
    base = _exports_base() / "_CAD" / "timereport" / "monthly"
    pattern = f"{year}_{month:02d}_timereport.*"
    return _check_export_file_exists("Response Times", base, year, month, pattern)


def check_summons(year: int, month: int) -> FreshnessResult:
    """Check for e-ticket export in 05_EXPORTS/_Summons/E_Ticket/{YYYY}/month/."""
    base = _exports_base() / "_Summons" / "E_Ticket" / str(year) / "month"
    pattern = f"{year}_{month:02d}_*.*"
    return _check_export_file_exists("Summons (E-Ticket)", base, year, month, pattern)


def check_summons_staging(year: int, month: int) -> FreshnessResult:
    """Check the staging file for content freshness."""
    target_ym = f"{year}-{month:02d}"
    staging_file = _staging() / "Summons" / "summons_powerbi_latest.xlsx"

    if not staging_file.exists():
        return FreshnessResult(
            pipeline="Summons (Staging)",
            file_path=_truncate_path(staging_file),
            expected_month=target_ym,
            latest_month="—",
            status="UNKNOWN",
            evidence_type="not-found",
            notes="Staging file not found",
        )

    # Try content-based check: look for ISSUE_DATE or VIOLATION_DATE column
    content_ym, ev = _check_excel_date_column(
        staging_file, sheet=None,
        date_cols=["ISSUE_DATE", "VIOLATION_DATE", "Date", "SUMMONS_DATE"],
    )
    if content_ym:
        status = "READY" if content_ym >= target_ym else "STALE"
        return FreshnessResult(
            pipeline="Summons (Staging)",
            file_path=_truncate_path(staging_file),
            expected_month=target_ym,
            latest_month=content_ym,
            status=status,
            evidence_type=ev,
            notes=f"Max date in date column: {content_ym}",
        )

    # Fallback to file timestamp
    mod_ym, ev = _file_mod_month(staging_file)
    status = "READY" if mod_ym >= target_ym else "STALE"
    return FreshnessResult(
        pipeline="Summons (Staging)",
        file_path=_truncate_path(staging_file),
        expected_month=target_ym,
        latest_month=mod_ym,
        status=status,
        evidence_type=ev,
        notes=f"File modified {mod_ym} (content check inconclusive)",
    )


def _check_workbook_freshness(
    pipeline: str,
    workbook_path: Path,
    sheet: str | None,
    date_cols: list[str],
    year: int,
    month: int,
) -> FreshnessResult:
    """Generic workbook freshness check: content → tab-name → timestamp."""
    target_ym = f"{year}-{month:02d}"

    if not workbook_path.exists():
        return FreshnessResult(
            pipeline=pipeline,
            file_path=_truncate_path(workbook_path),
            expected_month=target_ym,
            latest_month="—",
            status="UNKNOWN",
            evidence_type="not-found",
            notes="Workbook not found",
        )

    # 1. Content-based
    try:
        content_ym, ev = _check_excel_date_column(workbook_path, sheet, date_cols)
        if content_ym:
            status = "READY" if content_ym >= target_ym else "STALE"
            return FreshnessResult(
                pipeline=pipeline,
                file_path=_truncate_path(workbook_path),
                expected_month=target_ym,
                latest_month=content_ym,
                status=status,
                evidence_type=ev,
                notes=f"Max date in content: {content_ym}",
            )
    except Exception as exc:
        log.debug("Content check failed for %s: %s", pipeline, exc)

    # 2. Tab-name based
    try:
        tab_ym, ev = _check_excel_tab_names(workbook_path, year, month)
        if tab_ym:
            status = "READY" if tab_ym >= target_ym else "STALE"
            return FreshnessResult(
                pipeline=pipeline,
                file_path=_truncate_path(workbook_path),
                expected_month=target_ym,
                latest_month=tab_ym,
                status=status,
                evidence_type=ev,
                notes=f"Tab name match: {tab_ym}",
            )
    except Exception as exc:
        log.debug("Tab-name check failed for %s: %s", pipeline, exc)

    # 3. File timestamp fallback
    try:
        mod_ym, ev = _file_mod_month(workbook_path)
        status = "READY" if mod_ym >= target_ym else "STALE"
        return FreshnessResult(
            pipeline=pipeline,
            file_path=_truncate_path(workbook_path),
            expected_month=target_ym,
            latest_month=mod_ym,
            status=status,
            evidence_type=ev,
            notes=f"File modified {mod_ym} (content/tab checks inconclusive)",
        )
    except OSError as exc:
        return FreshnessResult(
            pipeline=pipeline,
            file_path=_truncate_path(workbook_path),
            expected_month=target_ym,
            latest_month="—",
            status="UNKNOWN",
            evidence_type="not-found",
            notes=f"Could not stat file: {exc}",
        )


def check_community_engagement(year: int, month: int) -> list[FreshnessResult]:
    """Check all CE source workbooks from config.json."""
    results: list[FreshnessResult] = []
    ce_cfg = _load_ce_config()
    sources = ce_cfg.get("sources", {})

    date_cols = ["date", "Date", "Event_Date", "event_date", "Start date", "DATE"]

    for key, src in sources.items():
        if src.get("disabled", False):
            continue
        fp = Path(src.get("file_path", ""))
        sheet = src.get("sheet_name")
        label = f"CE: {key.replace('_', ' ').title()}"
        results.append(_check_workbook_freshness(label, fp, sheet, date_cols, year, month))

    if not results:
        # No config found — check default path
        default_wb = _shared_contributions() / "Community_Engagement" / "Community_Engagement_Monthly.xlsx"
        results.append(_check_workbook_freshness(
            "CE: Community Engagement", default_wb, None, date_cols, year, month,
        ))

    return results


def check_policy_training(year: int, month: int) -> FreshnessResult:
    """Check Policy Training source workbook."""
    pt_cfg = _load_pt_config()
    wb_path_str = pt_cfg.get("source_workbook", "")
    if wb_path_str:
        wb_path = Path(wb_path_str)
    else:
        wb_path = _shared_contributions() / "Policy_Training" / "Policy_Training_Monthly.xlsx"

    sheet = pt_cfg.get("source_sheet", "Training_Log")
    date_cols = ["Start date", "Date", "Training_Date", "Start_Date", "date"]

    return _check_workbook_freshness("Policy Training", wb_path, sheet, date_cols, year, month)


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_table(results: list[FreshnessResult]) -> str:
    """Format results as a fixed-width text table."""
    headers = ["Pipeline", "File Path", "Expected", "Latest", "Status", "Evidence", "Notes"]
    rows = []
    for r in results:
        rows.append([
            r.pipeline,
            r.file_path,
            r.expected_month,
            r.latest_month,
            r.status,
            r.evidence_type,
            r.notes,
        ])

    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    # Cap notes column at 60 chars for readability
    max_notes = 60
    widths[-1] = min(widths[-1], max_notes)

    def fmt_row(cells: list[str]) -> str:
        parts = []
        for i, cell in enumerate(cells):
            w = widths[i]
            if i == len(cells) - 1:
                parts.append(cell[:max_notes])
            else:
                parts.append(cell.ljust(w))
        return "  ".join(parts)

    lines = []
    lines.append(fmt_row(headers))
    lines.append("  ".join("-" * w for w in widths))
    for row in rows:
        lines.append(fmt_row(row))

    return "\n".join(lines)


def summary_line(results: list[FreshnessResult]) -> str:
    ready = sum(1 for r in results if r.status == "READY")
    stale = sum(1 for r in results if r.status == "STALE")
    unknown = sum(1 for r in results if r.status == "UNKNOWN")
    total = len(results)
    return f"Summary: {ready} READY, {stale} STALE, {unknown} UNKNOWN out of {total} sources"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_all_checks(year: int, month: int) -> list[FreshnessResult]:
    """Execute all pipeline freshness checks. Returns list of results."""
    results: list[FreshnessResult] = []

    checks: list[tuple[str, Callable[[], list[FreshnessResult]]]] = [
        ("Arrests", lambda: [check_arrests(year, month)]),
        ("Overtime", lambda: [check_overtime(year, month)]),
        ("TimeOff", lambda: [check_timeoff(year, month)]),
        ("Response Times", lambda: [check_response_times(year, month)]),
        ("Summons E-Ticket", lambda: [check_summons(year, month)]),
        ("Summons Staging", lambda: [check_summons_staging(year, month)]),
        ("Community Engagement", lambda: check_community_engagement(year, month)),
        ("Policy Training", lambda: [check_policy_training(year, month)]),
    ]

    for label, fn in checks:
        try:
            partial = fn()
            results.extend(partial)
            for r in partial:
                log.info("[%s] %s — %s (%s)", r.status, r.pipeline, r.latest_month, r.evidence_type)
        except Exception as exc:
            log.error("Check failed for %s: %s", label, exc)
            results.append(FreshnessResult(
                pipeline=label,
                file_path="—",
                expected_month=f"{year}-{month:02d}",
                latest_month="—",
                status="UNKNOWN",
                evidence_type="not-found",
                notes=f"Check raised {type(exc).__name__}: {exc}",
            ))

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check source file freshness for all ETL pipelines.",
    )
    parser.add_argument(
        "--report-month",
        type=str,
        default=None,
        help="Target report month as YYYY-MM (default: previous complete month).",
    )
    args = parser.parse_args()

    # Resolve target month
    if args.report_month:
        try:
            parts = args.report_month.strip().split("-")
            year, month = int(parts[0]), int(parts[1])
            if not (1 <= month <= 12 and year >= 2000):
                raise ValueError("Month must be 1-12, year >= 2000")
        except (ValueError, IndexError) as exc:
            print(f"ERROR: Invalid --report-month '{args.report_month}' (use YYYY-MM): {exc}")
            return 1
    else:
        today = date.today()
        if today.month == 1:
            year, month = today.year - 1, 12
        else:
            year, month = today.year, today.month - 1

    target_ym = f"{year}-{month:02d}"
    log_label = f"{year}{month:02d}"
    log_file = setup_logging(log_label)

    log.info("=" * 70)
    log.info("Source Freshness Check — Target: %s", target_ym)
    log.info("OneDrive root: %s", _onedrive())
    log.info("=" * 70)

    results = run_all_checks(year, month)

    # Output
    table = format_table(results)
    summary = summary_line(results)

    print()
    print(f"Source Freshness Report — Target Month: {target_ym}")
    print("=" * 70)
    print(table)
    print()
    print(summary)
    print(f"\nLog written to: {log_file}")

    # Also write table to log
    log.info("\n%s", table)
    log.info(summary)

    # Exit code: 0 if no STALE, 1 if any STALE
    has_stale = any(r.status == "STALE" for r in results)
    return 1 if has_stale else 0


if __name__ == "__main__":
    sys.exit(main())

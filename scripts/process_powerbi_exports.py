#!/usr/bin/env python3
"""
Process Power BI visual exports from _DropExports: match to mapping, rename, optionally normalize,
move to Processed_Exports, and copy to Backfill when required.

Uses Standards/config/powerbi_visuals/visual_export_mapping.json for page/visual -> filename/target.
Features:
- Fuzzy matching (e.g. "Average Response Times  Values" double space)
- Pattern matching (NIBRS dynamic dates)
- Smart date inference (reads data for 13-month visuals, uses last period column)
- Skips Text Box / Administrative Commander
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import pandas as pd

try:
    from path_config import get_onedrive_root, get_powerbi_data_dir, get_powerbi_paths
except ImportError:
    import os

    def get_onedrive_root() -> Path:
        base = os.environ.get("ONEDRIVE_BASE") or os.environ.get("ONEDRIVE_HACKENSACK")
        if base:
            return Path(base)
        return Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack")

    def get_powerbi_data_dir() -> Path:
        return get_onedrive_root() / "PowerBI_Data"

    def get_powerbi_paths() -> tuple[Path, Path]:
        import json

        config_path = Path(__file__).resolve().parent.parent / "config" / "scripts.json"
        try:
            with open(config_path, encoding="utf-8") as f:
                data = json.load(f)
            drop = Path(data["settings"]["powerbi_drop_path"])
            return drop, drop.parent / "Backfill"
        except Exception:
            root = get_powerbi_data_dir()
            drop = root / "_DropExports"
            return drop, root / "Backfill"


# Repo root (parent of scripts/)
AUTOMATION_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = AUTOMATION_ROOT / "Standards" / "config" / "powerbi_visuals" / "visual_export_mapping.json"

# Canonical Backfill subfolder names (18 folders). Any backfill_folder not in this list
# triggers a warning — it likely indicates a mapping entry with a non-canonical target_folder.
CANONICAL_BACKFILL_FOLDERS = frozenset({
    "arrests", "benchmark", "chief", "community_outreach", "csb", "detectives",
    "drone", "nibrs", "patrol", "policy_and_training_qual", "remu", "response_time",
    "social_media", "ssocc", "stacp", "summons", "traffic", "vcs_time_report",
})


def _safe_print(msg: str) -> None:
    """Print with ASCII fallback for Unicode errors."""
    try:
        print(msg)
    except UnicodeEncodeError:
        safe_msg = msg.encode('ascii', errors='replace').decode('ascii')
        print(safe_msg)


def _normalize_visual_name_for_match(s: str) -> str:
    """Collapse multiple spaces/underscores to one space, strip, for matching."""
    if not s:
        return ""
    return " ".join(str(s).split())


def _safe_filename_from_stem(stem: str) -> str:
    """Produce a safe snake_case filename from stem when no mapping exists."""
    s = re.sub(r"[^\w\s\-]", "", stem)[:80].strip()
    s = "_".join(s.split()).lower()
    return s or "unknown_export"


def _parse_period_to_yyyymm(period: str) -> str | None:
    """
    Parse period to YYYY_MM format.
    Supports: MM-YY (12-25), YY-MMM (25-Dec), YY-MMM format variations.
    """
    if not isinstance(period, str):
        return None
    
    clean = period.strip()
    if clean.lower().startswith("sum of "):
        clean = clean[7:].strip()
    
    # Try MM-YY format first (12-25 → 2025_12)
    m = re.match(r"^(\d{2})-(\d{2})$", clean)
    if m:
        mm, yy = m.groups()
        month = int(mm)
        year = int(yy)
        
        if 1 <= month <= 12:
            if year < 100:
                year = 2000 + year
            return f"{year:04d}_{month:02d}"
    
    # Try YY-MMM format (25-Dec → 2025_12)
    month_abbrev = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    
    m = re.match(r"^(\d{2})-([a-zA-Z]{3})$", clean)
    if m:
        yy, mmm = m.groups()
        year = int(yy)
        month = month_abbrev.get(mmm.lower())
        
        if month and year < 100:
            year = 2000 + year
            return f"{year:04d}_{month:02d}"
    
    return None


@dataclass
class ProcessingStats:
    files_renamed: int = 0
    files_normalized: int = 0
    files_moved: int = 0
    files_skipped: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def load_config(config_path: Path) -> dict:
    """Load visual_export_mapping.json."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def infer_yyyymm_from_data(file_path: Path, enforce_13_month: bool = False) -> str | None:
    """
    Infer YYYY_MM by reading CSV data.
    
    For 13-month rolling: Use LAST period column (most recent month)
    For single-month: Use Period/Month_Year column value
    
    Returns None if data-based inference fails.
    """
    try:
        df = pd.read_csv(file_path, nrows=20, low_memory=False)
        
        if df.empty:
            return None
        
        # For 13-month rolling: find period columns, use LAST one
        if enforce_13_month:
            period_cols = []
            for col in df.columns:
                if isinstance(col, str):
                    clean_col = col.strip()
                    if clean_col.lower().startswith("sum of "):
                        clean_col = clean_col[7:].strip()
                    if re.match(r"^\d{2}-\d{2}$", clean_col):
                        period_cols.append(clean_col)
            
            if period_cols:
                last_period = period_cols[-1]
                yyyymm = _parse_period_to_yyyymm(last_period)
                if yyyymm:
                    _safe_print(f"[DATA] Inferred {yyyymm} from last period column '{last_period}' in {file_path.name}")
                    return yyyymm
        
        # For single-month: look for Period/Month_Year column
        date_columns = ["Period", "Month_Year", "PeriodLabel", "Date", "Month"]
        for col_name in date_columns:
            if col_name in df.columns:
                values = df[col_name].dropna().astype(str).str.strip()
                if values.empty:
                    continue
                
                # Parse all values and get the maximum (latest) date
                parsed_dates = []
                for val in values.unique():
                    yyyymm = _parse_period_to_yyyymm(val)
                    if yyyymm:
                        parsed_dates.append(yyyymm)
                
                if parsed_dates:
                    # Use the latest date (max YYYY_MM)
                    latest = max(parsed_dates)
                    _safe_print(f"[DATA] Inferred {latest} from '{col_name}' column (latest of {len(parsed_dates)} periods) in {file_path.name}")
                    return latest
        
        return None
        
    except Exception as e:
        _safe_print(f"[WARN] Could not read data for date inference: {e}")
        return None


def infer_yyyymm_from_path(file_path: Path) -> str:
    """
    Fallback: Infer YYYY_MM from filename or use previous month.
    """
    stem = file_path.stem
    m = re.search(r"(\d{4})_(\d{2})", stem)
    if m:
        y, mo = m.group(1), m.group(2)
        if 1 <= int(mo) <= 12 and int(y) >= 2000:
            return f"{y}_{mo}"
    
    # Default: previous month
    now = datetime.now()
    if now.month == 1:
        prev = now.replace(year=now.year - 1, month=12)
    else:
        prev = now.replace(month=now.month - 1)
    
    yyyy_mm = f"{prev.year:04d}_{prev.month:02d}"
    _safe_print(f"[FALLBACK] Using {yyyy_mm} (previous month) for {file_path.name}")
    return yyyy_mm


def infer_yyyymm_smart(
    file_path: Path,
    enforce_13_month: bool = False,
    report_month: str | None = None,
) -> str:
    """
    Smart date inference with optional explicit override.

    Priority:
    1. Explicit report_month override (from --report-month CLI arg)
    2. Read CSV data (13-month: last column, others: Period column)
    3. Parse filename for YYYY_MM
    4. Use previous complete month
    """
    if report_month:
        _safe_print(f"[OVERRIDE] Using explicit report month: {report_month} for {file_path.name}")
        return report_month

    yyyymm = infer_yyyymm_from_data(file_path, enforce_13_month)
    if yyyymm:
        return yyyymm

    return infer_yyyymm_from_path(file_path)


def find_mapping_for_file(config: dict, file_stem: str) -> tuple[dict | None, str | None]:
    """
    Match file stem to a mapping entry.
    Uses visual_name, match_pattern (regex), and match_aliases.
    Returns (mapping_dict, standardized_filename) or (None, None).
    """
    normalized_stem = _normalize_visual_name_for_match(file_stem)
    stem_no_date = re.sub(r"^\d{4}_\d{2}_?", "", normalized_stem)

    for entry in config.get("mappings", []):
        # 1. Try exact visual_name
        name = _normalize_visual_name_for_match(entry.get("visual_name", ""))
        if name and (name in normalized_stem or name in stem_no_date):
            return entry, entry.get("standardized_filename", "")
        
        # 2. Try match_pattern (regex)
        pattern = entry.get("match_pattern")
        if pattern:
            try:
                if re.search(pattern, normalized_stem) or re.search(pattern, stem_no_date):
                    return entry, entry.get("standardized_filename", "")
            except re.error as e:
                _safe_print(f"[WARN] Invalid regex pattern '{pattern}': {e}")
        
        # 3. Try match_aliases
        for alias in entry.get("match_aliases", []):
            a = _normalize_visual_name_for_match(alias)
            if a and (a in normalized_stem or a in stem_no_date):
                return entry, entry.get("standardized_filename", "")
    
    return None, None


def should_skip(config: dict, file_path: Path) -> bool:
    """True if file matches skip_patterns."""
    stem = file_path.stem.lower()
    for pattern in config.get("skip_patterns", []):
        if pattern.lower() in stem:
            return True
    return False


def run_normalize(
    input_path: Path,
    output_path: Path,
    dry_run: bool,
    normalizer_format: str | None = None,
    enforce_13_month: bool = False
) -> bool:
    """Run normalize_visual_export_for_backfill.py. Returns True on success."""
    script = Path(__file__).resolve().parent / "normalize_visual_export_for_backfill.py"
    if not script.exists():
        return False
    cmd = [sys.executable, str(script), "--input", str(input_path), "--output", str(output_path)]
    if normalizer_format and normalizer_format != "monthly_accrual":
        cmd.extend(["--format", normalizer_format])
    if enforce_13_month:
        cmd.append("--enforce-13-month")
    if dry_run:
        cmd.append("--dry-run")
    cmd_str = " ".join(f'"{x}"' if " " in x else x for x in cmd)
    if dry_run:
        print(f"[DRY RUN] Would run: {cmd_str}")
    else:
        print(f"[RUN] {cmd_str}")
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=str(script.parent))
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Normalization failed (exit {e.returncode})")
        if e.stderr:
            _safe_print(f"[ERROR] stderr: {e.stderr.strip()}")
        if e.stdout:
            _safe_print(f"[ERROR] stdout: {e.stdout.strip()}")
        return False
    except Exception as e:
        print(f"[ERROR] Normalization failed: {e}")
        return False


def process_exports(
    source_dir: Path | None = None,
    processed_root: Path | None = None,
    backfill_root: Path | None = None,
    config_path: Path | None = None,
    dry_run: bool = False,
    report_month: str | None = None,
) -> ProcessingStats:
    """
    Scan source_dir for CSVs, match to mapping, rename to YYYY_MM_{standardized_filename}.csv,
    normalize when required, move to processed_root/target_folder, copy to backfill when required.
    """
    config_path = config_path or CONFIG_PATH
    config = load_config(config_path)
    _drop, _backfill = get_powerbi_paths()
    source_dir = source_dir or _drop
    if config.get("source_folder_override"):
        source_dir = Path(config["source_folder_override"])
    processed_root = processed_root or (get_onedrive_root() / "09_Reference" / "Standards" / "Processed_Exports")
    backfill_root = backfill_root or _backfill

    stats = ProcessingStats()
    if not source_dir.exists():
        stats.errors.append(f"Source directory does not exist: {source_dir}")
        return stats

    csv_files = list(source_dir.glob("*.csv"))
    for file_path in csv_files:
        if should_skip(config, file_path):
            stats.files_skipped.append(file_path.name)
            _safe_print(f"[SKIP] {file_path.name} (matches skip pattern)")
            continue

        mapping, standardized_base = find_mapping_for_file(config, file_path.stem)
        if not mapping:
            # Fallback: move to Other/ with sanitized name
            stem_no_date = re.sub(r"^\d{4}_\d{2}_?", "", file_path.stem)
            standardized_base = _safe_filename_from_stem(stem_no_date)
            target_folder = "Other"
            enforce_13_month = False
            _safe_print(f"[WARN] No mapping for: {file_path.name} -> using {target_folder}/")
            mapping = {
                "standardized_filename": standardized_base,
                "requires_normalization": False,
                "is_backfill_required": False,
                "enforce_13_month_window": False,
                "target_folder": target_folder,
            }
            stats.files_skipped.append(file_path.name)
        else:
            enforce_13_month = mapping.get("enforce_13_month_window", False)
        
        # Smart date inference: explicit override > data > filename > previous month
        yyyy_mm = infer_yyyymm_smart(file_path, enforce_13_month, report_month=report_month)
        
        target_folder = mapping.get("target_folder", "Other")
        backfill_folder = mapping.get("backfill_folder") or target_folder
        new_name = f"{yyyy_mm}_{standardized_base}.csv"
        stats.files_renamed += 1

        dest_dir = processed_root / target_folder
        dest_path = dest_dir / new_name

        if dry_run:
            _safe_print(f"[DRY RUN] Would process: {file_path.name} -> {dest_path}")
            if mapping.get("requires_normalization"):
                fmt = mapping.get("normalizer_format") or "monthly_accrual"
                enforce_window = mapping.get("enforce_13_month_window", False)
                _norm_script = Path(__file__).resolve().parent / "normalize_visual_export_for_backfill.py"
                _dry_cmd = [sys.executable, str(_norm_script), "--input", str(file_path), "--output", str(dest_path)]
                if fmt in ("summons", "training_cost"):
                    _dry_cmd.extend(["--format", fmt])
                if enforce_window:
                    _dry_cmd.append("--enforce-13-month")
                _dry_cmd.append("--dry-run")
                _cmd_str = " ".join(f'"{x}"' if " " in str(x) else str(x) for x in _dry_cmd)
                _safe_print(f"[DRY RUN] Would run: {_cmd_str}")
            if mapping.get("is_backfill_required"):
                _safe_print(f"[DRY RUN] Would copy to Backfill: {backfill_root / yyyy_mm / backfill_folder / new_name}")
            stats.files_moved += 1
            continue

        # Normalize to dest, or copy then move to dest
        dest_dir.mkdir(parents=True, exist_ok=True)
        if mapping.get("requires_normalization"):
            fmt = mapping.get("normalizer_format")
            enforce_window = mapping.get("enforce_13_month_window", False)
            ok = run_normalize(
                file_path,
                dest_path,
                dry_run=False,
                normalizer_format=fmt,
                enforce_13_month=enforce_window
            )
            if not ok:
                stats.errors.append(f"Normalization failed: {file_path.name}")
                continue
            # Only remove source when normalization succeeded and output exists and is non-empty
            if not dest_path.exists():
                stats.errors.append(f"Normalization reported success but output missing: {dest_path}")
                continue
            if dest_path.stat().st_size == 0:
                stats.errors.append(f"Normalization produced empty file; not removing source: {file_path.name}")
                continue
            stats.files_normalized += 1
            try:
                file_path.unlink()
            except OSError:
                stats.errors.append(f"Could not remove source after normalize: {file_path}")
        else:
            try:
                shutil.copy2(file_path, dest_path)
                file_path.unlink()
            except OSError as e:
                stats.errors.append(f"Move failed: {file_path.name} -> {e}")
                continue
        stats.files_moved += 1

        if mapping.get("is_backfill_required"):
            if backfill_folder not in CANONICAL_BACKFILL_FOLDERS:
                _safe_print(f"[WARN] Non-canonical backfill folder: '{backfill_folder}' for {file_path.name}")
            backfill_dir = backfill_root / yyyy_mm / backfill_folder
            backfill_dir.mkdir(parents=True, exist_ok=True)
            backfill_file = backfill_dir / new_name
            try:
                shutil.copy2(dest_path, backfill_file)
            except OSError as e:
                stats.errors.append(f"Backfill copy failed: {backfill_file} -> {e}")

    return stats


def verify_processing(
    source_dir: Path | None = None,
    processed_root: Path | None = None,
    stats: ProcessingStats | None = None,
) -> bool:
    """Verify: source folder empty, destination files exist and not empty."""
    source_dir = source_dir or (get_powerbi_data_dir() / "_DropExports")
    processed_root = processed_root or (get_onedrive_root() / "09_Reference" / "Standards" / "Processed_Exports")

    print("--- Verification Report ---")
    if stats:
        print(f"Files Renamed:   {stats.files_renamed}")
        print(f"Files Normalized: {stats.files_normalized}")
        print(f"Files Moved:     {stats.files_moved}")
        if stats.files_skipped:
            _safe_print(f"Skipped:         {len(stats.files_skipped)} ({', '.join(stats.files_skipped[:5])}{'...' if len(stats.files_skipped) > 5 else ''})")
        if stats.errors:
            _safe_print("Errors:")
            for e in stats.errors:
                _safe_print(f"  - {e}")

    if source_dir.exists():
        remaining = list(source_dir.glob("*.csv"))
        if remaining:
            _safe_print(f"Source folder not empty: {len(remaining)} CSV(s) remaining: {[f.name for f in remaining[:5]]}")
        else:
            _safe_print("Source folder: no CSVs remaining (OK).")
    else:
        print("Source folder: does not exist.")

    if processed_root.exists():
        dest_files = list(processed_root.rglob("*.csv"))
        non_empty = [f for f in dest_files if f.stat().st_size > 0]
        print(f"Processed exports: {len(non_empty)} file(s) in {processed_root}")
    else:
        print(f"Processed exports folder does not exist: {processed_root}")

    return not (stats and stats.errors)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Process Power BI visual exports from _DropExports.")
    ap.add_argument("--source", type=Path, default=None, help="Source folder")
    ap.add_argument("--processed", type=Path, default=None, help="Processed exports root")
    ap.add_argument("--backfill", type=Path, default=None, help="Backfill root")
    ap.add_argument("--config", type=Path, default=None, help="Path to visual_export_mapping.json")
    ap.add_argument("--report-month", type=str, default=None,
                    help="Explicit report month in YYYY-MM format (overrides data/filename inference)")
    ap.add_argument("--dry-run", action="store_true", help="Do not move or delete files")
    ap.add_argument("--verify-only", action="store_true", help="Only verify (no process)")
    args = ap.parse_args()

    # Single canonical default so process_exports and verify_processing stay aligned
    default_drop = get_powerbi_data_dir() / "_DropExports"
    resolved_source = args.source if args.source is not None else default_drop

    if args.verify_only:
        verify_processing(source_dir=resolved_source, processed_root=args.processed)
        return 0

    # Parse --report-month to YYYY_MM format if provided
    report_month_override = None
    if args.report_month:
        try:
            parts = args.report_month.split("-")
            report_month_override = f"{int(parts[0]):04d}_{int(parts[1]):02d}"
            _safe_print(f"[INFO] Using explicit report month: {report_month_override}")
        except (ValueError, IndexError):
            _safe_print(f"[ERROR] Invalid --report-month format: {args.report_month} (expected YYYY-MM)")
            return 1

    stats = process_exports(
        source_dir=resolved_source,
        processed_root=args.processed,
        backfill_root=args.backfill,
        config_path=args.config,
        dry_run=args.dry_run,
        report_month=report_month_override,
    )
    verify_processing(source_dir=resolved_source, processed_root=args.processed, stats=stats)
    return 0 if not stats.errors else 1


if __name__ == "__main__":
    sys.exit(main())

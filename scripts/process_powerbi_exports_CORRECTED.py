#!/usr/bin/env python3
"""
Process Power BI visual exports from _DropExports: match to mapping, rename, optionally normalize,
move to Processed_Exports, and copy to Backfill when required.

Uses Standards/config/powerbi_visuals/visual_export_mapping.json for page/visual -> filename/target.
Handles fuzzy matching (e.g. "Average Response Times  Values" double space), pattern matching (NIBRS dynamic dates),
and skips Text Box / Administrative Commander.
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

try:
    from path_config import get_onedrive_root
except ImportError:
    import os
    def get_onedrive_root() -> Path:
        base = os.environ.get("ONEDRIVE_BASE") or os.environ.get("ONEDRIVE_HACKENSACK")
        if base:
            return Path(base)
        return Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack")


# Repo root (parent of scripts/)
AUTOMATION_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = AUTOMATION_ROOT / "Standards" / "config" / "powerbi_visuals" / "visual_export_mapping.json"


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


def infer_yyyymm_from_path(file_path: Path) -> str:
    """Infer YYYY_MM from filename (e.g. 2025_12_...) or fallback to previous month."""
    stem = file_path.stem
    m = re.search(r"(\d{4})_(\d{2})", stem)
    if m:
        y, mo = m.group(1), m.group(2)
        if 1 <= int(mo) <= 12 and int(y) >= 2000:
            return f"{y}_{mo}"
    # Default: previous month from now (e.g. mid-month drop for current month will get previous)
    now = datetime.now()
    if now.month == 1:
        prev = now.replace(year=now.year - 1, month=12)
    else:
        prev = now.replace(month=now.month - 1)
    yyyy_mm = f"{prev.year:04d}_{prev.month:02d}"
    print(f"[WARN] No date in filename '{file_path.name}'; using fallback YYYY_MM={yyyy_mm}. Verify prefix if this is for the current month.")
    return yyyy_mm


def find_mapping_for_file(config: dict, file_stem: str) -> tuple[dict | None, str | None]:
    """
    Match file stem to a mapping entry. Returns (mapping_dict, normalized_match_key) or (None, None).
    Uses visual_name, match_aliases, and match_pattern (regex); normalizes spaces for matching.
    """
    normalized_stem = _normalize_visual_name_for_match(file_stem)
    # Remove leading YYYY_MM_ for matching (e.g. "2025_12_Monthly Accrual..." -> "Monthly Accrual...")
    stem_no_date = re.sub(r"^\d{4}_\d{2}_?", "", normalized_stem)

    for entry in config.get("mappings", []):
        # 1. Try exact visual_name match
        name = _normalize_visual_name_for_match(entry.get("visual_name", ""))
        if name and (name in normalized_stem or name in stem_no_date):
            return entry, entry.get("standardized_filename", "")
        
        # 2. Try match_pattern (regex) - for dynamic names like NIBRS
        pattern = entry.get("match_pattern")
        if pattern:
            try:
                if re.search(pattern, normalized_stem) or re.search(pattern, stem_no_date):
                    return entry, entry.get("standardized_filename", "")
            except re.error as e:
                print(f"[WARN] Invalid regex pattern '{pattern}' in mapping: {e}")
        
        # 3. Try match_aliases
        for alias in entry.get("match_aliases", []):
            a = _normalize_visual_name_for_match(alias)
            if a and (a in normalized_stem or a in stem_no_date):
                return entry, entry.get("standardized_filename", "")
    
    return None, None


def should_skip(config: dict, file_path: Path) -> bool:
    """True if file matches skip_patterns (e.g. Text Box, Administrative Commander)."""
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
    """Run normalize_visual_export_for_backfill.py on input -> output. Returns True on success."""
    script = Path(__file__).resolve().parent / "normalize_visual_export_for_backfill.py"
    if not script.exists():
        return False
    cmd = [sys.executable, str(script), "--input", str(input_path), "--output", str(output_path)]
    if normalizer_format and normalizer_format in ("summons", "training_cost"):
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
            print(f"[ERROR] stderr: {e.stderr.strip()}")
        if e.stdout:
            print(f"[ERROR] stdout: {e.stdout.strip()}")
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
) -> ProcessingStats:
    """
    Scan source_dir for CSVs, match to mapping, rename to YYYY_MM_{standardized_filename}.csv,
    normalize when required, move to processed_root/target_folder, copy to backfill when required.
    """
    config_path = config_path or CONFIG_PATH
    config = load_config(config_path)
    source_dir = source_dir or (AUTOMATION_ROOT / "_DropExports")
    if config.get("source_folder_override"):
        source_dir = Path(config["source_folder_override"])
    processed_root = processed_root or (get_onedrive_root() / "09_Reference" / "Standards" / "Processed_Exports")
    backfill_root = backfill_root or (get_onedrive_root() / "PowerBI_Data" / "Backfill")

    stats = ProcessingStats()
    if not source_dir.exists():
        stats.errors.append(f"Source directory does not exist: {source_dir}")
        return stats

    csv_files = list(source_dir.glob("*.csv"))
    for file_path in csv_files:
        if should_skip(config, file_path):
            stats.files_skipped.append(file_path.name)
            print(f"[SKIP] {file_path.name} (matches skip pattern)")
            continue

        yyyy_mm = infer_yyyymm_from_path(file_path)
        mapping, standardized_base = find_mapping_for_file(config, file_path.stem)
        if not mapping:
            # Safe fallback: move to Other/ with sanitized name; strip any existing YYYY_MM_ to avoid double-dating
            stem_no_date = re.sub(r"^\d{4}_\d{2}_?", "", file_path.stem)
            standardized_base = _safe_filename_from_stem(stem_no_date)
            target_folder = "Other"
            print(f"[WARN] No mapping for: {file_path.name} -> using {target_folder}/{yyyy_mm}_{standardized_base}.csv")
            mapping = {
                "standardized_filename": standardized_base,
                "requires_normalization": False,
                "is_backfill_required": False,
                "enforce_13_month_window": False,
                "target_folder": target_folder,
            }
            stats.files_skipped.append(file_path.name)

        target_folder = mapping.get("target_folder", "Other")
        new_name = f"{yyyy_mm}_{standardized_base}.csv"
        stats.files_renamed += 1

        dest_dir = processed_root / target_folder
        dest_path = dest_dir / new_name

        if dry_run:
            print(f"[DRY RUN] Would process: {file_path.name} -> {dest_path}")
            if mapping.get("requires_normalization"):
                fmt = mapping.get("normalizer_format", "monthly_accrual")
                enforce_window = mapping.get("enforce_13_month_window", False)
                _norm_script = Path(__file__).resolve().parent / "normalize_visual_export_for_backfill.py"
                _dry_cmd = [sys.executable, str(_norm_script), "--input", str(file_path), "--output", str(dest_path)]
                if fmt in ("summons", "training_cost"):
                    _dry_cmd.extend(["--format", fmt])
                if enforce_window:
                    _dry_cmd.append("--enforce-13-month")
                _dry_cmd.append("--dry-run")
                _cmd_str = " ".join(f'"{x}"' if " " in str(x) else str(x) for x in _dry_cmd)
                print(f"[DRY RUN] Would run: {_cmd_str}")
            if mapping.get("is_backfill_required"):
                print(f"[DRY RUN] Would copy to Backfill: {backfill_root / yyyy_mm / target_folder / new_name}")
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
            backfill_dir = backfill_root / yyyy_mm / target_folder
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
    """
    Verify: source folder empty (or no CSVs), destination files exist and not empty.
    Prints summary report (Files Renamed, Files Normalized, Files Moved).
    """
    source_dir = source_dir or (AUTOMATION_ROOT / "_DropExports")
    processed_root = processed_root or (get_onedrive_root() / "09_Reference" / "Standards" / "Processed_Exports")

    print("--- Verification Report ---")
    if stats:
        print(f"Files Renamed:   {stats.files_renamed}")
        print(f"Files Normalized: {stats.files_normalized}")
        print(f"Files Moved:     {stats.files_moved}")
        if stats.files_skipped:
            print(f"Skipped:         {len(stats.files_skipped)} ({', '.join(stats.files_skipped[:5])}{'...' if len(stats.files_skipped) > 5 else ''})")
        if stats.errors:
            print("Errors:")
            for e in stats.errors:
                print(f"  - {e}")

    # Source folder empty of CSVs?
    if source_dir.exists():
        remaining = list(source_dir.glob("*.csv"))
        if remaining:
            print(f"Source folder not empty: {len(remaining)} CSV(s) remaining: {[f.name for f in remaining[:5]]}")
        else:
            print("Source folder: no CSVs remaining (OK).")
    else:
        print("Source folder: does not exist.")

    # Destination files exist and not empty (sample: list processed_root recursively)
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
    ap.add_argument("--source", type=Path, default=None, help="Source folder (default: Master_Automation/_DropExports)")
    ap.add_argument("--processed", type=Path, default=None, help="Processed exports root (default: 09_Reference/Standards/Processed_Exports)")
    ap.add_argument("--backfill", type=Path, default=None, help="Backfill root (default: PowerBI_Data/Backfill)")
    ap.add_argument("--config", type=Path, default=None, help="Path to visual_export_mapping.json")
    ap.add_argument("--dry-run", action="store_true", help="Do not move or delete files")
    ap.add_argument("--verify-only", action="store_true", help="Only run verify_processing (no process)")
    args = ap.parse_args()

    if args.verify_only:
        verify_processing(source_dir=args.source, processed_root=args.processed)
        return 0

    stats = process_exports(
        source_dir=args.source,
        processed_root=args.processed,
        backfill_root=args.backfill,
        config_path=args.config,
        dry_run=args.dry_run,
    )
    verify_processing(source_dir=args.source or (AUTOMATION_ROOT / "_DropExports"), processed_root=args.processed, stats=stats)
    return 0 if not stats.errors else 1


if __name__ == "__main__":
    sys.exit(main())

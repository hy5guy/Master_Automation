#!/usr/bin/env python3
"""
Processed_Exports routing helpers: canonical folder names, legacy directory resolution,
and archiving prior outputs before a new file lands in the same destination path.
"""

from __future__ import annotations

import filecmp
import re
import shutil
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

# Map legacy / split layout folder names (any case) to canonical lowercase targets for NEW writes.
LEGACY_FOLDER_TO_CANONICAL: dict[str, str] = {
    "social_media_and_time_report": "monthly_accrual_and_usage",
    "social_media_posts": "social_media",
    "traffic_mva": "traffic",
    "stacp_pt1": "stacp",
    "stacp_pt2": "stacp",
    "detectives_pt1": "detectives",
    "detectives_pt2": "detectives",
    "detectives_case_dispositions": "detectives",
    # Long-form names if a folder was created from standardized_filename
    "detective_division_part_1": "detectives",
    "detective_division_part_2": "detectives",
    "detective_case_dispositions": "detectives",
    "detective_clearance_rate_performance": "detectives",
    "stacp_part_1": "stacp",
    "stacp_part_2": "stacp",
    "monthly_accrual_and_usage_summary": "monthly_accrual_and_usage",
}

_ARCHIVE = "archive"
_UNDATED = "undated"


def snake_case_folder(name: str) -> str:
    """Lowercase + spaces/dashes to underscores (single source for comparisons)."""
    s = (name or "").strip().lower().replace(" ", "_").replace("-", "_")
    while "__" in s:
        s = s.replace("__", "_")
    return s


def canonical_folder_for_mapping(target_folder: str) -> str:
    """Normalize mapping JSON target_folder string to canonical directory name."""
    key = snake_case_folder(target_folder)
    return LEGACY_FOLDER_TO_CANONICAL.get(key, key)


def folder_on_disk_to_canonical(folder_name: str) -> str:
    """Resolve an on-disk Processed_Exports child name to canonical category."""
    return canonical_folder_for_mapping(folder_name)


def resolve_category_directory(processed_root: Path, logical_folder: str) -> Path:
    """
    Pick the directory to use for a logical category.

    - Prefer an existing child whose canonical name matches (handles Drone vs drone, old splits).
    - Otherwise use processed_root / canonical_name.
    """
    canonical = canonical_folder_for_mapping(logical_folder)
    if not processed_root.exists():
        return processed_root / canonical
    best: Path | None = None
    for child in sorted(processed_root.iterdir()):
        if not child.is_dir():
            continue
        if child.name.lower() == _ARCHIVE:
            continue
        if folder_on_disk_to_canonical(child.name) == canonical:
            best = child
            break
    if best is not None:
        return best
    return processed_root / canonical


def archive_prefix_from_filename(filename: str) -> str:
    """Leading YYYY_MM from standardized export names; else undated.

    Accepts: 2026_02_*, 2026 02_*, 202602_* (compact), optional space/underscore between year and month.
    """
    name = Path(filename).name
    m = re.match(r"^(\d{4})[_\s]+(\d{2})_", name)
    if m:
        return f"{m.group(1)}_{m.group(2)}"
    m = re.match(r"^(\d{4})(\d{2})_", name)
    if m and 1 <= int(m.group(2)) <= 12:
        return f"{m.group(1)}_{m.group(2)}"
    return _UNDATED


def _is_under_archive(path: Path) -> bool:
    return _ARCHIVE in [p.lower() for p in path.parts]


def archive_existing_destination(
    dest_path: Path,
    *,
    dry_run: bool,
    log: Callable[..., None] | None = None,
) -> bool:
    """
    If dest_path exists as a file, move it under archive/<prefix>/ with a timestamp suffix.

    Returns True if an existing file was archived (or would be in dry_run).
    Idempotent: if dest does not exist, returns False.
    Skips if path is already under .../archive/ (do not re-archive).
    """
    _log = log or (lambda *_a, **_k: None)

    if not dest_path.exists() or not dest_path.is_file():
        return False
    if _is_under_archive(dest_path):
        _log(f"[SKIP ARCHIVE] Already under archive: {dest_path}")
        return False

    prefix = archive_prefix_from_filename(dest_path.name)
    archive_dir = dest_path.parent / _ARCHIVE / prefix
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    arc_name = f"{dest_path.stem}__archived_{ts}{dest_path.suffix}"
    arc_path = archive_dir / arc_name

    if dry_run:
        _log(f"[DRY RUN] Would archive existing file to: {arc_path}")
        return True

    archive_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(dest_path), str(arc_path))
    _log(f"[ARCHIVE] Moved previous output to: {arc_path}")
    return True


def destinations_identical(a: Path, b: Path) -> bool:
    """Byte-compare two files; False if either missing."""
    if not a.is_file() or not b.is_file():
        return False
    try:
        return filecmp.cmp(a, b, shallow=False)
    except OSError:
        return False


def prepare_destination_file(
    dest_path: Path,
    source_path: Path,
    *,
    dry_run: bool,
    log: Callable[..., None] | None = None,
) -> str | None:
    """
    Ensure dest_path can be written: archive any different existing file, or no-op if identical.

    Returns:
      None — proceed with write
      "identical" — source matches dest; caller may delete source only
    """
    _log = log or (lambda *_a, **_k: None)
    if not dest_path.exists():
        return None
    if not dest_path.is_file():
        return None
    if destinations_identical(dest_path, source_path):
        _log(f"[SKIP] Destination already matches source (identical bytes): {dest_path.name}")
        return "identical"
    archive_existing_destination(dest_path, dry_run=dry_run, log=_log)
    return None

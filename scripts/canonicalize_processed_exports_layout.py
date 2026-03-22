#!/usr/bin/env python3
"""
One-time / occasional layout fix for 09_Reference/Standards/Processed_Exports:

- Merge split folders into canonical lowercase targets (traffic, stacp, detectives).
- Normalize PascalCase folder names to lowercase (Benchmark, Drone, NIBRS, Other,
  Patrol, Summons) using a two-step rename on Windows.

Does not touch archive/ subfolders except to block removal of non-empty sources.

Usage:
  python canonicalize_processed_exports_layout.py [--root PATH] [--dry-run]
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

try:
    from path_config import get_onedrive_root
except ImportError:

    def get_onedrive_root() -> Path:
        return Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack")


# Sources merged into one canonical directory (order: process all)
MERGE_GROUPS: list[tuple[str, list[str]]] = [
    (
        "detectives",
        [
            "detectives_case_dispositions",
            "detectives_pt1",
            "detectives_pt2",
        ],
    ),
    ("stacp", ["stacp_pt1", "stacp_pt2"]),
    ("traffic", ["traffic_mva", "Traffic", "traffic"]),
]

# Folders that should exist as exact lowercase names (case-only fix after merges)
CASE_CANONICAL = (
    "benchmark",
    "drone",
    "nibrs",
    "other",
    "patrol",
    "summons",
)


def _find_dir_ci(root: Path, name_lower: str) -> Path | None:
    for c in root.iterdir():
        if c.is_dir() and c.name.lower() == name_lower:
            return c
    return None


def _windows_case_rename(dir_path: Path, exact_name: str, dry_run: bool) -> None:
    """Rename folder to exact_name when only casing differs (Windows-safe)."""
    if dir_path.name == exact_name:
        return
    parent = dir_path.parent
    dest = parent / exact_name
    if dest.exists() and dest.resolve() != dir_path.resolve():
        raise OSError(f"Cannot case-rename {dir_path}: {dest} already exists")
    tmp = parent / f"{dir_path.name}.__casefix_tmp__"
    if dry_run:
        print(f"[DRY RUN] Case-rename: {dir_path.name} -> {exact_name} (via temp)")
        return
    if tmp.exists():
        raise OSError(f"Temp path exists: {tmp}")
    dir_path.rename(tmp)
    tmp.rename(dest)
    print(f"[OK] Case-rename: -> {exact_name}/")


def _move_csv(src_file: Path, dest_dir: Path, dry_run: bool) -> str:
    dest = dest_dir / src_file.name
    if dest.exists():
        if dest.stat().st_size == src_file.stat().st_size and dest.read_bytes() == src_file.read_bytes():
            if not dry_run:
                src_file.unlink()
            return "duplicate_skip"
        raise OSError(f"Name clash (different content): {dest}")
    if dry_run:
        return "moved"
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src_file), str(dest))
    return "moved"


def merge_group(processed: Path, target_lower: str, source_names: list[str], dry_run: bool) -> None:
    """Move *.csv from each source into canonical target folder."""
    dest = _find_dir_ci(processed, target_lower) or (processed / target_lower)
    if not dry_run and not dest.exists():
        dest.mkdir(parents=True, exist_ok=True)
        print(f"[OK] Created {dest.name}/")

    for src_name in source_names:
        src = processed / src_name
        if not src.is_dir():
            continue
        if src.resolve() == dest.resolve():
            continue
        for f in sorted(src.glob("*.csv")):
            action = _move_csv(f, dest, dry_run)
            label = "[DRY RUN]" if dry_run else "[OK]"
            print(f"{label} {f.parent.name}/{f.name} -> {target_lower}/ ({action})")
        # remove empty source (ignore archive subdirs with content)
        if dry_run:
            continue
        remaining = [x for x in src.iterdir() if x.name.lower() != "archive"]
        arch = src / "archive"
        if arch.is_dir() and any(arch.rglob("*")):
            print(f"[KEEP] {src.name}/ has non-empty archive/ — folder kept")
            continue
        if not list(src.glob("*.csv")) and not any(remaining):
            try:
                src.rmdir()
                print(f"[OK] Removed empty folder {src.name}/")
            except OSError:
                print(f"[KEEP] Could not remove {src.name}/ (not empty)")


def fix_case_only_dirs(processed: Path, dry_run: bool) -> None:
    for name in CASE_CANONICAL:
        p = _find_dir_ci(processed, name)
        if p is None or p.name == name:
            continue
        _windows_case_rename(p, name, dry_run)


def main() -> int:
    ap = argparse.ArgumentParser(description="Canonicalize Processed_Exports folder layout.")
    ap.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Processed_Exports root (default: <OneDrive>/09_Reference/Standards/Processed_Exports)",
    )
    ap.add_argument("--dry-run", action="store_true", help="Print actions only")
    args = ap.parse_args()

    processed = args.root or (get_onedrive_root() / "09_Reference" / "Standards" / "Processed_Exports")
    if not processed.is_dir():
        print(f"[ERROR] Not found: {processed}", file=sys.stderr)
        return 1

    print(f"Root: {processed}")
    if args.dry_run:
        print("--- DRY RUN ---")

    for target, sources in MERGE_GROUPS:
        merge_group(processed, target, sources, args.dry_run)

    # Ensure traffic/stacp/detectives exact casing
    for name in ("traffic", "stacp", "detectives"):
        p = _find_dir_ci(processed, name)
        if p and p.name != name:
            _windows_case_rename(p, name, args.dry_run)

    fix_case_only_dirs(processed, args.dry_run)

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

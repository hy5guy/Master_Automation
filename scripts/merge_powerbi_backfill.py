#!/usr/bin/env python3
"""
merge_powerbi_backfill.py

Merges Backfill data from the legacy 00_dev/projects/PowerBI_Data/Backfill location
into the canonical PowerBI_Data/Backfill location.

Run with DRY_RUN = True first to preview, then set DRY_RUN = False for live run.
"""

from __future__ import annotations

import logging
import shutil
from datetime import datetime
from pathlib import Path

# ─── Configuration ────────────────────────────────────────────────────────────
ONEDRIVE_ROOT = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack")

DEV_BACKFILL_DIR = ONEDRIVE_ROOT / "00_dev" / "projects" / "PowerBI_Data" / "Backfill"
CANONICAL_BACKFILL_DIR = ONEDRIVE_ROOT / "PowerBI_Data" / "Backfill"

LOG_DIR = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\logs")

DRY_RUN = False  # Set to False for live run

# File extensions considered valid data files
VALID_EXTENSIONS = {".csv", ".xlsx", ".json", ".txt", ".md"}
# ──────────────────────────────────────────────────────────────────────────────


def _setup_logging() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"powerbi_backfill_merge_{timestamp}.log"
    logger = logging.getLogger("powerbi_backfill_merge")
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s")
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(fmt)
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.info("Log file: %s", log_file)
    return logger


def is_valid_data_file(path: Path) -> bool:
    """Return True if path is a regular file with a valid data extension."""
    return path.is_file() and path.suffix.lower() in VALID_EXTENSIONS


def should_overwrite(src: Path, dst: Path) -> bool:
    """
    Return True if src should overwrite dst.
    Overwrites when:
      - dst does not exist
      - src is strictly newer than dst (by mtime)
      - src is larger (same mtime but different size → content diverged)
    """
    if not dst.exists():
        return True
    src_stat = src.stat()
    dst_stat = dst.stat()
    if src_stat.st_mtime > dst_stat.st_mtime + 1:  # 1-second grace period
        return True
    if src_stat.st_size != dst_stat.st_size:
        return True
    return False


def safe_copy(src: Path, dst: Path, dry_run: bool, logger: logging.Logger) -> str:
    """
    Copy src to dst.  Returns one of: 'MOVED', 'OVERWROTE', 'SKIPPED', 'ERROR'.
    On dry_run, logs intent but does not touch the filesystem.
    """
    action = "OVERWROTE" if dst.exists() else "MOVED"

    if not should_overwrite(src, dst):
        logger.info("SKIPPED  %s  (dst exists and is same/newer)", src.name)
        return "SKIPPED"

    if dry_run:
        logger.info("[DRY RUN] Would %s  %s  ->  %s", action, src, dst)
        return action

    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        logger.info("%s  %s  ->  %s", action, src, dst)
        return action
    except PermissionError as exc:
        logger.error("ERROR  PermissionError copying %s: %s", src, exc)
        return "ERROR"
    except OSError as exc:
        logger.error("ERROR  OSError copying %s: %s", src, exc)
        return "ERROR"


def merge_backfill(dry_run: bool, logger: logging.Logger) -> dict:
    """Walk DEV_BACKFILL_DIR and merge every valid data file into CANONICAL_BACKFILL_DIR."""
    counts = {"MOVED": 0, "OVERWROTE": 0, "SKIPPED": 0, "ERROR": 0}

    if not DEV_BACKFILL_DIR.exists():
        logger.warning("Source (dev) backfill directory not found: %s", DEV_BACKFILL_DIR)
        return counts

    if not CANONICAL_BACKFILL_DIR.exists():
        if dry_run:
            logger.info("[DRY RUN] Would create canonical dir: %s", CANONICAL_BACKFILL_DIR)
        else:
            try:
                CANONICAL_BACKFILL_DIR.mkdir(parents=True, exist_ok=True)
                logger.info("Created canonical dir: %s", CANONICAL_BACKFILL_DIR)
            except PermissionError as exc:
                logger.error("Cannot create canonical dir %s: %s", CANONICAL_BACKFILL_DIR, exc)
                return counts

    for src_file in sorted(DEV_BACKFILL_DIR.rglob("*")):
        if not is_valid_data_file(src_file):
            continue
        rel = src_file.relative_to(DEV_BACKFILL_DIR)
        dst_file = CANONICAL_BACKFILL_DIR / rel
        result = safe_copy(src_file, dst_file, dry_run, logger)
        counts[result] += 1

    return counts


def main() -> None:
    logger = _setup_logging()
    mode = "DRY RUN" if DRY_RUN else "LIVE"
    logger.info("=" * 60)
    logger.info("Power BI Backfill Merge  [%s]", mode)
    logger.info("Source : %s", DEV_BACKFILL_DIR)
    logger.info("Dest   : %s", CANONICAL_BACKFILL_DIR)
    logger.info("=" * 60)

    counts = merge_backfill(DRY_RUN, logger)

    logger.info("=" * 60)
    logger.info("Results: MOVED=%d  OVERWROTE=%d  SKIPPED=%d  ERROR=%d",
                counts["MOVED"], counts["OVERWROTE"], counts["SKIPPED"], counts["ERROR"])
    if counts["ERROR"] > 0:
        logger.warning("Errors encountered – review log before proceeding.")
    elif DRY_RUN:
        logger.info("Dry run complete. Set DRY_RUN = False to execute.")
    else:
        logger.info("Merge complete.")


if __name__ == "__main__":
    main()

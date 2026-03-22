#!/usr/bin/env python3
"""
Centralized path resolution for Master_Automation scripts.

Use ONEDRIVE_BASE or ONEDRIVE_HACKENSACK for portability; fallback is local default.
"""

from __future__ import annotations

import os
from pathlib import Path


def get_onedrive_root() -> Path:
    """Resolve OneDrive root dynamically. Auto-detects desktop (carucci_r) vs laptop (RobertCarucci)."""
    base = os.environ.get("ONEDRIVE_BASE") or os.environ.get("ONEDRIVE_HACKENSACK")
    if base:
        p = Path(base)
        if p.exists():
            return p
    # Auto-detect: try current user's OneDrive (works on desktop and laptop)
    home_onedrive = Path.home() / "OneDrive - City of Hackensack"
    if home_onedrive.exists():
        return home_onedrive
    # Fallback for local dev
    return Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack")


def get_powerbi_paths() -> tuple[Path, Path]:
    """Return (drop_path, backfill_root) from config/scripts.json.

    drop_path     – canonical _DropExports folder (PowerBI_Date\\_DropExports)
    backfill_root – canonical Backfill folder      (PowerBI_Date\\Backfill)
    """
    import json
    config_path = Path(__file__).resolve().parent.parent / "config" / "scripts.json"
    with open(config_path, encoding="utf-8") as f:
        data = json.load(f)
    drop = Path(data["settings"]["powerbi_drop_path"])
    backfill = drop.parent / "Backfill"
    return drop, backfill

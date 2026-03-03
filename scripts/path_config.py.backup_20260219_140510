#!/usr/bin/env python3
"""
Centralized path resolution for Master_Automation scripts.

Use ONEDRIVE_BASE or ONEDRIVE_HACKENSACK for portability; fallback is local default.
"""

from __future__ import annotations

import os
from pathlib import Path


def get_onedrive_root() -> Path:
    """Resolve OneDrive root dynamically. Prefer env vars for portability."""
    base = os.environ.get("ONEDRIVE_BASE") or os.environ.get("ONEDRIVE_HACKENSACK")
    if base:
        return Path(base)
    # Fallback for local dev
    return Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack")

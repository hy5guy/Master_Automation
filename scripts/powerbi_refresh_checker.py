#!/usr/bin/env python3
"""
Power BI Dataset Refresh Status Checker

Queries the Power BI REST API to verify that a dataset refresh completed
successfully after ETL processing. Used as Phase 5 of the visual validator.

Prerequisites:
  1. Azure AD app registration with Dataset.Read.All permission
  2. Service principal added to Power BI workspace as Member
  3. config/powerbi_api_config.json with tenant_id, client_id, client_secret,
     workspace_id, dataset_id

Usage:
  python scripts/powerbi_refresh_checker.py
  python scripts/powerbi_refresh_checker.py --after "2026-02-28T14:00:00"

Version: 1.0.0
Created: 2026-03-14
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

# Lazy imports for optional dependencies
_msal = None
_requests = None


def _import_msal():
    global _msal
    if _msal is None:
        try:
            import msal
            _msal = msal
        except ImportError:
            print("[ERROR] 'msal' package not installed. Run: pip install msal")
            sys.exit(1)
    return _msal


def _import_requests():
    global _requests
    if _requests is None:
        try:
            import requests
            _requests = requests
        except ImportError:
            print("[ERROR] 'requests' package not installed. Run: pip install requests")
            sys.exit(1)
    return _requests


CONFIG_PATH = Path(__file__).parent.parent / "config" / "powerbi_api_config.json"
POWER_BI_API_BASE = "https://api.powerbi.com/v1.0/myorg"
SCOPE = ["https://analysis.windows.net/powerbi/api/.default"]


def load_config() -> Dict:
    """Load Power BI API configuration from config file."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Power BI API config not found: {CONFIG_PATH}\n"
            "Create it from the template in config/powerbi_api_config.json"
        )
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    required_keys = ["tenant_id", "client_id", "client_secret", "workspace_id", "dataset_id"]
    missing = [k for k in required_keys if not config.get(k) or config[k].startswith("<")]
    if missing:
        raise ValueError(
            f"Power BI API config missing or has placeholder values for: {missing}\n"
            f"Edit {CONFIG_PATH} with your Azure AD credentials."
        )
    return config


def get_access_token(config: Dict) -> str:
    """Authenticate with Azure AD and return an access token."""
    msal = _import_msal()

    app = msal.ConfidentialClientApplication(
        client_id=config["client_id"],
        client_credential=config["client_secret"],
        authority=f"https://login.microsoftonline.com/{config['tenant_id']}",
    )

    result = app.acquire_token_for_client(scopes=SCOPE)

    if "access_token" not in result:
        error = result.get("error_description", result.get("error", "Unknown error"))
        raise RuntimeError(f"Failed to acquire access token: {error}")

    return result["access_token"]


def get_refresh_history(config: Dict, token: str, top: int = 5) -> list:
    """Fetch recent dataset refresh history from Power BI REST API."""
    requests = _import_requests()

    url = (
        f"{POWER_BI_API_BASE}/groups/{config['workspace_id']}"
        f"/datasets/{config['dataset_id']}/refreshes?$top={top}"
    )

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code == 401:
        raise RuntimeError("Authentication failed. Check your Azure AD credentials.")
    if response.status_code == 403:
        raise RuntimeError(
            "Access denied. Ensure the service principal is added to the "
            "Power BI workspace as a Member with Dataset.Read.All permission."
        )
    if response.status_code != 200:
        raise RuntimeError(
            f"Power BI API returned HTTP {response.status_code}: {response.text}"
        )

    data = response.json()
    return data.get("value", [])


def check_refresh_status(
    after_time: Optional[datetime] = None,
) -> Dict:
    """
    Check the latest Power BI dataset refresh status.

    Args:
        after_time: If provided, verify the refresh completed AFTER this time.

    Returns:
        Dict with keys: status ("PASS"/"FAIL"), message, refresh_details
    """
    config = load_config()
    token = get_access_token(config)
    refreshes = get_refresh_history(config, token, top=5)

    if not refreshes:
        return {
            "status": "FAIL",
            "message": "No refresh history found for this dataset.",
            "refresh_details": None,
        }

    latest = refreshes[0]
    refresh_status = latest.get("status", "Unknown")
    end_time_str = latest.get("endTime")
    start_time_str = latest.get("startTime")
    refresh_type = latest.get("refreshType", "Unknown")

    # Parse end time
    end_time = None
    if end_time_str:
        try:
            end_time = datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))
        except ValueError:
            pass

    details = {
        "refresh_status": refresh_status,
        "refresh_type": refresh_type,
        "start_time": start_time_str,
        "end_time": end_time_str,
        "dataset_id": config["dataset_id"],
    }

    # Check if refresh succeeded
    if refresh_status.lower() == "completed":
        msg = f"Refresh completed successfully at {end_time_str}"

        # If after_time specified, check timing
        if after_time and end_time:
            if after_time.tzinfo is None:
                after_time = after_time.replace(tzinfo=timezone.utc)
            if end_time < after_time:
                return {
                    "status": "FAIL",
                    "message": (
                        f"Refresh completed at {end_time_str} but ETL finished "
                        f"after {after_time.isoformat()}. Dataset may be stale."
                    ),
                    "refresh_details": details,
                }

        return {"status": "PASS", "message": msg, "refresh_details": details}

    elif refresh_status.lower() == "unknown":
        # Refresh is in progress
        return {
            "status": "FAIL",
            "message": f"Refresh is currently in progress (started {start_time_str}). Wait and retry.",
            "refresh_details": details,
        }

    else:
        # Failed or disabled
        error_msg = latest.get("serviceExceptionJson", "No error details available")
        return {
            "status": "FAIL",
            "message": f"Refresh failed with status '{refresh_status}': {error_msg}",
            "refresh_details": details,
        }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check Power BI dataset refresh status"
    )
    parser.add_argument(
        "--after",
        type=str,
        default=None,
        help="Verify refresh completed after this ISO timestamp (e.g. 2026-02-28T14:00:00)",
    )
    args = parser.parse_args()

    after_time = None
    if args.after:
        try:
            after_time = datetime.fromisoformat(args.after)
        except ValueError:
            print(f"[ERROR] Invalid timestamp format: {args.after}")
            return 1

    try:
        result = check_refresh_status(after_time=after_time)
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"[ERROR] {e}")
        return 1

    status = result["status"]
    print(f"[{status}] {result['message']}")

    if result.get("refresh_details"):
        d = result["refresh_details"]
        print(f"  Type: {d['refresh_type']}")
        print(f"  Started: {d['start_time']}")
        print(f"  Ended: {d['end_time']}")

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())

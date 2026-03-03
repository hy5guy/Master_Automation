# Desktop Configuration Troubleshooting Guide

**Project**: Hackensack PD | Data Ops & ETL Remediation  
**Created**: 2026-02-19  
**Author**: R. A. Carucci  
**Source**: Chat logs from desktop configuration testing and February 2026 ETL cycle

## Overview

This document provides troubleshooting guidance for setting up and validating the Master Automation suite on desktop environments, based on real-world configuration issues encountered during February 2026 ETL cycle testing.

## Common Configuration Issues

### 1. Path Resolution Problems

**Issue**: `path_config.py` resolves to incorrect OneDrive path (e.g., `RobertCarucci` instead of `carucci_r`)

**Symptoms**:
```
Resolved: C:\Users\RobertCarucci\OneDrive - City of Hackensack
Exists  : True
```

**Root Cause**: Environment variables not set, falling back to hardcoded path with outdated username

**Fix**:
```powershell
# Set permanent environment variable
[System.Environment]::SetEnvironmentVariable("ONEDRIVE_BASE","C:\Users\carucci_r\OneDrive - City of Hackensack","User")
$env:ONEDRIVE_BASE = "C:\Users\carucci_r\OneDrive - City of Hackensack"

# Update path_config.py fallback path if needed
$fixedContent = @'
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
'@
$fixedContent | Set-Content "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\scripts\path_config.py" -Encoding UTF8
```

**Validation**:
```powershell
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"
python -c "import sys; sys.path.insert(0,'scripts'); from path_config import get_onedrive_root; p=get_onedrive_root(); print('Resolved:', p); print('Exists  :', p.exists())"
```

Expected output:
```
Resolved: C:\Users\carucci_r\OneDrive - City of Hackensack
Exists  : True
```

### 2. Missing January 2026 Source Data

**Issue**: Pre-flight validation fails with missing E-Ticket export

**Symptoms**:
```
[FAIL] Jan 2026 Summons Source MISSING at: C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Summons\E_Ticket\2026\2026_01_eticket_export.csv
```

**Resolution Strategy**: This is acceptable for controlled execution. The system has backfill merge capability via `summons_backfill_merge.py`.

**Action Required**: 
1. Note the gap in documentation
2. Proceed with ETL execution
3. Verify summons output uses December 2025 data + backfill after completion

### 3. Scripts.json Configuration Issues

**Issue**: Incorrect count of enabled scripts or missing expected scripts

**Symptoms**:
```
6 Enabled Scripts:
- Arrests
- Community Engagement
- Overtime TimeOff
- Response Times
- Summons
- Summons Derived Outputs (PowerBI_Date CSVs)
```

**Investigation Commands**:
```powershell
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"

# Check if Policy Training is actually enabled
python -c "import json; data=json.load(open('config/scripts.json')); policy=[s for s in data['scripts'] if 'Policy' in s['name']]; print('\nPolicy Training Status:'); [print(f\"  {s['name']}: enabled={s.get('enabled', False)}\") for s in policy]"

# List all enabled scripts with details
python -c "import json; data=json.load(open('config/scripts.json')); enabled=[s for s in data['scripts'] if s.get('enabled', False)]; print(f'\n{len(enabled)} Enabled Scripts:\n' + '\n'.join(f'{i+1}. {s[\"name\"]} (order: {s.get(\"order\", \"N/A\")})' for i, s in enumerate(enabled)))"
```

### 4. Visual Export Mapping JSON Structure

**Issue**: AttributeError when processing visual_export_mapping.json

**Symptoms**:
```
AttributeError: 'str' object has no attribute 'get'
```

**Investigation**:
```powershell
# Inspect JSON structure
python -c "import json; data=json.load(open('Standards/config/powerbi_visuals/visual_export_mapping.json')); print(f'\nJSON Type: {type(data)}'); print(f'Length: {len(data)}'); print(f'\nFirst entry preview:'); import pprint; pprint.pprint(list(data.items())[:2] if isinstance(data, dict) else data[:2])"

# Count enforced visuals (corrected logic)
python -c "import json; data=json.load(open('Standards/config/powerbi_visuals/visual_export_mapping.json')); items = data.items() if isinstance(data, dict) else enumerate(data); enforced = sum(1 for k, v in items if (isinstance(v, dict) and v.get('enforce_13_month', False))); print(f'\n13-Month Enforcement: {enforced} visuals')"
```

## Desktop Environment Validation Checklist

### Phase 1: Infrastructure Validation

```powershell
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"

Write-Host "`n=== PHASE 1: INFRASTRUCTURE VALIDATION ===`n" -ForegroundColor Cyan

Write-Host "Step 1.1: Environment Check" -ForegroundColor Yellow
python --version
pip list | findstr "pandas openpyxl"
python -c "from scripts.path_config import get_onedrive_root; print('OneDrive Root:', get_onedrive_root())"
Write-Host "Assignment_Master_V2.csv exists:" (Test-Path ".\Assignment_Master_V2.csv")

Write-Host "`nStep 1.2: Pre-Flight Validation" -ForegroundColor Yellow
python scripts\Pre_Flight_Validation.py

Write-Host "`nStep 1.3: Configuration Integrity" -ForegroundColor Yellow
python -c "import json; data=json.load(open('config/scripts.json')); enabled=[s['name'] for s in data['scripts'] if s.get('enabled', False)]; print(f'\n{len(enabled)} Enabled Scripts:\n' + '\n'.join(f'{i+1}. {name}' for i, name in enumerate(enabled)))"

Write-Host "`n=== PHASE 1 COMPLETE ===`n" -ForegroundColor Green
```

### Expected Results

**Environment Check**:
- Python 3.14.2+ ✓
- pandas 3.0.0+ and openpyxl 3.1.5+ ✓
- OneDrive root resolves to correct path ✓
- Assignment_Master_V2.csv exists: True ✓

**Pre-Flight Validation**:
- Critical Personnel File: PASS ✓
- ETL Orchestrator Config: PASS ✓
- Power BI Drop Folder Access: PASS ✓
- Source files: May show warnings for missing January 2026 data (acceptable)

**Configuration Integrity**:
- 6-7 enabled scripts depending on Policy Training status
- All scripts should have valid paths and configurations

## Machine-Specific Considerations

### PD_BCI_01 Desktop Configuration

**Hostname**: PD_BCI_01  
**Username**: carucci_r  
**OneDrive Path**: `C:\Users\carucci_r\OneDrive - City of Hackensack`  
**Python Version**: 3.14.2  

**Key Differences from Laptop**:
- Environment variables may not be set initially
- May have legacy OneDrive sync folders under different usernames
- Requires explicit ONEDRIVE_BASE environment variable setup

### Portability Best Practices

1. **Always set environment variables** for path resolution
2. **Verify Python environment** on each machine
3. **Test path_config.py resolution** before running ETL
4. **Document machine-specific configurations** in this guide

## Troubleshooting Commands Reference

### Quick Diagnostic Block
```powershell
Write-Host "`n=== MACHINE DIAGNOSTIC ===`n" -ForegroundColor Cyan
Write-Host "Hostname : $env:COMPUTERNAME"
Write-Host "Username : $env:USERNAME"
Write-Host "ONEDRIVE_BASE      : $env:ONEDRIVE_BASE"
Write-Host "ONEDRIVE_HACKENSACK: $env:ONEDRIVE_HACKENSACK"
Write-Host "ONEDRIVE (default) : $env:OneDrive"

$candidates = @(
    "C:\Users\$env:USERNAME\OneDrive - City of Hackensack",
    $env:ONEDRIVE_BASE,
    $env:ONEDRIVE_HACKENSACK
) | Where-Object { $_ }

foreach ($p in $candidates) {
    $exists = Test-Path $p
    $color = if ($exists) { "Green" } else { "Red" }
    Write-Host "  [$( if($exists){'FOUND'}else{'MISS '})] $p" -ForegroundColor $color
}
```

### Python Environment Check
```powershell
python --version
pip list | Select-String "pandas|openpyxl|pyodbc"
```

### Path Resolution Test
```powershell
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"
python -c "import sys; sys.path.insert(0,'scripts'); from path_config import get_onedrive_root; p=get_onedrive_root(); print(f'Resolved: {p}'); print(f'Exists  : {p.exists()}')"
```

## Related Documentation

- `docs/FEBRUARY_2026_ETL_CYCLE_SUMMARY.md` - Complete ETL cycle execution results
- `docs/SUMMONS_DERIVED_OUTPUTS_FIX.md` - Summons data processing fixes
- `config/scripts.json` - ETL script configuration
- `scripts/path_config.py` - Path resolution logic
- `scripts/Pre_Flight_Validation.py` - Automated validation script

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-02-19 | Initial creation from desktop configuration testing | R. A. Carucci |
| 2026-02-19 | Added summons derived outputs troubleshooting | R. A. Carucci |
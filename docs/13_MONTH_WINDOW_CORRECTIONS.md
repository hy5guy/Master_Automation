# 13-Month Window Enforcement - CORRECTED Implementation

// 🕒 2026-02-12-16-00-00
// Project: Master_Automation/PowerBI_Visual_Exports
// Author: R. A. Carucci
// Purpose: Corrected implementation with selective enforcement and pattern matching

---

## What Changed (Corrections)

### Issue 1: Over-Application of 13-Month Enforcement ❌ → ✅

**Problem**: Original implementation applied 13-month window to ALL 32 visuals.

**Correction**: Now applies ONLY to the 24 visuals you specified.

**Visuals WITHOUT 13-Month Enforcement** (should use all available data):
- ❌ Arrest Categories by Type and Gender
- ❌ Arrest Distribution by Local, State & Out of State
- ❌ TOP 5 ARREST LEADERS
- ❌ Summons  Moving & Parking  All Bureaus
- ❌ Top 5 Parking Violations - Department Wide
- ❌ Top 5 Moving Violations - Department Wide
- ❌ In-Person Training
- ❌ Incident Distribution by Event Type

**Visuals WITH 13-Month Enforcement** (24 total):
- ✅ Department-Wide Summons Moving and Parking
- ✅ Training Cost by Delivery Method
- ✅ Monthly Accrual and Usage Summary
- ✅ 13-Month NIBRS Clearance Rate Trend
- ✅ Average Response Times  Values are in mmss
- ✅ Response Times by Priority
- ✅ Incident Count by Date and Event Type
- ✅ Use of Force Incident Matrix
- ✅ DFR Activity Performance Metrics
- ✅ Non-DFR Performance Metrics
- ✅ Patrol Division
- ✅ Traffic Bureau
- ✅ Motor Vehicle Accidents - Summary
- ✅ Detective Division  Part 1
- ✅ Detective Division  Part 2
- ✅ Detective Clearance Rate Performance
- ✅ Detective Case Dispositions - Performance Review
- ✅ Crime Suppressions Bureau Monthly Activity Analysis
- ✅ School Threat Assessment & Crime Prevention  Part 1
- ✅ School Threat Assessment & Crime Prevention  Part 2
- ✅ Social Media Posts
- ✅ Chief Law Enforcement Executive Duties
- ✅ Records & Evidence Unit
- ✅ Safe Streets Operations Control Center - Service Breakdown

---

### Issue 2: NIBRS Dynamic Visual Name ❌ → ✅

**Problem**: Visual name changes monthly due to DAX subtitle.

**Current Month** (Feb 2026):
```
"13-Month NIBRS Clearance Rate Trend January 2025 - January 2026"
```

**Next Month** (Mar 2026):
```
"13-Month NIBRS Clearance Rate Trend February 2025 - February 2026"
```

**Original Approach**: Exact string matching would fail next month.

**Corrected Approach**: Pattern-based matching using regex.

**New Mapping Field**: `match_pattern`

```json
{
  "visual_name": "13-Month NIBRS Clearance Rate Trend",
  "match_pattern": "^13-Month NIBRS Clearance Rate Trend",
  "match_aliases": [
    "13-Month NIBRS Clearance Rate Trend January 2025 - January 2026",
    "13-Month NIBRS Clearance Rate Trend February 2025 - February 2026"
  ],
  "standardized_filename": "nibrs_clearance_rate_13_month",
  "enforce_13_month_window": true,
  "target_folder": "NIBRS"
}
```

**How It Works**:
- `match_pattern: "^13-Month NIBRS Clearance Rate Trend"` matches ANY filename starting with this prefix
- Works for: "...January 2025 - January 2026", "...February 2025 - February 2026", etc.
- Automatically handles monthly DAX subtitle changes

---

## Updated Files

### 1. Mapping JSON (`visual_export_mapping_CORRECTED.json`) ✅

**Changes**:
- 8 visuals now have `enforce_13_month_window: false` (Arrests, Top 5s, All Bureaus Summons, In-Person Training, Incident Distribution)
- 24 visuals have `enforce_13_month_window: true` (per your list)
- NIBRS mapping includes `match_pattern: "^13-Month NIBRS Clearance Rate Trend"` for dynamic date range handling

**Example - NIBRS**:
```json
{
  "visual_name": "13-Month NIBRS Clearance Rate Trend",
  "match_pattern": "^13-Month NIBRS Clearance Rate Trend",
  "standardized_filename": "nibrs_clearance_rate_13_month",
  "enforce_13_month_window": true,
  "target_folder": "NIBRS",
  "notes": "Visual name changes monthly due to DAX subtitle. Use match_pattern to handle dynamic date range."
}
```

**Example - Top 5 (NO enforcement)**:
```json
{
  "visual_name": "Top 5 Parking Violations - Department Wide",
  "standardized_filename": "top_5_parking_violations",
  "normalizer_format": "summons",
  "enforce_13_month_window": false,  // ← NOT enforced
  "target_folder": "Summons"
}
```

---

### 2. Process Script (`process_powerbi_exports.py`) ✅

**New Feature**: Pattern matching support

**Changes to `find_mapping_for_file()` function**:

```python
def find_mapping_for_file(config: dict, file_stem: str) -> tuple[dict | None, str | None]:
    """Match file stem to mapping entry using visual_name, match_aliases, OR match_pattern (regex)."""
    
    normalized_stem = _normalize_visual_name_for_match(file_stem)
    stem_no_date = re.sub(r"^\d{4}_\d{2}_?", "", normalized_stem)

    for entry in config.get("mappings", []):
        # 1. Try exact visual_name match
        name = _normalize_visual_name_for_match(entry.get("visual_name", ""))
        if name and (name in normalized_stem or name in stem_no_date):
            return entry, entry.get("standardized_filename", "")
        
        # 2. Try match_pattern (regex) - NEW for dynamic names like NIBRS
        pattern = entry.get("match_pattern")
        if pattern:
            try:
                if re.search(pattern, normalized_stem) or re.search(pattern, stem_no_date):
                    return entry, entry.get("standardized_filename", "")
            except re.error as e:
                print(f"[WARN] Invalid regex pattern '{pattern}': {e}")
        
        # 3. Try match_aliases
        for alias in entry.get("match_aliases", []):
            a = _normalize_visual_name_for_match(alias)
            if a and (a in normalized_stem or a in stem_no_date):
                return entry, entry.get("standardized_filename", "")
    
    return None, None
```

**Matching Priority**:
1. Exact `visual_name` match
2. Regex `match_pattern` match (new)
3. `match_aliases` match

This ensures NIBRS matches even when the date range changes monthly.

---

## Testing the NIBRS Pattern Match

### Current Month (Feb 2026)
```bash
# Filename: 2026_02_13-Month NIBRS Clearance Rate Trend January 2025 - January 2026.csv
python process_powerbi_exports.py --dry-run

# Expected output:
# [DRY RUN] Would process: 2026_02_13-Month NIBRS Clearance Rate Trend January 2025 - January 2026.csv
#                       -> Processed_Exports/NIBRS/2026_02_nibrs_clearance_rate_13_month.csv
# [DRY RUN] Would run: ... --enforce-13-month
```

### Next Month (Mar 2026)
```bash
# Filename: 2026_03_13-Month NIBRS Clearance Rate Trend February 2025 - February 2026.csv
python process_powerbi_exports.py --dry-run

# Expected output:
# [DRY RUN] Would process: 2026_03_13-Month NIBRS Clearance Rate Trend February 2025 - February 2026.csv
#                       -> Processed_Exports/NIBRS/2026_03_nibrs_clearance_rate_13_month.csv
# [DRY RUN] Would run: ... --enforce-13-month
```

**Pattern** `^13-Month NIBRS Clearance Rate Trend` matches both filenames automatically.

---

## Deployment Steps (Corrected)

### Step 1: Deploy Corrected Files
```powershell
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"

# Backup existing
Copy-Item "Standards\config\powerbi_visuals\visual_export_mapping.json" `
          "Standards\config\powerbi_visuals\visual_export_mapping_BACKUP.json"

Copy-Item "scripts\process_powerbi_exports.py" `
          "scripts\process_powerbi_exports_BACKUP.py"

# Deploy corrected files
Copy-Item "visual_export_mapping_CORRECTED.json" `
          "Standards\config\powerbi_visuals\visual_export_mapping.json" -Force

Copy-Item "process_powerbi_exports_CORRECTED.py" `
          "scripts\process_powerbi_exports.py" -Force

# Deploy enhanced normalizer (same as before)
Copy-Item "normalize_visual_export_for_backfill_v2.py" `
          "scripts\normalize_visual_export_for_backfill.py" -Force
```

### Step 2: Test Pattern Matching
```powershell
# Create test NIBRS export with current date range
$testFile = "_DropExports\2026_02_13-Month NIBRS Clearance Rate Trend January 2025 - January 2026.csv"
# (Create or copy an actual export to this location)

# Test dry-run
python scripts\process_powerbi_exports.py --dry-run

# Verify output shows:
# - Correct mapping found (nibrs_clearance_rate_13_month)
# - 13-month enforcement flag present
# - No "No mapping for" warning
```

### Step 3: Verify Selective Enforcement
```powershell
# Check which visuals have enforcement
python -c "
import json
with open('Standards/config/powerbi_visuals/visual_export_mapping.json') as f:
    config = json.load(f)
    enforced = [m['visual_name'] for m in config['mappings'] if m.get('enforce_13_month_window')]
    not_enforced = [m['visual_name'] for m in config['mappings'] if not m.get('enforce_13_month_window')]
    print(f'WITH 13-month enforcement ({len(enforced)}):')
    for v in enforced:
        print(f'  ✓ {v}')
    print(f'\nWITHOUT 13-month enforcement ({len(not_enforced)}):')
    for v in not_enforced:
        print(f'  ✗ {v}')
"

# Expected:
# WITH 13-month enforcement (24): [your 24 visuals]
# WITHOUT 13-month enforcement (8): Arrests, Top 5s, etc.
```

---

## Validation Checklist

### Pre-Deployment ✅
- [x] 24 visuals have `enforce_13_month_window: true` (matching your list exactly)
- [x] 8 visuals have `enforce_13_month_window: false` (Arrests, Top 5s, All Bureaus, In-Person, Incident Distribution)
- [x] NIBRS mapping includes `match_pattern: "^13-Month NIBRS Clearance Rate Trend"`
- [x] Process script has pattern matching logic in `find_mapping_for_file()`
- [x] Normalizer has `--enforce-13-month` flag support (unchanged from v2)

### Post-Deployment 
- [ ] Corrected mapping deployed
- [ ] Corrected process script deployed
- [ ] Enhanced normalizer deployed
- [ ] Pattern match test: NIBRS export matches correctly
- [ ] Enforcement test: Only specified 24 visuals have --enforce-13-month flag
- [ ] Non-enforcement test: Arrest/Top 5 visuals process without window enforcement

---

## Key Differences: Original vs Corrected

| Aspect | Original | Corrected |
|--------|----------|-----------|
| **Visuals with 13-month enforcement** | 24/32 (over-applied) | 24/32 (exact match to your list) |
| **Arrest visuals** | ❌ Enforced | ✅ NOT enforced |
| **Top 5 Summons** | ❌ Enforced | ✅ NOT enforced |
| **Summons All Bureaus** | ❌ Enforced | ✅ NOT enforced |
| **In-Person Training** | ❌ Enforced | ✅ NOT enforced |
| **Incident Distribution** | ❌ Enforced | ✅ NOT enforced |
| **NIBRS dynamic name** | ❌ Would fail next month | ✅ Pattern match works indefinitely |
| **Pattern matching** | ❌ Not implemented | ✅ Implemented with `match_pattern` field |

---

## Summary

**Problem 1**: 13-month enforcement applied too broadly
**Solution**: Updated mapping to set `enforce_13_month_window: false` for 8 visuals not in your list

**Problem 2**: NIBRS visual name changes monthly (DAX subtitle)
**Solution**: Added `match_pattern` regex field and pattern matching logic

**Result**: 
- ✅ Only your specified 24 visuals have 13-month enforcement
- ✅ NIBRS visual matches automatically every month regardless of date range
- ✅ Clean separation between rolling window visuals and full-history visuals

**Files to Deploy**:
1. `visual_export_mapping_CORRECTED.json` → `Standards/config/powerbi_visuals/visual_export_mapping.json`
2. `process_powerbi_exports_CORRECTED.py` → `scripts/process_powerbi_exports.py`
3. `normalize_visual_export_for_backfill_v2.py` → `scripts/normalize_visual_export_for_backfill.py`

*Corrected Implementation - 2026-02-12*

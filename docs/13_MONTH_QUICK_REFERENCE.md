# 13-Month Window Enforcement - Quick Reference

## ✅ WITH 13-Month Enforcement (24 visuals)

These visuals will ONLY contain the most recent 13 complete months (e.g., Feb 2026 = 01-25 to 01-26):

### Summons (1)
- ✅ Department-Wide Summons Moving and Parking

### Training (1)
- ✅ Training Cost by Delivery Method

### Time Off (1)
- ✅ Monthly Accrual and Usage Summary

### NIBRS (1)
- ✅ 13-Month NIBRS Clearance Rate Trend
  - **Note**: Uses pattern matching `^13-Month NIBRS Clearance Rate Trend`
  - Handles dynamic date range (e.g., "...January 2025 - January 2026" → "...February 2025 - February 2026")

### Response Times (2)
- ✅ Average Response Times  Values are in mmss
- ✅ Response Times by Priority

### Benchmark (2)
- ✅ Incident Count by Date and Event Type
- ✅ Use of Force Incident Matrix

### Drone (2)
- ✅ DFR Activity Performance Metrics
- ✅ Non-DFR Performance Metrics

### Divisions (7)
- ✅ Patrol Division
- ✅ Traffic Bureau
- ✅ Detective Division  Part 1
- ✅ Detective Division  Part 2
- ✅ Detective Clearance Rate Performance
- ✅ Detective Case Dispositions - Performance Review
- ✅ Crime Suppressions Bureau Monthly Activity Analysis

### Support/Operations (7)
- ✅ Motor Vehicle Accidents - Summary
- ✅ School Threat Assessment & Crime Prevention  Part 1
- ✅ School Threat Assessment & Crime Prevention  Part 2
- ✅ Social Media Posts
- ✅ Chief Law Enforcement Executive Duties
- ✅ Records & Evidence Unit
- ✅ Safe Streets Operations Control Center - Service Breakdown

---

## ❌ WITHOUT 13-Month Enforcement (8 visuals)

These visuals will contain ALL available data (no rolling window filter):

### Arrests (3)
- ❌ Arrest Categories by Type and Gender
- ❌ Arrest Distribution by Local, State & Out of State
- ❌ TOP 5 ARREST LEADERS

### Summons Top 5 (2)
- ❌ Top 5 Parking Violations - Department Wide
- ❌ Top 5 Moving Violations - Department Wide

### Summons All Bureaus (1)
- ❌ Summons  Moving & Parking  All Bureaus

### Training (1)
- ❌ In-Person Training

### Benchmark (1)
- ❌ Incident Distribution by Event Type

---

## Pattern Matching Example (NIBRS)

**Current Export** (Feb 2026):
```
2026_02_13-Month NIBRS Clearance Rate Trend January 2025 - January 2026.csv
```

**Next Month Export** (Mar 2026):
```
2026_03_13-Month NIBRS Clearance Rate Trend February 2025 - February 2026.csv
```

**Mapping**:
```json
{
  "visual_name": "13-Month NIBRS Clearance Rate Trend",
  "match_pattern": "^13-Month NIBRS Clearance Rate Trend",
  "enforce_13_month_window": true
}
```

**Result**: Both filenames match automatically using the pattern `^13-Month NIBRS Clearance Rate Trend`

---

## Deployment Checklist

- [ ] Deploy `visual_export_mapping_CORRECTED.json` to `Standards/config/powerbi_visuals/visual_export_mapping.json`
- [ ] Deploy `process_powerbi_exports_CORRECTED.py` to `scripts/process_powerbi_exports.py`
- [ ] Deploy `normalize_visual_export_for_backfill_v2.py` to `scripts/normalize_visual_export_for_backfill.py`
- [ ] Test NIBRS pattern match: `python scripts\process_powerbi_exports.py --dry-run`
- [ ] Verify only 24 visuals show `--enforce-13-month` flag in dry-run output

---

## Quick Test

```powershell
# Verify enforcement flags in mapping
python -c "
import json
with open('Standards/config/powerbi_visuals/visual_export_mapping.json') as f:
    config = json.load(f)
    enforced = sum(1 for m in config['mappings'] if m.get('enforce_13_month_window'))
    total = len(config['mappings'])
    print(f'Enforcement: {enforced}/{total} visuals')
    print(f'Expected: 24/32 visuals')
    print(f'Match: {\"✓ PASS\" if enforced == 24 else \"✗ FAIL\"}')
"
```

**Expected Output**:
```
Enforcement: 24/32 visuals
Expected: 24/32 visuals
Match: ✓ PASS
```

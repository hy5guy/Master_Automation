# Summons Data Discrepancy Report
## 2026-02-17

## Problem Identified

### Traffic Bureau Visual Export vs Staging File Mismatch

**Traffic Bureau Visual Export (Traffic Bureau.csv):**
- Moving: **191**
- Parking: **3,061**
- Total: **3,252**

**Staging File (summons_powerbi_latest.xlsx - Jan 2026):**
- Traffic Bureau Moving: **156**
- Traffic Bureau Parking: **2,995**
- Traffic Bureau Total: **3,151**

**Missing**: 35 Moving + 66 Parking = **101 summons**

---

## Root Cause Analysis

### The staging file currently contains ONLY:
1. **January 2026 E-ticket data**: 3,615 records from `2026_01_eticket_export.csv`
2. **No historical backfill**: Missing prior months (Feb 2025 - Dec 2025)

### The visual export represents:
1. **13-month rolling data**: January 2025 through January 2026
2. **Includes backfill months**: Historical data not in current staging file

### Why the numbers don't match:
- **E-ticket file**: 3,615 total records (all January 2026)
- **Staging file**: 3,611 records (4 missing due to date parse errors)
- **Visual export**: Shows 3,252 for Traffic Bureau (filtered subset)

The visual export is **filtered by bureau** and shows only Traffic Bureau entries from the 13-month dataset, while your staging file has **all bureaus** but **only January 2026**.

---

## Solution: Need to Load Historical Backfill

### Current State:
```
summons_powerbi_latest.xlsx
├── January 2026: 3,611 records ✅
├── December 2025: MISSING ❌
├── November 2025: MISSING ❌
└── ... (10 more months): MISSING ❌
```

### Required State:
```
summons_powerbi_latest.xlsx
├── January 2026: 3,611 records (from E-ticket)
├── December 2025: ~XXX records (from backfill)
├── November 2025: ~XXX records (from backfill)
└── ... (10 more months from backfill)
```

---

## Where Is Historical Data?

### Check these locations:

1. **Backfill folder structure:**
   ```
   PowerBI_Date\Backfill\YYYY_MM\summons\
   ```

2. **Visual exports:**
   ```
   PowerBI_Date\Backfill\2025_12\summons\
   PowerBI_Date\Backfill\2025_11\summons\
   etc.
   ```

3. **Department-Wide CSVs:**
   - Look for files like: `2025_12_Department-Wide_Summons_Moving_Parking.csv`

---

## Action Plan

### Step 1: Find Historical Backfill Files
```powershell
Get-ChildItem "C:\Users\RobertCarucci\OneDrive - City of Hackensack\PowerBI_Date\Backfill" -Recurse -Filter "*summons*.csv" | Select-Object FullName, Length
```

### Step 2: Use summons_backfill_merge.py
The script already exists: `scripts/summons_backfill_merge.py`

This will:
- Load historical summons from Backfill folders
- Merge with January 2026 data
- Create complete 13-month dataset

### Step 3: Re-run Classification
After merging backfill, run classification again to ensure all records have TYPE

---

## Immediate Fix for Power BI (Without Backfill)

Since you're on a tight deadline, you can use **JANUARY 2026 DATA ONLY** with these updated queries:

### Fixed Queries (January 2026 only):

All three queries now:
1. ✅ Use YearMonthKey for correct sorting
2. ✅ Include Month_Year column
3. ✅ Filter to latest month (January 2026)
4. ✅ Consolidate Housing + OSO with Patrol

### Expected Results (January 2026 ONLY):

**After consolidation:**
- PATROL DIVISION: M=84, P=373 (includes Housing + OSO)
- TRAFFIC BUREAU: M=156, P=2,995
- DETECTIVE BUREAU: M=1, P=0

---

## Why Visual Export Shows Higher Numbers

The Traffic Bureau.csv visual export shows **191 Moving** because it includes:
1. Traffic Bureau officers: ~156
2. Plus other officers who issued Moving summons: ~35

Your **All Bureaus visual** correctly shows Traffic Bureau = 156 M because it's **bureau-specific**, not **all Moving summons issued by all officers**.

---

## Next Steps

1. **Immediate (Use current January-only data)**:
   - Update Power BI queries with FIXED versions
   - Consolidate Housing + OSO with Patrol
   - Accept January 2026 only data for now

2. **Future (Add historical data)**:
   - Find historical backfill CSVs
   - Run `summons_backfill_merge.py`
   - Get complete 13-month view

---

**Files Updated:**
- ✅ `m_code/summons_13month_trend_FIXED.m` - Simplified, no missing columns
- ✅ `m_code/___Summons_All_Bureaus_STANDALONE.m` - Consolidates Housing + OSO with Patrol
- ✅ `m_code/___Summons_Top5_Moving_STANDALONE.m` - Includes Month_Year
- ✅ `m_code/___Summons_Top5_Parking_STANDALONE.m` - Includes Month_Year

**Status**: Queries fixed for January 2026 data. Historical backfill needed for complete 13-month view.

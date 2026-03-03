# STACP Visual - 13-Month Window Calculation Fix (2026-02-13)

## Issue Summary

**Symptom**: Diagnostic query shows only 2 months in window (12-25, 01-26) instead of 13 months (01-25 through 01-26).

**Root Cause**: Incorrect start month calculation logic in rolling window code.

**Impact**: Visual only displays 2 months of data instead of full 13-month rolling window.

---

## Diagnostic Results (Before Fix)

```
Metric                          | Count | Details
--------------------------------|-------|--------------------------------
Total Columns in MoMTotals      | 54    | ✅ Correct
Detected Month Columns          | 32    | ✅ Correct (06-23 to 01-26)
Columns in 13-Month Window      | 2     | ❌ WRONG (only 12-25, 01-26)
First Column Name               | 1     | ✅ Correct
```

**Analysis**: 
- Column detection is working perfectly (finds all 32 months)
- Window filtering is broken (only keeps 2 instead of 13)

---

## Root Cause Analysis

### The Broken Logic (Original)

```powerquery
Today = DateTime.LocalNow(),              // Feb 13, 2026
CurrentMonth = Date.Month(Today),         // 2
CurrentYear = Date.Year(Today),           // 2026

// Calculate end month (previous month)
EndMonth = if CurrentMonth = 1 then 12 else CurrentMonth - 1,    // 1 (January)
EndYear = if CurrentMonth = 1 then CurrentYear - 1 else CurrentYear,  // 2026

// ❌ BROKEN: Start month calculation
StartMonth = if EndMonth = 1 then 12 else EndMonth - 1,  // 12 (December)
StartYear = EndYear - 1,  // 2025
```

**Result**:
- Start: December 2025 (12-25)
- End: January 2026 (01-26)
- Window: **2 months** ❌

### Why This is Wrong

The logic tried to "go back 13 months" by subtracting 1 from the end month:
- End Month: January (1)
- Subtract 1: January - 1 = December (12)

But this only goes back **1 month**, not 13 months!

A 13-month rolling window ending in January 2026 should **start** in January 2025.

---

## The Fixed Logic

```powerquery
Today = DateTime.LocalNow(),              // Feb 13, 2026
CurrentMonth = Date.Month(Today),         // 2
CurrentYear = Date.Year(Today),           // 2026

// Calculate end month (previous month)
EndMonth = if CurrentMonth = 1 then 12 else CurrentMonth - 1,    // 1 (January)
EndYear = if CurrentMonth = 1 then CurrentYear - 1 else CurrentYear,  // 2026

// ✅ FIXED: Start month is same month, one year earlier
StartMonth = EndMonth,      // 1 (January)
StartYear = EndYear - 1,    // 2025
```

**Result**:
- Start: January 2025 (01-25)
- End: January 2026 (01-26)
- Window: **13 months** ✅ (01-25, 02-25, 03-25... 12-25, 01-26)

---

## Mathematical Explanation

**13-Month Rolling Window Definition**:
"The current complete month PLUS the previous 12 months"

**From today's perspective** (Feb 13, 2026):
- Current month: February 2026 (incomplete)
- Previous month: **January 2026** (end of window)
- 12 months before that: **January 2025** (start of window)

**Formula**:
```
Window = [End Month - 12 months, End Month]
       = [January 2025, January 2026]
       = 13 total months
```

**In code**:
```powerquery
StartMonth = EndMonth          // Same month number
StartYear = EndYear - 1        // One year earlier
```

---

## Verification Examples

### Example 1: Today = February 13, 2026

| Variable | Value | Calculation |
|----------|-------|-------------|
| CurrentMonth | 2 (February) | From today |
| EndMonth | 1 (January) | CurrentMonth - 1 |
| EndYear | 2026 | CurrentYear (not January) |
| StartMonth | 1 (January) | EndMonth |
| StartYear | 2025 | EndYear - 1 |
| **Window** | **01-25 to 01-26** | **13 months** ✅ |

### Example 2: Today = March 15, 2026

| Variable | Value | Calculation |
|----------|-------|-------------|
| CurrentMonth | 3 (March) | From today |
| EndMonth | 2 (February) | CurrentMonth - 1 |
| EndYear | 2026 | CurrentYear |
| StartMonth | 2 (February) | EndMonth |
| StartYear | 2025 | EndYear - 1 |
| **Window** | **02-25 to 02-26** | **13 months** ✅ |

### Example 3: Today = January 5, 2027

| Variable | Value | Calculation |
|----------|-------|-------------|
| CurrentMonth | 1 (January) | From today |
| EndMonth | 12 (December) | if CurrentMonth = 1 then 12 |
| EndYear | 2026 | if CurrentMonth = 1 then CurrentYear - 1 |
| StartMonth | 12 (December) | EndMonth |
| StartYear | 2025 | EndYear - 1 |
| **Window** | **12-25 to 12-26** | **13 months** ✅ |

---

## Expected Diagnostic Results (After Fix)

Run the diagnostic query again. You should now see:

```
Metric                          | Count | Details
--------------------------------|-------|--------------------------------
Total Columns in MoMTotals      | 54    | ✅ (all columns)
Detected Month Columns          | 32    | ✅ (06-23 to 01-26)
Columns in 13-Month Window      | 13    | ✅ (01-25 to 01-26)
First Column Name               | 1     | ✅ (Tracked Items)
```

**Window should show**: 01-25, 02-25, 03-25, 04-25, 05-25, 06-25, 07-25, 08-25, 09-25, 10-25, 11-25, 12-25, 01-26

---

## Deployment Instructions

### Step 1: Update the Diagnostic Query (Optional - to verify fix)

1. In Power Query Editor, find `STACP_Diagnostic` query
2. Click **Advanced Editor**
3. Replace with updated version from:
   ```
   C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\m_code\stacp\STACP_DIAGNOSTIC.m
   ```
4. Click **Done**
5. Check the "Columns in 13-Month Window" count → should now be **13**

### Step 2: Update the Main Query

1. Find query `___STACP_pt_1_2`
2. Click **Advanced Editor**
3. Replace with updated version from:
   ```
   C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\m_code\stacp\STACP_pt_1_2_FIXED.m
   ```
4. Click **Done**
5. **Close & Apply**

### Step 3: Verify the Fix

1. Click on STACP visual
2. Open **Filters** pane
3. Check `Month_MM_YY` filter → should show **13 months**:
   ```
   ☑ 01-25, 02-25, 03-25, 04-25, 05-25, 06-25,
   ☑ 07-25, 08-25, 09-25, 10-25, 11-25, 12-25, 01-26
   ```

---

## What Changed in the Code

**File**: `STACP_pt_1_2_FIXED.m` (lines 17-20)

**Before**:
```powerquery
// Calculate start month (13 months back from end month)
StartMonth = if EndMonth = 1 then 12 else EndMonth - 1,
StartYear = EndYear - 1,
```

**After**:
```powerquery
// Calculate start month (13 months back = same month, one year earlier)
// For 13-month window: if end is Jan 2026, start is Jan 2025
StartMonth = EndMonth,
StartYear = EndYear - 1,
```

**Change**: Removed the incorrect `if EndMonth = 1 then 12 else EndMonth - 1` logic and replaced with simply `EndMonth`.

---

## Summary

**Status**: ✅ **Fixed**

**Problem**: Start month calculation was subtracting 1 month instead of going back 12 months

**Solution**: Set start month to same month as end month, but one year earlier

**Result**: Window now correctly spans 13 months (01-25 through 01-26)

**Files Updated**:
- `m_code/stacp/STACP_pt_1_2_FIXED.m` - Main query (line 19)
- `m_code/stacp/STACP_DIAGNOSTIC.m` - Diagnostic query (line 19)

---

*Fix Documentation - 2026-02-13*  
*Issue: 13-month window calculation error*  
*Resolution: Corrected start month logic from EndMonth-1 to EndMonth*

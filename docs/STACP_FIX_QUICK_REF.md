# STACP Visual Fix - Quick Reference

## Problem
Visual only shows December 2025 data (12-25) instead of full 13 months (01-25 through 01-26).

## Root Cause
M code year detection hardcoded for "24" or "25" - ignores "26" columns.

## Solution
Replace query `___STACP_pt_1_2` with fixed code.

## Deploy Steps
1. Open Power BI → **Transform Data**
2. Find query: `___STACP_pt_1_2`
3. Click **View** → **Advanced Editor**
4. Replace all code with: `m_code\stacp\STACP_pt_1_2_FIXED.m`
5. Click **Done** → **Close & Apply**

## Verify Fix
✅ Visual shows **13 months**: 01-25, 02-25... 12-25, 01-26  
✅ January 2026 data is present  
✅ No Power Query errors

## Files
- **Fixed M Code**: `m_code\stacp\STACP_pt_1_2_FIXED.m`
- **Full Documentation**: `docs\STACP_YEAR_DETECTION_FIX_2026_02_13.md`

---
*Quick Reference - 2026-02-13*

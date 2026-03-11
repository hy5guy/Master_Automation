# ___Social_Media Missing_References Fix

**Date:** 2026-03-04  
**Status:** ✅ Resolved  
**Query:** `___Social_Media` (loads from STACP.xlsm)

---

## Error

Power BI reported `Missing_References` when refreshing the `___Social_Media` query, with detail: `(___Social_Media) 01-25`.

---

## Root Cause

The error was caused by a **table name mismatch** in the Excel workbook. The M code expects a table named exactly `_stacp_mom_sm` in the STACP workbook. If the table name in Excel differs (e.g., extra characters, wrong underscores), Power Query cannot resolve the reference.

---

## Fix

1. **Verify table name in Excel:**
   - Open `Shared Folder\Compstat\Contributions\STACP\STACP.xlsm`
   - Click anywhere in the Social_Media table
   - Go to **Table Design** tab → check the **Table Name** field (top-left)
   - It must be exactly `_stacp_mom_sm` (no extra characters, correct underscores)

2. **M code requirements:**
   - Source: `Excel.Workbook(File.Contents(...STACP.xlsm), null, true)`
   - Navigation: `Source{[Item = "_stacp_mom_sm", Kind = "Table"]}[Data]`
   - Table structure: Columns from "Platform" through MM-YY date columns (e.g., "01-25" … "12-26")
   - No "Total" column required — `MissingField.Ignore` handles it if absent

3. **Syntax fix applied:** Lambda `(c) = >` corrected to `(c) =>` (no space before `=>`)

---

## M Code Location

`m_code/___Social_Media.m` (or `m_code/social_media/___Social_Media.m` depending on folder structure)

---

## References

- Claude In Excel session 2026-03-04
- STACP workbook: `Shared Folder\Compstat\Contributions\STACP\STACP.xlsm`

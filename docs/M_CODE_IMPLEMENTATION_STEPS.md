# Response Times M Code Implementation - Step by Step

**Target File:** `25_11_Monthly_FINAL.pbix`  
**Query Name:** `___ResponseTimeCalculator`  
**Due Date:** Tomorrow (2025-12-11)

---

## Quick Start

1. **Open Power BI File:**
   - Navigate to: `C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Monthly Reports\2025\11 - November - 2025\`
   - Open: `25_11_Monthly_FINAL.pbix`

2. **Open Power Query Editor:**
   - Click **Transform Data** button (Home ribbon)
   - Or: **Home** → **Transform Data**

3. **Find the Query:**
   - In left panel, locate: `___ResponseTimeCalculator`
   - Right-click → **Advanced Editor**

4. **Replace M Code:**
   - Copy entire contents from `RESPONSE_TIMES_M_CODE_SIMPLE.txt` (recommended for first try)
   - Or use `RESPONSE_TIMES_M_CODE_FINAL.txt` for full error handling
   - Paste into Advanced Editor
   - Click **Done**

5. **Apply Changes:**
   - Click **Close & Apply**
   - Review any errors in the query pane

---

## Detailed Steps

### Step 1: Backup Current Query (Recommended)

Before making changes:

1. In Power Query Editor, right-click `___ResponseTimeCalculator`
2. Select **Duplicate**
3. Rename duplicate to `___ResponseTimeCalculator_BACKUP`
4. This allows you to revert if needed

### Step 2: Open Advanced Editor

1. Select `___ResponseTimeCalculator` query
2. Click **Advanced Editor** button (Home ribbon)
3. The entire M code will be displayed

### Step 3: Choose Your Script

**Option A: Simple Script (Recommended for Testing)**
- Use: `RESPONSE_TIMES_M_CODE_SIMPLE.txt`
- Easier to understand and modify
- Basic error handling

**Option B: Full Script (Production Ready)**
- Use: `RESPONSE_TIMES_M_CODE_FINAL.txt`
- Comprehensive error handling
- Handles missing files gracefully
- More robust

### Step 4: Copy and Paste

1. Open the chosen script file (`RESPONSE_TIMES_M_CODE_SIMPLE.txt` or `RESPONSE_TIMES_M_CODE_FINAL.txt`)
2. Select all text (Ctrl+A)
3. Copy (Ctrl+C)
4. In Power BI Advanced Editor:
   - Select all existing code (Ctrl+A)
   - Paste new code (Ctrl+V)
5. Click **Done**

### Step 5: Fix Any Syntax Errors

If you see red errors:

1. **Common Issue:** Extra commas or missing brackets
   - Check the last line of each section
   - Ensure proper comma placement

2. **File Not Found Error:**
   - Verify file paths are correct
   - Check that files exist in specified locations

3. **Column Name Errors:**
   - The script uses `Table.PromoteHeaders` which should work automatically
   - If column names differ, you may need to adjust

### Step 6: Test the Query

1. In Power Query Editor, click **Refresh Preview** (right-side panel)
2. Check for errors:
   - Red error messages
   - "Expression.Error" messages
3. Review data preview:
   - Should show backfill data (Nov 2024 - Oct 2025)
   - Should include November 2025 data
   - Check row counts and date ranges

### Step 7: Apply and Verify

1. Click **Close & Apply**
2. Wait for data refresh to complete
3. Check Power BI report:
   - Verify visualizations update
   - Check date ranges are correct
   - Ensure no data gaps

---

## Troubleshooting

### Error: "File not found"
**Solution:** Verify file paths match exactly:
- Backfill: `C:\Dev\PowerBI_Date\Backfill\2025_10\response_time\2025_10_Average Response Times Values are in mmss.csv`
- November 2025: `C:\Dev\PowerBI_Date\Backfill\2025_12\response_time\2025_12_Average_Response_Times__Values_are_in_mmss.csv`

### Error: "Table.PromoteHeaders failed"
**Solution:** Your CSV may already have headers. Remove the `Table.PromoteHeaders` line or adjust the logic.

### Error: "Column not found"
**Solution:** Column names may differ. Review the actual column names in your CSV files and update the script accordingly.

### Data Missing or Incomplete
**Solution:**
1. Check if both files exist
2. Verify file contents (open in Excel)
3. Check file encoding (should be UTF-8 or Windows-1252)

### Performance Issues (Slow Refresh)
**Solution:**
1. Large backfill files may take time to load
2. Consider filtering data if possible
3. Check if incremental refresh is enabled

---

## Verification Checklist

After implementing:

- [ ] Query loads without errors
- [ ] Backfill data (Nov 2024 - Oct 2025) appears in preview
- [ ] November 2025 data appears in preview
- [ ] Data is properly combined (no duplicates or gaps)
- [ ] Date ranges are continuous
- [ ] Visualizations update correctly
- [ ] Report refresh completes successfully
- [ ] Data totals match expectations

---

## Files Reference

- **Simple Script:** `RESPONSE_TIMES_M_CODE_SIMPLE.txt` ← Start here
- **Full Script:** `RESPONSE_TIMES_M_CODE_FINAL.txt` ← Use if simple version works
- **This Guide:** `M_CODE_IMPLEMENTATION_STEPS.md`
- **General Guide:** `M_CODE_UPDATE_GUIDE.md`

---

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review error messages in Power Query Editor
3. Verify file paths and file existence
4. Check `ACTION_ITEMS.md` for latest status

---

**Ready to implement?** Start with Step 1 above!


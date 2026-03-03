# Troubleshooting: Average_Response_Time Column Not Found

## Error Message
```
Column 'Average_Response_Time' in table '___ResponseTimeCalculator' cannot be found or may not be used in this expression.
```

## Root Cause
The column `Average_Response_Time` is not visible to Power BI DAX expressions, even though the M code creates it.

## Solution Steps

### Step 1: Verify M Code is Updated
1. Open Power Query Editor
2. Select `___ResponseTimeCalculator` query
3. Open Advanced Editor
4. Ensure you're using the code from `RESPONSE_TIMES_M_CODE_COMPLETE_FIX.txt`
5. Verify the code includes:
   - Creation of `Average_Response_Time` column (converted from MM:SS)
   - Final verification step that ensures column exists
   - Column included in `Table.SelectColumns` at the end

### Step 2: Refresh the Query
1. In Power Query Editor, click **Refresh Preview** (or F5)
2. Check for any errors in the query preview
3. Verify `Average_Response_Time` appears in the column list
4. Verify data type shows as **Decimal Number** or **Number**

### Step 3: Close and Apply
1. Click **Close & Apply**
2. Wait for data refresh to complete
3. Check for refresh errors

### Step 4: Verify Column in Data Model
1. Go to **Data** view in Power BI
2. Select `___ResponseTimeCalculator` table
3. Verify `Average_Response_Time` column exists
4. Verify it's data type is **Decimal Number**

### Step 5: Check DAX Measures
1. Go to **Model** view
2. Select one of the measures (`Emergency_Avg_13M`, `Routine_Avg_13M`, or `Urgent_Avg_13M`)
3. Verify the measure formula uses the correct column name:
   ```dax
   AVERAGE('___ResponseTimeCalculator'[Average_Response_Time])
   ```
4. Use the updated DAX from `FIXED_DAX_MEASURES.txt`

## Common Issues

### Issue 1: Column Exists but Shows Errors
**Symptom:** Column appears in query but DAX says it can't find it

**Solution:**
- Check column name has exact spelling (case-sensitive): `Average_Response_Time`
- Ensure there are no hidden spaces or special characters
- Verify column data type is numeric (not text)

### Issue 2: Query Refreshes but Column Missing
**Symptom:** Query runs successfully but column doesn't appear in output

**Solution:**
- Check `Table.SelectColumns` includes `"Average_Response_Time"`
- Verify no steps are removing the column
- Check if any transformations are dropping columns

### Issue 3: Type Mismatch
**Symptom:** Column exists but DAX can't use it in AVERAGE()

**Solution:**
- Ensure column type is explicitly set to `type number` in M code
- Check that null values aren't causing issues
- Use `Table.TransformColumnTypes` to force numeric type

## Quick Fix Command

If the column still doesn't work, add this as the LAST step before the `in` statement:

```m
// Emergency fix - ensure column exists and is numeric
FinalFix = Table.TransformColumnTypes(
    Result,
    {{"Average_Response_Time", type number}},
    "en-US"
)
```

Then change the final `Result` to `FinalFix`.

## Verification Checklist

- [ ] M code includes `Average_Response_Time` creation
- [ ] Column is included in final `Table.SelectColumns`
- [ ] Query preview shows the column
- [ ] Column data type is numeric
- [ ] Query refresh completes without errors
- [ ] Column appears in Data view
- [ ] DAX measures updated to use correct column name
- [ ] Report visuals update correctly

## Still Not Working?

1. **Delete and recreate the query:**
   - Create new blank query
   - Paste the M code
   - Rename to `___ResponseTimeCalculator`

2. **Check for hidden characters:**
   - Copy column name from working query
   - Use exact same spelling

3. **Verify file paths:**
   - Ensure CSV files exist at specified paths
   - Check file permissions
   - Verify CSV has expected columns

4. **Clear cache:**
   - In Power Query Editor: Right-click query → Refresh
   - Or: File → Options → Data Source Settings → Clear Permissions


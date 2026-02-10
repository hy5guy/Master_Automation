# ETL Classification Fix Required

**Issue:** The ETL script is reclassifying violations, but it should use the raw export's `Case Type Code` directly.

**Expected Behavior:**
- Raw export: M=443, P=2,896 → Visual should show: M=443, P=2,896
- **Current Behavior:** Visual shows M=526, P=2,835 (reclassified)

**Root Cause:**
The `classify_violations()` function in `SummonsMaster_Simple.py` is reclassifying tickets based on:
- Statute number patterns (Title 39 → Moving)
- Keywords in violation descriptions
- Default rules

**Required Fix:**
The ETL script should use the `Case Type Code` column from the raw export directly, without reclassification.

**Files to Update:**
1. `SummonsMaster_Simple.py` - Modify `load_eticket_data()` to use `Case Type Code` directly
2. Remove or disable `classify_violations()` function for e-ticket data
3. Verify assignment file path: `C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Personnel\Assignment_Master_V2.csv`

**Current Assignment File Path:**
```python
ASSIGNMENT_FILE = Path(
    r"C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Personnel\Assignment_Master_V2.csv"
)
```

This path is already correct - no update needed unless the file has moved.

**Next Steps:**
1. Locate `SummonsMaster_Simple.py` file
2. Find `load_eticket_data()` function
3. Map `Case Type Code` column directly to `TYPE` field
4. Remove call to `classify_violations()` for e-ticket data
5. Test to ensure visual matches raw export (443 M, 2,896 P)

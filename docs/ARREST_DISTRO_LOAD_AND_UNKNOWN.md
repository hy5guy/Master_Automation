# ___Arrest_Distro — Load Error and Unknown Residence

**Date:** 2026-03-04

---

## Load Error

**Error:** `Expression.Error: Failed to load file: 2026_02_Arrests_PowerBI_Ready.xlsx at step "LoadedData"`

**Cause:** The M code loads from `01_DataSources\ARREST_DATA\Power_BI\` and selects the most recent file matching `*PowerBI_Ready*` or `*ucr_updated*`. The error occurs when `Excel.Workbook([Content], ...)` fails (e.g., file locked, corrupted, or format issue).

**Impact:** When the load fails, the entire query errors and returns no data. The visual would show an error or stale/cached data from a prior refresh.

---

## Unknown Residence Category

**Observation:** One arrest shows "Unknown" in Arrestee's Residence Category (1 male, Feb 2026).

**Cause:** The load error and the "Unknown" category are **separate issues**:

1. **Load error** → Query fails → No new data; visual may show error or cached data.
2. **Unknown** → Comes from the `Home_Category` logic in the M code when:
   - `state_id` is empty (ZIP not found in `uszips.csv` lookup, or no address)
   - Address does not match Local, In-County, or Out-of-State patterns

**Conclusion:** The 1 unknown is a **data quality issue** in the source — one arrestee has an address or ZIP that could not be resolved to a state/county. It is not caused by the file load error. If the file loads successfully, the unknown appears because that specific record lacks resolvable geographic data.

**Remediation:** Review the arrest record with "Unknown" residence; correct the address or ZIP in the source, or add the ZIP to `09_Reference\GeographicData\ZipCodes\uszips.csv` if it is valid but missing.

---

## Resolution (2026-03-04)

Arrest load and unknown residence issues were corrected. Data was manually added and the source file updated. The ___Arrest_Distro visual now loads successfully from `2026_02_Arrests_PowerBI_Ready.xlsx` with complete residence categorization.

---

## Source Path

`m_code/arrests/___Arrest_Distro.m` loads from:
`01_DataSources\ARREST_DATA\Power_BI\`

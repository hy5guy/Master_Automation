# Assignment Master Reference File - Column Explanation

**File:** `C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Personnel\Assignment_Master_V2.csv`

**Yes, this is a reference file** - It's the primary reference file used by the ETL script to map officers to their organizational assignments.

---

## 📋 Column Structure

The Assignment Master contains the following columns:

### Core Identity Columns
- **REF_NUMBER** - Internal reference number
- **FULL_NAME** - Full officer name
- **TITLE** - Job title (e.g., "P.O.", "SGT", "LT")
- **FIRST_NAME** - First name
- **LAST_NAME** - Last name
- **BADGE_NUMBER** - Badge number (numeric)
- **PADDED_BADGE_NUMBER** - Badge number as 4-digit string (e.g., "0390", "0123")

### Organizational Assignment Columns (Work Groups)
- **WG1** - Division level (e.g., "OPERATIONS DIVISION", "ADMINISTRATIVE DIVISION")
- **WG2** - Bureau level (e.g., "PATROL DIVISION", "TRAFFIC BUREAU", "DETECTIVE BUREAU")
- **WG3** - Platoon/Team level
- **WG4** - Additional organizational level
- **WG5** - Additional organizational level
- **TEAM** - Team designation

### Employment Information
- **POSS_CONTRACT_TYPE** - Contract type (e.g., "PBA LOCAL 9 (12 HOUR)")
- **DOB** - Date of birth
- **JOINED_SERVICE** - Date joined service
- **STATUS** - Employment status (e.g., "ACTIVE")
- **RANK** - Officer rank

### Promotion Dates (Seniority Tracking)
- **SGT** - Sergeant promotion date
- **LT** - Lieutenant promotion date
- **CAPT** - Captain promotion date
- **DEP_CHIEF** - Deputy Chief promotion date
- **CHIEF** - Chief promotion date

### Additional Metadata
- **Proposed 4-Digit Format** - Proposed badge format
- **Conflict Resolution** - Notes on conflicts
- **Special Notes** - Special notes
- **CODE** - Code designation
- **WORKING_GROUP** - Working group designation

### Duplicate Columns with "_seniority" and "_workgroup" suffixes
- These appear to be historical or alternate versions of the data
- Used for tracking changes over time or different data sources

---

## 🔄 How the ETL Uses This File

The ETL script (`SummonsMaster_Simple.py`) uses this file to:

1. **Join e-ticket data with officer assignments** - Matches on `PADDED_BADGE_NUMBER`
2. **Enrich summons data** - Adds WG1, WG2, WG3, WG4, WG5 organizational hierarchy
3. **Map officers to bureaus** - Primarily uses WG2 for bureau-level reporting
4. **Data quality scoring** - Uses assignment matching to calculate data quality scores

---

## 📝 Current Organizational Structure

Based on the organizational hierarchy:
- **WG1 (Division)** - Supervised by a Captain (e.g., "PATROL DIVISION", "OPERATIONS DIVISION")
- **WG2 (Bureau)** - Supervised by a Lieutenant (e.g., "TRAFFIC BUREAU", "DETECTIVE BUREAU")
- **WG3 (Platoon/Team)** - Further subdivision

**Note:** Recently updated from "PATROL BUREAU" to "PATROL DIVISION" to align with organizational structure.

---

**Last Updated:** 2026-01-11

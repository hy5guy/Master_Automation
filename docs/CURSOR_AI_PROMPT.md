# Cursor AI Prompt for workspace verification (historical)

> **Note (2026-03-25, v1.19.7 doc sync):** The live Git repo root is **`06_Workspace_Management`** (`C:\Users\carucci_r\OneDrive - City of Hackensack\06_Workspace_Management`). Older prompts below may still say **Master_Automation**; treat that as an alias for the same automation hub unless you still use a separate junction clone.

**Copy and paste this entire prompt into Cursor AI:**

---

## Context: Master_Automation Workspace Migration Verification

I just completed a migration where the PowerBI_Date directory was moved from `C:\Dev\PowerBI_Date_Merged` to `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date`. The Master_Automation workspace needs to be verified to ensure all paths and configurations are correct.

### What Was Done:
1. ✅ Updated `config\scripts.json` - `powerbi_drop_path` changed from `C:\Dev\PowerBI_Data\_DropExports` to `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\_DropExports`
2. ✅ Fixed path references in `scripts\run_all_etl.ps1` (removed old `C:\Dev\PowerBI_Date` references)
3. ✅ Updated documentation (`README.md` and `QUICK_START.md`) with new paths
4. ✅ Created verification script (`verify_migration.ps1`)

### Current Workspace Location:
`C:\Users\carucci_r\OneDrive - City of Hackensack\06_Workspace_Management` (or legacy junction **`...\Master_Automation`** if present)

### New PowerBI_Date Location:
`C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date`

---

## Tasks Needed:

### 1. Verify All Path References
Please scan all files in this workspace and check for any remaining references to:
- `C:\Dev\PowerBI_Date`
- `C:\Dev\PowerBI_Date_Merged`
- `C:\Dev\Power_BI_Data`
- `C:\Dev\PowerBI_Date_Laptop`

**Files to check:**
- All `.ps1` files in `scripts\` directory
- All `.md` files (README, QUICK_START, etc.)
- `config\scripts.json`
- Any other configuration or documentation files

**Action:** If you find any old path references, show me the file, line number, and suggest the correct replacement.

---

### 2. Verify ETL Script Configuration
Check `config\scripts.json` and verify that:
- All ETL script paths point to valid locations in OneDrive
- Script filenames match actual files (may not be `main.py`)
- All enabled scripts have valid paths

**Expected script locations:**
- `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\*`
- `C:\Users\carucci_r\OneDrive - City of Hackensack\01_DataSources\*`

**Action:** 
- List all scripts in `config\scripts.json`
- For each script, check if the path exists and if the script file exists
- If script files don't exist or have different names, suggest corrections

---

### 3. Verify PowerBI Drop Path
Check that `config\scripts.json` has the correct `powerbi_drop_path`:

**Expected:**
```json
"powerbi_drop_path": "C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\PowerBI_Date\\_DropExports"
```

**Action:** Verify this path exists and is accessible.

---

### 4. Check Script Logic
Review `scripts\run_all_etl.ps1` and verify:
- It correctly reads `powerbi_drop_path` from config
- Path handling works with OneDrive paths (spaces in path names)
- Error handling for missing paths is adequate
- Logging paths are correct

**Action:** Review the script and suggest any improvements for OneDrive path handling.

---

### 5. Verify Junction/Symlink
Check if there's a junction or symlink at:
`C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\Master_Automation`

This should point to:
`C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation`

**Action:** Verify the junction exists and points to the correct location. If missing, provide command to create it.

---

### 6. Test Readiness
Provide a checklist of:
- ✅ What's verified and working
- ⚠️ What needs attention
- 📝 What should be tested before running ETL scripts

---

### 7. Create Quick Reference
Generate a quick reference card showing:
- How to run ETL scripts (with new paths)
- How to check logs
- How to verify outputs
- Common troubleshooting steps

---

## Expected Output Format:

Please provide:
1. **Path Reference Scan Results** - List any old paths found
2. **ETL Script Status** - Status of each script in config
3. **Configuration Verification** - Confirm config is correct
4. **Script Review** - Any issues or improvements needed
5. **Junction Status** - Verify junction exists
6. **Testing Checklist** - What to test before running
7. **Quick Reference** - Commands and paths for daily use

---

## Additional Context:

- Python executable: `python` (Python 3.13.7)
- Log directory: `logs\` (created automatically on first run)
- All scripts should handle OneDrive paths with spaces correctly
- Scripts use `config\scripts.json` for configuration (not hardcoded paths)

---

**Please analyze this workspace and provide a comprehensive verification report with actionable recommendations.**


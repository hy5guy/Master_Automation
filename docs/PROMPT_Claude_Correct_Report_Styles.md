# Prompt: Claude — Correct Report_Styles Directory

**Use this prompt with Claude (in Cursor or Claude Code) to review and correct the Report_Styles directory.**

---

## Instructions

Copy everything below the line and paste it into a new Claude chat. Ensure your workspace includes `08_Templates/Report_Styles` and `06_Workspace_Management`. Claude will review the files and apply corrections.

---

Review and correct the `08_Templates/Report_Styles` directory. Your workspace root should include both `09_Reference` and `06_Workspace_Management` (or equivalent paths).

## Tasks

1. **Read** all files in `08_Templates/Report_Styles/`:
   - `README.md`
   - `CLAUDE.md`
   - `templates/HPD_Report_Style_Prompt.md` (if present)

2. **Verify**:
   - Paths to `06_Workspace_Management` are correct and work from 09_Reference context
   - Naming conventions in CLAUDE.md match actual usage (e.g., `YYYY_MM_DD_...html`)
   - No broken internal links or references
   - Canonical source note is accurate

3. **Correct** any issues you find:
   - Typos, grammar, unclear phrasing
   - Incorrect or inconsistent paths
   - Missing or redundant information
   - Formatting inconsistencies

4. **Sync check**: If `templates/HPD_Report_Style_Prompt.md` exists, compare it to `06_Workspace_Management/docs/templates/HPD_Report_Style_Prompt.md`. If the 06_Workspace_Management version is newer or different, update the Report_Styles copy to match (or note the divergence in README).

5. **Report** what you changed (or confirm no changes were needed).

## Paths (adjust if your workspace differs)

- Report_Styles: `08_Templates/Report_Styles/` or `C:\Users\carucci_r\OneDrive - City of Hackensack\08_Templates\Report_Styles\`
- Canonical style prompt: `06_Workspace_Management/docs/templates/HPD_Report_Style_Prompt.md`
- Reference HTML example: `06_Workspace_Management/docs/response_time/Response_Time_Correction_Report_Chief_Antista_2026_02_26.html`

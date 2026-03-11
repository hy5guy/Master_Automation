# Prompt: Create 09_Reference Report Styles Directory

**Use this prompt with Claude (in Cursor or Claude Code) to create a new reference directory for report styles, HTML templates, and monthly reports.**

---

## Instructions

Copy everything below the line and paste it into a new Claude chat. Claude will create the directory structure and files.

---

Create a new directory under `C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference` for report styles, HTML templates, and monthly reports. Follow the conventions used by sibling directories (Personnel, Standards) — include a README, clear structure, and documentation.

## Target Structure

```
09_Reference/
└── Report_Styles/
    ├── README.md                 # Index, purpose, and usage
    ├── html/                     # HTML report templates and styled outputs
    │   └── .gitkeep              # (or a sample template if preferred)
    ├── monthly/                  # Monthly report templates and examples
    │   └── .gitkeep
    ├── scrap/                    # Scrap reports, quick one-offs, ad-hoc outputs
    │   └── .gitkeep
    ├── templates/                # Reusable AI prompts and style definitions
    │   └── HPD_Report_Style_Prompt.md   # Copy from Master_Automation/docs/templates/
    └── CLAUDE.md                 # AI instructions for this directory
```

## Requirements

1. **README.md** — Explain:
   - Purpose: Central reference for Hackensack PD report styles, HTML design system, monthly report templates, and scrap/quick reports
   - How to use: Point to `templates/HPD_Report_Style_Prompt.md` when generating HTML reports
   - Relationship to Master_Automation: Style prompt is canonical in `Master_Automation/docs/templates/HPD_Report_Style_Prompt.md`; this copy is for 09_Reference consumers
   - Subdirectory roles: `html/` for styled HTML outputs, `monthly/` for monthly report templates, `scrap/` for ad-hoc reports

2. **templates/HPD_Report_Style_Prompt.md** — Copy the full content from:
   `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\docs\templates\HPD_Report_Style_Prompt.md`
   (Or add a README in templates/ that points to the canonical location if you prefer not to duplicate.)

3. **CLAUDE.md** — Brief AI instructions:
   - When generating HTML reports for Hackensack PD, use the design system in `templates/HPD_Report_Style_Prompt.md`
   - Output styled HTML reports to `html/` or `scrap/` as appropriate
   - Monthly report templates go in `monthly/`
   - Colors: Navy #1a2744, Gold #c8a84b, self-contained HTML only

4. **Subdirectories** — Create `html/`, `monthly/`, `scrap/`, `templates/` with `.gitkeep` files so empty directories are tracked (or omit .gitkeep if your repo handles empty dirs).

## Context

- **09_Reference** holds canonical reference data and standards (Personnel, Standards, Classifications).
- **Report_Styles** will hold report formatting standards, HTML design system, and report templates so they live alongside other reference material.
- **Master_Automation** remains the primary project for ETL and Power BI; its `docs/templates/HPD_Report_Style_Prompt.md` is the source of truth. This 09_Reference copy makes the style guide discoverable for projects that only use 09_Reference.

## Optional

- Add `09_Reference/Report_Styles` to any parent README or index if one exists.
- If 09_Reference has a top-level README, add a line for Report_Styles in the directory list.

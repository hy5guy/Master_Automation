---
name: M Code Folder Reorganization
overview: Reorganize M code into cleaner per-visual folders (remu, chief, social_media) and update the visual export mapping to mirror the same structure.
todos:
  - id: create-folders
    content: "Create new m_code folders: remu/, chief/, social_media/"
    status: completed
  - id: move-remu
    content: Move ___REMU.m from patrol/ to remu/ and update header
    status: completed
  - id: move-chief
    content: Move ___Chief2.m from patrol/ to chief/ and ___chief_projects.m from community/ to chief/, update headers
    status: completed
  - id: move-social
    content: Move ___Social_Media.m from stacp/ to social_media/ and update header
    status: completed
  - id: update-mapping
    content: Update visual_export_mapping.json target_folder values for chief and social_media entries
    status: completed
  - id: update-claude-md
    content: Update CLAUDE.md m_code project map with new folder structure
    status: completed
isProject: false
---

# M Code Folder Reorganization

## Current vs Proposed Structure

```mermaid
flowchart LR
    subgraph current ["Current"]
        P1["patrol/"]
        P1a["___Patrol.m"]
        P1b["___Chief2.m"]
        P1c["___REMU.m"]
        C1["community/"]
        C1a["___Combined_Outreach_All.m"]
        C1b["___chief_projects.m"]
        S1["stacp/"]
        S1a["___STACP_pt_1_2.m"]
        S1b["STACP_DIAGNOSTIC.m"]
        S1c["___Social_Media.m"]
    end

    subgraph proposed ["Proposed"]
        P2["patrol/"]
        P2a["___Patrol.m"]
        R2["remu/"]
        R2a["___REMU.m"]
        CH2["chief/"]
        CH2a["___Chief2.m"]
        CH2b["___chief_projects.m"]
        C2["community/"]
        C2a["___Combined_Outreach_All.m"]
        SM2["social_media/"]
        SM2a["___Social_Media.m"]
        ST2["stacp/"]
        ST2a["___STACP_pt_1_2.m"]
        ST2b["STACP_DIAGNOSTIC.m"]
    end
```



## File Moves


| File | From | To  |
| ---- | ---- | --- |


- `___REMU.m`: `m_code/patrol/` --> `m_code/remu/`
- `___Chief2.m`: `m_code/patrol/` --> `m_code/chief/`
- `___chief_projects.m`: `m_code/community/` --> `m_code/chief/`
- `___Social_Media.m`: `m_code/stacp/` --> `m_code/social_media/`

## Folders After Reorganization

- `m_code/patrol/` -- only `___Patrol.m`
- `m_code/remu/` -- `___REMU.m` (new folder)
- `m_code/chief/` -- `___Chief2.m` + `___chief_projects.m` (new folder)
- `m_code/community/` -- only `___Combined_Outreach_All.m`
- `m_code/social_media/` -- `___Social_Media.m` (new folder)
- `m_code/stacp/` -- `___STACP_pt_1_2.m` + `STACP_DIAGNOSTIC.m`

## Visual Export Mapping Updates

**File**: [Standards/config/powerbi_visuals/visual_export_mapping.json](Standards/config/powerbi_visuals/visual_export_mapping.json)

Changes to `target_folder` values:

- "Chief Michael Antista's Projects and Initiatives": `chief_projects` --> `chief`
- "Chief Law Enforcement Executive Duties": `law_enforcement_duties` --> `chief`
- "Social Media Posts": `social_media_and_time_report` --> `social_media`
- "Monthly Accrual and Usage Summary": stays at `social_media_and_time_report` (unchanged)
- `patrol` and `remu`: already correct, no changes needed

## Header Updates

Each moved `.m` file gets its `// # path` header comment updated to reflect the new folder location (e.g., `// # remu/___REMU.m`).

## Documentation Updates

Update [CLAUDE.md](CLAUDE.md) project map -- add `remu/`, `chief/`, `social_media/` to the m_code subfolder listing and remove the moved files from their old folder descriptions.
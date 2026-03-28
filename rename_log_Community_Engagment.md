# Rename Reference Map: Community_Engagment -> Community_Engagement
## Generated: 2026-03-28

## Summary
- Total files with references: 151 (18 in Community_Engagment repo, 129 in 06_Workspace_Management, 2 in 02_ETL_Scripts/config, 1 in Summons docs, 1 in 02_ETL_Scripts root README)
- Total actionable files (non-chatlog, non-archive): 42
- STOP flags: 2 (Windows Scheduled Task XMLs)
- Chatlog/archive files (historical, no action): ~109

## STOP FLAGS

### task_schedule.xml (Windows Scheduled Task)
| Line | Content | Type | Action |
|------|---------|------|--------|
| 40 | `<Arguments>C:\Users\carucci_r\...\Community_Engagment\src\main_processor.py</Arguments>` | Scheduled Task XML | **DO NOT MODIFY** -- must be re-imported via Task Scheduler after filesystem rename |
| 41 | `<WorkingDirectory>C:\Users\carucci_r\...\Community_Engagment</WorkingDirectory>` | Scheduled Task XML | **DO NOT MODIFY** -- must be re-imported via Task Scheduler after filesystem rename |

### task_schedule (1).xml (Windows Scheduled Task backup)
| Line | Content | Type | Action |
|------|---------|------|--------|
| 40 | `<Arguments>C:\Users\carucci_r\...\Community_Engagment\src\main_processor.py</Arguments>` | Scheduled Task XML | **DO NOT MODIFY** |
| 41 | `<WorkingDirectory>C:\Users\carucci_r\...\Community_Engagment</WorkingDirectory>` | Scheduled Task XML | **DO NOT MODIFY** |

**Manual action required:** After filesystem rename, update the Windows Scheduled Task via Task Scheduler GUI or `schtasks /Change` to point to `Community_Engagement`.

---

## Reference Map -- Actionable Files

### 02_ETL_Scripts/Community_Engagment/CLAUDE.md
| Line | Content | Type | Action |
|------|---------|------|--------|
| 3 | `> **Repo**: \`Community_Engagment\` (note: directory name has typo...)` | doc reference | find-replace |
| 148 | `\| \`Community_Engagment.code-workspace\` \| VS Code workspace file \|` | doc reference | find-replace |
| 224 | `1. **Directory name typo**: \`Community_Engagment\` missing 'e'...` | doc reference | find-replace / remove note |
| 256 | `cd "C:\Users\carucci_r\...\Community_Engagment"` | hardcoded path | find-replace |

### 02_ETL_Scripts/Community_Engagment/findings.json
| Line | Content | Type | Action |
|------|---------|------|--------|
| 2 | `"repo": "Community_Engagment"` | JSON field | find-replace |
| 50 | `"Rename directory: Community_Engagment -> Community_Engagement..."` | JSON field | find-replace / mark resolved |
| 65 | `"CRITICAL: Directory name typo 'Community_Engagment'..."` | JSON field | find-replace / mark resolved |
| 73 | `"commit_message": "docs(Community_Engagment):..."` | JSON field | find-replace |

### 02_ETL_Scripts/Community_Engagment/monitor_etl.py
| Line | Content | Type | Action |
|------|---------|------|--------|
| 4 | `sys.path.append(r"...\Community_Engagment")` | hardcoded path | find-replace |

### 02_ETL_Scripts/Community_Engagment/project_scaffold.py
| Line | Content | Type | Action |
|------|---------|------|--------|
| 14 | `base_dir = Path(r"...\Community_Engagment")` | hardcoded path | find-replace |
| 99 | `"output_dir": r"...\Community_Engagment\data\output"` | hardcoded path | find-replace |
| 100 | `"backup_dir": r"...\Community_Engagment\data\backup"` | hardcoded path | find-replace |
| 101 | `"logs_dir": r"...\Community_Engagment\logs"` | hardcoded path | find-replace |
| 159 | `Community_Engagment/` | directory tree | find-replace |

### 02_ETL_Scripts/Community_Engagment/Combined_Outreach_All.m
| Line | Content | Type | Action |
|------|---------|------|--------|
| 7 | `OutputFolder = "...\Community_Engagment\output\"` | M code path | find-replace |

### 02_ETL_Scripts/Community_Engagment/src/___Combined_Outreach_All.m
| Line | Content | Type | Action |
|------|---------|------|--------|
| 8 | `"...\Community_Engagment\output\"` | M code path | find-replace |

### 02_ETL_Scripts/Community_Engagment/SUMMARY.md
| Line | Content | Type | Action |
|------|---------|------|--------|
| 33 | `1. Directory name typo: \`Community_Engagment\` (missing 'e').` | doc reference | find-replace / mark resolved |

### 02_ETL_Scripts/Community_Engagment/README.md
| Line | Content | Type | Action |
|------|---------|------|--------|
| 9 | `**Note:** The directory name \`Community_Engagment\` contains a typo...` | doc reference | find-replace / remove warning |
| 38 | `Community_Engagment/` | directory tree | find-replace |
| 76 | `cd "...\Community_Engagment"` | hardcoded path | find-replace |

### 02_ETL_Scripts/Community_Engagment/reorganization_proposal.md
| Line | Content | Type | Action |
|------|---------|------|--------|
| 10 | `**Current:** \`Community_Engagment\` (missing 'e')` | doc reference | find-replace |
| 18 | `\`Community_Engagment.code-workspace\` filename` | doc reference | find-replace |

### 02_ETL_Scripts/Community_Engagment/CHANGELOG.md
| Line | Content | Type | Action |
|------|---------|------|--------|
| 24 | `Directory name typo: \`Community_Engagment\` should be \`Community_Engagement\`.` | doc reference | find-replace / mark resolved |

### 02_ETL_Scripts/config/scripts.json
| Line | Content | Type | Action |
|------|---------|------|--------|
| 24 | `"path": "C:\\Users\\carucci_r\\...\\Community_Engagment"` | JSON config | find-replace |

### 02_ETL_Scripts/config/VERIFICATION_REPORT.md
| Line | Content | Type | Action |
|------|---------|------|--------|
| 31 | `**Path**: \`C:\Users\carucci_r\...\Community_Engagment\`` | doc reference | find-replace |
| 106 | `The "Community_Engagment" directory has a typo...` | doc reference | find-replace |

### 06_Workspace_Management/CLAUDE.md
| Line | Content | Type | Action |
|------|---------|------|--------|
| 144 | `02_ETL_Scripts/Community_Engagment/` | doc reference | find-replace |
| 308 | `\| Community_Engagment \| Community outreach tracking...` | table row | find-replace |
| 314 | `Note: Directory name \`Community_Engagment\` has a typo...` | doc note | find-replace / remove |
| 345 | `\| Community_Engagment \| \`racmac57/Community_Engagement.git\`...` | table row | find-replace |
| 371 | `9. **\`Community_Engagment\` directory typo**...` | known issues | find-replace / mark resolved |

### 06_Workspace_Management/cross_repo_audit.md
| Line | Content | Type | Action |
|------|---------|------|--------|
| 6 | Header row with `Community_Engagment` | table header | find-replace |
| 21 | `Community_Engagment: 7 dead scripts` | text | find-replace |
| 43 | `Community_Engagment \| JSON` | table row | find-replace |
| 69 | `Community_Engagment (missing 'e')` | naming issue row | find-replace / mark resolved |
| 77 | Header row with `Community_Engagment` | table header | find-replace |
| 90+ | Multiple table rows and references | various | find-replace |
| 289 | `Rename \`Community_Engagment\` to \`Community_Engagement\`` | recommendation | mark resolved |

### 06_Workspace_Management/HUMAN_REVIEW.md
| Line | Content | Type | Action |
|------|---------|------|--------|
| 23 | `## Community_Engagment (7 items)` | section header | find-replace |
| 26 | `**Directory name typo**: \`Community_Engagment\`...` | review item | mark RESOLVED |
| 114 | `Community_Engagment (dir rename)` | summary table | find-replace |

### 06_Workspace_Management/findings.json
| Line | Content | Type | Action |
|------|---------|------|--------|
| 73 | `CRITICAL: Community_Engagment directory name typo...` | JSON | find-replace / mark resolved |

### 06_Workspace_Management/config/scripts.json
| Line | Content | Type | Action |
|------|---------|------|--------|
| 76 | `"path": "C:\\Users\\carucci_r\\...\\Community_Engagment"` | JSON config | find-replace |

### 06_Workspace_Management/config/scripts-PD_BCI_LTP.json
| Line | Content | Type | Action |
|------|---------|------|--------|
| 24 | `"path": "C:\\Users\\carucci_r\\...\\Community_Engagment"` | JSON config | find-replace |

### 06_Workspace_Management/m_code/community/___Combined_Outreach_All.m
| Line | Content | Type | Action |
|------|---------|------|--------|
| 13 | `OutputFolder = "...\Community_Engagment\output\"` | M code path | find-replace |

### 06_Workspace_Management/m_code/community/___Combined_Outreach_All.txt
| Line | Content | Type | Action |
|------|---------|------|--------|
| 11 | `OutputFolder = "...\Community_Engagment\output\"` | M code path | find-replace |

### 06_Workspace_Management/m_code/tmdl_export/tables/___Combined_Outreach_All.tmdl
| Line | Content | Type | Action |
|------|---------|------|--------|
| 202 | `OutputFolder = "...\Community_Engagment\output\"` | TMDL/M code path | find-replace |

### 06_Workspace_Management/m_code/2026_03_09_all_queries.m
| Line | Content | Type | Action |
|------|---------|------|--------|
| 688 | `OutputFolder = "...\Community_Engagment\output\"` | M code path | find-replace |

### 06_Workspace_Management/m_code/all_m_code_26_january_monthly.m
| Line | Content | Type | Action |
|------|---------|------|--------|
| 857 | `OutputFolder = "...\Community_Engagment\output\"` | M code path | find-replace |

### 06_Workspace_Management/m_code/2026_02_26_template_m_codes.m
| Line | Content | Type | Action |
|------|---------|------|--------|
| 652 | `OutputFolder = "...\Community_Engagment\output\"` | M code path | find-replace |

### 06_Workspace_Management/m_code/2026_03_05_combined_outreach.txt
| Line | Content | Type | Action |
|------|---------|------|--------|
| 7 | `OutputFolder = "...\Community_Engagment\output\"` | M code path | find-replace |

### 06_Workspace_Management/docs/2026_03_05_combined_outreach.txt
| Line | Content | Type | Action |
|------|---------|------|--------|
| 7 | `OutputFolder = "...\Community_Engagment\output\"` | M code path | find-replace |

### 06_Workspace_Management/scripts/community_engagement_data_flow_check.py
| Line | Content | Type | Action |
|------|---------|------|--------|
| 30 | `SOURCE_DIR = r'...\Community_Engagment'` | hardcoded path | find-replace |

### 06_Workspace_Management/scripts/diagnose_community_engagement_missing.py
| Line | Content | Type | Action |
|------|---------|------|--------|
| 13 | `ETL_OUTPUT = r"...\Community_Engagment\output\..."` | hardcoded path | find-replace |

### 06_Workspace_Management/swarm_run_report_2026-03-28.md
| Line | Content | Type | Action |
|------|---------|------|--------|
| Multiple | 20+ references throughout | doc/report | find-replace |

### 06_Workspace_Management/push_report.md
| Line | Content | Type | Action |
|------|---------|------|--------|
| 6 | `Community_Engagment` in push table | doc/report | find-replace |

### 06_Workspace_Management/CHANGELOG.md
| Line | Content | Type | Action |
|------|---------|------|--------|
| 99 | `02_ETL_Scripts/Community_Engagment/` | doc reference | find-replace |
| 436 | `02_ETL_Scripts/Community_Engagment` | doc reference | find-replace |
| 444 | `02_ETL_Scripts/Community_Engagment/` | doc reference | find-replace |

### 06_Workspace_Management/README.md
| Line | Content | Type | Action |
|------|---------|------|--------|
| 27 | `Community_Engagment \`CHANGELOG.md\`` | doc reference | find-replace |
| 197 | `"path": "...\Community_Engagment"` | embedded JSON | find-replace |

### 06_Workspace_Management/docs/ (active docs, not chatlogs)
| File | Lines | Type | Action |
|------|-------|------|--------|
| handoffs/HANDOFF_Community_Outreach_PBIX_2026_03_25.md | 16, 18, 86, 99 | doc paths | find-replace |
| POST_SESSION_ACTION_ITEMS.md | 149 | doc reference | find-replace |
| Community_Outreach_YTD_And_Combined_Outreach_Import_2026_03.md | 30 | doc path | find-replace |
| cursor_prompt_fix_duration_and_attendees.md | 198, 252 | doc paths | find-replace |
| Response_Time_ETL_Golden_Standard_And_CallType_Mapping.md | 230, 408 | doc paths | find-replace |
| VISUAL_EXPORT_GUIDE.md | 18, 84 | doc paths | find-replace |
| PRE_RUN_CHECKLIST_2026_02_09.md | 38, 49, 73, 239 | hardcoded paths | find-replace |
| BACKFILL_DATA_PATHS.md | 84 | doc path | find-replace |
| PROMPT_Fix_Social_Media_MMYY_Columns.md | 16, 159, 168 | doc paths | find-replace |
| SCRIPT_FILENAME_UPDATE_SUMMARY.md | 65 | doc path | find-replace |
| DIRECTORY_STRUCTURE_RECOMMENDATION.md | 29, 49 | doc paths | find-replace |
| VERIFICATION_REPORT-PD_BCI_LTP.md | 31, 106 | doc paths | find-replace |
| Monthly_Report_Data_Population_Technical_Summary.html | 174, 212 | HTML paths | find-replace |

### 06_Workspace_Management/outputs/metadata/scripts_duplicate.json
| Line | Content | Type | Action |
|------|---------|------|--------|
| 24 | `"path": "...\Community_Engagment"` | JSON config | find-replace |

### 06_Workspace_Management/config/scripts.json.backup_20260217_210333
| Line | Content | Type | Action |
|------|---------|------|--------|
| N/A | backup of old config | backup file | find-replace (it's in repo) |

---

## Chatlog / Archive Files (NO ACTION -- historical records)

~109 files in `06_Workspace_Management/docs/chatlogs/` and `m_code/archive/` directories. These are historical chat transcripts, chunks, and sidecar JSON files. They record what the path *was* at the time. Modifying them would falsify historical records.

Also: `02_ETL_Scripts/Summons/documents/2025_11_10_16_15_52_cursor_stage_commit_and_push_changes_to.md` -- historical chatlog, no action.

Also: `02_ETL_Scripts/Community_Engagment/documents/` (6 files) -- historical chatlogs within the repo, no action.

---

## Post-Rename Manual Actions Required

1. **Windows Task Scheduler**: Update the scheduled task to use `Community_Engagement` path (task_schedule.xml is reference only; the live task is in Task Scheduler)
2. **Power BI**: Update M code data source path in the live .pbix file (the M code files here are exports/references, not the live source)
3. **VS Code**: Rename `Community_Engagment.code-workspace` to `Community_Engagement.code-workspace`

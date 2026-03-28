# Handoff: AI_Context_Reference Sheet Injection — 2026-03-28

## Status: 3/10 workbooks working, 7 need debugging

### What works (injection verified clean in Excel)
| Workbook | Path |
|----------|------|
| csb_monthly.xlsm | `Contributions/CSB/csb_monthly.xlsm` |
| chief_monthly.xlsx | `Contributions/Chief/chief_monthly.xlsx` |
| Drone_Monthly.xlsx | `Contributions/Drone_Monthly.xlsx` |

### What's broken (restored to pre-injection state)
| Workbook | Path |
|----------|------|
| STACP.xlsm | `Contributions/STACP/STACP.xlsm` |
| patrol_monthly.xlsm | `Contributions/Patrol/patrol_monthly.xlsm` |
| Policy_Training_Monthly.xlsx | `Contributions/Policy_Training/Policy_Training_Monthly.xlsx` |
| detectives_monthly.xlsx | `Contributions/Detectives/detectives_monthly.xlsx` |
| ESU.xlsx | `Contributions/ESU/ESU.xlsx` |
| Traffic_Monthly.xlsx | `Contributions/Traffic/Traffic_Monthly.xlsx` |
| dfr_directed_patrol_enforcement.xlsx | `Contributions/Drone/dfr_directed_patrol_enforcement.xlsx` |

All 7 are restored to clean state from `archive/*_pre_injection.*` backups. They are NOT corrupted.

---

## Architecture

### Script: `scripts/inject_ai_context_reference.py`

**v3 approach (current):**
1. **Analyze** workbook via openpyxl read-only (never saves target)
2. **Build** AI_Context_Reference sheet in a temp .xlsx via openpyxl
3. **Extract** sheet XML from temp, convert shared strings → inline strings, strip style indices (via ElementTree on TEMP file only)
4. **Post-process** sheet XML: add `standalone="yes"`, `xmlns:r` namespace declaration
5. **Inject** into target zip via TEXT-LEVEL string insertion:
   - `xl/workbook.xml` — insert `<sheet>` before `</sheets>`
   - `xl/_rels/workbook.xml.rels` — insert `<Relationship>` before `</Relationships>`
   - `[Content_Types].xml` — insert `<Override>` before `</Types>`
6. **Copy** all other zip entries byte-for-byte (preserving ZipInfo objects)
7. `xl/styles.xml` is NEVER touched

### Key safety rules (memory: `feedback_xlsx_zip_surgery.md`)
- NEVER use openpyxl load+save on target (strips Data Validation, Conditional Formatting, Web Extensions)
- NEVER parse target XML through ElementTree (drops namespace declarations, `mc:Ignorable`)
- When removing formulas, MUST clean `xl/calcChain.xml` (orphaned entries trigger repair dialog)
- MUST preserve ZipInfo objects when rewriting zip entries
- MUST include `standalone="yes"` and `xmlns:r` in injected sheet XML declaration

---

## What we've ruled out

1. ~~openpyxl load+save corruption~~ — v1 issue, rewritten in v2/v3
2. ~~ElementTree on target XML~~ — v2 issue, rewritten in v3 to use text-level insertion
3. ~~Missing `standalone="yes"`~~ — added in v3 fix
4. ~~Missing `xmlns:r` namespace~~ — added in v3 fix
5. ~~calcChain.xml orphaned entries~~ — only relevant for Drone circular ref fix, not general injection

## What we haven't tested

- **Whether the 3 metadata file text insertions are byte-correct** for the 7 broken workbooks. The text replacements target `</sheets>`, `</Relationships>`, `</Types>` — if any of these have whitespace, namespace prefixes, or BOM differences, the insertions could be malformed.
- **Whether the injected sheet XML needs additional namespace declarations** beyond `xmlns:r` (e.g., `xmlns:mc`, `mc:Ignorable`, `xmlns:x14ac`). The 3 working workbooks may have passed by coincidence.
- **Whether Python's `zipfile.ZIP_DEFLATED` recompression** of the 3 modified metadata files changes something Excel cares about (CRC, compression ratio, etc.)
- **Whether there are workbook-level XML elements** (e.g., `<definedNames>`, `<calcPr>`) that reference sheet indices and are invalidated by the new sheet.
- **Binary diff of a broken workbook** (injection output vs pre-injection backup) to isolate exactly which bytes changed.

---

## Drone_Monthly circular reference fix (COMPLETE)

11 cells fixed via zip-level XML surgery + calcChain cleanup:

**DFR Activity sheet (sheet2.xml):**
- K3, L3, M3 — shared formula group removed → plain value `0`
- M4 — shared ref removed → plain value `0`
- K10, L10, M10 — self-referencing shared refs → plain value `0`
- C11 — column ref B→C: `=$C$9+$C$10`

**Non-DFR sheet (sheet4.xml):**
- C4 — shared master, column B→C: `=$C$2+$C$3`
- D4 — shared ref → explicit: `=$D$2+$D$3`
- H4 — shared ref → explicit: `=$H$2+$H$3`

**calcChain.xml:** 7 orphaned entries removed (K3/L3/M3/M4/K10/L10/M10 with i="4")

---

## `/fix-excel` slash command (COMPLETE)

Located at:
- `~/.claude/commands/fix-excel.md` (global)
- `.claude/commands/fix-excel.md` (project)

Documents the safe zip-level Excel editing process for future cell-level fixes.

---

## Backup locations

All pre-injection backups are in `archive/` subfolders with timestamp `20260328_042448` through `20260328_042457`:
- `CSB/archive/csb_monthly_20260328_042448_pre_injection.xlsm`
- `STACP/archive/STACP_20260328_042450_pre_injection.xlsm`
- `Patrol/archive/patrol_monthly_20260328_042451_pre_injection.xlsm`
- `Policy_Training/archive/Policy_Training_Monthly_20260328_042452_pre_injection.xlsx`
- `Detectives/archive/detectives_monthly_20260328_042454_pre_injection.xlsx`
- `ESU/archive/ESU_20260328_042455_pre_injection.xlsx`
- `Traffic/archive/Traffic_Monthly_20260328_042456_pre_injection.xlsx`
- `Chief/archive/chief_monthly_20260328_042456_pre_injection.xlsx`
- `archive/Drone_Monthly_20260328_042457_pre_injection.xlsx`
- `Drone/archive/dfr_directed_patrol_enforcement_20260328_042457_pre_injection.xlsx`

Earlier backups from v1/v2 attempts also exist (timestamps `_041311` through `_041320`).

---

## Files modified this session

| File | Change |
|------|--------|
| `scripts/inject_ai_context_reference.py` | Rewritten from v1 (openpyxl save) → v2 (zip + ET) → v3 (zip + text-level). Current state is v3. |
| `.claude/commands/fix-excel.md` | New slash command for safe Excel editing |
| `CLAUDE.md` | Updated to v1.20.0-rc |
| `SUMMARY.md` | Updated to v1.20.0-rc |
| `CHANGELOG.md` | Added v1.20.0 entry |
| `docs/handoffs/HANDOFF_AI_Context_Injection_2026_03_28.md` | This file |

---

## Recommended next steps

1. **Diagnose root cause** on ONE broken workbook (e.g., Traffic_Monthly.xlsx — simplest at 26 sheets):
   - Copy to temp, inject, compare zip byte-for-byte with backup
   - Check each of the 3 modified XML files for malformed content
   - Test: does the file open if you ONLY add the sheet XML + content type override (skip workbook.xml and rels changes)?
   - Test: does the file open if you copy the exact sheet XML from a working workbook?

2. **Check for BOM or encoding differences** in the 3 metadata files between working and broken workbooks

3. **Consider alternative injection approach**: Use Excel COM automation via `win32com.client` (or `xlwings`) instead of zip manipulation — this is the most reliable method since Excel itself handles all XML consistency

4. Once fixed, re-run on the 7 remaining workbooks and verify all open clean

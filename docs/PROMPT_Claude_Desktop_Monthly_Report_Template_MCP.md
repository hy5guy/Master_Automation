# Claude Desktop MCP Prompts — Monthly_Report_Template.pbix

**Use with:** Claude Desktop + Power BI MCP (connected, working).  
**Target:** `Monthly_Report_Template.pbix` (gold template; path may be `08_Templates\` or as opened in Desktop).  
**Paste:** Use **Main**, **Concise**, or **Detailed** blocks as-is; adjust bracketed placeholders if needed.

---

## How to use these prompts

1. Open the template in **Power BI Desktop** (or ensure MCP targets the correct semantic model).
2. Paste the chosen prompt into Claude Desktop.
3. If Claude needs scope, add one line: *“Workspace repo: `06_Workspace_Management`; M source of truth: `m_code/`.”*
4. For **directory consolidation, path refactors, PowerBI_Data vs PowerBI_Date, template folder moves (08 vs 15), or batch M updates**, point Claude at the chatlog below and/or attach the transcript.

---

## Additional context — Directory consolidation (ground truth)

**Location (OneDrive):**  
`C:\Users\carucci_r\OneDrive - City of Hackensack\14_Workspace\chatlogs\Directory_Consolidation_Documentation_Update_And_Commit`

**Contents:** Claude session artifacts for the workspace directory consolidation: transcript (`*_transcript.md`), sidecar JSON, and chunked text (`chunk_00000.txt` …). Use when prompts involve **canonical paths**, **what was renamed when**, **Phase 4 M-code / config refactors**, or **“treat directory consolidation documentation as ground truth”** (as in monthly report enhancement specs).

**Related checklist in this repo:**  
[`_consolidation_project/IMPLEMENTATION_CHECKLIST_Directory_Consolidation.md`](../_consolidation_project/IMPLEMENTATION_CHECKLIST_Directory_Consolidation.md) — phase status; cross-check with the chatlog for narrative and decisions.

**Paste snippet for Claude Desktop (prepend to any prompt when needed):**

```text
Additional context: Read or summarize the directory consolidation session under:
C:\Users\carucci_r\OneDrive - City of Hackensack\14_Workspace\chatlogs\Directory_Consolidation_Documentation_Update_And_Commit
(especially *_transcript.md). Use it as ground truth for path changes, template locations (e.g. 08_Templates), PowerBI_Data naming, and batch refactor scope. If repo checklist differs, note the conflict.
```

---

# Prompt 1 — Refresh failures and blocked queries

### 1a. Main prompt

**Context**  
I am working on the CompStat **Monthly_Report_Template.pbix** connected via MCP. After changing **pReportMonth** or refreshing, some Power Query queries fail on Close & Apply.

**Task**  
Identify all queries that are in error or blocked, summarize the root cause from query metadata or error text, and recommend fixes (ETL file missing, M logic, path, or parameter).

**Instructions**  
- List query names in failure state with exact error messages.  
- Group by theme (e.g. missing source file, permission, type, relationship).  
- For “missing file” errors, infer required filename pattern and month from M code if visible.  
- Do not guess paths; quote only what the model or error shows.

**Constraints**  
- Do not modify the model unless I explicitly ask in a follow-up.  
- Prefer facts from the connected PBIX / MCP over generic Power BI advice.

**Output format**  
1. Executive summary (3–5 bullets)  
2. Table: `Query | Error snippet | Likely cause | Suggested fix`  
3. Ordered checklist of actions (ETL vs M vs Desktop steps)

### 1b. Concise

`Monthly_Report_Template.pbix` via MCP: list all Power Query queries in error after refresh. Table: name, error text, likely fix. No model changes.`

### 1c. Detailed

**Context:** Gold monthly template; `pReportMonth` drives windows; some queries error on load.  
**Task:** Full diagnostic of failed/blocked queries with actionable remediation.  
**Instructions:** Enumerate failures; for each, trace whether error is file discovery, `error` in M, firewall, credential, or schema. Cross-check arrest/summons/response-time style queries for month-offset logic vs required `YYYY_MM` files. Suggest running specific ETL `--report-month` values only when M code or errors justify it.  
**Constraints:** Read-only analysis first; cite query names exactly as in the model.  
**Output:** Summary bullets + markdown table + numbered remediation list + “verify after” short list.

### 1d. Suggested output format for Claude

- **Failed queries:** markdown table  
- **Remediation:** numbered list grouped by ETL / M / manual file placement  
- **Risks:** short “if you change X, watch Y”

---

# Prompt 2 — pReportMonth consistency audit

### 2a. Main prompt

**Context**  
The template uses parameter **pReportMonth** (date, first of report month). Rolling windows and filters must not use `DateTime.LocalNow()` or `TODAY()` in M where the project standard is pReportMonth-driven.

**Task**  
Audit Power Query (M) for: (1) references to `pReportMonth`, (2) any `DateTime.LocalNow`, `DateTimeZone.LocalNow`, or obvious “today” patterns, (3) inconsistent month boundaries (e.g. EndOfMonth vs previous month).

**Instructions**  
- Produce a table per query: uses pReportMonth? (Y/N), red flags, one-line note.  
- Flag queries that mix “report month” and “previous month” without comment.  
- Do not rewrite M unless I ask.

**Constraints**  
Work from the connected model; if a query body is not fully exposed via MCP, state that limitation.

**Output format**  
1. Compliance summary (% or count)  
2. Query audit table  
3. List of queries needing human review  
4. Optional: single paragraph on arrest queries if both “report month” and “previous month” patterns appear

### 2b. Concise

`Via MCP on Monthly_Report_Template.pbix: audit all M queries for pReportMonth usage and any DateTime.LocalNow/TODAY. Table: query, compliant Y/N, notes. Read-only.`

### 2c. Detailed

**Context:** Hackensack PD monthly CompStat; immutable snapshot per report month; repo standard windows use `Date.EndOfMonth(pReportMonth)` and `Date.StartOfMonth(Date.AddMonths(pReportMonth,-12))` where applicable.  
**Task:** Systematic M audit for time intelligence and parameter discipline.  
**Instructions:** Scan each query; classify: parameter-driven, static date, relative now, or hybrid. Highlight mismatches between queries that should align (e.g. summons 13-month vs arrest month file selection). Note DAX measures that use TODAY/NOW if MCP exposes them.  
**Constraints:** No edits; flag uncertainty explicitly.  
**Output:** Compliance stats + sortable table + prioritized fix list (P0/P1/P2).

### 2d. Suggested output format

- **Summary:** 5 bullets max  
- **Table:** columns `Query | Parameter OK | Anti-patterns | Severity | Notes`  
- **Appendix:** queries MCP could not fully read

---

# Prompt 3 — DAX inventory and measure health

### 3a. Main prompt

**Context**  
The template has many DAX measures (including YTD, subtitles, and visual-specific measures).

**Task**  
Produce an inventory of measures: table name, measure name, brief purpose if inferable from name/expression, and flag measures that reference non-existent columns/tables if errors are visible.

**Instructions**  
- Group measures by display folder or home table if available.  
- Flag duplicate or near-duplicate names.  
- List measures with errors or “Semantic error” state.

**Constraints**  
Read-only unless I request patches.

**Output format**  
1. Count by table  
2. Alphabetical or grouped list  
3. Error measures table  
4. Suggestions for consolidation (optional)

### 3b. Concise

`MCP on Monthly_Report_Template.pbix: export list of all DAX measures (table, name, error state if any). Group by table. Read-only.`

### 3c. Detailed

**Context:** Large model; YTD and subtitle measures added over time; need documentation and error scan.  
**Task:** Build measure catalog suitable for handoff to another developer.  
**Instructions:** For each measure: home table, name, format string if any, description annotation if any, expression length (not necessarily full paste unless short). Identify broken measures and dependency chains if tooling allows. Highlight measures using `TODAY()` or `NOW()`.  
**Constraints:** Do not change measures.  
**Output:** Markdown: TOC + tables by table + “broken” section + “TODAY/NOW” section.

### 3d. Suggested output format

- **Measures by table:** nested bullet or table  
- **Errors:** `Measure | Table | Error text`  
- **TODAY/NOW:** bullet list

---

# Prompt 4 — Align template pages with export mapping

### 4a. Main prompt

**Context**  
Visual exports are routed using `visual_export_mapping.json` (page names and `match_pattern`). Report page names in the PBIX should match or be deliberately mapped.

**Task**  
Compare report **page names** in the template to a list I will paste from `visual_export_mapping.json` (or summarize unique `page_name` values). Report mismatches and renames needed.

**Instructions**  
- List PBIX pages vs mapping `page_name` values.  
- Flag pages with no mapping entry.  
- Suggest canonical names (underscores vs spaces) — one recommendation only.

**Constraints**  
I will paste mapping JSON excerpt or unique page names in a follow-up message if you ask.

**Output format**  
1. Match / mismatch table  
2. Renames to apply in Desktop (from → to)  
3. JSON lines to update (high level, not full file)

### 4b. Concise

`List all report page names in Monthly_Report_Template.pbix via MCP. I will paste mapping `page_name` list next; diff and suggest renames.`

### 4c. Detailed

**Context:** Repo uses `Standards/config/powerbi_visuals/visual_export_mapping.json`; `page_name` is metadata for traceability; Processed_Exports pipeline uses `match_pattern` for files.  
**Task:** Reconciliation between PBIX page tabs and mapping.  
**Instructions:** Extract exact page names from model/report. Compare to provided mapping list. Identify orphans both sides. Propose minimal rename set to align. Note new pages (e.g. Summons_YTD) that need new mapping entries later when exports exist.  
**Constraints:** Do not rename in tool without confirmation.  
**Output:** Diff table + rename checklist + “new mapping rows needed” list.

### 4d. Suggested output format

- `PBIX page | Mapping page_name | Status (match / rename / orphan)`  
- **Action list:** numbered

---

# Prompt 5 — Deploy M code from repo into template

### 5a. Main prompt

**Context**  
Authoritative M code lives in git under `m_code/<area>/*.m`. The template must match for queries we maintain.

**Task**  
For query names I list below, compare Advanced Editor text in the PBIX to the repo snippet I paste (or describe), and report diffs. If I ask “apply”, prepare minimal surgical M patches.

**Instructions**  
- Prefer line-level diff summary.  
- Preserve query output schema; warn if column renames would break DAX.  
- Parameters first, then dependent queries.

**Constraints**  
Never replace entire model. One query at a time unless I say otherwise.

**Output format**  
1. Per query: match / drift / risk  
2. If patch: single fenced M block per query labeled for paste into Advanced Editor

### 5b. Concise

`MCP: for query [NAME] in Monthly_Report_Template.pbix, show current M vs this repo version [paste]. Diff only; no apply.`

### 5c. Detailed

**Context:** Surgical M deployment; bulk paste caused DAX/schema breaks in the past.  
**Task:** Safe reconciliation of repo `m_code` vs PBIX for a defined set of queries.  
**Instructions:** Read PBIX query via MCP. Compare to pasted repo M. List: added/removed steps, path changes, date logic changes. Rate risk to downstream DAX. Provide step-by-step Desktop instructions: Transform Data → query → Advanced Editor → replace → Close & Apply → verify row count.  
**Constraints:** Schema-breaking changes require explicit warning and alternative.  
**Output:** Diff narrative + optional full replacement M in one code block + verification checklist.

### 5d. Suggested output format

- **Per query:** `Risk: Low/Med/High` + bullet diff + **M block** (if replacement)

---

# Prompt 6 — New measure / visual wiring (DAX + fields)

### 6a. Main prompt

**Context**  
I am adding a Card or Matrix to an existing page. The data is already loaded in table `[TableName]`.

**Task**  
Write DAX measure(s) for: [describe KPI, e.g. YTD count Jan–pReportMonth]. Specify filter columns and grain.

**Instructions**  
- Use `pReportMonth` for YTD bounds: start `DATE(YEAR(pReportMonth),1,1)`, end `EOMONTH(pReportMonth,0)` unless I specify otherwise.  
- Name measures clearly.  
- Note which fields to put in visual wells.

**Constraints**  
Measures only; do not change M unless necessary and I ask.

**Output format**  
1. Measure names + DAX in fenced blocks  
2. Visual setup: Fields + Filters  
3. Common failure checks (BLANK, relationship direction)

### 6b. Concise

`PBIX model: table [T], date column [D]. DAX: YTD sum of [Value] from Jan through pReportMonth. Card visual fields.`

### 6c. Detailed

**Context:** Monthly_Report_Template.pbix; measure table may be `STACP_Measures` or similar hidden table.  
**Task:** Implement [KPI description] with correct time intelligence and filters.  
**Instructions:** Provide DAX with comments stripped for production. Handle BLANK. If relationship to date table exists, prefer USERELATIONSHIP or physical relationship pattern appropriate to model — infer from table list if possible.  
**Constraints:** No verbose tutorial; keep DAX copy-paste ready.  
**Output:** Measures + visual binding + 2-line validation (what number to expect if filters applied).

### 6d. Suggested output format

- **DAX:** ```dax ... ```  
- **Visual:** bullet “Well: …”

---

# Prompt 7 — Relationship and key sanity check

### 7a. Main prompt

**Context**  
Blank visuals or inflated totals often come from missing/inactive relationships or wrong cardinality.

**Task**  
Summarize the model’s relationships: fact tables, dimension tables, active vs inactive, cross-filter direction. Flag obvious risks for many-to-many or ambiguous paths to `___DimMonth` / date tables.

**Instructions**  
Use MCP-visible relationship metadata. Do not change relationships unless I ask.

**Output format**  
1. Diagram description (text) or mermaid if allowed  
2. Risk table  
3. Top 3 checks to run in Desktop (Performance analyzer optional)

### 7b. Concise

`MCP: summarize relationships in Monthly_Report_Template.pbix; flag inactive or bi-di on fact tables. Read-only.`

### 7c. Detailed

**Context:** CompStat model; multiple fact tables (summons, arrests, patrol, etc.).  
**Task:** Relationship audit for report correctness.  
**Instructions:** List from→to, cardinality, active, cross-filter. Identify tables with no relationship to primary date dimension. Note bridge tables.  
**Constraints:** Read-only.  
**Output:** Table + “if visual X is blank, check Y” mapping (generic).

### 7d. Suggested output format

- **Mermaid** `flowchart` or table `From | To | Active | Cross-filter | Note`

---

# Prompt 8 — Export readiness (for Processed_Exports pipeline)

### 8a. Main prompt

**Context**  
After refresh, I export visual data to CSV for `PowerBI_Data\_DropExports` and run `process_powerbi_exports.py` with `--report-month`.

**Task**  
List visuals or pages that are good candidates for CSV export this month, and any visuals using TODAY-relative filters that would make exports non-reproducible.

**Instructions**  
- If MCP exposes filter expressions or measure summaries, flag `TODAY`/`NOW`.  
- Align suggestions with standard CompStat pages (Summons, Response Time, etc.).

**Output format**  
1. Page + visual name list  
2. “Risk: dynamic date” flags  
3. Suggested export order (largest/slowest first optional)

### 8b. Concise

`Monthly_Report_Template.pbix: flag visuals/measures likely using TODAY/NOW; list report pages. Read-only.`

### 8c. Detailed

**Context:** Monthly close; exports feed `Processed_Exports` and Backfill; `pReportMonth` should freeze time.  
**Task:** Audit for export reliability.  
**Instructions:** Identify DAX or M that still depends on wall-clock time. Recommend replacing with pReportMonth-based equivalents at high level.  
**Constraints:** No file edits in repo from Claude unless I ask.  
**Output:** Table `Location | Pattern | Risk | Fix type` + export checklist.

### 8d. Suggested output format

- **Flags:** P0 / P1  
- **Checklist:** markdown `- [ ]`

---

## Meta-prompt (ask Claude to refine any prompt)

**Context:** I use Claude Desktop with MCP on Monthly_Report_Template.pbix.  
**Task:** Rewrite the following prompt to be clearer, shorter, and less ambiguous for MCP tool use. Preserve intent.  
**Instructions:** Output: (1) revised prompt, (2) one-line “when to use,” (3) expected output shape.  
**Constraints:** Keep under 200 words for the revised prompt unless I say otherwise.  
**Output format:** three sections as labeled.

---

*Document version: 1.0 | For: Claude Desktop + Power BI MCP | Template: Monthly_Report_Template.pbix*

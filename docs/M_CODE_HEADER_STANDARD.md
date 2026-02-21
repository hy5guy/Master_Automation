# M Code Standard Header

All M code (Power Query) files in this project use a standard 4-line header for traceability and authorship.

## Format (M Code)

```text
// 🕒 YYYY-MM-DD-HH-MM-SS
// # Master_Automation/m_code/<path-from-m_code>.m
// # Author: R. A. Carucci
// # Purpose: One-line, AI-generated purpose.
```

- **Timestamp**: Eastern Standard Time (EST), `YYYY-MM-DD-HH-MM-SS`.
- **Project / File**: `Master_Automation` and path under `m_code` (e.g. `___Summons_Top5_Moving_STANDALONE.m` or `esu/fnCleanText.m`).
- **Author**: `R. A. Carucci` (exact spelling).
- **Purpose**: Single line, clear and concise.

## Comment style by language

| Language | Comment symbol | Example |
|----------|----------------|---------|
| M Code   | `//`           | `// # Master_Automation/m_code/___Summons.m` |
| Python   | `#`            | `# Master_Automation/scripts/path_config.py` |
| VBA      | `'`            | `' Master_Automation/ExportQueries.bas` |
| SQL      | `--`           | `-- Master_Automation/daily_extract.sql` |
| JavaScript | `//`         | `// Master_Automation/init.js` |

## When to update

- **New or updated code**: Insert this header at the top; use current EST timestamp.
- **Existing files**: All active M code under `m_code/` has been updated to this standard. Archive files may be updated when next edited.

## Status

- **Active M code** under `m_code/` (root and subfolders: `summons/`, `esu/`, `stacp/`, `detectives/`, etc.) has been updated to this header.
- **Archive** (`m_code/archive/`): Standard is in place; individual files are updated when touched.

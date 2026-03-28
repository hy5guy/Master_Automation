# .gitignore Coverage Audit
## Generated: 2026-03-28

## Coverage Matrix

| Pattern | Benchmark | Community_Engagement | Overtime_TimeOff | Policy_Training | Response_Times | Summons |
|---------|-----------|---------------------|------------------|-----------------|----------------|---------|
| `*.xlsx~` | ADDED | ADDED | ADDED | ADDED | ADDED | ADDED |
| `~$*.xlsx` | present | present (via `~$*`) | ADDED | present (via `~$*`) | ADDED | ADDED |
| `*.xlsm~` | ADDED | ADDED | ADDED | ADDED | ADDED | ADDED |
| `~$*.xlsm` | ADDED | present (via `~$*`) | ADDED | present (via `~$*`) | ADDED | ADDED |
| `*.pyc` | present (via `*.py[cod]`) | present (via `*.py[cod]`) | ADDED | present | present | ADDED |
| `__pycache__/` | present | present | present | present | present | present |
| `.env` | present | ADDED | present | ADDED | ADDED | present |
| `*.env` | present | ADDED | ADDED | ADDED | ADDED | ADDED |
| `*.log` | present | ADDED | present | ADDED | present | present |
| `archive/` | ADDED | ADDED | present | ADDED | ADDED | present |
| `output/` | ADDED | present | present | present | ADDED | present |
| `temp/` | ADDED | ADDED | ADDED | ADDED | ADDED | ADDED |

## Changes Applied

### Benchmark/.gitignore
Added: `*.xlsx~`, `*.xlsm~`, `~$*.xlsm`, `archive/`, `output/`, `temp/`

### Community_Engagement/.gitignore
Added: `*.xlsx~`, `*.xlsm~`, `.env`, `*.env`, `*.log`, `archive/`, `temp/`

### Overtime_TimeOff/.gitignore
Added: `*.xlsx~`, `~$*.xlsx`, `*.xlsm~`, `~$*.xlsm`, `*.pyc`, `*.env`, `temp/`

### Policy_Training_Monthly/.gitignore
Added: `*.xlsx~`, `*.xlsm~`, `.env`, `*.env`, `*.log`, `archive/`, `temp/`

### Response_Times/.gitignore
Added: `*.xlsx~`, `~$*.xlsx`, `*.xlsm~`, `~$*.xlsm`, `.env`, `*.env`, `output/`, `archive/`, `temp/`

### Summons/.gitignore
Added: `*.xlsx~`, `~$*.xlsx`, `*.xlsm~`, `~$*.xlsm`, `*.pyc`, `*.env`, `temp/`

## Recommendations

1. **Benchmark**: Consider adding `*.csv` for data files in root (preview tables are already listed individually). Add `nppBackup/` if Notepad++ is used.
2. **Community_Engagement**: Consider adding `*.xlsx` and `*.csv` patterns for root-level data files. The `backups/` directory is covered but `src/output/`, `src/reports/`, `src/logs/` could use a broader `src/**/output/` pattern.
3. **Overtime_TimeOff**: Already has broad `*.csv`, `*.xlsx`, `*.xls` patterns. Well covered. Consider adding `nppBackup/` consistently.
4. **Policy_Training_Monthly**: Consider adding `*.csv` and `*.xlsx` for root-level Power BI export snapshots. The `qc/` directory is already covered.
5. **Response_Times**: Consider adding `diagnostic_output/`, `nppBackup/`, `claude_code_inputs/`, `claude_ouputs/` to match CLAUDE.md known artifacts. Broad `*.xlsx` and `*.csv` patterns would reduce noise from data files.
6. **Summons**: Already has broad `*.csv`, `*.xlsx`, `*.xls` patterns. Consider adding `nppBackup/` and the shell artifact junk files (`#`, `cd`, `echo`, `python`, `_ul`).
7. **All repos**: The `temp/` directory pattern was missing from all 6 repos. Consider adding `*.tmp` universally (only Community_Engagement and Policy_Training_Monthly currently have it).

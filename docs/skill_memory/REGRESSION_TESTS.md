# Cross-Skill Regression Test Inventory

## Registry
| ID | Skill | Protects Against | How to Run |
|----|-------|-----------------|------------|
| R-PF1 | preflight | Master_Automation path in Pre_Flight_Validation.py | `grep -c Master_Automation scripts/Pre_Flight_Validation.py` → expect 0 |
| R-PF2 | preflight | Wrong personnel file (V3_FINAL.xlsx) | `grep -c V3_FINAL scripts/Pre_Flight_Validation.py` → expect 0 |
| R-PF3 | preflight | Wrong CSV column names (camelCase vs UPPER_SNAKE) | `grep -c "Badge.*LastName.*FirstName" scripts/Pre_Flight_Validation.py` → expect 0 |
| R-VW1 | validate-window | Missing --scan-folder in invocation | `grep "scan-folder" .claude/commands/validate-window.md` → expect match |
| R-VW2 | validate-window | Hardcoded enforced count (was 24/25) | `grep -c "!= 25" scripts/Pre_Flight_Validation.py` → expect 0 |
| R-DP1 | diagnose-pipeline | Script rename fragility | `ls scripts/diagnose_*.py scripts/validate_*.py scripts/check_*.py scripts/compare_*.py scripts/dfr_reconcile.py scripts/debug_december_paytypes.py scripts/find_unknown_badges.py` — all must exist |
| R-DP2 | diagnose-pipeline | Wrong script name (debug_december_pay_types with extra _) | `grep -c debug_december_pay_types .claude/commands/diagnose-pipeline.md` → expect 0 |
| R-SP1 | sync-personnel | WG2 list mismatch with data | `grep "PATROL DIVISION" .claude/commands/sync-personnel.md` → expect match |
| R-PE1 | process-exports | YYYY_MM format passed to --report-month (wants YYYY-MM) | `grep -c "YYYY_MM" .claude/commands/process-exports.md` → expect 0 in command blocks |
| R-PE2 | process-exports | Wrong destination path (PowerBI_Data/Processed_Exports) | `grep -c "PowerBI_Data/Processed_Exports" .claude/commands/process-exports.md` → expect 0 |
| R-MC1 | monthly-cycle | deploy_production.py instead of src/main_processor.py | `grep -c deploy_production .claude/commands/monthly-cycle.md` → expect 0 |
| R-MC2 | monthly-cycle | Hardcoded path placeholder (cd /path/to) | `grep -c "cd /path/to" .claude/commands/monthly-cycle.md` → expect 0 |

## Shared Regressions
- All skills: `grep -c "cd /path/to" .claude/commands/*.md` → expect 0 (no hardcoded path placeholders)
- All skills: No `DateTime.LocalNow()` in M code
- All skills: PYTHONIOENCODING=utf-8 documented for Windows execution
- process-exports + monthly-cycle: `--report-month` uses YYYY-MM (hyphen), not YYYY_MM (underscore)
- preflight + monthly-cycle: Pre_Flight_Validation.py casing must be uppercase P, F, V

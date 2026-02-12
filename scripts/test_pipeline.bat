@echo off
REM Overtime/TimeOff pipeline test: pre-flight, dry-run, then output validation.
REM Run from Master_Automation: scripts\test_pipeline.bat

set SCRIPTDIR=%~dp0
set ROOT=%SCRIPTDIR%..
cd /d "%ROOT%"

echo [1/3] Validating exports...
python scripts\validate_exports.py
if errorlevel 1 goto :fail

echo.
echo [2/3] Running pipeline (dry-run)...
python scripts\overtime_timeoff_with_backfill.py --dry-run
if errorlevel 1 goto :fail

echo.
echo [3/3] Validating outputs...
python scripts\validate_outputs.py
if errorlevel 1 goto :fail

echo.
echo [SUCCESS] All tests passed.
exit /b 0

:fail
echo [FAIL] Pipeline test failed. Fix errors above. If FIXED file not found, run: python scripts\overtime_timeoff_with_backfill.py
exit /b 1

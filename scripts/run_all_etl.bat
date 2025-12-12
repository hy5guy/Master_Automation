@echo off
REM Master ETL Orchestrator - Batch File Wrapper
REM Calls PowerShell script with proper execution policy

setlocal

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "AUTOMATION_DIR=%SCRIPT_DIR%.."

REM Change to automation directory
cd /d "%AUTOMATION_DIR%"

REM Run PowerShell script
powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%run_all_etl.ps1" %*

REM Capture exit code
set EXIT_CODE=%ERRORLEVEL%

endlocal
exit /b %EXIT_CODE%


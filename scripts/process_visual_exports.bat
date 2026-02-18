@echo off
REM ============================================================================
REM Visual Export Processing Batch Script
REM Streamlines the monthly Power BI visual export workflow
REM Author: Master_Automation System
REM Updated: 2026-02-17
REM ============================================================================

setlocal EnableDelayedExpansion

echo.
echo ========================================
echo   Master Automation Visual Export
echo   Processing Utility
echo ========================================
echo.

REM Get current directory (should be Master_Automation\scripts)
set "SCRIPT_DIR=%~dp0"
set "AUTOMATION_ROOT=%SCRIPT_DIR%.."

REM Check if we're in the right location
if not exist "%AUTOMATION_ROOT%\Standards\config\powerbi_visuals\visual_export_mapping.json" (
    echo ERROR: Cannot find visual export mapping configuration.
    echo Make sure you're running this from Master_Automation\scripts\ directory.
    echo Expected: %AUTOMATION_ROOT%\Standards\config\powerbi_visuals\visual_export_mapping.json
    pause
    exit /b 1
)

REM Check if _DropExports folder exists
set "DROP_EXPORTS=%AUTOMATION_ROOT%\_DropExports"
if not exist "%DROP_EXPORTS%" (
    echo WARNING: _DropExports folder not found at: %DROP_EXPORTS%
    echo Creating folder...
    mkdir "%DROP_EXPORTS%"
)

echo Current _DropExports location: %DROP_EXPORTS%
echo.

REM Count existing files in _DropExports
set FILE_COUNT=0
for %%f in ("%DROP_EXPORTS%\*.csv") do set /a FILE_COUNT+=1

echo Found %FILE_COUNT% CSV files in _DropExports folder.
echo.

if %FILE_COUNT% EQU 0 (
    echo No CSV files found in _DropExports.
    echo.
    echo INSTRUCTIONS:
    echo 1. Export your Power BI visuals as CSV files
    echo 2. Save them directly to: %DROP_EXPORTS%
    echo 3. Re-run this script to process them
    echo.
    set /p CONTINUE="Press Enter to continue anyway, or Ctrl+C to exit..."
    echo.
)

REM Prompt for report date
echo Enter the report month for these visual exports.
echo This will be used for date inference and file organization.
echo.
set /p REPORT_DATE="Report Date (YYYY-MM format, e.g., 2026-01): "

REM Validate date format
echo %REPORT_DATE% | findstr /r "^[0-9][0-9][0-9][0-9]-[0-9][0-9]$" >nul
if errorlevel 1 (
    echo ERROR: Invalid date format. Please use YYYY-MM format (e.g., 2026-01)
    pause
    exit /b 1
)

echo.
echo ========================================
echo Processing Mode Selection
echo ========================================
echo.
echo 1. DRY RUN - Preview what would be processed (recommended first)
echo 2. FULL PROCESS - Process and organize all exports
echo 3. MAPPING REVIEW - Check for new visuals not in mapping
echo.
set /p MODE="Select mode (1-3): "

echo.
echo ========================================
echo Processing Visual Exports
echo ========================================
echo.
echo Report Date: %REPORT_DATE%
echo Drop Exports: %DROP_EXPORTS%
echo Files to process: %FILE_COUNT%
echo.

REM Change to automation root directory
cd /d "%AUTOMATION_ROOT%"

REM Execute based on selected mode
if "%MODE%"=="1" (
    echo Running DRY RUN mode...
    python scripts\process_powerbi_exports.py --dry-run --report-date %REPORT_DATE%
) else if "%MODE%"=="2" (
    echo Running FULL PROCESS mode...
    python scripts\process_powerbi_exports.py --report-date %REPORT_DATE% --auto-organize
) else if "%MODE%"=="3" (
    echo Running MAPPING REVIEW mode...
    python scripts\process_powerbi_exports.py --dry-run --report-date %REPORT_DATE% --verbose
) else (
    echo ERROR: Invalid mode selection. Please choose 1, 2, or 3.
    pause
    exit /b 1
)

set PYTHON_EXIT_CODE=%ERRORLEVEL%

echo.
echo ========================================
echo Processing Complete
echo ========================================
echo.

if %PYTHON_EXIT_CODE% EQU 0 (
    echo SUCCESS: Visual export processing completed successfully.
    echo.
    if "%MODE%"=="2" (
        echo Next steps:
        echo 1. Review processed files in PowerBI_Date\Processed_Exports\
        echo 2. Run: PowerBI_Date\tools\organize_backfill_exports.ps1
        echo 3. Refresh Power BI reports to load new data
    )
) else (
    echo ERROR: Processing failed with exit code %PYTHON_EXIT_CODE%
    echo Check the output above for error details.
)

echo.
echo Log files location: %AUTOMATION_ROOT%\logs\
echo.
pause
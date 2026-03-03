# Monthly Report Folder Rename Script
# WARNING: This script is NOT RECOMMENDED
# Current format (MM_monthname) is better for usability
# Only run this if you have a specific requirement for YYYY_MM format

<#
.SYNOPSIS
Renames monthly report folders from MM_monthname to YYYY_MM format.

.DESCRIPTION
This script renames folders in the Monthly Reports directory from the current
format (e.g., "01_january") to YYYY_MM format (e.g., "2026_01").

WARNING: This is NOT recommended! The current format is more user-friendly.
See MONTHLY_REPORT_NAMING_ANALYSIS_2026_02_09.md for detailed analysis.

.PARAMETER Year
The year to process (default: 2026)

.PARAMETER WhatIf
Show what would be renamed without actually renaming

.EXAMPLE
.\Rename-MonthlyReportFolders.ps1 -WhatIf
Shows what would be renamed

.EXAMPLE
.\Rename-MonthlyReportFolders.ps1 -Year 2026
Renames folders for 2026
#>

param(
    [int]$Year = 2026,
    [switch]$WhatIf
)

$ErrorActionPreference = 'Stop'

# Base directory
$baseDir = "C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Monthly Reports\$Year"

# Verify directory exists
if (-not (Test-Path $baseDir)) {
    Write-Error "Directory not found: $baseDir"
    exit 1
}

# Folder mapping
$folderMap = @{
    "01_january"   = "${Year}_01"
    "02_february"  = "${Year}_02"
    "03_march"     = "${Year}_03"
    "04_april"     = "${Year}_04"
    "05_may"       = "${Year}_05"
    "06_june"      = "${Year}_06"
    "07_july"      = "${Year}_07"
    "08_august"    = "${Year}_08"
    "09_september" = "${Year}_09"
    "10_october"   = "${Year}_10"
    "11_november"  = "${Year}_11"
    "12_december"  = "${Year}_12"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "  Monthly Report Folder Rename" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Year: $Year" -ForegroundColor Cyan
Write-Host "Base Directory: $baseDir" -ForegroundColor Cyan
Write-Host ""

if ($WhatIf) {
    Write-Host "=== WHATIF MODE - No changes will be made ===" -ForegroundColor Magenta
    Write-Host ""
}

# Track statistics
$renamed = 0
$skipped = 0
$errors = 0

foreach ($old in $folderMap.Keys) {
    $new = $folderMap[$old]
    $oldPath = Join-Path $baseDir $old
    $newPath = Join-Path $baseDir $new
    
    # Check if old folder exists
    if (-not (Test-Path $oldPath)) {
        Write-Host "SKIP: $old (not found)" -ForegroundColor Gray
        $skipped++
        continue
    }
    
    # Check if new folder already exists
    if (Test-Path $newPath) {
        Write-Host "SKIP: $old -> $new (target already exists)" -ForegroundColor Yellow
        $skipped++
        continue
    }
    
    # Perform rename
    try {
        if ($WhatIf) {
            Write-Host "WOULD RENAME: $old -> $new" -ForegroundColor Cyan
            $renamed++
        }
        else {
            Rename-Item -Path $oldPath -NewName $new -ErrorAction Stop
            Write-Host "RENAMED: $old -> $new" -ForegroundColor Green
            $renamed++
        }
    }
    catch {
        Write-Host "ERROR: Failed to rename $old - $_" -ForegroundColor Red
        $errors++
    }
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "  Summary" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "Renamed: $renamed" -ForegroundColor $(if ($renamed -gt 0) { "Green" } else { "Gray" })
Write-Host "Skipped: $skipped" -ForegroundColor Gray
Write-Host "Errors:  $errors" -ForegroundColor $(if ($errors -gt 0) { "Red" } else { "Gray" })
Write-Host ""

if ($WhatIf) {
    Write-Host "This was a dry run. Run without -WhatIf to perform actual renames." -ForegroundColor Magenta
}
elseif ($renamed -gt 0 -and $errors -eq 0) {
    Write-Host "SUCCESS: All folders renamed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: You must now update run_all_etl.ps1!" -ForegroundColor Yellow
    Write-Host "Edit line 69 in scripts\run_all_etl.ps1:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  OLD: `$targetDir = Join-Path `$targetDir `"`${monthNum}_`${monthNameLower}`"" -ForegroundColor Red
    Write-Host "  NEW: `$targetDir = Join-Path `$targetDir `"`${year}_`${monthNum}`"" -ForegroundColor Green
    Write-Host ""
}
elseif ($errors -gt 0) {
    Write-Host "PARTIAL SUCCESS: Some folders were not renamed due to errors." -ForegroundColor Yellow
}
else {
    Write-Host "No changes made (all folders already correct or not found)." -ForegroundColor Gray
}

Write-Host ""

# List final structure
Write-Host "Current folder structure:" -ForegroundColor Cyan
Get-ChildItem -Path $baseDir -Directory | Sort-Object Name | ForEach-Object {
    Write-Host "  - $($_.Name)" -ForegroundColor Gray
}

Write-Host ""

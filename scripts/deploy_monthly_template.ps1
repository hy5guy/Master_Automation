# DEPRECATED: Logic folded into run_all_etl.ps1 Save-MonthlyReport — do not use.

param(
    [Parameter(Mandatory)][string]$ReportMonth  # Format: YYYY-MM (e.g., 2026-03)
)

# Parse month parts
$parts     = $ReportMonth -split "-"
$year      = $parts[0]
$month     = $parts[1]
$monthName = (Get-Date -Year $year -Month $month -Day 1).ToString("MM_MMMM").ToLower()  # e.g. 03_march
$fileName  = "${year}_${month}_Monthly_Report.pbix"

# Resolve paths via OneDrive root (matches pathconfig.py convention)
$oneDriveRoot = "C:\Users\carucci_r\OneDrive - City of Hackensack"
$source       = Join-Path $oneDriveRoot "08_Templates\Monthly_Report_Template.pbix"
$destDir      = Join-Path $oneDriveRoot "Shared Folder\Compstat\Monthly Reports\$year\$monthName"
$destFile     = Join-Path $destDir $fileName

# Validate source exists
if (-not (Test-Path $source)) {
    Write-Error "Template not found: $source"; exit 1
}

# Create destination folder if needed
if (-not (Test-Path $destDir)) {
    New-Item -ItemType Directory -Path $destDir | Out-Null
    Write-Host "Created folder: $destDir"
}

# Skip if already exists
if (Test-Path $destFile) {
    Write-Warning "Already exists, skipping: $destFile"; exit 0
}

Copy-Item $source -Destination $destFile
Write-Host "Deployed: $destFile"
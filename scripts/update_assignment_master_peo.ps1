# Simple Assignment Master Update Script
# Date: 2026-02-17
# Purpose: Add 6 missing PEO records to Assignment_Master_V2.csv

$ErrorActionPreference = "Stop"

$line = "=" * 70

Write-Host $line -ForegroundColor Cyan
Write-Host "ASSIGNMENT MASTER UPDATE - TRAFFIC BUREAU PEO ADDITION" -ForegroundColor Cyan
Write-Host $line -ForegroundColor Cyan

# File paths
$masterFile = "C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Personnel\Assignment_Master_V2.csv"
$additionsFile = "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\data\traffic_peo_additions_2026_02_17.csv"
$backupDir = "C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Personnel\backups"

# Verify files exist
if (-not (Test-Path $masterFile)) {
    Write-Host "`nERROR: Assignment Master not found" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $additionsFile)) {
    Write-Host "`nERROR: PEO additions file not found" -ForegroundColor Red
    exit 1
}

# Create backup directory
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
}

# STEP 1: BACKUP
Write-Host "`n[1/4] Creating backup..." -ForegroundColor Yellow

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = Join-Path $backupDir "Assignment_Master_V2_backup_$timestamp.csv"

Copy-Item $masterFile $backupFile
Write-Host "  Backup created: $backupFile" -ForegroundColor Green

# STEP 2: LOAD FILES (Raw content to avoid duplicate column issues)
Write-Host "`n[2/4] Loading files..." -ForegroundColor Yellow

# Read as raw text lines
$masterLines = Get-Content $masterFile
$additionsLines = Get-Content $additionsFile | Where-Object { $_ -notlike "#*" -and $_ -ne "" }

Write-Host "  Current master lines: $($masterLines.Count)" -ForegroundColor Green
Write-Host "  Addition lines to append: $($additionsLines.Count - 1)" -ForegroundColor Green

# STEP 3: CHECK FOR DUPLICATES
Write-Host "`n[3/4] Checking for duplicates..." -ForegroundColor Yellow

# Get badge column index (column 7 = PADDED_BADGE_NUMBER)
$existingBadges = $masterLines | Select-Object -Skip 1 | ForEach-Object {
    ($_ -split ',')[6]  # Index 6 = 7th column (PADDED_BADGE_NUMBER)
}

$newBadges = $additionsLines | Select-Object -Skip 1 | ForEach-Object {
    ($_ -split ',')[6]
}

$duplicates = $newBadges | Where-Object { $existingBadges -contains $_ }

if ($duplicates) {
    Write-Host "  WARNING: Duplicate badges found: $($duplicates -join ', ')" -ForegroundColor Yellow
    Write-Host "  Skipping duplicate records" -ForegroundColor Yellow
    
    # Filter out duplicates
    $additionsLines = @($additionsLines[0]) + @($additionsLines | Select-Object -Skip 1 | Where-Object {
        $badge = ($_ -split ',')[6]
        $duplicates -notcontains $badge
    })
}

$recordsToAdd = $additionsLines.Count - 1  # Exclude header

if ($recordsToAdd -eq 0) {
    Write-Host "`nAll PEO records already exist" -ForegroundColor Green
    exit 0
}

Write-Host "  No duplicates found" -ForegroundColor Green
Write-Host "  Records to add: $recordsToAdd" -ForegroundColor Green

# STEP 4: APPEND NEW RECORDS
Write-Host "`n[4/4] Appending PEO records..." -ForegroundColor Yellow

# Append new lines (skip header from additions)
$updatedContent = $masterLines + ($additionsLines | Select-Object -Skip 1)

# Write back to file
$updatedContent | Set-Content $masterFile

Write-Host "  Added $recordsToAdd PEO records" -ForegroundColor Green
Write-Host "  Updated master records: $($updatedContent.Count - 1)" -ForegroundColor Green

# VERIFICATION
Write-Host ""
Write-Host $line -ForegroundColor Cyan
Write-Host "VERIFICATION" -ForegroundColor Cyan
Write-Host $line -ForegroundColor Cyan

# Re-read and check badges
$verifyLines = Get-Content $masterFile
$peo_badges = @('2027', '2030', '2025', '2021', '2026', '2022')
$found_count = 0

foreach ($badge in $peo_badges) {
    $found = $verifyLines | Where-Object { $_ -like "*,$badge,*" -or $_ -like "*,0$badge,*" }
    if ($found) {
        $found_count++
        Write-Host "  Badge $badge found" -ForegroundColor Green
    } else {
        Write-Host "  Badge $badge NOT FOUND" -ForegroundColor Red
    }
}

Write-Host "`nSummary:" -ForegroundColor Cyan
Write-Host "  PEO badges verified: $found_count / 6" -ForegroundColor $(if ($found_count -eq 6) { 'Green' } else { 'Red' })

if ($found_count -eq 6) {
    Write-Host "`nSUCCESS! All PEO records added!" -ForegroundColor Green
}

# MANUAL CORRECTION REMINDER
Write-Host ""
Write-Host $line -ForegroundColor Cyan
Write-Host "MANUAL CORRECTION REQUIRED" -ForegroundColor Yellow
Write-Host $line -ForegroundColor Cyan

Write-Host "`nREMINDER: Manually update G. GALLORINI (Badge 0256)" -ForegroundColor Yellow
Write-Host "  1. Open Assignment_Master_V2.csv in Excel" -ForegroundColor White
Write-Host "  2. Find PADDED_BADGE_NUMBER = 0256" -ForegroundColor White
Write-Host "  3. Change WG2: PATROL DIVISION -> TRAFFIC BUREAU" -ForegroundColor White
Write-Host "  4. Save and close" -ForegroundColor White

Write-Host "`nNext Steps:" -ForegroundColor Cyan
Write-Host "  1. Make the manual correction for Badge 0256" -ForegroundColor White
Write-Host "  2. Run: python scripts/summons_etl_normalize.py" -ForegroundColor White
Write-Host "  3. Run: python scripts/verify_summons_remediation.py" -ForegroundColor White

Write-Host ""
Write-Host $line -ForegroundColor Cyan
Write-Host "COMPLETE" -ForegroundColor Green
Write-Host $line -ForegroundColor Cyan

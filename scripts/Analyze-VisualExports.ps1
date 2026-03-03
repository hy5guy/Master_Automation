# Visual Export Analysis Script
# Analyzes Power BI visual exports and identifies mapping gaps
# Author: Master_Automation System
# Updated: 2026-02-17

param(
    [string]$ReportDate,
    [switch]$DryRun,
    [switch]$ShowUnmapped,
    [switch]$UpdateMapping
)

$ErrorActionPreference = 'Stop'

# Get script directory and automation root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$automationRoot = Split-Path -Parent $scriptDir

# Key paths
$dropExportsPath = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports"
$mappingPath = Join-Path $automationRoot "Standards\config\powerbi_visuals\visual_export_mapping.json"
$logDir = Join-Path $automationRoot "logs"

# Ensure log directory exists
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

# Create timestamped log
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$logFile = Join-Path $logDir "visual_export_analysis_$timestamp.log"

function Write-Log([string]$message) {
    $logMessage = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $message"
    Add-Content -Path $logFile -Value $logMessage
    Write-Host $message
}

function Get-VisualNameFromFilename([string]$filename) {
    # Extract visual name from Power BI export filename
    # Common patterns: "Visual Name.csv", "2026_01_Visual Name.csv", etc.
    
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($filename)
    
    # Remove date prefixes (YYYY_MM_)
    $cleaned = $baseName -replace '^20\d{2}_\d{2}_', ''
    
    # Remove common suffixes
    $cleaned = $cleaned -replace '\s*Values are in mmss$', ''
    $cleaned = $cleaned -replace '\s*\(\d+\)$', ''  # Remove (1), (2) duplicates
    
    return $cleaned.Trim()
}

Write-Log "=== Visual Export Analysis Started ==="
Write-Log "Automation Root: $automationRoot"
Write-Log "Drop Exports: $dropExportsPath"
Write-Log "Mapping Config: $mappingPath"

# Check if _DropExports exists
if (-not (Test-Path $dropExportsPath)) {
    Write-Log "ERROR: _DropExports folder not found: $dropExportsPath"
    exit 1
}

# Load existing mapping configuration
if (-not (Test-Path $mappingPath)) {
    Write-Log "ERROR: Visual export mapping not found: $mappingPath"
    exit 1
}

try {
    $mappingConfig = Get-Content $mappingPath -Raw | ConvertFrom-Json
    $existingMappings = @{}
    
    foreach ($mapping in $mappingConfig.mappings) {
        $visualName = $mapping.visual_name
        $existingMappings[$visualName] = $mapping
        
        # Also map aliases
        if ($mapping.match_aliases) {
            foreach ($alias in $mapping.match_aliases) {
                $existingMappings[$alias] = $mapping
            }
        }
    }
    
    Write-Log "Loaded $($mappingConfig.mappings.Count) existing visual mappings"
}
catch {
    Write-Log "ERROR: Failed to load mapping configuration: $_"
    exit 1
}

# Scan CSV files in _DropExports
$csvFiles = Get-ChildItem -Path $dropExportsPath -Filter "*.csv" -File
Write-Log "Found $($csvFiles.Count) CSV files in _DropExports"

if ($csvFiles.Count -eq 0) {
    Write-Log "No CSV files found to analyze. Export some Power BI visuals first."
    exit 0
}

# Analyze each file
$analysisResults = @()
$unmappedVisuals = @()

foreach ($file in $csvFiles) {
    Write-Log "Analyzing: $($file.Name)"
    
    $visualName = Get-VisualNameFromFilename $file.Name
    $fileSize = [math]::Round($file.Length / 1KB, 2)
    
    # Check if visual is mapped
    $isMapped = $existingMappings.ContainsKey($visualName)
    $mapping = if ($isMapped) { $existingMappings[$visualName] } else { $null }
    
    # Try to read CSV structure for additional analysis
    $columnCount = 0
    $rowCount = 0
    $hasDateColumns = $false
    $dateColumns = @()
    
    try {
        $csvContent = Import-Csv $file.FullName -ErrorAction SilentlyContinue
        if ($csvContent) {
            $rowCount = $csvContent.Count
            $columnCount = ($csvContent | Get-Member -MemberType NoteProperty).Count
            
            # Check for date-like columns (MM-YY pattern)
            $headers = ($csvContent | Get-Member -MemberType NoteProperty).Name
            $dateColumns = $headers | Where-Object { $_ -match '^\d{2}-\d{2}$' }
            $hasDateColumns = $dateColumns.Count -gt 0
        }
    }
    catch {
        Write-Log "  Warning: Could not parse CSV content for $($file.Name)"
    }
    
    $result = [PSCustomObject]@{
        FileName = $file.Name
        VisualName = $visualName
        IsMapped = $isMapped
        FileSize_KB = $fileSize
        RowCount = $rowCount
        ColumnCount = $columnCount
        HasDateColumns = $hasDateColumns
        DateColumnCount = $dateColumns.Count
        DateColumns = ($dateColumns -join ', ')
        MappingTarget = if ($mapping) { $mapping.target_folder } else { 'UNMAPPED' }
        Enforce13Month = if ($mapping) { $mapping.enforce_13_month_window } else { $null }
    }
    
    $analysisResults += $result
    
    if (-not $isMapped) {
        $unmappedVisuals += $visualName
        Write-Log "  ⚠️  UNMAPPED: $visualName"
    } else {
        Write-Log "  ✅ MAPPED: $visualName → $($mapping.target_folder)"
    }
}

# Generate summary report
Write-Log ""
Write-Log "=== Analysis Summary ==="
Write-Log "Total files analyzed: $($csvFiles.Count)"
Write-Log "Mapped visuals: $(($analysisResults | Where-Object { $_.IsMapped }).Count)"
Write-Log "Unmapped visuals: $(($analysisResults | Where-Object { -not $_.IsMapped }).Count)"
Write-Log "Files with date columns: $(($analysisResults | Where-Object { $_.HasDateColumns }).Count)"

if ($ShowUnmapped -and $unmappedVisuals.Count -gt 0) {
    Write-Log ""
    Write-Log "=== Unmapped Visuals ==="
    foreach ($visual in $unmappedVisuals) {
        Write-Log "- $visual"
    }
}

# Export detailed analysis to CSV
$analysisPath = Join-Path $logDir "visual_export_analysis_$timestamp.csv"
$analysisResults | Export-Csv -Path $analysisPath -NoTypeInformation
Write-Log ""
Write-Log "Detailed analysis exported to: $analysisPath"

# Generate mapping template for unmapped visuals
if ($unmappedVisuals.Count -gt 0) {
    $templatePath = Join-Path $logDir "unmapped_visuals_template_$timestamp.json"
    
    $template = @{
        "_comment" = "Template for unmapped visuals found in analysis"
        "new_mappings" = @()
    }
    
    foreach ($visual in $unmappedVisuals) {
        $fileInfo = $analysisResults | Where-Object { $_.VisualName -eq $visual } | Select-Object -First 1
        
        $newMapping = @{
            "visual_name" = $visual
            "page_name" = "UNKNOWN"
            "standardized_filename" = ($visual -replace '[^\w\s-]', '' -replace '\s+', '_').ToLower()
            "normalized_folder" = "misc"
            "data_format" = if ($fileInfo.HasDateColumns) { "Long" } else { "Wide" }
            "date_column" = if ($fileInfo.HasDateColumns) { "Period" } else { "None" }
            "time_period" = if ($fileInfo.DateColumnCount -gt 1) { "Rolling 13 months" } else { "Single month" }
            "requires_normalization" = $true
            "enforce_13_month_window" = ($fileInfo.DateColumnCount -gt 1)
            "target_folder" = "misc"
            "notes" = "Auto-generated template - requires review and customization"
        }
        
        $template.new_mappings += $newMapping
    }
    
    $template | ConvertTo-Json -Depth 10 | Out-File -FilePath $templatePath -Encoding UTF8
    Write-Log "Mapping template for unmapped visuals: $templatePath"
}

Write-Log ""
Write-Log "=== Next Steps ==="
if ($unmappedVisuals.Count -gt 0) {
    Write-Log "1. Review unmapped visuals and update mapping configuration"
    Write-Log "2. Use the generated template as a starting point"
    Write-Log "3. Test with: python scripts\process_powerbi_exports.py --dry-run"
} else {
    Write-Log "1. All visuals are mapped - ready for processing"
    Write-Log "2. Run: python scripts\process_powerbi_exports.py --report-date $ReportDate"
}

Write-Log "=== Visual Export Analysis Complete ==="
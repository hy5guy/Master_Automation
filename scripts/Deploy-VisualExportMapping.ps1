<# 
Deploy-VisualExportMapping.ps1
Archives older mapping files, then moves Downloads\visual_export_mapping_merged.json
into Master_Automation\Standards\config\powerbi_visuals\visual_export_mapping.json,
then appends a short entry to the root docs.
#>

param(
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"

$MergedSource = "C:\Users\carucci_r\Downloads\visual_export_mapping_merged.json"
$TargetPath = Join-Path $Root "Standards\config\powerbi_visuals\visual_export_mapping.json"

$ArchiveBase = Join-Path $Root "scripts\_archive\visual_export_mapping"
$Stamp = Get-Date -Format "yyyy_MM_dd_HHmmss"
$ArchiveStamp = Join-Path $ArchiveBase $Stamp

$FilesToArchive = @(
    "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\visual_export_mapping_CORRECTED.json",
    "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\scripts\visual_export_mapping_updated.json",
    "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\scripts\visual_export_mapping_with_13month.json",
    "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\Standards\config\powerbi_visuals\visual_export_mapping.json",
    "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\Standards\config\powerbi_visuals\visual_export_mapping_v2.json"
)

$DocsToUpdate = @(
    "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\CHANGELOG.md",
    "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\Claude.md",
    "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\README.md",
    "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\SUMMARY.md"
)

function Ensure-Dir([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) {
        if ($DryRun) { Write-Host "DRYRUN mkdir $Path"; return }
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Get-RelativePath([string]$BasePath, [string]$FullPath) {
    $base = (Resolve-Path -LiteralPath $BasePath).Path.TrimEnd('\') + '\'
    $full = (Resolve-Path -LiteralPath $FullPath).Path
    if ($full.StartsWith($base, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $full.Substring($base.Length)
    }
    return ("_ABS_" + ($full -replace "[:\\\/]", "_"))
}

function Move-File([string]$Src, [string]$Dest) {
    if ($DryRun) { Write-Host "DRYRUN move `"$Src`" -> `"$Dest`""; return }
    Move-Item -LiteralPath $Src -Destination $Dest -Force
}

function Append-Doc([string]$DocPath, [string]$Block) {
    if (-not (Test-Path -LiteralPath $DocPath)) {
        Write-Host "SKIP missing doc: $DocPath"
        return
    }
    if ($DryRun) { Write-Host "DRYRUN update doc $DocPath"; return }
    Add-Content -LiteralPath $DocPath -Value $Block
}

# Validate merged JSON exists and parses
if (-not (Test-Path -LiteralPath $MergedSource)) {
    throw "Merged file not found: $MergedSource"
}
try {
    $null = Get-Content -LiteralPath $MergedSource -Raw | ConvertFrom-Json
}
catch {
    throw "Merged file is not valid JSON: $MergedSource. $($_.Exception.Message)"
}

# Create archive folder
Ensure-Dir $ArchiveStamp

# Archive listed files (preserve folder structure under archive stamp)
foreach ($f in $FilesToArchive) {
    if (-not (Test-Path -LiteralPath $f)) {
        Write-Host "SKIP missing: $f"
        continue
    }
    $rel = Get-RelativePath $Root $f
    $dest = Join-Path $ArchiveStamp $rel
    Ensure-Dir (Split-Path -Parent $dest)
    Move-File $f $dest
}

# Deploy merged file into Standards\config\powerbi_visuals as visual_export_mapping.json
Ensure-Dir (Split-Path -Parent $TargetPath)
Move-File $MergedSource $TargetPath

# Append doc entry
$DateLine = Get-Date -Format "yyyy-MM-dd"
$DocBlock = @"
`n## $DateLine
- Consolidated Power BI visual export mapping into one file.
- Primary path: Standards\config\powerbi_visuals\visual_export_mapping.json
- Archived prior mapping files under scripts\_archive\visual_export_mapping\$Stamp\
"@

foreach ($d in $DocsToUpdate) {
    Append-Doc $d $DocBlock
}

Write-Host "Done."
Write-Host "Archive folder: $ArchiveStamp"
Write-Host "Deployed mapping: $TargetPath"

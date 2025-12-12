# Run a single ETL script by name

param(
    [Parameter(Mandatory=$true)]
    [string]$ScriptName
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$orchestrator = Join-Path $scriptDir "run_all_etl.ps1"

& $orchestrator -ScriptNames $ScriptName


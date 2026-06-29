# run.ps1 — run the full Public Safety GIS pipeline on Windows (PowerShell).
# Usage:  .\run.ps1            # full pipeline
#         .\run.ps1 -Tests     # run tests first, then pipeline
param([switch]$Tests, [switch]$Quick)

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

$flags = @()
if ($Tests) { $flags += "--tests" }
if ($Quick) { $flags += "--quick" }

python scripts/run_pipeline.py @flags

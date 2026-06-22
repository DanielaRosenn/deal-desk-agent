# -----------------------------------------------------------------------------
# Downloads agent .nupkg files into DealDeskSolution/files/... for local reference
# or Studio-side workflows.
#
# Important: `uip solution pack` (CLI 1.195.x) does **not** currently embed these
# paths into the published solution zip (publish fails with missing
# files/adaptive-approval-agent-core_0.1.10/...). Use an already-valid artifact
# such as out/solution/DealDeskSolution_1.1.0.zip for `uip solution publish`, or
# publish from Studio Web until pack embeds agent packages again.
#
# Prerequisites: `uip login` to the target tenant (same as download source).
# -----------------------------------------------------------------------------

$ErrorActionPreference = "Stop"
$solRoot = Split-Path $PSScriptRoot -Parent
$dealDesk = Join-Path $solRoot "DealDeskSolution"
$filesRoot = Join-Path $dealDesk "files"

$d1 = Join-Path $filesRoot "adaptive-approval-agent-core_0.1.10"
$d2 = Join-Path $filesRoot "Package_adaptive-approval-agent-core_1_0.1.15"
New-Item -ItemType Directory -Force -Path $d1, $d2 | Out-Null

$tmp1 = Join-Path ([System.IO.Path]::GetTempPath()) "adaptive-approval-agent-core.0.1.10.nupkg"
$tmp2 = Join-Path ([System.IO.Path]::GetTempPath()) "Package_adaptive-approval-agent-core_1.0.1.15.nupkg"

uip or packages download "adaptive-approval-agent-core:0.1.10" --destination $tmp1 --output json | Out-Null
if (-not (Test-Path $tmp1)) { throw "Download failed: adaptive-approval-agent-core:0.1.10" }

uip or packages download "adaptive-approval-agent-core:0.1.15" --destination $tmp2 --output json | Out-Null
if (-not (Test-Path $tmp2)) { throw "Download failed: adaptive-approval-agent-core:0.1.15" }

Copy-Item $tmp1 (Join-Path $d1 "adaptive-approval-agent-core.0.1.10.nupkg") -Force
Copy-Item $tmp2 (Join-Path $d2 "Package_adaptive-approval-agent-core_1.0.1.15.nupkg") -Force

Get-ChildItem $filesRoot -Recurse -File | ForEach-Object { $_.FullName + " (" + $_.Length + " bytes)" }

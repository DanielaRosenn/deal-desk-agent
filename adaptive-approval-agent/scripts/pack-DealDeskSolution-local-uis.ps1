# -----------------------------------------------------------------------------
# Local folder backup only (ZIP renamed to .uis). No cloud calls.
#
# NOT VALID for UiPath Studio Web "Solution/Import" or similar import APIs.
# Those expect a platform-produced archive (e.g. from `uip solution download`).
# Importing this file typically returns 400 / "corrupt or compression isn't
# supported" because the layout is a plain workspace zip, not UiPath's export
# contract.
#
# For Studio Web: log in to the target tenant and run:
#   uip solution upload <path-to-DealDeskSolution-folder> [--force]
#
# Excludes: out, .local, bin, obj, .git, node_modules
# Output: adaptive-approval-agent/out/local/DealDeskSolution.uis
# -----------------------------------------------------------------------------
$ErrorActionPreference = "Stop"
$solRoot = Split-Path $PSScriptRoot -Parent
$src = Join-Path $solRoot "DealDeskSolution"
$outDir = Join-Path $solRoot "out\local"
$work = Join-Path $solRoot "out\local\uis-stage"
$uis = Join-Path $outDir "DealDeskSolution.uis"
$zip = Join-Path $outDir "DealDeskSolution.zip"

New-Item -ItemType Directory -Force -Path $outDir | Out-Null
if (Test-Path $work) { Remove-Item $work -Recurse -Force }
New-Item -ItemType Directory -Force -Path $work | Out-Null

robocopy $src $work /E /XD out .local bin obj .git node_modules /NFL /NDL /NJH /NJS /nc /ns /np | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy failed with exit code $LASTEXITCODE" }

if (Test-Path $zip) { Remove-Item $zip -Force }
if (Test-Path $uis) { Remove-Item $uis -Force }
Compress-Archive -Path (Join-Path $work "*") -DestinationPath $zip -CompressionLevel Optimal
Rename-Item -Path $zip -NewName "DealDeskSolution.uis"
Remove-Item $work -Recurse -Force

Get-Item $uis | Format-List FullName, Length, LastWriteTime
exit 0

param(
    [string]$SourceDir = $PSScriptRoot,
    [switch]$ReplaceExisting
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
Set-Location -LiteralPath $PSScriptRoot

if (-not (Test-Path -LiteralPath $SourceDir -PathType Container)) {
    throw "Source directory does not exist: $SourceDir"
}

$imports = @(
    @{ Zip = "version_info_v3_1.zip"; Target = "TapeReelDesigner3D" },
    @{ Zip = "TapeDesigner_Development_Migration_Recovery_Guide.zip"; Target = "TapeDesigner" },
    @{ Zip = "_patch_backups.zip"; Target = "RadiaToPythonStudio" },
    @{ Zip = "vite.config.zip"; Target = "ModelInterpreter" },
    @{ Zip = "PeperTranslator.zip"; Target = "PeperTranslator" }
)

$inboxDir = Join-Path $PSScriptRoot "inbox"
$stagingDir = Join-Path $PSScriptRoot "staging"
$appsDir = Join-Path $PSScriptRoot "apps-local"
$archiveDir = Join-Path $PSScriptRoot "archive"

New-Item -ItemType Directory -Force -Path $inboxDir, $stagingDir, $appsDir, $archiveDir | Out-Null

$imported = 0
$skipped = 0
$missing = 0

foreach ($item in $imports) {
    $source = Join-Path $SourceDir $item.Zip
    $inboxZip = Join-Path $inboxDir $item.Zip
    $target = Join-Path $appsDir $item.Target
    $stageTarget = Join-Path $stagingDir $item.Target

    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
        Write-Warning "ZIP not found; skipped: $source"
        $missing++
        continue
    }

    $sourceFull = [System.IO.Path]::GetFullPath($source)
    $inboxFull = [System.IO.Path]::GetFullPath($inboxZip)
    if (-not [System.String]::Equals($sourceFull, $inboxFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        Copy-Item -LiteralPath $source -Destination $inboxZip -Force
    }

    if ((Test-Path -LiteralPath $target) -and (-not $ReplaceExisting)) {
        Write-Warning "Target already exists; skipped: $target"
        Write-Warning "Use -ReplaceExisting to archive the current folder and import again."
        $skipped++
        continue
    }

    if (Test-Path -LiteralPath $stageTarget) {
        Remove-Item -LiteralPath $stageTarget -Recurse -Force
    }

    Write-Host "Extracting: $($item.Zip)"
    Write-Host "Destination: $target"

    try {
        Expand-Archive -LiteralPath $inboxZip -DestinationPath $stageTarget -Force

        if (Test-Path -LiteralPath $target) {
            $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
            $archiveTarget = Join-Path $archiveDir ("{0}_{1}" -f $item.Target, $timestamp)
            Move-Item -LiteralPath $target -Destination $archiveTarget
            Write-Host "Archived current app: $archiveTarget"
        }

        Move-Item -LiteralPath $stageTarget -Destination $target
        $imported++
    }
    catch {
        if (Test-Path -LiteralPath $stageTarget) {
            Remove-Item -LiteralPath $stageTarget -Recurse -Force
        }
        throw
    }
}

Write-Host ""
Write-Host "Import finished." -ForegroundColor Green
Write-Host "Imported: $imported"
Write-Host "Skipped : $skipped"
Write-Host "Missing : $missing"
Write-Host ""
Write-Host "The Hub will validate required files when it starts."
Write-Host "An imported ZIP may still appear as incomplete if files or environments are missing."

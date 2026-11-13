$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
Set-Location -LiteralPath $PSScriptRoot

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$pyInstaller = Join-Path $PSScriptRoot ".venv\Scripts\pyinstaller.exe"

if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
    throw "Run setup_windows.ps1 first."
}

& $venvPython -m pip install pyinstaller
& $pyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --onedir `
    --name ResearchToolHub `
    run_hub.py

$target = Join-Path $PSScriptRoot "dist\ResearchToolHub"
Copy-Item -Recurse -Force .\manifests (Join-Path $target "manifests")
Copy-Item -Recurse -Force .\data (Join-Path $target "data")
New-Item -ItemType Directory -Force (Join-Path $target "logs") | Out-Null
New-Item -ItemType Directory -Force (Join-Path $target "apps-local") | Out-Null
Copy-Item -Force .\apps-local\README.txt (Join-Path $target "apps-local\README.txt")
Copy-Item -Recurse -Force .\docs (Join-Path $target "docs")

Write-Host "Build finished: dist\ResearchToolHub" -ForegroundColor Green

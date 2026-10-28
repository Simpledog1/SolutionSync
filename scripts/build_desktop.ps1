# Builds the SolutionSync desktop app into dist\.
#   powershell -ExecutionPolicy Bypass -File scripts\build_desktop.ps1
# Output:
#   dist\SolutionSync\SolutionSync.exe                  the app folder
#   dist\SolutionSync-<version>-win64-portable.zip      that folder, zipped
#   dist\SolutionSync-<version>-setup.exe               installer (only if Inno Setup 6 is installed)
param([string]$Python = "py")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

# A private build environment, so nothing is installed into your normal Python.
$venv = Join-Path $Root ".venv-build"
if (-not (Test-Path "$venv\Scripts\python.exe")) { & $Python -m venv $venv }
$py = "$venv\Scripts\python.exe"
& $py -m pip install --disable-pip-version-check --quiet -r requirements-desktop.txt
if ($LASTEXITCODE) { throw "Installing build requirements failed." }

$version = & $py -c "from solsync import __version__; print(__version__)"
& $py -m PyInstaller --noconfirm --clean SolutionSync.spec
if ($LASTEXITCODE) { throw "PyInstaller failed." }
if (-not (Test-Path "dist\SolutionSync\SolutionSync.exe")) { throw "Build finished but SolutionSync.exe is missing." }

$zip = "dist\SolutionSync-$version-win64-portable.zip"
Remove-Item $zip -ErrorAction SilentlyContinue
Compress-Archive -Path "dist\SolutionSync" -DestinationPath $zip
Write-Output "Built: $Root\dist\SolutionSync\SolutionSync.exe"
Write-Output "Built: $Root\$zip"

$iscc = @("${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe", "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
          "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($iscc) {
    & $iscc /Qp "/DAppVersion=$version" "installer\SolutionSync.iss"
    if ($LASTEXITCODE) { throw "Inno Setup failed." }
    Write-Output "Built: $Root\dist\SolutionSync-$version-setup.exe"
} else {
    Write-Output "Inno Setup 6 not found: skipped the installer (the portable zip is complete)."
}

[CmdletBinding()]
param(
    [switch]$SkipDependencyInstall
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$virtualEnvironment = Join-Path $projectRoot ".venv"
$python = Join-Path $virtualEnvironment "Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
    $launcher = Get-Command "py" -ErrorAction SilentlyContinue
    $launcherArguments = @("-3")

    if ($null -eq $launcher) {
        $launcher = Get-Command "python" -ErrorAction SilentlyContinue
        $launcherArguments = @()
    }

    if ($null -eq $launcher) {
        throw "Python 3.10 이상을 찾을 수 없습니다. Python을 설치한 뒤 다시 실행해 주세요."
    }

    & $launcher.Source @launcherArguments -m venv $virtualEnvironment
    if ($LASTEXITCODE -ne 0) {
        throw "Python 가상환경을 만들지 못했습니다. 설치된 Python 실행 경로를 확인해 주세요."
    }
}

if (-not $SkipDependencyInstall) {
    & $python -m pip install --disable-pip-version-check -r (Join-Path $projectRoot "requirements-build.txt")
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller 설치에 실패했습니다. 네트워크 연결을 확인해 주세요."
    }
}

Push-Location $projectRoot
try {
    & $python -m PyInstaller --noconfirm --clean --distpath (Join-Path $projectRoot "dist") --workpath (Join-Path $projectRoot ".build\pyinstaller") (Join-Path $projectRoot "AutoMouseMover.spec")
    if ($LASTEXITCODE -ne 0) {
        throw "Windows 실행 파일 빌드에 실패했습니다."
    }
}
finally {
    Pop-Location
}

Write-Host "완료: $(Join-Path $projectRoot 'dist\AutoMouseMover.exe')"

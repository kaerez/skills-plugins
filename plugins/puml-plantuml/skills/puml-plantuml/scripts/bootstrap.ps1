# ============================================================
# plantuml-expert/scripts/bootstrap.ps1
# One-shot bootstrap for Windows 10/11.
# Requires: PowerShell 5.1+ (built into Windows 10/11, no install needed)
#
# Usage (in PowerShell as Administrator for installs):
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#   .\scripts\bootstrap.ps1
#   .\scripts\bootstrap.ps1 -Verify       # also run a test render
#   .\scripts\bootstrap.ps1 -JavaOnly     # only ensure Java
# ============================================================
param(
    [switch]$Verify,
    [switch]$JavaOnly
)
$ErrorActionPreference = "Stop"

function Write-Ok   { param($msg) Write-Host "  V  $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "  !  $msg" -ForegroundColor Yellow }
function Write-Info { param($msg) Write-Host "  >  $msg" -ForegroundColor Cyan }
function Write-Err  { param($msg) Write-Host "  X  $msg" -ForegroundColor Red }
function Write-Sep  { param($msg) Write-Host "`n-- $msg " -ForegroundColor Magenta }

# ── Package manager helpers ───────────────────────────────────────────────────
function Get-PackageManager {
    if (Get-Command winget  -ErrorAction SilentlyContinue) { return "winget" }
    if (Get-Command choco   -ErrorAction SilentlyContinue) { return "choco"  }
    if (Get-Command scoop   -ErrorAction SilentlyContinue) { return "scoop"  }
    return $null
}

function Install-Via-PM {
    param([string]$Tool, [string]$WingetId, [string]$ChocoId, [string]$ScoopId)
    $pm = Get-PackageManager
    switch ($pm) {
        "winget" { winget install --id $WingetId -e --silent --accept-package-agreements --accept-source-agreements }
        "choco"  { choco install $ChocoId -y }
        "scoop"  { scoop install $ScoopId }
        default  { throw "No package manager found. Install winget, choco, or scoop first." }
    }
}

# ── Python detection ──────────────────────────────────────────────────────────
function Find-Python {
    # Try Windows py launcher first (most reliable on Windows)
    foreach ($cmd in @("py", "python3", "python")) {
        try {
            $p = Get-Command $cmd -ErrorAction Stop
            # Check version >= 3.9
            $ver = & $cmd -c "import sys; print(sys.version_info[0], sys.version_info[1])" 2>$null
            if ($ver -match "^3 ([9-9]|[1-9]\d)") { return $cmd }
            if ($ver -match "^3 (\d+)" -and [int]$Matches[1] -ge 9) { return $cmd }
        } catch {}
    }
    # Check Windows Store / Program Files paths
    $paths = @(
        "$env:LOCALAPPDATA\Programs\Python\Python3*\python.exe",
        "$env:ProgramFiles\Python3*\python.exe",
        "$env:ProgramFiles\Python\python.exe"
    )
    foreach ($pat in $paths) {
        $found = Get-Item $pat -ErrorAction SilentlyContinue | Sort-Object -Descending | Select-Object -First 1
        if ($found -and (Test-Path $found)) { return $found.FullName }
    }
    return $null
}

function Install-Python {
    Write-Info "Python 3.9+ not found. Installing..."
    try {
        Install-Via-PM -Tool "Python" `
            -WingetId "Python.Python.3.12" `
            -ChocoId  "python312" `
            -ScoopId  "python"
    } catch {
        Write-Warn "Package manager install failed. Trying Microsoft Store..."
        Start-Process "ms-windows-store://pdp/?productid=9NRWMJLIVE2T"
        throw "Please install Python 3.9+ from the Microsoft Store or https://python.org then re-run this script."
    }
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path","User")
}

# ── Java detection ────────────────────────────────────────────────────────────
function Find-Java {
    # 1. java in PATH
    if (Get-Command java -ErrorAction SilentlyContinue) { return (Get-Command java).Source }

    # 2. JAVA_HOME
    if ($env:JAVA_HOME -and (Test-Path "$env:JAVA_HOME\bin\java.exe")) {
        return "$env:JAVA_HOME\bin\java.exe"
    }

    # 3. Well-known install locations (Azul/Zulu, Adoptium/Temurin, Microsoft, Oracle)
    $patterns = @(
        "C:\Program Files\Zulu\zulu*\bin\java.exe",
        "C:\Program Files\Eclipse Adoptium\jdk*\bin\java.exe",
        "C:\Program Files\Eclipse Adoptium\jre*\bin\java.exe",
        "C:\Program Files\Microsoft\jdk*\bin\java.exe",
        "C:\Program Files\Java\jdk*\bin\java.exe",
        "C:\Program Files\Java\jre*\bin\java.exe",
        "$env:LOCALAPPDATA\Programs\Eclipse Adoptium\jre*\bin\java.exe"
    )
    foreach ($pat in $patterns) {
        $found = Get-Item $pat -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | Select-Object -First 1
        if ($found) { return $found.FullName }
    }
    return $null
}

function Install-Java {
    Write-Info "Java 11+ not found. Installing Temurin 21 JRE..."
    try {
        # Try Adoptium Temurin first, then Azul Zulu
        Install-Via-PM -Tool "Java" `
            -WingetId "EclipseAdoptium.Temurin.21.JRE" `
            -ChocoId  "temurin21" `
            -ScoopId  "temurin-jre"
    } catch {
        Write-Warn "Adoptium install failed. Trying Azul Zulu..."
        try {
            Install-Via-PM -Tool "Java" `
                -WingetId "Azul.Zulu.21.JRE" `
                -ChocoId  "zulu21" `
                -ScoopId  "zulu"
        } catch {
            throw "Java install failed. Install manually from https://adoptium.net"
        }
    }
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path","User")
}

# ── PlantUML detection ────────────────────────────────────────────────────────
function Find-PlantUML {
    if (Get-Command plantuml -ErrorAction SilentlyContinue) { return "binary" }
    $jarPaths = @(
        "C:\ProgramData\chocolatey\lib\plantuml\tools\plantuml.jar",
        "$env:USERPROFILE\scoop\apps\plantuml\current\plantuml.jar",
        "$env:USERPROFILE\.plantuml\plantuml.jar",
        "$env:LOCALAPPDATA\Programs\plantuml\plantuml.jar"
    )
    foreach ($p in $jarPaths) {
        if (Test-Path $p) { return "jar:$p" }
    }
    return $null
}

function Install-PlantUML {
    Write-Info "Installing PlantUML..."
    try {
        Install-Via-PM -Tool "PlantUML" `
            -WingetId "plantuml.plantuml" `
            -ChocoId  "plantuml" `
            -ScoopId  "plantuml"
    } catch {
        Write-Warn "Package manager install failed. Downloading JAR..."
        $javaExe = Find-Java
        if (-not $javaExe) { throw "Java required for JAR method but not found." }

        $jarDir = "$env:USERPROFILE\.plantuml"
        New-Item -ItemType Directory -Force -Path $jarDir | Out-Null
        $jarPath = "$jarDir\plantuml.jar"
        Write-Info "Downloading plantuml.jar to $jarPath ..."
        Invoke-WebRequest `
            -Uri "https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar" `
            -OutFile $jarPath
        Write-Ok "Downloaded: $jarPath"

        # Set user env var persistently
        [Environment]::SetEnvironmentVariable("PLANTUML_JAR", $jarPath, "User")
        $env:PLANTUML_JAR = $jarPath
        Write-Info "Set PLANTUML_JAR=$jarPath (User environment variable)"
    }
}

# ── Main ──────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║    plantuml-expert bootstrap (Windows)          ║" -ForegroundColor Blue
Write-Host "╚══════════════════════════════════════════════════╝" -ForegroundColor Blue

# Python
Write-Sep "Python 3"
$pythonCmd = Find-Python
if ($pythonCmd) {
    $ver = & $pythonCmd --version 2>&1
    Write-Ok "Found: $pythonCmd  ($ver)"
} else {
    Install-Python
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path","User")
    $pythonCmd = Find-Python
    if (-not $pythonCmd) { Write-Err "Python install failed."; exit 1 }
    Write-Ok "Installed: $pythonCmd"
}

# Java
Write-Sep "Java"
$javaExe = Find-Java
if ($javaExe) {
    $ver = & $javaExe -version 2>&1 | Select-Object -First 1
    Write-Ok "Found: $javaExe  ($ver)"
} else {
    Install-Java
    $javaExe = Find-Java
    if (-not $javaExe) { Write-Err "Java install failed."; exit 1 }
    Write-Ok "Installed: $javaExe"
}

if ($JavaOnly) {
    Write-Host "`nV  Java ready." -ForegroundColor Green
    exit 0
}

# PlantUML
Write-Sep "PlantUML"
$puml = Find-PlantUML
if ($puml) {
    Write-Ok "Found: $puml"
} else {
    Install-PlantUML
    $puml = Find-PlantUML
    if (-not $puml) { Write-Err "PlantUML install failed."; exit 1 }
    Write-Ok "Installed: $puml"
}

# Delegate to Python setup.py for final verify
Write-Sep "Verify"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$setupArgs = if ($Verify) { @("$scriptDir\setup.py", "--verify") } else { @("$scriptDir\setup.py", "--check") }
& $pythonCmd @setupArgs

Write-Host ""
Write-Host "V  Bootstrap complete." -ForegroundColor Green
Write-Host "   Run: $pythonCmd $scriptDir\render.py --detect"

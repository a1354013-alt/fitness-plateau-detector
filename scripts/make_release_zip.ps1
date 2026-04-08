param(
  [string]$OutDir = ".\\release"
)

$ErrorActionPreference = "Stop"

function Ensure-EmptyDir([string]$Path) {
  if (Test-Path -LiteralPath $Path) {
    try {
      Get-ChildItem -Recurse -Force -LiteralPath $Path | ForEach-Object { $_.Attributes = 'Normal' }
    } catch {}
    Remove-Item -Recurse -Force -LiteralPath $Path -ErrorAction SilentlyContinue
  }
  New-Item -ItemType Directory -Path $Path | Out-Null
}

function Copy-Tree([string]$Source, [string]$Dest) {
  $excludeDirs = @(
    "node_modules",
    "dist",
    "dist-ssr",
    "__pycache__",
    ".venv",
    "venv",
    "backend\\data",
    "release",
    "release_tmp",
    ".vscode",
    ".idea",
    ".git"
  )
  $excludeFiles = @("*.pyc", "*.pyo", "*.pyd", "*.db", "*.sqlite", "*.sqlite3", ".env", ".env.*")

  $xdArgs = @()
  foreach ($d in $excludeDirs) { $xdArgs += @("/XD", $d) }

  $xfArgs = @()
  foreach ($f in $excludeFiles) { $xfArgs += @("/XF", $f) }

  New-Item -ItemType Directory -Path $Dest -Force | Out-Null

  # /E: include subdirs (incl empty), /NFL /NDL /NJH /NJS /NP: quiet output
  $args = @($Source, $Dest, "/E", "/NFL", "/NDL", "/NJH", "/NJS", "/NP") + $xdArgs + $xfArgs
  $rc = (Start-Process -FilePath "robocopy.exe" -ArgumentList $args -Wait -PassThru).ExitCode

  # robocopy uses bitmask exit codes; 0 and 1 are success
  if ($rc -gt 1) {
    throw "robocopy failed with exit code $rc"
  }
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Ensure-EmptyDir -Path $OutDir

$tmp = ".\\release_tmp"
Ensure-EmptyDir -Path $tmp

Copy-Tree -Source ".\\backend" -Dest (Join-Path $tmp "backend")
Copy-Tree -Source ".\\frontend" -Dest (Join-Path $tmp "frontend")

Copy-Item -LiteralPath ".\\README.md" -Destination (Join-Path $tmp "README.md") -Force
Copy-Item -LiteralPath ".\\PlateauBreaker_Technical_Guide.md" -Destination (Join-Path $tmp "PlateauBreaker_Technical_Guide.md") -Force
Copy-Item -LiteralPath ".\\.gitignore" -Destination (Join-Path $tmp ".gitignore") -Force
Copy-Item -LiteralPath ".\\.dockerignore" -Destination (Join-Path $tmp ".dockerignore") -Force

$zipPath = Join-Path $OutDir ("PlateauBreaker_release_{0}.zip" -f $timestamp)
if (Test-Path -LiteralPath $zipPath) { Remove-Item -Force -LiteralPath $zipPath }

Compress-Archive -Path (Join-Path $tmp "*") -DestinationPath $zipPath -CompressionLevel Optimal

try {
  Get-ChildItem -Recurse -Force -LiteralPath $tmp | ForEach-Object { $_.Attributes = 'Normal' }
} catch {}

try {
  Remove-Item -Recurse -Force -LiteralPath $tmp -ErrorAction Stop
} catch {
  Write-Warning ("Failed to remove release_tmp: " + $_.Exception.Message)
}

Write-Output "Created: $zipPath"

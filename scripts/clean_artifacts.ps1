param(
  [switch]$All
)

$ErrorActionPreference = "Stop"

function Remove-IfExists([string]$Path) {
  if (Test-Path -LiteralPath $Path) {
    try {
      Get-ChildItem -Recurse -Force -LiteralPath $Path -ErrorAction SilentlyContinue | ForEach-Object {
        try { $_.Attributes = "Normal" } catch {}
      }
    } catch {}

    try {
      Remove-Item -Recurse -Force -LiteralPath $Path -ErrorAction Stop
    } catch {
      # Retry once after another attribute normalization pass.
      try {
        Get-ChildItem -Recurse -Force -LiteralPath $Path -ErrorAction SilentlyContinue | ForEach-Object {
          try { $_.Attributes = "Normal" } catch {}
        }
      } catch {}
      Remove-Item -Recurse -Force -LiteralPath $Path -ErrorAction Stop
    }

    if (Test-Path -LiteralPath $Path) {
      throw "Failed to remove path: $Path (it may be locked or require elevated permissions)"
    }
  }
}

# Frontend artifacts
Remove-IfExists ".\\frontend\\dist"
Remove-IfExists ".\\frontend\\.npm-cache"
if ($All) {
  Remove-IfExists ".\\frontend\\node_modules"
}

# Backend caches
Get-ChildItem -Recurse -Force -Directory ".\\backend" |
  Where-Object { $_.Name -eq "__pycache__" } |
  ForEach-Object { Remove-IfExists $_.FullName }

# Release artifacts
if (Test-Path -LiteralPath ".\\release") {
  Get-ChildItem -Force -File ".\\release" -Filter "*.zip" | ForEach-Object {
    Remove-Item -Force -LiteralPath $_.FullName -ErrorAction SilentlyContinue
  }
}

Write-Output "Cleaned build artifacts. (Use -All to also remove frontend/node_modules.)"

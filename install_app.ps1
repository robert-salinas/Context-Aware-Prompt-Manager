param([switch]$Repair)
$ErrorActionPreference = 'Stop'
$appRoot = Join-Path $env:LOCALAPPDATA 'RS-Prompt-Manager\app'
$logRoot = Join-Path $env:APPDATA 'RS-Prompt-Manager'
New-Item -ItemType Directory -Force -Path $appRoot, $logRoot | Out-Null
Start-Transcript -Path (Join-Path $logRoot 'install.log') -Append | Out-Null
try {
    $source = Join-Path $PSScriptRoot 'dist\RS-Context-Prompt-Manager.exe'
    if (-not (Test-Path -LiteralPath $source)) { throw 'Falta el ejecutable de distribución.' }
    $target = Join-Path $appRoot 'RS-Context-Prompt-Manager.exe'
    $icon = Join-Path $appRoot 'icon.ico'
    $running = Get-Process 'RS-Context-Prompt-Manager' -ErrorAction SilentlyContinue
    if ($running) { throw 'Cierra RS Context Prompt Manager antes de instalar o actualizar.' }
    Copy-Item -LiteralPath $source -Destination $target -Force
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'assets\icon.ico') -Destination $icon -Force
    & (Join-Path $PSScriptRoot 'create_shortcut.ps1') -TargetPath $target -IconPath $icon -WorkingDirectory $appRoot
} finally { Stop-Transcript | Out-Null }

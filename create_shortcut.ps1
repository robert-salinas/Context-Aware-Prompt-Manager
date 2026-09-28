param(
    [string]$DesktopPath = [Environment]::GetFolderPath('DesktopDirectory'),
    [string]$TargetPath = '', [string]$IconPath = '', [string]$WorkingDirectory = ''
)
$ErrorActionPreference = 'Stop'
$target = if ($TargetPath) { $TargetPath } else { Join-Path $PSScriptRoot 'run_app.bat' }
$icon = if ($IconPath) { $IconPath } else { Join-Path $PSScriptRoot 'assets\icon.ico' }
$working = if ($WorkingDirectory) { $WorkingDirectory } else { Split-Path -Parent $target }
if (-not (Test-Path -LiteralPath $DesktopPath -PathType Container)) { throw 'No se encontró el Escritorio.' }
$link = Join-Path $DesktopPath 'RS Prompt Manager.lnk'
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($link)
$shortcut.TargetPath = $target
$shortcut.WorkingDirectory = $working
$shortcut.IconLocation = "$icon,0"
$shortcut.Description = 'RS Context Prompt Manager'
$shortcut.Save()
Write-Output "Acceso directo listo: $link"

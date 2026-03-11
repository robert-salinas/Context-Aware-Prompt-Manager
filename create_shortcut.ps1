$sLinkFile = "$env:USERPROFILE\Desktop\RS Prompt Manager.lnk" 
$oldLinkFile = "$env:USERPROFILE\Desktop\RS-Prompt-Manager.lnk"
$sTargetFile = "$PSScriptRoot\run_app.bat" 
$iconPath = "$PSScriptRoot\assets\icon.ico"

# Limpiar acceso directo viejo si existe
if (Test-Path $oldLinkFile) {
    Remove-Item $oldLinkFile -Force
}

$WshShell = New-Object -ComObject WScript.Shell 
$Shortcut = $WshShell.CreateShortcut($sLinkFile) 
$Shortcut.TargetPath = "cmd.exe"
$Shortcut.Arguments = "/c `"$sTargetFile`""
$Shortcut.WorkingDirectory = $PSScriptRoot 
$Shortcut.Description = "RS Prompt Manager Desktop App"

if (Test-Path $iconPath) {
    $Shortcut.IconLocation = "$iconPath,0"
}

$Shortcut.Save()
Write-Host "[SUCCESS] Acceso directo actualizado en el Escritorio con icono RS." -ForegroundColor Green

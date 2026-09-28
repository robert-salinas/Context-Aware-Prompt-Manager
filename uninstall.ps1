param([switch]$RemoveLibrary)
$desktopLink = Join-Path ([Environment]::GetFolderPath('DesktopDirectory')) 'RS Prompt Manager.lnk'
if (Test-Path -LiteralPath $desktopLink) { Remove-Item -LiteralPath $desktopLink -Force }
$app = Join-Path $env:LOCALAPPDATA 'RS-Prompt-Manager'
if (Test-Path -LiteralPath $app) { Remove-Item -LiteralPath $app -Recurse -Force }
if ($RemoveLibrary) {
    $data = Join-Path $env:APPDATA 'RS-Prompt-Manager'
    if (Test-Path -LiteralPath $data) { Remove-Item -LiteralPath $data -Recurse -Force }
}
Write-Output 'Aplicación desinstalada. La biblioteca se conserva salvo que uses -RemoveLibrary.'

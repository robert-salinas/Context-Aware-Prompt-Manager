param([Parameter(Mandatory=$true)][string]$CertificateThumbprint)
$ErrorActionPreference = 'Stop'
$signtool = Get-Command signtool.exe -ErrorAction Stop
$targets = @(
    (Join-Path $PSScriptRoot 'dist\RS-Context-Prompt-Manager.exe'),
    (Get-ChildItem (Join-Path $PSScriptRoot 'release\*.exe') -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName)
) | Where-Object { $_ -and (Test-Path -LiteralPath $_) }
foreach ($target in $targets) {
    & $signtool.Source sign /sha1 $CertificateThumbprint /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 $target
    if ($LASTEXITCODE -ne 0) { throw "No se pudo firmar $target" }
}

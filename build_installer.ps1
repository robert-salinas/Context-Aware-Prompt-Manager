$ErrorActionPreference = 'Stop'
$compiler = Get-Command iscc.exe -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $compiler) {
    $candidate = @(
        Get-ChildItem "$env:ProgramFiles\Inno Setup*\ISCC.exe" -ErrorAction SilentlyContinue
        Get-ChildItem "${env:ProgramFiles(x86)}\Inno Setup*\ISCC.exe" -ErrorAction SilentlyContinue
        Get-ChildItem "$env:LOCALAPPDATA\Programs\Inno Setup*\ISCC.exe" -ErrorAction SilentlyContinue
    ) | Sort-Object FullName -Descending | Select-Object -First 1
    if ($candidate) { $compilerPath = $candidate.FullName }
} else {
    $compilerPath = $compiler.Source
}
if (-not $compilerPath) { throw 'Instala Inno Setup para generar el instalador profesional.' }
& $compilerPath (Join-Path $PSScriptRoot 'installer.iss')
if ($LASTEXITCODE -ne 0) { throw 'No se pudo compilar el instalador.' }

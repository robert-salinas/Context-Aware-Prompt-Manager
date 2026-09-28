$ErrorActionPreference = 'Stop'
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Ejecuta run_app.bat --setup-only primero.' }
& $python -m pip install -e '.[dev]'
if ($LASTEXITCODE -ne 0) { throw 'No se pudieron preparar las herramientas.' }
& $python -m PyInstaller --noconfirm --clean (Join-Path $PSScriptRoot 'RS-Context-Prompt-Manager.spec')
if ($LASTEXITCODE -ne 0) { throw 'No se pudo construir el ejecutable.' }

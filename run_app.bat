@echo off
setlocal
cd /d "%~dp0"
title RS Context Prompt Manager
if not exist "%APPDATA%\RS-Prompt-Manager" mkdir "%APPDATA%\RS-Prompt-Manager"
set "RS_LOG=%APPDATA%\RS-Prompt-Manager\install.log"
if /I "%~1"=="--repair" goto :repair
powershell.exe -NoProfile -Command "if (Get-Process 'RS-Context-Prompt-Manager' -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }"
if not errorlevel 1 goto :already_running
if exist "dist\RS-Context-Prompt-Manager.exe" goto :installed
if exist ".venv\Scripts\python.exe" goto :check
py -3 -c "import sys; sys.exit(not sys.version_info >= (3, 11))" >nul 2>&1
if not errorlevel 1 (
  py -3 -m venv .venv >>"%RS_LOG%" 2>&1
  goto :check
)
python -c "import sys; sys.exit(not sys.version_info >= (3, 11))" >nul 2>&1
if errorlevel 1 goto :python_missing
python -m venv .venv >>"%RS_LOG%" 2>&1
:check
.venv\Scripts\python.exe -c "import prompt_mgr.gui" >nul 2>&1
if not errorlevel 1 goto :shortcut
echo Comprobando conexion con PyPI...
.venv\Scripts\python.exe -c "import urllib.request; urllib.request.urlopen('https://pypi.org/simple/', timeout=8)" >>"%RS_LOG%" 2>&1
if errorlevel 1 goto :network_error
.venv\Scripts\python.exe -m pip install -e . >>"%RS_LOG%" 2>&1
if errorlevel 1 goto :error
:shortcut
if exist ".venv\.desktop-shortcut-created" goto :launch
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0create_shortcut.ps1" >>"%RS_LOG%" 2>&1
if errorlevel 1 goto :error
type nul > ".venv\.desktop-shortcut-created"
:launch
if /I "%~1"=="--setup-only" exit /b 0
.venv\Scripts\python.exe -m prompt_mgr.gui
exit /b %errorlevel%
:installed
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_app.ps1"
if errorlevel 1 goto :error
if /I "%~1"=="--setup-only" exit /b 0
start "" "%LOCALAPPDATA%\RS-Prompt-Manager\app\RS-Context-Prompt-Manager.exe"
exit /b 0
:already_running
if /I "%~1"=="--setup-only" exit /b 0
start "" "%LOCALAPPDATA%\RS-Prompt-Manager\app\RS-Context-Prompt-Manager.exe"
exit /b 0
:repair
if exist "dist\RS-Context-Prompt-Manager.exe" (
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_app.ps1" -Repair
  exit /b %errorlevel%
)
if exist ".venv\Scripts\python.exe" goto :repair_install
py -3 -c "import sys; sys.exit(not sys.version_info >= (3, 11))" >nul 2>&1
if not errorlevel 1 (
  py -3 -m venv .venv >>"%RS_LOG%" 2>&1
  goto :repair_install
)
python -c "import sys; sys.exit(not sys.version_info >= (3, 11))" >nul 2>&1
if errorlevel 1 goto :python_missing
python -m venv .venv >>"%RS_LOG%" 2>&1
:repair_install
.venv\Scripts\python.exe -m pip install --upgrade --force-reinstall -e . >>"%RS_LOG%" 2>&1
del /q ".venv\.desktop-shortcut-created" >nul 2>&1
goto :shortcut
:network_error
echo [ERROR] No hay conexion con PyPI. Revisa %RS_LOG%
goto :fail
:python_missing
echo [ERROR] Se necesita Python 3.11 o el ejecutable publicado.
goto :fail
:error
echo [ERROR] No se pudo iniciar. Revisa %RS_LOG%
:fail
if /I not "%~1"=="--setup-only" pause
exit /b 1

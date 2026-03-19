@echo off 
setlocal 
title RS Prompt Manager - Launcher 
 
:: Configuración de colores (Naranja RS sobre fondo oscuro)
color 06 
 
echo ============================================ 
echo      RS DIGITAL - PROMPT MANAGER 
echo ============================================ 
 
:: 1. Verificar si existe el entorno virtual 
if not exist ".venv" ( 
    echo [INFO] Primera instalacion detectada... 
    echo [INFO] Creando entorno virtual Python... 
    python -m venv .venv 
    
    echo [INFO] Instalando dependencias desde requirements.txt... 
    call .venv\Scripts\activate 
    pip install -r requirements.txt 
    
    echo [SUCCESS] Instalacion completada. 
) else ( 
    echo [INFO] Entorno virtual encontrado. 
    call .venv\Scripts\activate 
) 
 
:: 2. Iniciar la aplicación 
echo [INFO] Iniciando RS Prompt Manager... 
:: Usamos PYTHONPATH para asegurar que encuentre el paquete prompt_mgr
set PYTHONPATH=src
start /b pythonw -m prompt_mgr.gui 
 
:: 3. (Opcional) Crear acceso directo en el escritorio si no existe 
if not exist "%USERPROFILE%\Desktop\RS Prompt Manager.lnk" ( 
    echo [INFO] Creando acceso directo en el Escritorio... 
    powershell -ExecutionPolicy Bypass -File create_shortcut.ps1 
) 
 
echo [OK] Aplicacion en ejecucion. Puedes cerrar esta ventana. 
timeout /t 3
exit

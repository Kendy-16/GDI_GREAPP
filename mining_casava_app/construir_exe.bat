@echo off
setlocal
cd /d "%~dp0"
echo === Generando MiningCasavaGRE.exe ===

if not exist .venv (
    python -m venv .venv || goto :error
)
call .venv\Scripts\activate.bat || goto :error
python -m pip install --upgrade pip || goto :error
pip install -r requirements-dev.txt || goto :error

pyinstaller --noconfirm --clean --onefile --windowed --name MiningCasavaGRE --collect-all mysql.connector main.py || goto :error

set SALIDA=dist\MiningCasavaGRE_v1.0
if exist "%SALIDA%" rmdir /s /q "%SALIDA%"
mkdir "%SALIDA%"
copy dist\MiningCasavaGRE.exe "%SALIDA%\" >nul
copy config.ini.example "%SALIDA%\config.ini.example" >nul
copy config.ini.example "%SALIDA%\config.ini" >nul
copy LEEME_EJECUTABLE.txt "%SALIDA%\LEEME.txt" >nul
if exist assets\logo.png (
    mkdir "%SALIDA%\assets"
    copy assets\logo.png "%SALIDA%\assets\" >nul
)

powershell -NoProfile -Command "Compress-Archive -Path '%SALIDA%\*' -DestinationPath 'dist\MiningCasavaGRE_v1.0.zip' -Force"

echo.
echo Listo. Ejecutable en: %SALIDA%\MiningCasavaGRE.exe
echo Paquete para GitHub:  dist\MiningCasavaGRE_v1.0.zip
exit /b 0

:error
echo.
echo ERROR: no se pudo generar el ejecutable. Revise los mensajes de arriba.
exit /b 1
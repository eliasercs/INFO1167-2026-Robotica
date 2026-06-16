@echo off
setlocal

set VENV_DIR=venv

if not exist "%VENV_DIR%" (
    echo Creando entorno virtual...
    virtualenv %VENV_DIR%
)

if "%1"=="activate" (
    echo Activando entorno virtual...
    endlocal
    call %VENV_DIR%\Scripts\activate.bat
    goto :eof
)

endlocal
@echo off
setlocal
cd /d "%~dp0"

set PYTHON_EXEC=python
if exist "venv\Scripts\python.exe" (
  set PYTHON_EXEC=venv\Scripts\python.exe
)

echo [1/2] Starting PlantVision AI Unified Platform...
echo Python interpreter: %PYTHON_EXEC%
echo Open in browser: http://127.0.0.1:5000
echo.
%PYTHON_EXEC% app.py

endlocal

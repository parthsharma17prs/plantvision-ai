@echo off
setlocal
cd /d "%~dp0"

set PYTHON_EXEC=python
if exist "venv\Scripts\python.exe" (
  set PYTHON_EXEC=venv\Scripts\python.exe
)

echo Starting PlantVision AI at http://127.0.0.1:5000
echo Drive Ingestion, YOLOv8 Model, and Real-Time Dashboard are enabled.
echo.
%PYTHON_EXEC% "app.py"

endlocal

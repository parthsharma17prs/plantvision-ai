@echo off
setlocal
cd /d "%~dp0"

set PYTHON_EXEC=python
if exist "venv\Scripts\python.exe" (
  set PYTHON_EXEC=venv\Scripts\python.exe
)
where %PYTHON_EXEC% >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python not found. Please install Python from https://python.org
  exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
  echo [ERROR] npm not found. Install Node.js from https://nodejs.org/
  exit /b 1
)

echo [1/3] Python dependencies ^(google-generativeai, etc.^)...
"%PYTHON_EXEC%" -m pip install -q -r requirements.txt
if errorlevel 1 (
  echo [ERROR] pip install failed.
  exit /b 1
)

echo [2/3] Building DTI frontend...
pushd DTI
call npm run build
if errorlevel 1 (
  echo [ERROR] npm run build failed.
  popd
  exit /b 1
)
popd

echo [3/3] Starting Flask backend + static frontend...
echo Open: http://127.0.0.1:5000
echo Optional: copy .env.example to .env for weather and to override Gemini key.
"%PYTHON_EXEC%" "app.py"

endlocal

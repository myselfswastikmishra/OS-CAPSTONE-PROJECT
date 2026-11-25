@echo off
cd /d "%~dp0"
python -c "import psutil, matplotlib" >nul 2>&1
if errorlevel 1 (
  echo Installing dependencies...
  python -m pip install -r requirements.txt
)
python src\monitor.py %*
pause

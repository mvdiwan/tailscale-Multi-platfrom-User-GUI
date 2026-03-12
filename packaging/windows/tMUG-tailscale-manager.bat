@echo off
REM tMUG - Tailscale Multi-platform User GUI
REM By DEC-LLC (Diwan Enterprise Consulting LLC)
REM License: Apache-2.0
REM
REM This launcher requires Python 3 and PyQt5 to be installed.
REM Install Python from https://www.python.org/downloads/
REM Then run: pip install PyQt5

setlocal

REM Try pythonw first (no console window), fall back to python, then python3
where pythonw >nul 2>&1
if %errorlevel% equ 0 (
    start "" pythonw "%~dp0tailscale_manager.py"
    goto :eof
)

where python >nul 2>&1
if %errorlevel% equ 0 (
    start "" python "%~dp0tailscale_manager.py"
    goto :eof
)

where python3 >nul 2>&1
if %errorlevel% equ 0 (
    start "" python3 "%~dp0tailscale_manager.py"
    goto :eof
)

echo ERROR: Python 3 is not installed or not in PATH.
echo.
echo Install Python from https://www.python.org/downloads/
echo Make sure to check "Add Python to PATH" during installation.
echo Then run: pip install PyQt5
echo.
pause

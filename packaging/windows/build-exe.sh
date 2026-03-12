#!/bin/bash
# =============================================================================
# tMUG - Build Standalone Windows .exe with PyInstaller
# By DEC-LLC (Diwan Enterprise Consulting LLC)
# License: Apache-2.0
#
# This script documents the PyInstaller build process for creating a
# standalone tMUG executable on Windows. It is meant to be run on a
# Windows machine (via Git Bash, MSYS2, or WSL) or adapted into a
# PowerShell/CMD workflow.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
APP_NAME="tMUG-tailscale-manager"
APP_VERSION="1.2.0"
MAIN_SCRIPT="$PROJECT_ROOT/cross-platform/tailscale_manager.py"

echo "=== tMUG Windows .exe Build ==="
echo "Version: $APP_VERSION"
echo ""

# ---- Prerequisites ---------------------------------------------------------
# Run these on your Windows build machine before executing this script:
#
#   1. Install Python 3.x from https://www.python.org/downloads/
#      - Check "Add Python to PATH" during installation
#
#   2. Install dependencies:
#        pip install PyQt5 pyinstaller
#
#   3. (Optional) Install Inno Setup for creating an installer:
#        https://jrsoftware.org/isinfo.php
#
# ---- Building the .exe -----------------------------------------------------
#
# The PyInstaller command below creates a single-file Windows executable.
# Run this from the project root directory on a Windows machine.

echo "Checking for PyInstaller..."
if ! command -v pyinstaller &>/dev/null; then
    echo "ERROR: PyInstaller is not installed."
    echo "  Install it with: pip install pyinstaller"
    exit 1
fi

echo "Checking for main script at: $MAIN_SCRIPT"
if [[ ! -f "$MAIN_SCRIPT" ]]; then
    echo "ERROR: tailscale_manager.py not found at $MAIN_SCRIPT"
    exit 1
fi

echo ""
echo "Building standalone .exe with PyInstaller..."
echo ""

# --onefile     : bundle everything into a single .exe
# --windowed    : do not show a console window (GUI app)
# --name        : output executable name
# --add-data    : include the SVG icon alongside the exe
# --distpath    : output directory for the final .exe
# --workpath    : temp build directory
# --specpath    : where to write the .spec file
pyinstaller \
    --onefile \
    --windowed \
    --name "$APP_NAME" \
    --add-data "$PROJECT_ROOT/tmug.svg;." \
    --distpath "$SCRIPT_DIR/dist" \
    --workpath "$SCRIPT_DIR/build" \
    --specpath "$SCRIPT_DIR" \
    "$MAIN_SCRIPT"

echo ""
echo "=== Build Complete ==="
echo "Executable: $SCRIPT_DIR/dist/$APP_NAME.exe"
echo ""
echo "To create a full installer, open tmug-setup.iss in Inno Setup Compiler."

# ---- Alternative: manual PyInstaller command --------------------------------
# If you prefer to run PyInstaller directly from a Windows Command Prompt:
#
#   cd path\to\tailscale-manager
#   pyinstaller --onefile --windowed --name tMUG-tailscale-manager ^
#       --add-data "tmug.svg;." ^
#       cross-platform\tailscale_manager.py
#
# The resulting .exe will be in the dist\ directory.
#
# ---- Notes ------------------------------------------------------------------
# - The --add-data separator is ";" on Windows and ":" on Linux/macOS.
# - If you have a .ico icon file, add: --icon=path\to\icon.ico
#   (SVG is not supported as a Windows icon; convert to .ico first)
# - To reduce file size, consider using UPX: --upx-dir=path\to\upx
# - For code signing, use signtool.exe after building:
#     signtool sign /f cert.pfx /p password /t http://timestamp.url dist\tMUG-tailscale-manager.exe

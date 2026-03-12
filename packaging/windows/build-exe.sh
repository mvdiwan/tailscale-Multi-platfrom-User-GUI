#!/bin/bash
# =============================================================================
# tMUG - Build Standalone Windows .exe with PyInstaller
# By DEC-LLC (Diwan Enterprise Consulting LLC)
# License: Apache-2.0
#
# This script builds a standalone tMUG executable using PyInstaller.
# The resulting .exe includes Python, PyQt5, and all dependencies —
# no Python installation is required on the target Windows machine.
#
# Run on Windows (Git Bash, MSYS2, or WSL) or Linux for cross-compilation.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
APP_NAME="tMUG-tailscale-manager"
APP_VERSION="1.3.0"
MAIN_SCRIPT="$PROJECT_ROOT/cross-platform/tailscale_manager.py"

echo "=== tMUG Windows .exe Build ==="
echo "Version: $APP_VERSION"
echo ""

# ---- Determine platform-specific --add-data separator -----------------------
# Windows uses ";" and Linux/macOS uses ":"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    SEP=";"
else
    SEP=":"
fi

# ---- Prerequisites ---------------------------------------------------------
# Run these on your build machine before executing this script:
#
#   pip install PyQt5 pyinstaller Pillow cairosvg
#
# To generate the .ico icon file:
#   python packaging/windows/create-icon.py

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

# ---- Generate icon if missing -----------------------------------------------
if [[ ! -f "$SCRIPT_DIR/tmug.ico" ]]; then
    echo "Generating tmug.ico from SVG..."
    if command -v python3 &>/dev/null; then
        python3 "$SCRIPT_DIR/create-icon.py"
    elif command -v python &>/dev/null; then
        python "$SCRIPT_DIR/create-icon.py"
    else
        echo "WARNING: Python not found, skipping icon generation."
        echo "  Run: python packaging/windows/create-icon.py"
    fi
fi

echo ""
echo "Building standalone .exe with PyInstaller..."
echo ""

# --onefile     : bundle everything into a single .exe
# --windowed    : do not show a console window (GUI app)
# --uac-admin   : request UAC elevation on launch (needed for Tailscale management)
# --name        : output executable name
# --icon        : Windows application icon (.ico)
# --add-data    : include the SVG icon alongside the exe
# --distpath    : output directory for the final .exe
# --workpath    : temp build directory
# --specpath    : where to write the .spec file
pyinstaller \
    --onefile \
    --windowed \
    --uac-admin \
    --name "$APP_NAME" \
    --icon "$SCRIPT_DIR/tmug.ico" \
    --add-data "$PROJECT_ROOT/tmug.svg${SEP}." \
    --distpath "$SCRIPT_DIR/dist" \
    --workpath "$SCRIPT_DIR/build" \
    --specpath "$SCRIPT_DIR" \
    "$MAIN_SCRIPT"

echo ""
echo "=== Build Complete ==="
echo "Executable: $SCRIPT_DIR/dist/$APP_NAME.exe"
echo ""
echo "To create a full installer, open tmug-setup.iss in Inno Setup Compiler."
echo "Or run the GitHub Actions workflow for automated builds."

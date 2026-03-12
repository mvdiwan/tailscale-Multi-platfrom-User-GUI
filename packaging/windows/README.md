# tMUG - Windows Packaging

Windows packaging files for **tMUG - Tailscale Multi-platform User GUI**.

Publisher: DEC-LLC (Diwan Enterprise Consulting LLC)
License: Apache-2.0

## Contents

| File | Purpose |
|------|---------|
| `tMUG-tailscale-manager.bat` | Launcher script for the PyQt5 version |
| `tmug-setup.iss` | Inno Setup installer script |
| `build-exe.sh` | PyInstaller build script for standalone .exe |

## Option 1: Run Directly (No Build Required)

If Python 3 and PyQt5 are already installed on the target Windows machine:

1. Copy the project files to the target machine.
2. Double-click `tMUG-tailscale-manager.bat` to launch.

The .bat launcher automatically finds Python (`pythonw`, `python`, or `python3`) and runs the application without showing a console window.

## Option 2: Standalone .exe with PyInstaller

Creates a single self-contained executable that does not require Python to be installed on the target machine.

**On a Windows build machine:**

```
pip install PyQt5 pyinstaller
cd path\to\tailscale-manager
pyinstaller --onefile --windowed --name tMUG-tailscale-manager ^
    --add-data "tmug.svg;." ^
    cross-platform\tailscale_manager.py
```

The resulting `tMUG-tailscale-manager.exe` will be in the `dist\` directory.

Alternatively, run `build-exe.sh` from Git Bash or WSL on the Windows build machine.

## Option 3: Windows Installer with Inno Setup

Creates a traditional Windows installer (.exe setup wizard) for end-user distribution.

**Prerequisites:**
- [Inno Setup 6](https://jrsoftware.org/isinfo.php) installed on the build machine
- Python 3 and PyQt5 on the target machine (the installer warns if Python is missing)

**Build the installer:**

1. Open `tmug-setup.iss` in Inno Setup Compiler.
2. Click Build > Compile (or press Ctrl+F9).
3. The installer will be created in the `output\` subdirectory.

The installer:
- Copies the Python source and launcher to `Program Files\tMUG\`
- Creates Start Menu shortcuts
- Optionally creates a desktop shortcut
- Provides a standard uninstaller
- Checks for Python at install time and warns if not found

## Option 4: Installer + Standalone .exe (Recommended for Distribution)

For the best end-user experience, combine both approaches:

1. Build the standalone .exe with PyInstaller (Option 2).
2. Modify `tmug-setup.iss` to install the .exe instead of the .py + .bat files.
3. Build the installer with Inno Setup (Option 3).

This gives users a familiar install wizard that installs a self-contained application with no Python dependency.

## Notes

- **Icon:** Windows executables and shortcuts require .ico format icons. Convert `tmug.svg` to `.ico` before building. The SVG reference in the .iss file will need to be updated to point to the .ico file.
- **Code signing:** For distribution outside your organization, consider signing the .exe with a code signing certificate to avoid SmartScreen warnings.
- **UAC:** tMUG needs administrator privileges to manage Tailscale. The application requests elevation at runtime as needed.

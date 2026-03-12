# tMUG - Windows Packaging

Windows packaging files for **tMUG - Tailscale Multi-platform User GUI**.

Publisher: DEC-LLC (Diwan Enterprise Consulting LLC)
License: Apache-2.0

## Contents

| File | Purpose |
|------|---------|
| `build-exe.sh` | PyInstaller build script for standalone .exe |
| `create-icon.py` | Converts tmug.svg to tmug.ico for Windows |
| `tmug-setup.iss` | Inno Setup installer script |
| `tmug.wxs` | WiX source for MSI builds |

## Architecture

tMUG is packaged as a standalone Windows executable using PyInstaller. The `.exe` bundles Python, PyQt5, and all dependencies -- no Python installation is required on the target machine.

```
PyInstaller --onefile --windowed --uac-admin
  -> tMUG-tailscale-manager.exe (standalone, ~80-100MB)
  -> Inno Setup wraps into tMUG-1.3.0-setup.exe
  -> User gets native Windows experience with UAC prompt
```

The `--uac-admin` flag ensures Windows displays a UAC elevation prompt when the application is launched, which is required for managing Tailscale.

## Building Locally

### Prerequisites

```
pip install PyQt5 pyinstaller Pillow cairosvg
```

### Step 1: Generate the icon

```
python packaging/windows/create-icon.py
```

### Step 2: Build the standalone .exe

On Windows (Git Bash or WSL):

```bash
bash packaging/windows/build-exe.sh
```

Or run PyInstaller directly from a Windows Command Prompt:

```
pyinstaller --onefile --windowed --uac-admin ^
    --name tMUG-tailscale-manager ^
    --icon packaging\windows\tmug.ico ^
    --add-data "tmug.svg;." ^
    cross-platform\tailscale_manager.py
```

The resulting `tMUG-tailscale-manager.exe` will be in the `dist\` directory.

### Step 3: Build the installer (optional)

**Inno Setup (.exe installer):**

1. Install [Inno Setup 6](https://jrsoftware.org/isinfo.php).
2. Copy `dist/tMUG-tailscale-manager.exe` to `packaging/windows/`.
3. Open `tmug-setup.iss` in Inno Setup Compiler and build.
4. The installer is created in the `output\` subdirectory.

**WiX (.msi installer):**

1. Place the built .exe in `packaging/windows/dist/`.
2. Run: `wixl -o tMUG-1.3.0-setup.msi tmug.wxs`

## Automated Builds (GitHub Actions)

The `build-windows.yml` workflow automatically builds the .exe and Inno Setup installer on:
- Version tags (`v*`)
- Manual dispatch

Artifacts are uploaded and available for download from the workflow run.

## Notes

- **Code signing:** For distribution outside your organization, consider signing the .exe with a code signing certificate to avoid SmartScreen warnings.
- **UAC:** The `--uac-admin` PyInstaller flag embeds a manifest requesting administrator privileges. Windows will show a UAC prompt on launch.
- **Icon:** The `create-icon.py` script converts `tmug.svg` to a multi-resolution `.ico` file (16x16, 32x32, 48x48, 256x256).

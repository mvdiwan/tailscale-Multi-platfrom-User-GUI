# tMUG — Tailscale Multi-platform User GUI

A lightweight GUI for managing [Tailscale](https://tailscale.com/) on desktop systems.

Provides a graphical interface with system tray integration for connecting, disconnecting, authenticating, and configuring Tailscale — no terminal required.

**Author:** DEC-LLC (Diwan Enterprise Consulting LLC)
**License:** MIT

## Features

- **System Tray** — minimizes to tray with status icon; right-click menu for quick actions
- **Connect / Disconnect** — bring Tailscale up or down
- **Login / Sign Up** — opens Tailscale authentication in your default browser to sign up, log in, or add the device to your tailnet
- **Logout** — disconnect and expire the node key
- **Status** — view your Tailscale IP, hostname, and connected peers
- **Exit Node** — select or clear an exit node to route traffic through
- **Settings** — toggle Accept DNS, Accept Routes, SSH, and Advertise as Exit Node
- **About** — version and author info

## Two Versions

### Bash + YAD (Linux only)

A lightweight version using Bash and [YAD](https://github.com/v1cont/yad) dialogs. Located in the project root.

**Dependencies:** `tailscale`, `yad`, `pkexec`, `xdg-open`

```bash
# Install
chmod +x install.sh
./install.sh

# Or run directly
./tMUG-tailscale-manager
```

### Python + PyQt5 (Cross-platform)

A full cross-platform version using Python and PyQt5. Located in `cross-platform/`. Works on Linux, macOS, and Windows.

**Dependencies:** Python 3.7+, PyQt5, Tailscale CLI

```bash
cd cross-platform
pip install -r requirements.txt
python3 tailscale_manager.py
```

See [cross-platform/README.md](cross-platform/README.md) for platform-specific details.

## Installation (Bash version)

```bash
git clone https://github.com/mvdiwan/tailscale-Multi-platfrom-User-GUI.git
cd tailscale-Multi-platfrom-User-GUI
chmod +x install.sh
./install.sh
```

Or manually:

```bash
sudo install -m 755 tMUG-tailscale-manager /usr/local/bin/tMUG-tailscale-manager
sudo install -m 644 tMUG-tailscale-manager.desktop /usr/share/applications/tMUG-tailscale-manager.desktop
sudo install -m 644 tailscale.svg /usr/share/pixmaps/tailscale.svg
sudo update-desktop-database /usr/share/applications/
```

## Uninstallation

```bash
chmod +x uninstall.sh
./uninstall.sh
```

## Usage

Launch "tMUG" from your application menu, or run:

```bash
tMUG-tailscale-manager
```

### First-time setup

1. Click **Login / Sign Up**
2. Your browser will open to the Tailscale login page
3. Sign up or log in with your account
4. Authorize the device
5. Click **Connect** to bring Tailscale up

The app minimizes to the system tray when you close the window. Right-click the tray icon for quick actions, or click "Quit" to fully exit.

## How it works

Both versions wrap the `tailscale` CLI in a GUI. Privileged operations (connect, disconnect, login, settings changes) use `pkexec` on Linux for a graphical authentication prompt. The system tray icon shows connection status and provides quick access to common actions.

## License

MIT - Copyright (c) 2026 DEC-LLC (Diwan Enterprise Consulting LLC)

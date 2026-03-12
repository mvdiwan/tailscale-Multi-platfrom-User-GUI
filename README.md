# tMUG — Tailscale Multi-platform User GUI

**tMUG** is a lightweight, open-source graphical interface for managing [Tailscale](https://tailscale.com/) VPN connections on desktop systems. It provides system tray integration and a simple point-and-click interface so users can connect, disconnect, authenticate, and configure Tailscale without ever touching a terminal.

**Author:** DEC-LLC (Diwan Enterprise Consulting LLC)
**License:** Apache 2.0

---

## Why tMUG?

Tailscale is an excellent mesh VPN built on WireGuard, but on Linux (and to some extent macOS/Windows), managing it typically requires the command line. There is no official Tailscale GUI for Linux desktops.

tMUG fills that gap by wrapping the `tailscale` CLI in a friendly desktop application that:

- Lives in your **system tray** so it's always accessible
- Handles **authentication** by opening your browser automatically — no copy-pasting URLs
- Lets you **connect/disconnect** with a single click
- Provides **exit node selection**, **DNS/route settings**, and **status monitoring** through simple dialogs
- Works on **Linux, macOS, and Windows** (via the cross-platform PyQt5 version)

Whether you're a sysadmin managing multiple machines, a remote worker who needs VPN access, or someone who just wants Tailscale to be as easy as clicking an icon — tMUG is for you.

---

## Features

| Feature | Description |
|---------|-------------|
| **System Tray** | Sits in your system tray with a status icon. Right-click for quick actions. Closing the window minimizes to tray — only "Quit" fully exits. |
| **Connect / Disconnect** | One-click to bring Tailscale up or down. |
| **Login / Sign Up** | Opens the Tailscale authentication page in your default browser. Sign up for a new account, log in, or add the device to your tailnet. |
| **Logout** | Disconnects and expires the node key. You'll need to re-authenticate to reconnect. |
| **Status** | View your Tailscale IP address, hostname, and all connected peers. |
| **Exit Node** | Browse available exit nodes, select one to route traffic through, or clear the selection. |
| **Settings** | Toggle Accept DNS, Accept Routes, Enable SSH, and Advertise as Exit Node. |
| **About** | Shows version, author (DEC-LLC), and license information. |

---

## Two Versions

tMUG ships in two flavors to suit different needs:

### 1. Bash + YAD (Linux only)

A lightweight version using Bash scripting and [YAD](https://github.com/v1cont/yad) (Yet Another Dialog) for the GUI. Minimal dependencies, installs in seconds.

- **Location:** Project root (`tMUG-tailscale-manager`)
- **Best for:** Linux users who want a simple, dependency-light solution

### 2. Python + PyQt5 (Cross-platform)

A full-featured version using Python and PyQt5. Runs on Linux, macOS, and Windows with native-looking widgets and a programmatically generated tray icon that changes color based on connection status (green = connected, grey = disconnected).

- **Location:** `cross-platform/` directory
- **Best for:** Users on macOS/Windows, or Linux users who prefer a more polished UI

---

## Installation

### Prerequisites

- **Tailscale** must be installed and the `tailscaled` daemon must be running.
  - Linux: https://tailscale.com/download/linux
  - macOS: https://tailscale.com/download/mac
  - Windows: https://tailscale.com/download/windows

### Bash version (Linux)

```bash
# Clone the repo
git clone https://github.com/mvdiwan/tailscale-Multi-platfrom-User-GUI.git
cd tailscale-Multi-platfrom-User-GUI

# Run the installer
chmod +x install.sh
./install.sh
```

**Dependencies:** `yad`, `tailscale`, `sudo`, `xdg-open`

Install YAD if you don't have it:
```bash
sudo apt install yad        # Debian/Ubuntu
sudo dnf install yad        # Fedora
sudo pacman -S yad          # Arch
```

### PyQt5 version (Cross-platform)

```bash
cd cross-platform
pip install -r requirements.txt
python3 tailscale_manager.py
```

**Dependencies:** Python 3.7+, PyQt5

See [cross-platform/README.md](cross-platform/README.md) for platform-specific notes.

### Manual installation (Bash version)

```bash
sudo install -m 755 tMUG-tailscale-manager /usr/local/bin/tMUG-tailscale-manager
sudo install -m 644 tMUG-tailscale-manager.desktop /usr/share/applications/tMUG-tailscale-manager.desktop
sudo install -m 644 tmug.svg /usr/share/pixmaps/tmug.svg
sudo update-desktop-database /usr/share/applications/
```

### Uninstallation

```bash
chmod +x uninstall.sh
./uninstall.sh
```

---

## User Guide

### Launching tMUG

- **From your app menu:** Search for **tMUG** in your desktop environment's application launcher
- **From a terminal:** Run `tMUG-tailscale-manager`

### First-time setup

1. Launch tMUG
2. Click **Login / Sign Up**
3. Your default browser opens to the Tailscale login page
4. Sign up for a new account or log in with an existing one (Google, Microsoft, GitHub, etc.)
5. Authorize this device to join your tailnet
6. Return to tMUG and click **Connect**
7. You should see "Status: Connected" with your Tailscale IP address

### Day-to-day usage

Once authenticated, tMUG lives in your system tray:

- **Left-click** the tray icon to open the main window
- **Right-click** the tray icon for a quick menu: Open Manager, Connect/Disconnect, Status, Quit
- **Close** the main window to minimize back to the tray
- Click **Quit** from the tray menu to fully exit tMUG

### Connecting and disconnecting

- Click **Connect** to bring Tailscale up. If you haven't authenticated yet, tMUG will open a browser window for you.
- Click **Disconnect** to take Tailscale down. Your device stays registered in your tailnet but goes offline.

### Using exit nodes

Exit nodes let you route all your internet traffic through another device on your tailnet (useful for accessing region-restricted content or routing through a trusted network).

1. Click **Exit Node**
2. Select a node from the list and click **Use Selected**
3. To stop using an exit node, click **Clear Exit Node**

Note: Exit nodes must be configured and approved in your Tailscale admin console.

### Changing settings

Click **Settings** to toggle:

- **Accept DNS** — use Tailscale's DNS (MagicDNS) for name resolution
- **Accept Routes** — accept subnet routes advertised by other nodes
- **Enable SSH** — allow incoming Tailscale SSH connections to this device
- **Advertise as Exit Node** — offer this device as an exit node for others

### Logging out

Click **Logout** to disconnect and expire your node key. This is useful when:
- Switching to a different Tailscale account
- Removing this device from your tailnet
- Troubleshooting authentication issues

You will need to re-authenticate (Login / Sign Up) to reconnect.

---

## Architecture

```
tMUG
├── tMUG-tailscale-manager          # Bash + YAD version (Linux)
├── tMUG-tailscale-manager.desktop  # Desktop entry for app menus
├── tmug.svg                        # Application icon (generic mesh network)
├── install.sh                      # Installer script
├── uninstall.sh                    # Uninstaller script
├── LICENSE                         # Apache 2.0 license
└── cross-platform/
    ├── tailscale_manager.py        # PyQt5 cross-platform version
    ├── requirements.txt            # Python dependencies
    ├── setup.py                    # Python packaging config
    └── README.md                   # Platform-specific notes
```

### How it works

Both versions follow the same architecture:

1. **CLI wrapper** — tMUG does not communicate with the Tailscale daemon directly. It invokes the `tailscale` CLI (`tailscale up`, `tailscale down`, `tailscale status`, etc.) and parses the output.

2. **Privilege escalation** — commands that modify Tailscale state (connect, disconnect, settings) require root privileges. On Linux, tMUG uses `sudo` for privilege escalation. On macOS/Windows, the user may need to run with administrator privileges.

3. **Authentication flow** — when `tailscale up` or `tailscale login` outputs an authentication URL, tMUG captures it and opens it in the user's default browser via `xdg-open` (Linux), `open` (macOS), or `start` (Windows).

4. **System tray** — the Bash version uses `yad --notification` with a named pipe for IPC. The PyQt5 version uses `QSystemTrayIcon` with a `QTimer` polling Tailscale status every 10 seconds to update the icon and tooltip.

5. **Status polling** — the PyQt5 version polls `tailscale status` every 10 seconds to keep the tray icon (green/grey) and tooltip (IP address) current. The Bash version updates on user actions.

---

## Troubleshooting

### tMUG won't launch

- **"yad: command not found"** — install YAD: `sudo apt install yad`
- **"tailscale: command not found"** — install Tailscale: https://tailscale.com/download/linux
- **No system tray** — tMUG requires a system tray. If your desktop environment doesn't have one (some GNOME configurations), install a tray extension like [AppIndicator](https://extensions.gnome.org/extension/615/appindicator-support/) or use the PyQt5 version.

### "Failed to connect" error

- Make sure the Tailscale daemon is running: `sudo systemctl status tailscaled`
- If it's not running: `sudo systemctl start tailscaled`
- Check for errors: `sudo tailscale status`

### Authentication URL doesn't open

- tMUG opens URLs with your system's default browser via `xdg-open`
- If no browser opens, check your default browser: `xdg-settings get default-web-browser`
- You can manually copy the URL shown in the dialog and paste it into any browser

### "No exit nodes available"

- Exit nodes must be enabled and approved in the [Tailscale admin console](https://login.tailscale.com/admin/machines)
- The device advertising as an exit node must have `--advertise-exit-node` set and be approved by an admin
- Run `tailscale exit-node list` in a terminal to verify

### Settings changes don't take effect

- Some settings require the Tailscale connection to be restarted. Try disconnecting and reconnecting.
- Check the Tailscale admin console for any policy overrides (ACLs) that might be enforcing settings.

### sudo password prompt doesn't appear

- Ensure `sudo` is installed and the current user has sudo privileges.
- If using passwordless sudo, the prompt will not appear (expected behavior).

### PyQt5 version: "System tray is not available"

- Your desktop environment may not support system tray icons natively
- On GNOME, install the AppIndicator extension
- On Wayland, tray support depends on your compositor

### General debugging

```bash
# Check Tailscale daemon status
sudo systemctl status tailscaled

# View Tailscale logs
sudo journalctl -u tailscaled -f

# Test Tailscale connectivity
tailscale status
tailscale ping <peer-hostname>

# Run tMUG from terminal to see error output
tMUG-tailscale-manager
```

---

## Contributing

Contributions are welcome. Please open an issue or pull request on GitHub.

## License

Copyright 2026 DEC-LLC (Diwan Enterprise Consulting LLC)

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for the full text.

---

*tMUG is not affiliated with or endorsed by Tailscale Inc. Tailscale is a registered trademark of Tailscale Inc.*

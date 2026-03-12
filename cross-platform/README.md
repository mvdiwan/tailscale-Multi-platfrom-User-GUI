# tMUG — Cross-Platform Version

A cross-platform GUI for managing Tailscale VPN connections, built with Python and PyQt5.

By DEC-LLC (Diwan Enterprise Consulting LLC) | MIT License

## Requirements

- Python 3.7+
- Tailscale CLI installed and in PATH
- A desktop environment with system tray support

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
python3 tailscale_manager.py
```

## Platform Notes

### Linux
- Privileged Tailscale commands (connect, disconnect, settings changes) are wrapped with `pkexec` for authorization.
- Ensure `polkit` (PolicyKit) is installed for the `pkexec` prompts to work.
- The `tailscale` CLI is expected at `/usr/bin/tailscale` (default).

### macOS
- The `tailscale` CLI is expected at `/usr/local/bin/tailscale`.
- You may need to run the app with administrator privileges for commands that modify Tailscale state.

### Windows
- The `tailscale` CLI is expected at `C:\Program Files\Tailscale\tailscale.exe`.
- Run the app as Administrator for full functionality.

## Features

- System tray icon with status indicator (green = connected, grey = disconnected)
- Connect / Disconnect with automatic auth URL detection
- Login / Sign Up / Logout
- View detailed status (IP, hostname, peers)
- Select or clear exit nodes
- Configure settings: Accept DNS, Accept Routes, Enable SSH, Advertise as Exit Node
- Periodic status polling (every 10 seconds)

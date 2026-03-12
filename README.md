# Tailscale Manager

A lightweight GUI for managing [Tailscale](https://tailscale.com/) on Linux desktops. Built with Bash and [YAD](https://github.com/v1cont/yad) (Yet Another Dialog).

## Features

- **Connect / Disconnect** — bring Tailscale up or down
- **Login / Sign Up** — opens Tailscale authentication in your default browser to sign up, log in, or add the device to your tailnet
- **Logout** — disconnect and expire the node key
- **Status** — view your Tailscale IP, hostname, and connected peers
- **Exit Node** — select or clear an exit node to route traffic through
- **Settings** — toggle Accept DNS, Accept Routes, SSH, and Advertise as Exit Node

Uses `pkexec` for privilege escalation (graphical sudo prompt) and `xdg-open` to open auth URLs in your default browser.

## Screenshots

The main window shows your connection status and provides buttons for all operations.

## Dependencies

- **tailscale** — the Tailscale CLI and daemon ([install](https://tailscale.com/download/linux))
- **yad** — Yet Another Dialog (`sudo apt install yad`)
- **pkexec** — PolicyKit agent (included in most desktop environments)
- **xdg-open** — desktop URL opener (included in most desktop environments)

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/tailscale-manager.git
cd tailscale-manager
chmod +x install.sh
./install.sh
```

Or manually:

```bash
sudo install -m 755 tailscale-manager /usr/local/bin/tailscale-manager
sudo install -m 644 tailscale-manager.desktop /usr/share/applications/tailscale-manager.desktop
sudo install -m 644 tailscale.svg /usr/share/pixmaps/tailscale.svg
sudo update-desktop-database /usr/share/applications/
```

## Uninstallation

```bash
chmod +x uninstall.sh
./uninstall.sh
```

## Usage

Launch "Tailscale Manager" from your application menu, or run:

```bash
tailscale-manager
```

### First-time setup

1. Click **Login / Sign Up**
2. Your browser will open to the Tailscale login page
3. Sign up or log in with your account
4. Authorize the device
5. Click **Connect** to bring Tailscale up

## How it works

This is a simple Bash script that wraps the `tailscale` CLI commands in a YAD-based GUI. All privileged operations (connect, disconnect, login, settings changes) go through `pkexec` so you get a proper graphical authentication prompt.

## License

MIT

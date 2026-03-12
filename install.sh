#!/usr/bin/env bash
# Installer for Tailscale Manager GUI
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Installing Tailscale Manager..."

# Check dependencies
for cmd in yad tailscale pkexec xdg-open; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "Error: '$cmd' is required but not installed."
        [ "$cmd" = "yad" ] && echo "  Install with: sudo apt install yad"
        [ "$cmd" = "tailscale" ] && echo "  Install from: https://tailscale.com/download/linux"
        exit 1
    fi
done

sudo install -m 755 "$SCRIPT_DIR/tailscale-manager" /usr/local/bin/tailscale-manager
sudo install -m 644 "$SCRIPT_DIR/tailscale-manager.desktop" /usr/share/applications/tailscale-manager.desktop
sudo install -m 644 "$SCRIPT_DIR/tailscale.svg" /usr/share/pixmaps/tailscale.svg
sudo update-desktop-database /usr/share/applications/ 2>/dev/null || true

echo "Done! Tailscale Manager is now available in your application menu."

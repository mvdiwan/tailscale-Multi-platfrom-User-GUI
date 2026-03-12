#!/usr/bin/env bash
# Installer for Tailscale Manager GUI
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Installing tMUG (Tailscale Multi-platform User GUI)..."

# Check dependencies
for cmd in yad tailscale sudo xdg-open; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "Error: '$cmd' is required but not installed."
        [ "$cmd" = "yad" ] && echo "  Install with: sudo apt install yad"
        [ "$cmd" = "tailscale" ] && echo "  Install from: https://tailscale.com/download/linux"
        exit 1
    fi
done

sudo install -m 755 "$SCRIPT_DIR/tMUG-tailscale-manager" /usr/local/bin/tMUG-tailscale-manager
sudo install -m 644 "$SCRIPT_DIR/tMUG-tailscale-manager.desktop" /usr/share/applications/tMUG-tailscale-manager.desktop
sudo install -m 644 "$SCRIPT_DIR/tmug.svg" /usr/share/pixmaps/tmug.svg
sudo update-desktop-database /usr/share/applications/ 2>/dev/null || true

echo "Done! tMUG is now available in your application menu."

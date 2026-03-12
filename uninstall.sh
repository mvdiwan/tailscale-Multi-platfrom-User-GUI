#!/usr/bin/env bash
# Uninstaller for Tailscale Manager GUI
set -e

echo "Removing Tailscale Manager..."

sudo rm -f /usr/local/bin/tailscale-manager
sudo rm -f /usr/share/applications/tailscale-manager.desktop
sudo rm -f /usr/share/pixmaps/tailscale.svg
sudo update-desktop-database /usr/share/applications/ 2>/dev/null || true

echo "Done! Tailscale Manager has been removed."

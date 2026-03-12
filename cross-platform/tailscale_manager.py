#!/usr/bin/env python3
"""
Tailscale Manager - Cross-platform GUI for managing Tailscale
By DEC-LLC (Diwan Enterprise Consulting LLC)
License: MIT
"""

import json
import platform
import re
import subprocess
import sys
import webbrowser

from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QColor, QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSystemTrayIcon,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

VERSION = "1.0.0"
AUTHOR = "DEC-LLC (Diwan Enterprise Consulting LLC)"
LICENSE = "MIT"
POLL_INTERVAL_MS = 10000  # 10 seconds


# ---------------------------------------------------------------------------
# Platform helpers
# ---------------------------------------------------------------------------

def _system():
    return platform.system()  # "Linux", "Darwin", "Windows"


def _tailscale_cmd():
    """Return the base tailscale CLI command for this platform."""
    s = _system()
    if s == "Windows":
        return r"C:\Program Files\Tailscale\tailscale.exe"
    if s == "Darwin":
        return "/usr/local/bin/tailscale"
    return "tailscale"


def _run(args, privileged=False, timeout=30):
    """Run a tailscale CLI command and return (returncode, stdout, stderr).

    On Linux privileged commands are wrapped with pkexec.
    On other platforms the caller is expected to run as admin if needed.
    """
    cmd = [_tailscale_cmd()] + args
    if privileged and _system() == "Linux":
        cmd = ["pkexec"] + cmd

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError:
        return -1, "", "tailscale command not found. Is Tailscale installed?"
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out."
    except Exception as e:
        return -1, "", str(e)


# ---------------------------------------------------------------------------
# Icon generation (3x3 dot grid, similar to tailscale.svg)
# ---------------------------------------------------------------------------

def _make_icon_pixmap(size=64, connected=None):
    """Draw a 3x3 dot-grid icon.

    connected=True  -> green dots
    connected=False -> grey dots
    connected=None  -> dark grey (neutral / app icon)
    """
    pix = QPixmap(QSize(size, size))
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)

    if connected is True:
        color = QColor("#2ecc71")
    elif connected is False:
        color = QColor("#95a5a6")
    else:
        color = QColor("#4a4a5a")

    p.setBrush(color)
    p.setPen(Qt.NoPen)

    margin = size * 0.15
    usable = size - 2 * margin
    spacing = usable / 2
    radius = size * 0.10

    for row in range(3):
        for col in range(3):
            cx = margin + col * spacing
            cy = margin + row * spacing
            p.drawEllipse(int(cx - radius), int(cy - radius),
                          int(radius * 2), int(radius * 2))
    p.end()
    return pix


def make_icon(connected=None):
    return QIcon(_make_icon_pixmap(64, connected))


# ---------------------------------------------------------------------------
# Tailscale helpers
# ---------------------------------------------------------------------------

def is_connected():
    rc, out, err = _run(["status"])
    return rc == 0


def get_ip():
    rc, out, err = _run(["ip", "-4"])
    if rc == 0 and out.strip():
        return out.strip()
    return None


def get_self_info():
    """Return (hostname, ip) from tailscale status --self --json."""
    rc, out, err = _run(["status", "--self", "--json"])
    hostname = "unknown"
    ip = get_ip()
    if rc == 0 and out.strip():
        try:
            data = json.loads(out)
            hostname = data.get("Self", {}).get("HostName", "unknown")
        except json.JSONDecodeError:
            pass
    return hostname, ip


def get_status_text():
    """Return full status text."""
    rc, out, err = _run(["status"])
    return out if rc == 0 else err


def get_exit_nodes():
    """Return list of (ip, name) tuples for available exit nodes."""
    rc, out, err = _run(["exit-node", "list"])
    if rc != 0 or not out.strip():
        return []
    lines = out.strip().splitlines()
    # skip header row
    nodes = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 2:
            nodes.append((parts[0], parts[1]))
    return nodes


def get_current_prefs():
    """Return dict of current preferences via tailscale debug prefs."""
    rc, out, err = _run(["debug", "prefs"])
    if rc == 0 and out.strip():
        try:
            return json.loads(out)
        except json.JSONDecodeError:
            pass
    return {}


# ---------------------------------------------------------------------------
# Dialogs
# ---------------------------------------------------------------------------

class StatusDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tailscale Status")
        self.setMinimumSize(550, 400)
        layout = QVBoxLayout(self)

        connected = is_connected()
        if connected:
            hostname, ip = get_self_info()
            header = QLabel(
                f"<b>Status:</b> Connected<br>"
                f"<b>IP:</b> {ip or 'N/A'}<br>"
                f"<b>Hostname:</b> {hostname}"
            )
        else:
            header = QLabel("<b>Status:</b> Disconnected")

        layout.addWidget(header)

        if connected:
            peers_label = QLabel("<b>Peers:</b>")
            layout.addWidget(peers_label)
            text = QTextEdit()
            text.setReadOnly(True)
            text.setFontFamily("monospace")
            text.setPlainText(get_status_text())
            layout.addWidget(text)

        btn = QDialogButtonBox(QDialogButtonBox.Ok)
        btn.accepted.connect(self.accept)
        layout.addWidget(btn)


class ExitNodeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tailscale - Exit Nodes")
        self.setMinimumSize(500, 400)
        self.selected_ip = None
        self.action = None  # "set" or "clear"

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select an exit node (or clear to remove):"))

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["IP", "Name"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        nodes = get_exit_nodes()
        self.table.setRowCount(len(nodes))
        for i, (ip, name) in enumerate(nodes):
            self.table.setItem(i, 0, QTableWidgetItem(ip))
            self.table.setItem(i, 1, QTableWidgetItem(name))

        if not nodes:
            layout.addWidget(QLabel("No exit nodes available."))

        btn_layout = QHBoxLayout()
        use_btn = QPushButton("Use Selected")
        use_btn.clicked.connect(self._use_selected)
        clear_btn = QPushButton("Clear Exit Node")
        clear_btn.clicked.connect(self._clear)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(use_btn)
        btn_layout.addWidget(clear_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _use_selected(self):
        rows = self.table.selectionModel().selectedRows()
        if rows:
            self.selected_ip = self.table.item(rows[0].row(), 0).text()
            self.action = "set"
            self.accept()
        else:
            QMessageBox.warning(self, "Tailscale", "No exit node selected.")

    def _clear(self):
        self.action = "clear"
        self.accept()


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tailscale - Settings")
        self.setMinimumWidth(400)

        prefs = get_current_prefs()

        layout = QVBoxLayout(self)
        group = QGroupBox("Tailscale Settings")
        gl = QVBoxLayout(group)

        self.dns_cb = QCheckBox("Accept DNS")
        self.dns_cb.setChecked(prefs.get("CorpDNS", True))
        gl.addWidget(self.dns_cb)

        self.routes_cb = QCheckBox("Accept Routes")
        self.routes_cb.setChecked(prefs.get("RouteAll", False))
        gl.addWidget(self.routes_cb)

        self.ssh_cb = QCheckBox("Enable SSH")
        self.ssh_cb.setChecked(prefs.get("RunSSH", False))
        gl.addWidget(self.ssh_cb)

        self.exit_node_cb = QCheckBox("Advertise as Exit Node")
        self.exit_node_cb.setChecked(False)
        gl.addWidget(self.exit_node_cb)

        layout.addWidget(group)

        btn = QDialogButtonBox(QDialogButtonBox.Apply | QDialogButtonBox.Cancel)
        btn.button(QDialogButtonBox.Apply).clicked.connect(self._apply)
        btn.rejected.connect(self.reject)
        layout.addWidget(btn)

    def _apply(self):
        args = ["set"]
        args.append(f"--accept-dns={'true' if self.dns_cb.isChecked() else 'false'}")
        args.append(f"--accept-routes={'true' if self.routes_cb.isChecked() else 'false'}")
        args.append(f"--ssh={'true' if self.ssh_cb.isChecked() else 'false'}")
        if self.exit_node_cb.isChecked():
            args.append("--advertise-exit-node")
        else:
            args.append("--advertise-exit-node=false")

        rc, out, err = _run(args, privileged=True)
        if rc == 0:
            QMessageBox.information(self, "Tailscale", "Settings applied.")
            self.accept()
        else:
            QMessageBox.critical(self, "Tailscale", f"Failed to apply settings.\n\n{err or out}")


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tailscale Manager")
        self.setFixedSize(420, 350)
        self.setWindowIcon(make_icon())

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Status label
        self.status_label = QLabel("Checking status...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; padding: 8px;")
        layout.addWidget(self.status_label)

        # Buttons
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setMinimumHeight(36)
        self.connect_btn.clicked.connect(self._on_connect_disconnect)
        layout.addWidget(self.connect_btn)

        self.auth_btn = QPushButton("Login / Sign Up")
        self.auth_btn.setMinimumHeight(36)
        self.auth_btn.clicked.connect(self._on_auth)
        layout.addWidget(self.auth_btn)

        row1 = QHBoxLayout()
        status_btn = QPushButton("Status")
        status_btn.setMinimumHeight(36)
        status_btn.clicked.connect(self._on_status)
        row1.addWidget(status_btn)

        exit_node_btn = QPushButton("Exit Node")
        exit_node_btn.setMinimumHeight(36)
        exit_node_btn.clicked.connect(self._on_exit_node)
        row1.addWidget(exit_node_btn)
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        settings_btn = QPushButton("Settings")
        settings_btn.setMinimumHeight(36)
        settings_btn.clicked.connect(self._on_settings)
        row2.addWidget(settings_btn)

        about_btn = QPushButton("About")
        about_btn.setMinimumHeight(36)
        about_btn.clicked.connect(self._on_about)
        row2.addWidget(about_btn)
        layout.addLayout(row2)

        close_btn = QPushButton("Close")
        close_btn.setMinimumHeight(36)
        close_btn.clicked.connect(self._minimize_to_tray)
        layout.addWidget(close_btn)

        # ---- System tray ----
        self.tray = QSystemTrayIcon(make_icon(), self)
        self.tray.setToolTip("Tailscale: Checking...")
        self.tray.activated.connect(self._tray_activated)

        tray_menu = QMenu()
        self.tray_connect_action = QAction("Connect", self)
        self.tray_connect_action.triggered.connect(self._on_connect_disconnect)
        tray_menu.addAction(self.tray_connect_action)

        tray_status_action = QAction("Status", self)
        tray_status_action.triggered.connect(self._on_status)
        tray_menu.addAction(tray_status_action)

        tray_open_action = QAction("Open Manager", self)
        tray_open_action.triggered.connect(self._show_window)
        tray_menu.addAction(tray_open_action)

        tray_menu.addSeparator()
        tray_quit_action = QAction("Quit", self)
        tray_quit_action.triggered.connect(self._quit)
        tray_menu.addAction(tray_quit_action)

        self.tray.setContextMenu(tray_menu)
        self.tray.show()

        # ---- Status polling timer ----
        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll_status)
        self._poll_timer.start(POLL_INTERVAL_MS)
        self._poll_status()  # initial

    # -- Polling ----------------------------------------------------------

    def _poll_status(self):
        connected = is_connected()
        ip = get_ip() if connected else None

        if connected:
            self.status_label.setText(f"<b>Connected</b> ({ip or 'N/A'})")
            self.connect_btn.setText("Disconnect")
            self.auth_btn.setText("Logout")
            self.tray.setIcon(make_icon(connected=True))
            self.tray.setToolTip(f"Tailscale: Connected ({ip})")
            self.tray_connect_action.setText("Disconnect")
        else:
            self.status_label.setText("<b>Disconnected</b>")
            self.connect_btn.setText("Connect")
            self.auth_btn.setText("Login / Sign Up")
            self.tray.setIcon(make_icon(connected=False))
            self.tray.setToolTip("Tailscale: Disconnected")
            self.tray_connect_action.setText("Connect")

    # -- Actions -----------------------------------------------------------

    def _on_connect_disconnect(self):
        if is_connected():
            self._do_disconnect()
        else:
            self._do_connect()

    def _do_connect(self):
        rc, out, err = _run(["up"], privileged=True, timeout=60)
        combined = out + err

        if rc == 0 and is_connected():
            ip = get_ip()
            QMessageBox.information(
                self, "Tailscale",
                f"Successfully connected to Tailscale!\n\nIP: {ip or 'N/A'}"
            )
        else:
            url = _extract_auth_url(combined)
            if url:
                webbrowser.open(url)
                QMessageBox.information(
                    self, "Tailscale",
                    "A browser window has been opened for authentication.\n\n"
                    "Once you log in and authorize this device, it will connect "
                    "automatically.\n\n"
                    f"If the browser didn't open, visit:\n{url}"
                )
            else:
                QMessageBox.critical(
                    self, "Tailscale",
                    f"Failed to connect.\n\n{combined}"
                )
        self._poll_status()

    def _do_disconnect(self):
        reply = QMessageBox.question(
            self, "Tailscale", "Disconnect from Tailscale?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            rc, out, err = _run(["down"], privileged=True)
            if rc == 0:
                QMessageBox.information(self, "Tailscale", "Disconnected from Tailscale.")
            else:
                QMessageBox.critical(self, "Tailscale", f"Failed to disconnect.\n\n{err or out}")
        self._poll_status()

    def _on_auth(self):
        if is_connected():
            self._do_logout()
        else:
            self._do_login()

    def _do_login(self):
        rc, out, err = _run(["login"], privileged=True, timeout=60)
        combined = out + err
        url = _extract_auth_url(combined)
        if url:
            webbrowser.open(url)
            QMessageBox.information(
                self, "Tailscale",
                "A browser window has been opened to log in to Tailscale.\n\n"
                "You can:\n"
                "  - Sign up for a new account\n"
                "  - Log in to an existing account\n"
                "  - Add this device to your tailnet\n\n"
                f"If the browser didn't open, visit:\n{url}"
            )
        elif rc == 0:
            QMessageBox.information(self, "Tailscale", "Already logged in and authenticated.")
        else:
            QMessageBox.critical(self, "Tailscale", f"Login failed.\n\n{combined}")
        self._poll_status()

    def _do_logout(self):
        reply = QMessageBox.question(
            self, "Tailscale",
            "Log out from Tailscale?\n\n"
            "This will disconnect and expire your node key.\n"
            "You will need to re-authenticate to reconnect.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            rc, out, err = _run(["logout"], privileged=True)
            if rc == 0:
                QMessageBox.information(self, "Tailscale", "Logged out from Tailscale.")
            else:
                QMessageBox.critical(self, "Tailscale", f"Logout failed.\n\n{err or out}")
        self._poll_status()

    def _on_status(self):
        dlg = StatusDialog(self)
        dlg.exec_()

    def _on_exit_node(self):
        dlg = ExitNodeDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            if dlg.action == "set" and dlg.selected_ip:
                rc, out, err = _run(
                    ["set", f"--exit-node={dlg.selected_ip}"], privileged=True
                )
                if rc == 0:
                    QMessageBox.information(
                        self, "Tailscale",
                        f"Exit node set to: {dlg.selected_ip}"
                    )
                else:
                    QMessageBox.critical(
                        self, "Tailscale",
                        f"Failed to set exit node.\n\n{err or out}"
                    )
            elif dlg.action == "clear":
                rc, out, err = _run(["set", "--exit-node="], privileged=True)
                if rc == 0:
                    QMessageBox.information(self, "Tailscale", "Exit node cleared.")
                else:
                    QMessageBox.critical(
                        self, "Tailscale",
                        f"Failed to clear exit node.\n\n{err or out}"
                    )

    def _on_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec_()

    def _on_about(self):
        QMessageBox.about(
            self, "About Tailscale Manager",
            f"<h3>Tailscale Manager v{VERSION}</h3>"
            f"<p>by {AUTHOR}</p>"
            f"<p>License: {LICENSE}</p>"
            "<p>A cross-platform GUI for managing Tailscale VPN connections.</p>"
        )

    # -- Window / tray management ------------------------------------------

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # left-click
            self._show_window()

    def _show_window(self):
        self._poll_status()
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def _minimize_to_tray(self):
        self.hide()

    def _quit(self):
        self.tray.hide()
        QApplication.quit()

    def closeEvent(self, event):
        # Override close to minimize to tray instead
        event.ignore()
        self._minimize_to_tray()


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _extract_auth_url(text):
    """Pull a https://login.tailscale.com/... URL from command output."""
    match = re.search(r'https://login\.tailscale\.com/\S+', text)
    return match.group(0) if match else None


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Tailscale Manager")
    app.setQuitOnLastWindowClosed(False)  # keep running in tray
    app.setWindowIcon(make_icon())

    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(
            None, "Tailscale Manager",
            "System tray is not available on this system.\n"
            "Tailscale Manager requires a system tray to run."
        )
        sys.exit(1)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

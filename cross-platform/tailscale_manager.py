#!/usr/bin/env python3
"""
tMUG - Tailscale Multi-platform User GUI
By DEC-LLC (Diwan Enterprise Consulting LLC)
License: Apache-2.0
"""

import atexit
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import time
import webbrowser

if platform.system() != "Windows":
    import fcntl
else:
    import msvcrt

from PyQt5.QtCore import Qt, QTimer, QSize, QThread, pyqtSignal
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

VERSION = "1.2.0"
AUTHOR = "DEC-LLC (Diwan Enterprise Consulting LLC)"
LICENSE = "Apache-2.0"
POLL_INTERVAL_MS = 10000  # 10 seconds
AUTH_SUBPROCESS_TIMEOUT = 60  # seconds (#8, #24)
MAX_ERROR_OUTPUT_LEN = 500  # characters (#22)


# ---------------------------------------------------------------------------
# Sanitization helpers (#22)
# ---------------------------------------------------------------------------

def _sanitize_output(text):
    """Strip sensitive info (node keys, internal IPs) from error output
    before displaying in dialogs."""
    if not text:
        return text
    # Remove lines containing key material
    lines = text.splitlines()
    sanitized = [
        line for line in lines
        if not re.search(r'\bkey:', line, re.IGNORECASE)
        and not re.search(r'nodekey:', line, re.IGNORECASE)
    ]
    result = "\n".join(sanitized)
    # Truncate overly long output
    if len(result) > MAX_ERROR_OUTPUT_LEN:
        result = result[:MAX_ERROR_OUTPUT_LEN] + "\n... (output truncated)"
    return result


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

    On Linux privileged commands are wrapped with sudo.
    On other platforms the caller is expected to run as admin if needed.
    """
    cmd = [_tailscale_cmd()] + args
    if privileged and _system() == "Linux":
        cmd = ["sudo"] + cmd

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


def _run_auth_command(args):
    """Run a tailscale command that may block for authentication.

    Runs the command in the background, polls for an auth URL in the output,
    and returns (url_or_none, full_output, process).
    Fixes #8, #18, #24: secure temp file, proper handle/process cleanup, timeout.
    """
    cmd = [_tailscale_cmd()] + args
    if _system() == "Linux":
        cmd = ["sudo"] + cmd

    # #18: Create temp file with restrictive permissions (0o600) to avoid
    # leaking auth URLs to other users on the system.
    tmpdir = tempfile.gettempdir()
    tmpname = os.path.join(tmpdir, f"tmug-auth-{os.getpid()}.txt")
    fd = os.open(
        tmpname,
        os.O_CREAT | os.O_WRONLY | os.O_EXCL,
        0o600,
    )
    os.close(fd)

    # #8, #24: Track file handle and process for proper cleanup
    stdout_fh = None
    proc = None
    try:
        stdout_fh = open(tmpname, "w")
        proc = subprocess.Popen(
            cmd,
            stdout=stdout_fh,
            stderr=subprocess.STDOUT,
        )

        # Poll for up to 15 seconds for a URL to appear
        url = None
        for _ in range(30):
            try:
                with open(tmpname, "r") as f:
                    content = f.read()
                url = _extract_auth_url(content)
                if url:
                    break
            except Exception:
                pass
            if proc.poll() is not None:
                break
            time.sleep(0.5)

        with open(tmpname, "r") as f:
            output = f.read()

        # #8, #24: If the process is still running after polling, give it a
        # timeout then forcefully terminate it.
        if proc.poll() is None:
            try:
                proc.wait(timeout=AUTH_SUBPROCESS_TIMEOUT)
            except subprocess.TimeoutExpired:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()

        return url, output, proc
    except Exception as e:
        # #24: Terminate orphaned process on exception
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
        return None, str(e), None
    finally:
        # #8, #24: Always close the file handle
        if stdout_fh is not None:
            try:
                stdout_fh.close()
            except Exception:
                pass
        try:
            os.unlink(tmpname)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Icon generation (3x3 dot grid, similar to tmug.svg)
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
# Status polling worker thread (#13)
# ---------------------------------------------------------------------------

class StatusWorker(QThread):
    """Runs tailscale status checks in a background thread to avoid
    blocking the GUI event loop (#13)."""
    status_ready = pyqtSignal(bool, str)  # (connected, ip_or_none)

    def run(self):
        connected = is_connected()
        ip = get_ip() if connected else None
        self.status_ready.emit(connected, ip or "")


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
            QMessageBox.critical(
                self, "Tailscale",
                f"Failed to apply settings.\n\n{_sanitize_output(err or out)}"
            )


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("tMUG")
        self.setFixedSize(420, 350)
        self.setWindowIcon(make_icon())
        self._status_worker = None  # Track active worker thread (#13)

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

        # ---- Status polling timer (#13) ----
        # The QTimer fires on the main thread, but the actual subprocess
        # call happens in a StatusWorker QThread to keep the GUI responsive.
        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll_status)
        self._poll_timer.start(POLL_INTERVAL_MS)
        self._poll_status()  # initial

    # -- Polling (#13) ----------------------------------------------------

    def _poll_status(self):
        """Start a background worker to check tailscale status without
        blocking the GUI event loop (#13)."""
        # Don't stack up workers if a previous one is still running
        if self._status_worker is not None and self._status_worker.isRunning():
            return
        self._status_worker = StatusWorker()
        self._status_worker.status_ready.connect(self._on_status_result)
        self._status_worker.start()

    def _on_status_result(self, connected, ip):
        """Handle status result from the background worker thread (#13)."""
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
        if is_connected():
            ip = get_ip()
            QMessageBox.information(
                self, "Tailscale",
                f"Already connected to Tailscale!\n\nIP: {ip or 'N/A'}"
            )
            self._poll_status()
            return

        url, output, proc = _run_auth_command(["up"])

        if is_connected():
            ip = get_ip()
            QMessageBox.information(
                self, "Tailscale",
                f"Successfully connected to Tailscale!\n\nIP: {ip or 'N/A'}"
            )
        elif url:
            open_url(url)
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
                f"Failed to connect.\n\n{_sanitize_output(output)}"
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
                QMessageBox.critical(
                    self, "Tailscale",
                    f"Failed to disconnect.\n\n{_sanitize_output(err or out)}"
                )
        self._poll_status()

    def _on_auth(self):
        if is_connected():
            self._do_logout()
        else:
            self._do_login()

    def _do_login(self):
        url, output, proc = _run_auth_command(["login"])

        if url:
            open_url(url)
            QMessageBox.information(
                self, "Tailscale",
                "A browser window has been opened to log in to Tailscale.\n\n"
                "You can:\n"
                "  - Sign up for a new account\n"
                "  - Log in to an existing account\n"
                "  - Add this device to your tailnet\n\n"
                f"If the browser didn't open, visit:\n{url}"
            )
        elif is_connected():
            QMessageBox.information(self, "Tailscale", "Already logged in and authenticated.")
        else:
            QMessageBox.critical(
                self, "Tailscale",
                f"Login failed.\n\n{_sanitize_output(output)}"
            )
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
                QMessageBox.critical(
                    self, "Tailscale",
                    f"Logout failed.\n\n{_sanitize_output(err or out)}"
                )
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
            self, "About tMUG",
            f"<h3>tMUG v{VERSION}</h3>"
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


def open_url(url):
    """Open a URL in the default browser, with fallbacks."""
    system = platform.system()
    try:
        if system == "Linux":
            # Try xdg-open first; only fall back to direct browser if unavailable
            try:
                subprocess.Popen(["xdg-open", url],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
                return
            except FileNotFoundError:
                pass
            # xdg-open not available — try direct browser invocation
            for browser in ["firefox", "google-chrome", "chromium-browser", "brave-browser"]:
                try:
                    subprocess.Popen([browser, url],
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
                    return
                except FileNotFoundError:
                    continue
            # Last resort
            webbrowser.open(url)
        else:
            webbrowser.open(url)
    except Exception:
        webbrowser.open(url)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def acquire_single_instance():
    """Ensure only one instance of tMUG is running using a lock file.
    Returns the lock file object (must stay open for the lifetime of the app)."""
    lock_path = os.path.join(tempfile.gettempdir(), ".tMUG-tailscale-manager.lock")
    lock_file = open(lock_path, "w")
    try:
        if platform.system() == "Windows":
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_file.write(str(os.getpid()))
        lock_file.flush()

        def _release_lock():
            try:
                lock_file.close()
                os.remove(lock_path)
            except OSError:
                pass

        atexit.register(_release_lock)
        return lock_file
    except (IOError, OSError):
        lock_file.close()
        return None


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("tMUG")
    app.setQuitOnLastWindowClosed(False)  # keep running in tray
    app.setWindowIcon(make_icon())

    # Single instance check
    lock = acquire_single_instance()
    if lock is None:
        QMessageBox.warning(
            None, "tMUG",
            "tMUG is already running.\n\nCheck your system tray."
        )
        sys.exit(0)

    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(
            None, "tMUG",
            "System tray is not available on this system.\n"
            "tMUG requires a system tray to run."
        )
        sys.exit(1)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

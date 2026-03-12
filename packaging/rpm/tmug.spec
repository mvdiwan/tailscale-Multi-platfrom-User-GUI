Name:           tmug
Version:        1.2.0
Release:        1%{?dist}
Summary:        tMUG - Tailscale Multi-platform User GUI
License:        Apache-2.0
Group:          Applications/Internet
URL:            https://github.com/mvdiwan/tailscale-Multi-platfrom-User-GUI
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

Requires:       tailscale
Requires:       yad
Requires:       python3
Requires:       python3-qt5

%description
tMUG (Tailscale Multi-platform User GUI) provides a graphical interface
for managing Tailscale VPN connections. It includes two versions:
a Bash+YAD version for Linux and a Python+PyQt5 cross-platform version.

%prep
%setup -q

%install
rm -rf %{buildroot}

# Bash version
install -D -m 0755 tMUG-tailscale-manager %{buildroot}/usr/local/bin/tMUG-tailscale-manager

# Qt wrapper script
install -D -m 0755 tMUG-tailscale-manager-qt %{buildroot}/usr/local/bin/tMUG-tailscale-manager-qt

# Python module
install -D -m 0644 tailscale_manager.py %{buildroot}/usr/share/tmug/tailscale_manager.py

# Desktop entries
install -D -m 0644 tMUG-tailscale-manager.desktop %{buildroot}/usr/share/applications/tMUG-tailscale-manager.desktop
install -D -m 0644 tMUG-tailscale-manager-qt.desktop %{buildroot}/usr/share/applications/tMUG-tailscale-manager-qt.desktop

# Icon
install -D -m 0644 tailscale.svg %{buildroot}/usr/share/pixmaps/tailscale.svg

%files
/usr/local/bin/tMUG-tailscale-manager
/usr/local/bin/tMUG-tailscale-manager-qt
/usr/share/tmug/tailscale_manager.py
/usr/share/applications/tMUG-tailscale-manager.desktop
/usr/share/applications/tMUG-tailscale-manager-qt.desktop
/usr/share/pixmaps/tailscale.svg

%dir /usr/share/tmug

%changelog
* Wed Mar 12 2026 Madhav Diwan <madhav@dec-llc.com> - 1.2.0-1
- Packaging and bug fixes release
- Includes Bash+YAD and PyQt5 cross-platform versions
- Fixed open_url() recursion, pkexec→sudo, duplicate tabs, Windows compat

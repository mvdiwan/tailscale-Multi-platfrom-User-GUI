#!/usr/bin/env bash
# build-rpm.sh — Build the tMUG RPM package
# Run this on an RPM-based system (Fedora, RHEL, CentOS, openSUSE, etc.)
#
# Prerequisites:
#   sudo dnf install rpm-build rpmdevtools    # Fedora/RHEL
#   sudo zypper install rpm-build rpmdevtools  # openSUSE

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

PKG_NAME="tmug"
PKG_VERSION="1.1.0"
TARBALL_DIR="${PKG_NAME}-${PKG_VERSION}"

# Check for rpmbuild
if ! command -v rpmbuild &>/dev/null; then
    echo "ERROR: rpmbuild is not installed."
    echo "Install it with:"
    echo "  Fedora/RHEL: sudo dnf install rpm-build rpmdevtools"
    echo "  openSUSE:    sudo zypper install rpm-build rpmdevtools"
    exit 1
fi

# Set up rpmbuild directory tree
RPMBUILD_DIR="${SCRIPT_DIR}/rpmbuild"
echo "Setting up rpmbuild tree in ${RPMBUILD_DIR} ..."
mkdir -p "${RPMBUILD_DIR}"/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# Copy spec file
cp "${SCRIPT_DIR}/tmug.spec" "${RPMBUILD_DIR}/SPECS/"

# Create source tarball
echo "Creating source tarball ..."
STAGING_DIR="$(mktemp -d)"
mkdir -p "${STAGING_DIR}/${TARBALL_DIR}"

# Copy all needed source files into the staging directory
cp "${PROJECT_ROOT}/tMUG-tailscale-manager"             "${STAGING_DIR}/${TARBALL_DIR}/"
cp "${PROJECT_ROOT}/tMUG-tailscale-manager.desktop"     "${STAGING_DIR}/${TARBALL_DIR}/"
cp "${PROJECT_ROOT}/tMUG-tailscale-manager-qt.desktop"  "${STAGING_DIR}/${TARBALL_DIR}/"
cp "${PROJECT_ROOT}/tailscale.svg"                      "${STAGING_DIR}/${TARBALL_DIR}/"
cp "${PROJECT_ROOT}/cross-platform/tailscale_manager.py" "${STAGING_DIR}/${TARBALL_DIR}/"

# Create the Qt wrapper script if it doesn't already exist in the project
if [[ -f "${PROJECT_ROOT}/tMUG-tailscale-manager-qt" ]]; then
    cp "${PROJECT_ROOT}/tMUG-tailscale-manager-qt" "${STAGING_DIR}/${TARBALL_DIR}/"
else
    cat > "${STAGING_DIR}/${TARBALL_DIR}/tMUG-tailscale-manager-qt" <<'WRAPPER'
#!/usr/bin/env bash
# Wrapper script for the PyQt5 version of tMUG
exec python3 /usr/share/tmug/tailscale_manager.py "$@"
WRAPPER
    chmod 0755 "${STAGING_DIR}/${TARBALL_DIR}/tMUG-tailscale-manager-qt"
fi

tar -czf "${RPMBUILD_DIR}/SOURCES/${PKG_NAME}-${PKG_VERSION}.tar.gz" \
    -C "${STAGING_DIR}" "${TARBALL_DIR}"

rm -rf "${STAGING_DIR}"

# Build the RPM
echo "Building RPM ..."
rpmbuild --define "_topdir ${RPMBUILD_DIR}" -ba "${RPMBUILD_DIR}/SPECS/tmug.spec"

# Copy resulting RPMs to the output directory
echo ""
echo "Build complete. Copying RPMs to ${SCRIPT_DIR}/ ..."
find "${RPMBUILD_DIR}/RPMS" -name '*.rpm' -exec cp -v {} "${SCRIPT_DIR}/" \;
find "${RPMBUILD_DIR}/SRPMS" -name '*.rpm' -exec cp -v {} "${SCRIPT_DIR}/" \;

echo ""
echo "Done. RPM files:"
ls -1 "${SCRIPT_DIR}"/*.rpm 2>/dev/null || echo "(no RPMs found — check build output above)"

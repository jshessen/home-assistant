#!/bin/bash
# Install Python 3.13 backport for Debian 12 Bookworm
# Based on: https://community.home-assistant.io/t/python-3-13-backport-for-debian-12-bookworm/842333

set -e  # Exit on error

echo "=========================================="
echo "Python 3.13 Backport Installation Script"
echo "=========================================="
echo ""

# Check if running on Debian 12 Bookworm
if ! grep -q "bookworm" /etc/os-release; then
    echo "ERROR: This script is for Debian 12 (Bookworm) only!"
    exit 1
fi

echo "Step 1: Adding PGP key for pascalroeleven.nl repository..."
if [ ! -f /etc/apt/keyrings/deb-pascalroeleven.gpg ]; then
    wget -qO- https://pascalroeleven.nl/deb-pascalroeleven.gpg | sudo tee /etc/apt/keyrings/deb-pascalroeleven.gpg > /dev/null
    echo "✓ PGP key added"
else
    echo "✓ PGP key already exists"
fi

echo ""
echo "Step 2: Adding Python 3.13 repository..."
if [ ! -f /etc/apt/sources.list.d/pascalroeleven.sources ]; then
    cat <<EOF | sudo tee /etc/apt/sources.list.d/pascalroeleven.sources > /dev/null
Types: deb
URIs: http://deb.pascalroeleven.nl/python3.13
Suites: bookworm-backports
Components: main
Signed-By: /etc/apt/keyrings/deb-pascalroeleven.gpg
EOF
    echo "✓ Repository added"
else
    echo "✓ Repository already configured"
fi

echo ""
echo "Step 3: Updating package lists..."
sudo apt update

echo ""
echo "Step 4: Installing Python 3.13 packages..."
# Note: python3.13-venv includes pip, no separate python3.13-pip package
sudo apt install -y python3.13 python3.13-venv python3.13-dev

echo ""
echo "=========================================="
echo "✓ Installation Complete!"
echo "=========================================="
echo ""
echo "Python 3.13 is now installed alongside your existing Python 3.11"
echo ""
echo "Verify installation:"
echo "  python3.13 --version"
echo ""
echo "To use with Home Assistant, replace 'python3' with 'python3.13'"
echo "when creating virtual environments:"
echo "  python3.13 -m venv /path/to/venv"
echo ""
echo "Important: Python 3.13 is in /usr/bin/python3.13 (coexists with python3)"
echo ""

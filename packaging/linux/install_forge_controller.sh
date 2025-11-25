#!/bin/bash
# Forge Controller - Install Script (Linux)
# Universal service monitor for managing web services

set -e

echo ""
echo "🔥 Installing Forge Controller (Linux)..."
echo "=========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Detect package manager
if command -v apt-get &> /dev/null; then
    echo "📦 Installing dependencies (apt)..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-gi gir1.2-gtk-3.0 gir1.2-appindicator3-0.1
elif command -v dnf &> /dev/null; then
    echo "📦 Installing dependencies (dnf)..."
    sudo dnf install -y python3 python3-pip gtk3 libappindicator-gtk3
elif command -v pacman &> /dev/null; then
    echo "📦 Installing dependencies (pacman)..."
    sudo pacman -S --noconfirm python python-pip gtk3 libappindicator-gtk3
else
    echo "⚠️  Unknown package manager. Please install dependencies manually:"
    echo "   - python3, python3-pip"
    echo "   - python3-gi, gtk3"
    echo "   - libappindicator-gtk3"
fi

echo ""
echo "📦 Installing Python dependencies..."
pip3 install --user requests 2>/dev/null || pip install requests

echo "✅ Dependencies installed"
echo ""

# Make controller executable
chmod +x "$SCRIPT_DIR/forge_controller.py"
echo "✅ Forge Controller is ready"
echo ""

echo "✅ Installation Complete!"
echo ""
echo "🚀 To start Forge Controller:"
echo "   python3 $SCRIPT_DIR/forge_controller.py"
echo ""
echo "📋 Features:"
echo "   • Automatically discovers services on ports 80-90 and 8000-9000"
echo "   • Shows status for each service"
echo "   • Start, Stop, Restart any service"
echo "   • View logs"
echo "   • Open services in browser"
echo ""
echo "💡 Add to autostart:"
echo "   1. Create ~/.config/autostart/forge-controller.desktop"
echo "   2. Add:"
echo "   [Desktop Entry]"
echo "   Type=Application"
echo "   Name=Forge Controller"
echo "   Exec=python3 $SCRIPT_DIR/forge_controller.py"
echo "   Icon=dialog-information"
echo ""

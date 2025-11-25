#!/bin/bash
# Install Dashboard Control App

set -e

echo "🚀 Installing Dashboard Controller..."
echo "===================================="

# Make the Python script executable
chmod +x dashboard_control.py

# Install required system packages
echo "📦 Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1 libnotify-bin
elif command -v dnf &> /dev/null; then
    sudo dnf install -y python3-gobject gtk3 libappindicator-gtk3 libnotify
elif command -v pacman &> /dev/null; then
    sudo pacman -S --noconfirm python-gobject gtk3 libappindicator-gtk3 libnotify
else
    echo "⚠️  Unsupported package manager. Please install manually:"
    echo "   - python3-gi (PyGObject)"
    echo "   - gir1.2-gtk-3.0 (GTK 3)"
    echo "   - gir1.2-appindicator3-0.1 (AppIndicator)"
    echo "   - libnotify-bin (Desktop notifications)"
fi

# Install Python requests if not already installed
echo "📦 Installing Python dependencies..."
if ! python3 -c "import requests" 2>/dev/null; then
    pip3 install --user requests
fi

# Copy desktop file to applications directory
echo "🖥️  Installing desktop entry..."
mkdir -p ~/.local/share/applications
cp dashboard-control.desktop ~/.local/share/applications/
sed -i "s|Exec=.*|Exec=$PWD/dashboard_control.py|g" ~/.local/share/applications/dashboard-control.desktop

# Copy logo if it exists
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DASHBOARD_DIR="$(dirname "$SCRIPT_DIR")"
DASHBOARD_DIR="$(dirname "$DASHBOARD_DIR")"
if [ -f "$DASHBOARD_DIR/assets/images/forge-logo.png" ]; then
    echo "📁 Copying forge logo..."
    cp "$DASHBOARD_DIR/assets/images/forge-logo.png" "$SCRIPT_DIR/forge-logo.png"
    echo "✅ Logo copied to installer directory"
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database ~/.local/share/applications
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "You can now:"
echo "  1. Run directly: ./dashboard_control.py"
echo "  2. Launch from applications menu: 'Dashboard Controller'"
echo "  3. Add to startup apps for auto-launch on login"
echo ""
echo "To add to startup:"
echo "  - GNOME: gnome-session-properties"
echo "  - KDE: System Settings → Startup and Shutdown → Autostart"
echo "  - XFCE: Settings → Session and Startup → Application Autostart"
echo ""

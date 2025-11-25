#!/bin/bash
# Install ForgeWeb Control App (Linux)
# Smart installer that integrates with existing Dashboard controller or installs standalone

set -e

echo ""
echo "🐧 Installing ForgeWeb Control App (Linux)..."
echo "================================================"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGING_DIR="$(dirname "$SCRIPT_DIR")"
FORGEWEB_DIR="$(dirname "$PACKAGING_DIR")"

# Verify ForgeWeb structure
if [ ! -f "$FORGEWEB_DIR/start.sh" ]; then
    echo "❌ Error: ForgeWeb not found at $FORGEWEB_DIR"
    echo "   Make sure you're running this from packaging/linux/"
    exit 1
fi

echo "✅ ForgeWeb found at: $FORGEWEB_DIR"
echo ""

# Check if Dashboard controller is installed
echo "🔍 Checking for existing Dashboard controller..."

DASHBOARD_RUNNING=false
if command -v pgrep &> /dev/null; then
    if pgrep -f "dashboard_control" > /dev/null 2>&1; then
        DASHBOARD_RUNNING=true
        DASHBOARD_PID=$(pgrep -f "dashboard_control" | head -1)
        echo "✅ Dashboard controller is running (PID: $DASHBOARD_PID)"
    fi
fi

DASHBOARD_EXISTS=false
if [ -f "$PACKAGING_DIR/linux/dashboard_control.py" ]; then
    DASHBOARD_EXISTS=true
    echo "✅ Dashboard controller app found"
fi

echo ""

# Determine installation mode
if [ "$DASHBOARD_EXISTS" = true ] || [ "$DASHBOARD_RUNNING" = true ]; then
    echo "📦 Integration Mode: Adding ForgeWeb to existing Dashboard controller"
    MODE="integrated"
else
    echo "📦 Installation Mode: Installing ForgeWeb as standalone controller"
    MODE="standalone"
fi

echo ""

# Install system dependencies
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

echo "✅ System dependencies installed"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if ! python3 -c "import requests" 2>/dev/null; then
    pip3 install --user requests
fi

echo "✅ Python dependencies installed"
echo ""

# Make control script executable
chmod +x "$SCRIPT_DIR/forgeweb_control.py"
echo "✅ Made forgeweb_control.py executable"
echo ""

# Install desktop file for application launcher
echo "🖥️  Installing desktop entry..."
mkdir -p ~/.local/share/applications

cat > ~/.local/share/applications/forgeweb-control.desktop << EOF
[Desktop Entry]
Type=Application
Name=ForgeWeb Controller
Comment=Control ForgeWeb Admin Server
Exec=$SCRIPT_DIR/forgeweb_control.py
Icon=application-default-icon
Terminal=false
Categories=Development;Utility;
X-GNOME-Autostart-enabled=false
EOF

chmod +x ~/.local/share/applications/forgeweb-control.desktop

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database ~/.local/share/applications
fi

echo "✅ Desktop entry installed"
echo ""

# For integrated mode, create a launcher that starts both
if [ "$MODE" = "integrated" ]; then
    echo "🔗 Creating integrated launcher..."
    
    cat > "$SCRIPT_DIR/launch_all.sh" << 'EOF'
#!/bin/bash
# Launch both Dashboard and ForgeWeb controllers

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Start Dashboard controller if not already running
if ! pgrep -f "dashboard_control" > /dev/null; then
    nohup python3 "$SCRIPT_DIR/dashboard_control.py" > /dev/null 2>&1 &
    sleep 2
fi

# Start ForgeWeb controller
python3 "$SCRIPT_DIR/forgeweb_control.py"
EOF
    
    chmod +x "$SCRIPT_DIR/launch_all.sh"
    echo "✅ Created integrated launcher: launch_all.sh"
    echo ""
fi

echo "✅ Installation complete!"
echo ""
echo "To run:"

if [ "$MODE" = "integrated" ]; then
    echo "  cd $SCRIPT_DIR"
    echo "  ./launch_all.sh"
    echo ""
    echo "Or run ForgeWeb controller alone:"
    echo "  python3 forgeweb_control.py"
    echo ""
    echo "Or from applications menu: 'ForgeWeb Controller'"
else
    echo "  cd $SCRIPT_DIR"
    echo "  python3 forgeweb_control.py"
    echo ""
    echo "Or from applications menu: 'ForgeWeb Controller'"
fi

echo ""
echo "To add to startup apps:"
echo "  - GNOME: gnome-session-properties"
echo "  - KDE: System Settings → Startup and Shutdown → Autostart"
echo "  - XFCE: Settings → Session and Startup → Application Autostart"
echo ""

echo "ℹ️  Configuration saved to: $FORGEWEB_DIR/.forgeweb_control_config.json"
echo ""
echo "📚 For more help, see: $SCRIPT_DIR/FORGEWEB_CONTROL_README.md"
echo ""

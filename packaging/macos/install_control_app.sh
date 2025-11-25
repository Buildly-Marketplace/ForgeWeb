#!/bin/bash
# Install macOS Dashboard Control App

set -e

echo "🍎 Installing Dashboard Controller for macOS..."
echo "===================================="

# Get script directory and verify dashboard exists
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DASHBOARD_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

if [ ! -f "$DASHBOARD_DIR/ops/startup.sh" ]; then
    echo "❌ Error: Dashboard not found at $DASHBOARD_DIR"
    echo "   Make sure you're running this from packaging/macos/"
    exit 1
fi

echo "✅ Dashboard found at: $DASHBOARD_DIR"
echo ""

# Install rumps (menu bar app framework)
echo "📦 Installing Python dependencies..."
pip3 install --user rumps requests 2>/dev/null || pip install rumps requests

echo "✅ Dependencies installed"
echo ""

# Copy logo if it exists
if [ -f "$DASHBOARD_DIR/assets/images/forge-logo.png" ]; then
    echo "📁 Copying forge logo..."
    cp "$DASHBOARD_DIR/assets/images/forge-logo.png" "$SCRIPT_DIR/forge-logo.png"
    echo "✅ Logo copied to installer directory"
    echo ""
fi

# Make executable
chmod +x "$SCRIPT_DIR/dashboard_control.py"
echo "✅ Made dashboard_control.py executable"

echo ""
echo "✅ Installation complete!"
echo ""
echo "To run the menu bar app:"
echo "  cd $SCRIPT_DIR"
echo "  python3 dashboard_control.py"
echo ""
echo "Or run in background:"
echo "  nohup python3 dashboard_control.py &"
echo ""
echo "To add to login items (auto-start):"
echo "  1. Open System Preferences → Users & Groups → Login Items"
echo "  2. Click '+' and select 'dashboard_control.py'"
echo "  3. Or drag it to the Login Items window"
echo ""
echo "📝 Note: The app will remain in the menu bar and manage the dashboard server."
echo ""

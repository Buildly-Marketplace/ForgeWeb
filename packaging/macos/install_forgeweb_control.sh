#!/bin/bash
# Install ForgeWeb Control App (macOS)
# Ensures Dashboard controller includes ForgeWeb integration

set -e

echo ""
echo "🍎 Installing ForgeWeb Control App (macOS)..."
echo "================================================"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGING_DIR="$(dirname "$SCRIPT_DIR")"
FORGEWEB_DIR="$(dirname "$PACKAGING_DIR")"

# Verify ForgeWeb structure
if [ ! -d "$FORGEWEB_DIR" ]; then
    echo "❌ Error: ForgeWeb not found at $FORGEWEB_DIR"
    echo "   Make sure you're running this from packaging/macos/"
    exit 1
fi

echo "✅ ForgeWeb found at: $FORGEWEB_DIR"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install --user rumps requests 2>/dev/null || pip install rumps requests

echo "✅ Dependencies installed"
echo ""

# Make Dashboard controller executable
chmod +x "$SCRIPT_DIR/dashboard_control.py"
echo "✅ Made dashboard_control.py executable"
echo ""

echo "✅ Installation Complete!"
echo ""
echo "📋 The Dashboard controller now includes ForgeWeb controls:"
echo "   • Dashboard Status & Controls"
echo "   • ForgeWeb Status & Controls (when ForgeWeb directory exists)"
echo ""
echo "🚀 To start the controller:"
echo "   cd $SCRIPT_DIR"
echo "   python3 dashboard_control.py"
echo ""
echo "   You'll see ONE menu bar icon (🔥 Forge logo) with controls for both services."
echo ""
echo "💡 To add to login items (auto-start):"
echo "   1. Open System Settings → General → Login Items"
echo "   2. Click '+' button under 'Open at Login'"
echo "   3. Select 'dashboard_control.py' from:"
echo "      $SCRIPT_DIR"
echo ""

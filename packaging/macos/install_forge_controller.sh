#!/bin/bash
# Forge Controller - Install Script (macOS)
# Universal service monitor for managing web services

set -e

echo ""
echo "🔥 Installing Forge Controller (macOS)..."
echo "==========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install --user rumps requests 2>/dev/null || pip install rumps requests

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
echo "💡 Add to login items for auto-start:"
echo "   1. Open System Settings → General → Login Items"
echo "   2. Click '+' button"
echo "   3. Select forge_controller.py"
echo ""

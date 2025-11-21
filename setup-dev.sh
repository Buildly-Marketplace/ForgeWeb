#!/bin/bash
# ForgeWeb Development Setup Script
# 
# NOTE: This script is deprecated!
# Please use ./start.sh instead for a better experience.
#
# The new start.sh script:
# - Has a wizard-like interface
# - Handles both setup and server startup
# - Provides helpful messages and troubleshooting
# - Works for both first-time setup and restarts
#

echo "⚠️  This script is deprecated!"
echo ""
echo "Please use the new startup script instead:"
echo ""
echo "  ./start.sh"
echo ""
echo "The new script provides a better experience with:"
echo "  ✓ Automatic setup and server startup"
echo "  ✓ Helpful messages and guides"
echo "  ✓ Error detection and troubleshooting"
echo ""
read -p "Would you like to run ./start.sh now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    exec ./start.sh
else
    echo "Okay! Run ./start.sh whenever you're ready."
    exit 0
fi

echo "🔍 Site Preview: http://localhost:8000/"
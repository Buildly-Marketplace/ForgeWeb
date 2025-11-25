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

# macOS Dashboard Controller - Setup Guide

## Quick Start

### 1. Install the Control App
```bash
cd packaging/macos
./install_control_app.sh
```

### 2. Run the App
```bash
python3 dashboard_control.py
```

You should see a menu bar icon appear at the top right of your screen.

### 3. Use the Menu Bar App
Click the menu bar icon (⭕/✅/⏳) to:
- **Start Server** - Start the dashboard server
- **Restart Server** - Restart if it's already running
- **Stop Server** - Stop the dashboard server
- **Open Dashboard** - Open http://localhost:8008 in browser
- **View Logs** - Open dashboard.log in Terminal
- **Quit** - Exit the control app

## Auto-Start on Login

To have the controller start automatically when you log in:

### Option 1: System Preferences (Easiest)
1. Open **System Preferences** → **Users & Groups**
2. Select your user account
3. Click **Login Items** tab
4. Click **+** button
5. Navigate to `packaging/macos/dashboard_control.py` and add it
6. The app will now auto-start at login

### Option 2: Background Script
```bash
# Run in background without terminal window
nohup python3 dashboard_control.py > /dev/null 2>&1 &
```

Add this to `.zshrc` or `.bash_profile` to auto-start.

## Features

✅ **Status Monitoring** - Real-time server status with visual indicator  
✅ **One-Click Controls** - Start, stop, restart from menu bar  
✅ **Browser Integration** - Quick access to dashboard in browser  
✅ **Log Viewer** - View server logs directly in Terminal  
✅ **Notifications** - Native macOS notifications for status changes  
✅ **Health Checks** - Automatic health check via `/api/health` endpoint  

## Status Indicators

- **✅ Running (PID: 12345)** - Server is healthy and running
- **⏳ Starting (PID: 12345)** - Server is initializing
- **⭕ Stopped** - Server is not running

## Troubleshooting

### Icon doesn't appear
- Restart the app: `python3 dashboard_control.py`
- Check if it's hidden: Look at the far right of your menu bar

### Server won't start
- Check permissions: `chmod +x ../../../ops/startup.sh`
- Verify Python path: `which python3`
- Check logs: View Logs from menu

### "Cannot find rumps"
- Reinstall: `./install_control_app.sh`
- Or manually: `pip3 install --user rumps requests`

### Network error
- Ensure dashboard is configured at `http://localhost:8008`
- Check if port 8008 is in use: `lsof -i :8008`

## Requirements

- Python 3.7+
- macOS 10.12+
- `rumps` library (installed by setup script)
- `requests` library (installed by setup script)

## Advanced

### Running as a daemon
```bash
mkdir -p ~/Library/LaunchAgents
cat > ~/Library/LaunchAgents/com.dashboard.controller.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dashboard.controller</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/packaging/macos/dashboard_control.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/dashboard-controller.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/dashboard-controller-error.log</string>
</dict>
</plist>
EOF

# Load it
launchctl load ~/Library/LaunchAgents/com.dashboard.controller.plist
```

## Support

For issues or feature requests, check:
- Server logs: Dashboard Log menu item
- Health status: `curl http://localhost:8008/api/health`
- Process status: `ps aux | grep python.*main.py`

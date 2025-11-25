# ForgeWeb Control App - Installation & Usage Guide

## Overview

The ForgeWeb Control App is a platform-specific desktop application that provides one-click control over the ForgeWeb admin server. It can **intelligently integrate with your existing Dashboard controller** if you have one, or run **standalone** if not.

### Smart Integration Features

✅ **Auto-Detection**: Detects if Dashboard controller is already running  
✅ **Seamless Integration**: Adds ForgeWeb controls to existing Dashboard app  
✅ **Dual Management**: Control both services from a single menu  
✅ **Fallback Mode**: Works standalone if Dashboard isn't installed  
✅ **Config Persistence**: Remembers your setup in `.forgeweb_control_config.json`

---

## Platform-Specific Installation

### macOS

#### Quick Install

```bash
cd forgeweb/packaging/macos
./install_forgeweb_control.sh
```

#### After Installation

Run the controller:
```bash
python3 forgeweb_control.py
```

Or in background:
```bash
nohup python3 forgeweb_control.py > /dev/null 2>&1 &
```

#### Auto-Start on Login

1. Open **System Preferences** → **Users & Groups**
2. Select your user account
3. Click **Login Items** tab
4. Click **+** button
5. Navigate to `forgeweb/packaging/macos/` and add `forgeweb_control.py`

#### Integration with Dashboard

If you have Dashboard controller installed, you can launch both together:

```bash
./launch_all.sh
```

This will start Dashboard first, then add ForgeWeb controls to the menu.

---

### Linux

#### Quick Install

```bash
cd forgeweb/packaging/linux
./install_forgeweb_control.sh
```

#### After Installation

Run the controller:
```bash
python3 forgeweb_control.py
```

Or from Applications menu:
- Search for "ForgeWeb Controller"
- Click to launch

#### Add to Startup (GNOME)

```bash
gnome-session-properties
```
- Click **Add**
- Set name: `ForgeWeb Controller`
- Set command: `/path/to/forgeweb/packaging/linux/forgeweb_control.py`

#### Add to Startup (KDE)

1. System Settings
2. Startup and Shutdown → Autostart
3. Click **+** and add the script

#### Add to Startup (XFCE)

1. Settings → Session and Startup
2. Application Autostart tab
3. Click **+** and add the script

#### Integration with Dashboard

If you have Dashboard controller, use the integrated launcher:

```bash
./launch_all.sh
```

---

### Windows

#### Quick Install

1. Open Command Prompt or PowerShell
2. Navigate to `forgeweb\packaging\windows\`
3. Run:
```cmd
install_forgeweb_control.bat
```

#### After Installation

Run the controller:
```cmd
python forgeweb_control.py
```

Or in background (no console window):
```cmd
pythonw forgeweb_control.py
```

#### Auto-Start on Login

1. Press **Win+R**
2. Type: `shell:startup`
3. Create a shortcut to `forgeweb_control.py` in that folder

Or use Task Scheduler:
1. Open **Task Scheduler**
2. Click **Create Task**
3. Name: `ForgeWeb Controller`
4. Trigger: **At log on**
5. Action: Start a program → `pythonw.exe`
6. Add arguments: `full_path_to_forgeweb_control.py`

#### Integration with Dashboard

If you have Dashboard controller, you can manage both from the same tray menu.

---

## Menu Options

### Status Indicators

- **✅ Running (PID: 12345)** - Server is healthy and running
- **⏳ Starting (PID: 12345)** - Server is initializing
- **⭕ Stopped** - Server is not running

### Available Controls

| Option | Description |
|--------|-------------|
| **Start ForgeWeb** | Start the ForgeWeb admin server |
| **Restart ForgeWeb** | Gracefully restart the server |
| **Stop ForgeWeb** | Shut down the ForgeWeb server |
| **Open Admin Panel** | Open http://localhost:8000/admin/ in browser |
| **Open ForgeWeb Site** | Open http://localhost:8000/ in browser |
| **View Logs** | Open forgeweb.log in your default viewer |
| **Quit** | Close the controller app |

### ForgeWeb Controls (when integrated)

When running in integrated mode with Dashboard, you'll see a **🔧 ForgeWeb Controls** section with all the options above.

---

## Installation Modes

### Integrated Mode

**Detected when:**
- Dashboard controller is already running
- Dashboard controller script is found in packaging directory

**Behavior:**
- ForgeWeb controls added to existing Dashboard menu
- Single menu bar/tray icon manages both services
- Shared configuration file
- Use `launch_all.sh` to start both together

**Benefits:**
- Cleaner desktop (one icon instead of two)
- Single interface for multiple services
- Automatic coordination

### Standalone Mode

**Detected when:**
- Dashboard controller not found or not running

**Behavior:**
- ForgeWeb runs with its own menu bar/tray icon
- Independent configuration file
- Can be upgraded to integrated mode later if Dashboard is installed

**Benefits:**
- Simple setup
- No dependencies on other services
- Easy to uninstall

---

## Configuration

### Config File

Settings are stored in:
```
forgeweb/.forgeweb_control_config.json
```

Example:
```json
{
  "mode": "integrated",
  "services": [
    {
      "name": "ForgeWeb",
      "port": 8000,
      "health_endpoint": "http://localhost:8000/api/health",
      "enabled": true
    }
  ]
}
```

### Customizing the App

To change default settings:

1. Open `.forgeweb_control_config.json`
2. Modify the values:
   - `"port": 8000` - Change ForgeWeb port
   - `"enabled": true/false` - Enable/disable service
3. Restart the controller app

---

## Troubleshooting

### The app icon doesn't appear

**macOS:**
```bash
# Restart the app
python3 forgeweb_control.py

# Check if hidden in far right of menu bar
```

**Linux:**
```bash
# Verify dependencies
python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import AppIndicator3"

# Try running from terminal
python3 forgeweb_control.py
```

**Windows:**
```cmd
# Check if running
tasklist | find "pythonw"

# Try running with visible console
python forgeweb_control.py
```

### Server won't start

```bash
# Check permissions on startup script
chmod +x forgeweb/start.sh  (macOS/Linux)

# Check if port is already in use
lsof -i :8000  (macOS/Linux)
netstat -ano | findstr :8000  (Windows)

# View logs
tail -f forgeweb/forgeweb.log
```

### "Cannot find requests"

```bash
# Reinstall dependencies
pip3 install --user requests

# Or for Windows
pip install requests
```

### Dashboard Integration Not Working

```bash
# Check if Dashboard is actually running
pgrep -f dashboard_control  (macOS/Linux)

# Restart the installer to reconfigure
./install_forgeweb_control.sh

# Check config file
cat forgeweb/.forgeweb_control_config.json
```

### Browser won't open

- **macOS**: Ensure you have a default browser set
- **Linux**: Install xdg-open: `sudo apt install xdg-utils`
- **Windows**: Check default browser in Settings

---

## Advanced Usage

### Running Multiple Instances

To run different ForgeWeb ports with separate controllers:

1. Create a copy of the control app:
   ```bash
   cp forgeweb_control.py forgeweb_control_8001.py
   ```

2. Edit the copy and change:
   ```python
   FORGEWEB_PORT = 8001
   ```

3. Run both:
   ```bash
   python3 forgeweb_control.py &
   python3 forgeweb_control_8001.py &
   ```

### Running as a Service (Advanced)

**Linux (systemd):**
```bash
sudo cat > /etc/systemd/user/forgeweb-control.service << EOF
[Unit]
Description=ForgeWeb Controller
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/forgeweb_control.py
Restart=on-failure

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable forgeweb-control
```

**Windows (Task Scheduler):**
See "Auto-Start on Login" section above.

### Debugging

To see verbose output:

```bash
# macOS/Linux
python3 forgeweb_control.py

# Windows
python forgeweb_control.py
```

Check output for:
- `ForgeWeb Controller started in integrated mode`
- `ForgeWeb Controller started in standalone mode`
- Error messages with troubleshooting info

---

## Support & Issues

If you encounter problems:

1. Check this guide's **Troubleshooting** section
2. View the logs: `forgeweb/forgeweb.log`
3. Check the config: `forgeweb/.forgeweb_control_config.json`
4. Try reinstalling: `./install_forgeweb_control.*`

---

## Uninstalling

### macOS

```bash
# Remove from Login Items (System Preferences)
# Stop any running instances
pkill -f forgeweb_control

# Delete the app directory (optional)
rm -rf forgeweb/packaging/macos/forgeweb_control.py
```

### Linux

```bash
# Remove from autostart
rm ~/.local/share/applications/forgeweb-control.desktop

# Stop any running instances
pkill -f forgeweb_control

# Delete the app directory (optional)
rm -rf forgeweb/packaging/linux/forgeweb_control.py
```

### Windows

```cmd
# Remove from startup folder
del %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\forgeweb_control.lnk

# Kill any running instances
taskkill /F /IM pythonw.exe /C "forgeweb_control"

# Delete the app directory (optional)
del forgeweb\packaging\windows\forgeweb_control.py
```

---

## Version Info

- **ForgeWeb Control App**: v1.0
- **Supported Platforms**: macOS 10.12+, Linux (systemd-based), Windows 7+
- **Python Requirements**: 3.7+
- **Dashboard Integration**: Compatible with Dashboard v1.0+

---

Last Updated: November 24, 2025

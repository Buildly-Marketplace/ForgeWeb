# ForgeWeb Control App - Quick Reference

## 🚀 Installation (Pick Your Platform)

### macOS
```bash
cd forgeweb/packaging/macos
./install_forgeweb_control.sh
python3 forgeweb_control.py
```

### Linux
```bash
cd forgeweb/packaging/linux
./install_forgeweb_control.sh
python3 forgeweb_control.py
```

### Windows
```cmd
cd forgeweb\packaging\windows
install_forgeweb_control.bat
python forgeweb_control.py
```

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **Auto-Integration** | Detects Dashboard controller and integrates automatically |
| **Fallback** | Works standalone if Dashboard not installed |
| **One-Click Control** | Start, stop, restart from menu bar/system tray |
| **Status Display** | ✅ Running / ⏳ Starting / ⭕ Stopped |
| **Quick Links** | Open admin panel and test site with one click |
| **Logs Viewer** | Easy access to server logs |
| **Config Persistence** | Settings saved in `.forgeweb_control_config.json` |

---

## 📁 What Was Created

```
forgeweb/packaging/
├── control_integration.py              # Shared detection logic
├── FORGEWEB_CONTROL_README.md          # Full documentation
├── macos/
│   ├── forgeweb_control.py            # macOS menu bar app
│   ├── install_forgeweb_control.sh    # macOS installer
│   └── launch_all.sh                  # (created if Dashboard exists)
├── linux/
│   ├── forgeweb_control.py            # Linux system tray app
│   ├── install_forgeweb_control.sh    # Linux installer
│   └── launch_all.sh                  # (created if Dashboard exists)
└── windows/
    ├── forgeweb_control.py            # Windows system tray app
    └── install_forgeweb_control.bat   # Windows installer

Root project:
├── FORGEWEB_CONTROL_IMPLEMENTATION.md  # Technical details
└── PACKAGING_ADAPTATION_PROPOSAL.md    # Original proposal
```

---

## 🎮 Menu Options (All Platforms)

When running, you'll see these options in the menu bar/system tray:

```
ForgeWeb Controls (if integrated with Dashboard)
├─ ✅ Running (PID: 12345)
├─ ▶️ Start ForgeWeb
├─ 🔄 Restart ForgeWeb
├─ ⏹️ Stop ForgeWeb
├─ 🔧 Open Admin Panel
├─ 🌐 Open ForgeWeb Site
├─ 📋 View Logs
└─ ❌ Quit
```

---

## 🔄 Integration Modes

### Integrated (Dashboard + ForgeWeb)

**When:** Dashboard controller already installed or running

**Benefits:**
- Single menu icon
- Both services managed together
- Use: `./launch_all.sh` to start both

```bash
./launch_all.sh
# Starts Dashboard first, then adds ForgeWeb controls
```

### Standalone (ForgeWeb Only)

**When:** Dashboard not detected

**Benefits:**
- Simple setup
- Independent operation
- Can add Dashboard later

```bash
python3 forgeweb_control.py
# Runs ForgeWeb controller standalone
```

---

## 📊 Configuration

The app creates a configuration file:

**Location:** `forgeweb/.forgeweb_control_config.json`

**Example:**
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

**To modify:**
1. Open the config file
2. Change values (e.g., port from 8000 to 8001)
3. Restart the controller

---

## 🔗 URLs

After starting the server:

| URL | Purpose |
|-----|---------|
| http://localhost:8000/ | ForgeWeb website |
| http://localhost:8000/admin/ | Admin panel |

Both accessible via menu → "Open Admin Panel" / "Open ForgeWeb Site"

---

## 🆘 Troubleshooting

### App won't start

```bash
# Check Python version (need 3.7+)
python3 --version

# Try running with verbose output
python3 forgeweb_control.py

# Check if port is already in use
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

### Icon not showing

- macOS: Check far right of menu bar, restart with `python3 forgeweb_control.py`
- Linux: Verify dependencies: `python3 -m gi`
- Windows: Try running `pythonw.exe forgeweb_control.py`

### Dashboard integration not working

```bash
# Reinstall to detect Dashboard again
./install_forgeweb_control.sh  # macOS/Linux
install_forgeweb_control.bat   # Windows

# Check if Dashboard is running
pgrep -f dashboard_control  # macOS/Linux
```

### Server won't start

```bash
# Check permissions
chmod +x forgeweb/start.sh  # macOS/Linux

# Check logs
tail -f forgeweb/forgeweb.log
```

---

## 🔧 Auto-Start Setup

### macOS

1. System Preferences → Users & Groups → Login Items
2. Click `+` button
3. Navigate to `forgeweb/packaging/macos/`
4. Select `forgeweb_control.py`

### Linux (GNOME)

```bash
gnome-session-properties
# Or: Settings → Startup Applications
```

### Linux (Other Desktop Environments)

- **KDE:** System Settings → Startup and Shutdown → Autostart
- **XFCE:** Settings → Session and Startup → Application Autostart

### Windows

1. Press `Win+R`
2. Type: `shell:startup`
3. Create shortcut to `forgeweb_control.py` in that folder

---

## 💻 Command Line Reference

### macOS/Linux

```bash
# Run normally (see console output)
python3 forgeweb_control.py

# Run in background
nohup python3 forgeweb_control.py > /dev/null 2>&1 &

# Kill the app
pkill -f forgeweb_control

# View logs
tail -f forgeweb/forgeweb.log

# Install
./install_forgeweb_control.sh

# Install and launch both
./launch_all.sh
```

### Windows

```cmd
# Run normally (with console)
python forgeweb_control.py

# Run in background (hidden)
pythonw forgeweb_control.py

# Kill the app
taskkill /F /IM pythonw.exe

# View logs
type forgeweb\forgeweb.log

# Install
install_forgeweb_control.bat
```

---

## 📚 Full Documentation

For complete details, see:
- **Installation:** `forgeweb/packaging/FORGEWEB_CONTROL_README.md`
- **Technical Details:** `FORGEWEB_CONTROL_IMPLEMENTATION.md`

---

## ✅ What's Included

- ✅ macOS menu bar controller (rumps)
- ✅ Linux system tray controller (GTK3)
- ✅ Windows system tray controller (PyQt5)
- ✅ Platform-specific installers
- ✅ Intelligent Dashboard detection
- ✅ Automatic integration
- ✅ Standalone fallback mode
- ✅ Configuration persistence
- ✅ Health monitoring
- ✅ Log access
- ✅ Browser integration
- ✅ Complete documentation

---

**Last Updated:** November 24, 2025  
**Status:** Ready for use ✨

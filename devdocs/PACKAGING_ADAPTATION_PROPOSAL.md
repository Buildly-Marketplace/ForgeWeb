# ForgeWeb Admin - Packaging & Control App Proposal

## Current State

You have a well-designed macOS menu bar controller from a Personal Dashboard app that can be adapted for ForgeWeb. Here's what we can leverage:

### Existing Packaging Structure
- **Location**: `forgeweb/packaging/macos/`
- **Main Component**: `dashboard_control.py` - A macOS menu bar app using `rumps` library
- **Features**: Start/stop/restart server, open in browser, view logs, status monitoring
- **Logos Available**:
  - `buildly_icon.icns` (native macOS icon)
  - `buildly_icon.png` 
  - `forge-logo.png`
  - Full icon set at various resolutions (16x16 to 1024x1024)

### Current ForgeWeb Setup
- `start.sh` - Comprehensive startup wizard with Python/venv management
- Runs on configurable port (default 8000)
- Admin panel at `/admin/`
- Full test server with database initialization

---

## Proposed Adaptation for ForgeWeb

### 1. **Create ForgeWeb Control App** (`forgeweb_control.py`)
   - Fork from `dashboard_control.py`
   - Target ForgeWeb admin panel instead of personal dashboard
   - Point to ForgeWeb startup script (`forgeweb/start.sh`)
   - Change API endpoint from `:8008` to `:8000`
   - Update menu items and notifications for ForgeWeb context

### 2. **Menu Features for ForgeWeb**
   ```
   ✅ Running (PID: 12345)
   ├─ Start ForgeWeb Admin Server
   ├─ Restart Server
   ├─ Stop Server
   ├─ Open Admin Panel (http://localhost:8000/admin/)
   ├─ Open Website (http://localhost:8000/)
   ├─ View Logs
   └─ Quit
   ```

### 3. **Use Buildly Logos**
   - Menu bar icon: `buildly_icon.png` or `forge-logo.png`
   - App icon: `buildly_icon.icns`
   - Maintains visual consistency with Buildly branding

### 4. **Installation & Setup**
   - Create `install_forgeweb_control.sh` script
   - Auto-install Python dependencies:
     - `rumps` (macOS menu bar)
     - `requests` (health checks)
   - Optional: Auto-start on login setup

### 5. **Health Check Integration**
   - Poll `/api/health` endpoint on ForgeWeb
   - Visual status in menu bar (✅/⏳/⭕)
   - Automatic recovery attempts on failure

---

## Files to Create/Modify

### New Files
```
forgeweb/packaging/macos/
├── forgeweb_control.py          (Main control app - adapted from dashboard_control.py)
├── install_forgeweb_control.sh  (Installation script)
└── FORGEWEB_CONTROL_README.md   (User guide)
```

### Logo Reuse
- Copy/link existing icons from `forgeweb/packaging/macos/buildly_icon.*`
- Use `forge-logo.png` for menu bar icon

---

## Benefits

✅ **One-Click Control**: Start/stop ForgeWeb admin from menu bar  
✅ **Status Monitoring**: Always know if server is running  
✅ **Improved UX**: No terminal needed for development  
✅ **Browser Integration**: Quick access to admin panel  
✅ **Log Viewing**: Monitor server logs from menu  
✅ **Native Integration**: macOS menu bar notifications  
✅ **Buildly Branding**: Use existing logos  

---

## Implementation Steps

1. **Adapt `dashboard_control.py`** → Create `forgeweb_control.py`
   - Update paths to use ForgeWeb structure
   - Change port from 8008 to 8000
   - Update menu labels and URLs
   - Point to correct startup script

2. **Create Installation Script** 
   - Check Python version
   - Install rumps and requests
   - Set permissions
   - Create symlink or launcher

3. **Create User Documentation**
   - Quick start guide
   - Menu options reference
   - Troubleshooting tips
   - Auto-start setup instructions

4. **Test on macOS**
   - Verify menu bar integration
   - Test all control options
   - Verify logo display
   - Check health monitoring

---

## Questions for You

1. **Port Configuration**: Should control app use hardcoded 8000 or make it configurable?
2. **Logo Preference**: Use `buildly_icon` or `forge-logo` for menu bar?
3. **Auto-start**: Should we include auto-start on login setup?
4. **Windows/Linux**: Want equivalent control apps for those platforms later?

---

## Next Steps

Would you like me to:
1. ✅ Create adapted `forgeweb_control.py`
2. ✅ Create installation script `install_forgeweb_control.sh`
3. ✅ Create user documentation
4. ✅ All of the above

Let me know and I'll implement it!

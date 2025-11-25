#!/usr/bin/env python3
"""
Dashboard Control App - macOS Menu Bar Version
A simple menu bar application to control the Personal Dashboard server
"""

import rumps
import subprocess
import os
import signal
import requests
from pathlib import Path
import time

class DashboardController(rumps.App):
    def __init__(self):
        super(DashboardController, self).__init__("Dashboard")
        
        # Find dashboard directory (this is the forgeweb directory since we're in packaging/macos)
        self.dashboard_dir = Path(__file__).parent.parent.parent.absolute()
        
        # Check if traditional Dashboard structure exists (ops/startup.sh)
        # Otherwise fall back to ForgeWeb structure
        traditional_startup = self.dashboard_dir / "ops" / "startup.sh"
        forgeweb_startup = self.dashboard_dir / "start.sh"
        
        if traditional_startup.exists():
            self.startup_script = traditional_startup
            self.pid_file = self.dashboard_dir / "dashboard.pid"
        elif forgeweb_startup.exists():
            # We're in ForgeWeb - use its startup script
            self.startup_script = forgeweb_startup
            self.pid_file = self.dashboard_dir / "dashboard.pid"
        else:
            # No startup script found - Dashboard controls will be disabled
            self.startup_script = None
            self.pid_file = self.dashboard_dir / "dashboard.pid"
        
        # Check for Forge branding (new logo)
        logo_candidates = [
            self.dashboard_dir / "packaging" / "forge-logo.png",
            self.dashboard_dir / "packaging" / "macos" / "forge-logo.png",
            self.dashboard_dir / "forgeweb" / "assets" / "images" / "forge-logo.png",
            self.dashboard_dir / "packaging" / "buildly_icon.png",
            self.dashboard_dir / "packaging" / "macos" / "buildly_icon.png",
            self.dashboard_dir / "packaging" / "buildly_icon.icns",
            self.dashboard_dir / "packaging" / "macos" / "buildly_icon.icns",
        ]
        self.logo = None
        for candidate in logo_candidates:
            if candidate.exists():
                self.logo = str(candidate)
                break
        
        # Check if ForgeWeb is available
        # Since dashboard_control.py is in forgeweb/packaging/macos,
        # dashboard_dir IS the forgeweb directory
        self.forgeweb_dir = self.dashboard_dir
        # Check if this is actually a ForgeWeb installation
        self.forgeweb_available = (self.forgeweb_dir / "admin" / "file-api.py").exists()
        
        # Build menu dynamically based on what's available
        menu_items = []
        
        # Add ForgeWeb controls if available
        if self.forgeweb_available:
            menu_items.extend([
                rumps.MenuItem("ForgeWeb Status: Checking...", callback=None),
                None,  # Separator
                "Start ForgeWeb",
                "Stop ForgeWeb",
                "Open ForgeWeb Admin",
            ])
        
        # Only add Dashboard controls if we have a traditional dashboard setup
        if self.startup_script and self.startup_script.exists() and "ops/startup.sh" in str(self.startup_script):
            menu_items.extend([
                None,  # Separator
                rumps.MenuItem("Dashboard Status: Checking...", callback=None),
                None,  # Separator
                "Start Dashboard",
                "Restart Dashboard",
                "Stop Dashboard",
                None,
                "Open Dashboard",
                "View Dashboard Logs",
            ])
        
        menu_items.extend([
            None,
            "Quit"
        ])
        
        self.menu = menu_items
        
        # Set icon to logo
        if self.logo:
            self.icon = self.logo
        
        # Start status checker
        self.timer = rumps.Timer(self.update_status, 5)
        self.timer.start()
        self.update_status(None)
    
    def get_server_status(self):
        """Check if server is running"""
        try:
            if self.pid_file.exists():
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                try:
                    os.kill(pid, 0)  # Check if process exists
                    
                    try:
                        response = requests.get('http://localhost:8008/api/health', timeout=2)
                        if response.status_code == 200:
                            return 'running', pid
                    except:
                        pass
                    
                    return 'starting', pid
                except OSError:
                    self.pid_file.unlink()
                    return 'stopped', None
            
            return 'stopped', None
        except Exception as e:
            print(f"Error checking status: {e}")
            return 'unknown', None
    
    def get_forgeweb_status(self):
        """Check if ForgeWeb is running"""
        if not self.forgeweb_available:
            return 'unavailable', None
        
        try:
            # Try to check health endpoint
            response = requests.get('http://localhost:8000/api/health', timeout=2)
            if response.status_code == 200:
                # Find the process
                try:
                    result = subprocess.run(
                        ['pgrep', '-f', 'file-api.py'],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    if result.stdout.strip():
                        pid = int(result.stdout.strip().split('\n')[0])
                        return 'running', pid
                except:
                    pass
                return 'running', None
        except:
            pass
        
        # Check if process exists even if health endpoint fails
        try:
            result = subprocess.run(
                ['pgrep', '-f', 'file-api.py'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.stdout.strip():
                pid = int(result.stdout.strip().split('\n')[0])
                return 'starting', pid
        except:
            pass
        
        return 'stopped', None
    
    def update_status(self, sender):
        """Update status display for ForgeWeb and Dashboard (if present)"""
        
        # Update ForgeWeb status if available
        if self.forgeweb_available:
            fw_status, fw_pid = self.get_forgeweb_status()
            
            if fw_status == 'running':
                self.menu["ForgeWeb Status: Checking..."].title = f"✅ ForgeWeb Running (PID: {fw_pid})"
                self.title = "✅"
                self.menu["Start ForgeWeb"].set_callback(None)
                self.menu["Stop ForgeWeb"].set_callback(self.stop_forgeweb)
                self.menu["Open ForgeWeb Admin"].set_callback(self.open_forgeweb)
            elif fw_status == 'starting':
                self.menu["ForgeWeb Status: Checking..."].title = f"⏳ ForgeWeb Starting (PID: {fw_pid})"
                self.title = "⏳"
                self.menu["Start ForgeWeb"].set_callback(None)
                self.menu["Stop ForgeWeb"].set_callback(self.stop_forgeweb)
                self.menu["Open ForgeWeb Admin"].set_callback(None)
            else:
                self.menu["ForgeWeb Status: Checking..."].title = "⭕ ForgeWeb Stopped"
                self.title = "⭕"
                self.menu["Start ForgeWeb"].set_callback(self.start_forgeweb)
                self.menu["Stop ForgeWeb"].set_callback(None)
                self.menu["Open ForgeWeb Admin"].set_callback(None)
        
        # Update Dashboard status only if Dashboard controls exist in menu
        if "Dashboard Status: Checking..." in self.menu:
            status, pid = self.get_server_status()
            
            if status == 'running':
                self.menu["Dashboard Status: Checking..."].title = f"✅ Dashboard Running (PID: {pid})"
                self.title = "✅"
                self.menu["Start Dashboard"].set_callback(None)
                self.menu["Restart Dashboard"].set_callback(self.restart_server)
                self.menu["Stop Dashboard"].set_callback(self.stop_server)
                self.menu["Open Dashboard"].set_callback(self.open_dashboard)
            elif status == 'starting':
                self.menu["Dashboard Status: Checking..."].title = f"⏳ Dashboard Starting (PID: {pid})"
                self.title = "⏳"
                self.menu["Start Dashboard"].set_callback(None)
                self.menu["Restart Dashboard"].set_callback(self.restart_server)
                self.menu["Stop Dashboard"].set_callback(self.stop_server)
                self.menu["Open Dashboard"].set_callback(None)
            else:
                self.menu["Dashboard Status: Checking..."].title = "⭕ Dashboard Stopped"
                self.title = "⭕"
                self.menu["Start Dashboard"].set_callback(self.start_server)
                self.menu["Restart Dashboard"].set_callback(None)
                self.menu["Stop Dashboard"].set_callback(None)
                self.menu["Open Dashboard"].set_callback(None)
    
    def kill_existing_server(self):
        """Kill any existing server process"""
        try:
            result = subprocess.run(
                ['pgrep', '-f', 'python.*main.py'],
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                    except:
                        pass
                time.sleep(1)
        except Exception as e:
            print(f"Error killing existing server: {e}")
    
    @rumps.clicked("Start Dashboard")
    def start_server(self, _):
        """Start the dashboard server"""
        if not self.startup_script or not self.startup_script.exists():
            rumps.alert("Dashboard", "Dashboard startup script not found. This controller only manages ForgeWeb.")
            return
        
        try:
            self.kill_existing_server()
            subprocess.Popen(
                [str(self.startup_script)],
                cwd=str(self.dashboard_dir),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            rumps.notification("Dashboard", "Server Starting", "The dashboard server is starting up...")
            rumps.Timer(self.update_status, 2).start()
        except Exception as e:
            rumps.alert(f"Failed to start server: {e}")
    
    @rumps.clicked("Restart Dashboard")
    def restart_server(self, _):
        """Restart the dashboard server"""
        if not self.startup_script or not self.startup_script.exists():
            rumps.alert("Dashboard", "Dashboard startup script not found. This controller only manages ForgeWeb.")
            return
        
        try:
            self.kill_existing_server()
            subprocess.Popen(
                [str(self.startup_script), 'restart'],
                cwd=str(self.dashboard_dir),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            rumps.notification("Dashboard", "Server Restarting", "The dashboard server is restarting...")
            rumps.Timer(self.update_status, 2).start()
        except Exception as e:
            rumps.alert(f"Failed to restart server: {e}")
    
    @rumps.clicked("Stop Dashboard")
    def stop_server(self, _):
        """Stop the dashboard server"""
        if not self.startup_script or not self.startup_script.exists():
            # Just kill processes if no startup script
            self.kill_existing_server()
            rumps.notification("Dashboard", "Server Stopped", "Killed dashboard processes")
            rumps.Timer(self.update_status, 2).start()
            return
        
        try:
            subprocess.Popen(
                [str(self.startup_script), 'stop'],
                cwd=str(self.dashboard_dir),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            rumps.notification("Dashboard", "Server Stopping", "The dashboard server is shutting down...")
            rumps.Timer(self.update_status, 2).start()
        except Exception as e:
            rumps.alert(f"Failed to stop server: {e}")
    
    @rumps.clicked("Open Dashboard")
    def open_dashboard(self, _):
        """Open dashboard in browser"""
        subprocess.run(['open', 'http://localhost:8008'])
    
    @rumps.clicked("View Dashboard Logs")
    def view_logs(self, _):
        """Open logs in terminal"""
        log_file = self.dashboard_dir / "dashboard.log"
        if log_file.exists():
            subprocess.Popen([
                'open', '-a', 'Terminal',
                str(log_file)
            ])
        else:
            rumps.alert("Dashboard", "No logs found yet. Start the server first.")
    
    @rumps.clicked("Start ForgeWeb")
    def start_forgeweb(self, _):
        """Start ForgeWeb server"""
        if not self.forgeweb_available:
            rumps.alert("ForgeWeb", "ForgeWeb is not available in this installation")
            return
        
        try:
            # Kill any existing ForgeWeb process
            try:
                result = subprocess.run(
                    ['pgrep', '-f', 'file-api.py'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        try:
                            os.kill(int(pid), signal.SIGTERM)
                        except:
                            pass
                    time.sleep(1)
            except:
                pass
            
            # Start ForgeWeb directly (bypass interactive start.sh)
            forgeweb_script = self.forgeweb_dir / "admin" / "file-api.py"
            if forgeweb_script.exists():
                subprocess.Popen(
                    ['python3', 'file-api.py'],
                    cwd=str(self.forgeweb_dir / "admin"),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                rumps.notification("ForgeWeb", "Server Starting", "ForgeWeb is starting up...")
                rumps.Timer(self.update_status, 2).start()
            else:
                rumps.alert("ForgeWeb", f"ForgeWeb script not found at {forgeweb_script}")
        except Exception as e:
            rumps.alert(f"Failed to start ForgeWeb: {e}")
    
    @rumps.clicked("Open ForgeWeb Admin")
    def open_forgeweb(self, _):
        """Open ForgeWeb admin in browser"""
        subprocess.run(['open', 'http://localhost:8000/admin/'])
    
    @rumps.clicked("Stop ForgeWeb")
    def stop_forgeweb(self, _):
        """Stop ForgeWeb server"""
        if not self.forgeweb_available:
            return
        
        try:
            result = subprocess.run(
                ['pgrep', '-f', 'file-api.py'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                    except:
                        pass
                
                rumps.notification("ForgeWeb", "Server Stopping", "ForgeWeb is shutting down...")
                rumps.Timer(self.update_status, 2).start()
        except Exception as e:
            rumps.alert(f"Failed to stop ForgeWeb: {e}")

if __name__ == '__main__':
    try:
        app = DashboardController()
        app.run()
    except Exception as e:
        print(f"Error starting app: {e}")
        import traceback
        traceback.print_exc()

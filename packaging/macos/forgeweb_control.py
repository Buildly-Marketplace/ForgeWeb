#!/usr/bin/env python3
"""
ForgeWeb Control App - macOS Menu Bar Version (Integrated with Dashboard)
A menu bar application to control ForgeWeb admin server
Can integrate with existing Dashboard controller or run standalone
"""

import rumps
import subprocess
import os
import signal
import requests
from pathlib import Path
import sys
import time

# Add parent packaging dir to path for control_integration import
sys.path.insert(0, str(Path(__file__).parent.parent))
from control_integration import DashboardIntegration, ControllerConfig, get_startup_script, get_pid_file, get_logo_path


class ForgeWebController(rumps.App):
    def __init__(self):
        super(ForgeWebController, self).__init__("ForgeWeb")
        
        # Find ForgeWeb directory
        packaging_dir = Path(__file__).parent
        self.forgeweb_dir = packaging_dir.parent.parent.absolute()
        
        # Check integration status
        self.integration = DashboardIntegration(packaging_dir)
        self.mode = self.integration.get_installation_mode()
        
        # Get paths
        self.startup_script = get_startup_script(self.forgeweb_dir)
        self.pid_file = get_pid_file(self.forgeweb_dir)
        self.logo = get_logo_path(packaging_dir)
        
        if not self.startup_script:
            self._show_error("ForgeWeb startup script not found")
            
        # Update config
        self.integration.add_forgeweb_service()
        
        # Build menu based on integration mode
        self._build_menu()
        
        # Set icon
        if self.logo and Path(self.logo).exists():
            self.icon = str(self.logo)
        
        # Start status checker
        self.timer = rumps.Timer(self.update_status, 5)
        self.timer.start()
        self.update_status(None)
        
        # Log startup mode
        print(f"ForgeWeb Controller started in {self.mode} mode")
    
    def _build_menu(self):
        """Build menu based on integration mode"""
        if self.mode == "integrated":
            self.menu = [
                rumps.MenuItem("🔧 ForgeWeb Controls", callback=None),
                rumps.MenuItem("Status: Checking...", callback=None),
                None,
                "Start ForgeWeb",
                "Restart ForgeWeb",
                "Stop ForgeWeb",
                None,
                "Open ForgeWeb Admin",
                "Open ForgeWeb Site",
                "View Logs",
                None,
                "About",
                "Quit"
            ]
        else:
            # Standalone mode - simpler menu
            self.menu = [
                rumps.MenuItem("Status: Checking...", callback=None),
                None,
                "Start ForgeWeb",
                "Restart ForgeWeb",
                "Stop ForgeWeb",
                None,
                "Open ForgeWeb Admin",
                "Open ForgeWeb Site",
                "View Logs",
                None,
                "Quit"
            ]
    
    def get_server_status(self):
        """Check if ForgeWeb server is running"""
        try:
            if self.pid_file.exists():
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                try:
                    os.kill(pid, 0)  # Check if process exists
                    
                    # Check if ForgeWeb responds
                    try:
                        response = requests.get(
                            ControllerConfig.FORGEWEB_HEALTH_ENDPOINT,
                            timeout=2
                        )
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
    
    def update_status(self, sender):
        """Update status display"""
        status, pid = self.get_server_status()
        
        if status == 'running':
            self.menu["Status: Checking..."].title = f"✅ Running (PID: {pid})"
            self.title = "✅"
            self.menu["Start ForgeWeb"].set_callback(None)
            self.menu["Restart ForgeWeb"].set_callback(self.restart_forgeweb)
            self.menu["Stop ForgeWeb"].set_callback(self.stop_forgeweb)
            self.menu["Open ForgeWeb Admin"].set_callback(self.open_admin)
            self.menu["Open ForgeWeb Site"].set_callback(self.open_site)
        elif status == 'starting':
            self.menu["Status: Checking..."].title = f"⏳ Starting (PID: {pid})"
            self.title = "⏳"
            self.menu["Start ForgeWeb"].set_callback(None)
            self.menu["Restart ForgeWeb"].set_callback(self.restart_forgeweb)
            self.menu["Stop ForgeWeb"].set_callback(self.stop_forgeweb)
            self.menu["Open ForgeWeb Admin"].set_callback(None)
            self.menu["Open ForgeWeb Site"].set_callback(None)
        else:
            self.menu["Status: Checking..."].title = "⭕ Stopped"
            self.title = "⭕"
            self.menu["Start ForgeWeb"].set_callback(self.start_forgeweb)
            self.menu["Restart ForgeWeb"].set_callback(None)
            self.menu["Stop ForgeWeb"].set_callback(None)
            self.menu["Open ForgeWeb Admin"].set_callback(None)
            self.menu["Open ForgeWeb Site"].set_callback(None)
    
    def kill_existing_server(self):
        """Kill any existing ForgeWeb server process"""
        try:
            result = subprocess.run(
                ['pgrep', '-f', 'forgeweb.*main.py'],
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
    
    @rumps.clicked("Start ForgeWeb")
    def start_forgeweb(self, _):
        """Start ForgeWeb server"""
        if not self.startup_script:
            rumps.alert("Error", "ForgeWeb startup script not found")
            return
        
        try:
            self.kill_existing_server()
            subprocess.Popen(
                [str(self.startup_script)],
                cwd=str(self.forgeweb_dir),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            rumps.notification(
                "ForgeWeb",
                "Server Starting",
                "The ForgeWeb server is starting up..."
            )
            rumps.Timer(self.update_status, 2).start()
        except Exception as e:
            rumps.alert("Error", f"Failed to start ForgeWeb: {e}")
    
    @rumps.clicked("Restart ForgeWeb")
    def restart_forgeweb(self, _):
        """Restart ForgeWeb server"""
        if not self.startup_script:
            rumps.alert("Error", "ForgeWeb startup script not found")
            return
        
        try:
            self.kill_existing_server()
            subprocess.Popen(
                [str(self.startup_script), 'restart'],
                cwd=str(self.forgeweb_dir),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            rumps.notification(
                "ForgeWeb",
                "Server Restarting",
                "The ForgeWeb server is restarting..."
            )
            rumps.Timer(self.update_status, 2).start()
        except Exception as e:
            rumps.alert("Error", f"Failed to restart ForgeWeb: {e}")
    
    @rumps.clicked("Stop ForgeWeb")
    def stop_forgeweb(self, _):
        """Stop ForgeWeb server"""
        if not self.startup_script:
            rumps.alert("Error", "ForgeWeb startup script not found")
            return
        
        try:
            subprocess.Popen(
                [str(self.startup_script), 'stop'],
                cwd=str(self.forgeweb_dir),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            rumps.notification(
                "ForgeWeb",
                "Server Stopping",
                "The ForgeWeb server is shutting down..."
            )
            rumps.Timer(self.update_status, 2).start()
        except Exception as e:
            rumps.alert("Error", f"Failed to stop ForgeWeb: {e}")
    
    @rumps.clicked("Open ForgeWeb Admin")
    def open_admin(self, _):
        """Open ForgeWeb admin panel"""
        subprocess.run([
            'open',
            f'http://localhost:{ControllerConfig.FORGEWEB_PORT}/admin/'
        ])
    
    @rumps.clicked("Open ForgeWeb Site")
    def open_site(self, _):
        """Open ForgeWeb test site"""
        subprocess.run([
            'open',
            f'http://localhost:{ControllerConfig.FORGEWEB_PORT}/'
        ])
    
    @rumps.clicked("View Logs")
    def view_logs(self, _):
        """Open logs in terminal"""
        log_file = self.forgeweb_dir / "forgeweb.log"
        if log_file.exists():
            subprocess.Popen([
                'open', '-a', 'Terminal',
                str(log_file)
            ])
        else:
            rumps.alert(
                "ForgeWeb",
                "No logs found yet. Start the server first."
            )
    
    @rumps.clicked("About")
    def show_about(self, _):
        """Show about dialog"""
        mode_text = "integrated with Dashboard" if self.mode == "integrated" else "standalone"
        rumps.alert(
            "ForgeWeb Control",
            f"ForgeWeb Admin Server Controller\n\n"
            f"Running in {mode_text} mode\n\n"
            f"Port: {ControllerConfig.FORGEWEB_PORT}\n"
            f"Version: 1.0"
        )
    
    def _show_error(self, message):
        """Show error and exit"""
        rumps.alert("ForgeWeb Control Error", message)
        sys.exit(1)


if __name__ == '__main__':
    try:
        app = ForgeWebController()
        app.run()
    except Exception as e:
        print(f"Error starting ForgeWeb Controller: {e}")
        import traceback
        traceback.print_exc()

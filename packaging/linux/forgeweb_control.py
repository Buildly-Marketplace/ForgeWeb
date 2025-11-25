#!/usr/bin/env python3
"""
ForgeWeb Control App - Linux Desktop Version (Integrated with Dashboard)
A system tray application to control ForgeWeb admin server
Can integrate with existing Dashboard controller or run standalone
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3, GLib
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


class ForgeWebController:
    def __init__(self):
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
        
        # Create indicator
        self.indicator = AppIndicator3.Indicator.new(
            "forgeweb-controller",
            "application-default-icon",
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.build_menu())
        
        # Start status check loop
        GLib.timeout_add_seconds(5, self.update_status)
        self.update_status()
        
        # Log startup mode
        print(f"ForgeWeb Controller started in {self.mode} mode")
    
    def build_menu(self):
        """Build the system tray menu"""
        menu = Gtk.Menu()
        
        # ForgeWeb section header (if integrated)
        if self.mode == "integrated":
            header = Gtk.MenuItem(label="🔧 ForgeWeb Controls")
            header.set_sensitive(False)
            menu.append(header)
        
        # Status item (non-clickable)
        self.status_item = Gtk.MenuItem(label="Checking status...")
        self.status_item.set_sensitive(False)
        menu.append(self.status_item)
        
        # Separator
        menu.append(Gtk.SeparatorMenuItem())
        
        # Start button
        self.start_item = Gtk.MenuItem(label="▶️ Start ForgeWeb")
        self.start_item.connect('activate', self.start_forgeweb)
        menu.append(self.start_item)
        
        # Restart button
        self.restart_item = Gtk.MenuItem(label="🔄 Restart ForgeWeb")
        self.restart_item.connect('activate', self.restart_forgeweb)
        menu.append(self.restart_item)
        
        # Stop button
        self.stop_item = Gtk.MenuItem(label="⏹️ Stop ForgeWeb")
        self.stop_item.connect('activate', self.stop_forgeweb)
        menu.append(self.stop_item)
        
        # Separator
        menu.append(Gtk.SeparatorMenuItem())
        
        # Open Admin button
        self.admin_item = Gtk.MenuItem(label="🔧 Open Admin Panel")
        self.admin_item.connect('activate', self.open_admin)
        menu.append(self.admin_item)
        
        # Open Site button
        self.site_item = Gtk.MenuItem(label="🌐 Open ForgeWeb Site")
        self.site_item.connect('activate', self.open_site)
        menu.append(self.site_item)
        
        # View Logs button
        self.logs_item = Gtk.MenuItem(label="📋 View Logs")
        self.logs_item.connect('activate', self.view_logs)
        menu.append(self.logs_item)
        
        # Separator
        menu.append(Gtk.SeparatorMenuItem())
        
        # Quit button
        quit_item = Gtk.MenuItem(label="❌ Quit Controller")
        quit_item.connect('activate', self.quit_app)
        menu.append(quit_item)
        
        menu.show_all()
        return menu
    
    def get_server_status(self):
        """Check if ForgeWeb server is running"""
        try:
            if self.pid_file.exists():
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                try:
                    os.kill(pid, 0)  # This doesn't kill, just checks
                    
                    # Check if server responds
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
    
    def update_status(self):
        """Update status display"""
        status, pid = self.get_server_status()
        
        if status == 'running':
            self.status_item.set_label(f"✅ Running (PID: {pid})")
            self.start_item.set_sensitive(False)
            self.restart_item.set_sensitive(True)
            self.stop_item.set_sensitive(True)
            self.admin_item.set_sensitive(True)
            self.site_item.set_sensitive(True)
        elif status == 'starting':
            self.status_item.set_label(f"⏳ Starting (PID: {pid})")
            self.start_item.set_sensitive(False)
            self.restart_item.set_sensitive(True)
            self.stop_item.set_sensitive(True)
            self.admin_item.set_sensitive(False)
            self.site_item.set_sensitive(False)
        else:
            self.status_item.set_label("⭕ Stopped")
            self.start_item.set_sensitive(True)
            self.restart_item.set_sensitive(False)
            self.stop_item.set_sensitive(False)
            self.admin_item.set_sensitive(False)
            self.site_item.set_sensitive(False)
        
        return True  # Continue timer
    
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
    
    def start_forgeweb(self, widget):
        """Start ForgeWeb server"""
        try:
            self.kill_existing_server()
            subprocess.Popen(
                [str(self.startup_script)],
                cwd=str(self.forgeweb_dir),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.show_notification("ForgeWeb", "Server is starting...")
            GLib.timeout_add_seconds(2, self.update_status)
        except Exception as e:
            self.show_notification("ForgeWeb", f"Failed to start: {e}")
    
    def restart_forgeweb(self, widget):
        """Restart ForgeWeb server"""
        try:
            self.kill_existing_server()
            subprocess.Popen(
                [str(self.startup_script), 'restart'],
                cwd=str(self.forgeweb_dir),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.show_notification("ForgeWeb", "Server is restarting...")
            GLib.timeout_add_seconds(2, self.update_status)
        except Exception as e:
            self.show_notification("ForgeWeb", f"Failed to restart: {e}")
    
    def stop_forgeweb(self, widget):
        """Stop ForgeWeb server"""
        try:
            subprocess.Popen(
                [str(self.startup_script), 'stop'],
                cwd=str(self.forgeweb_dir),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.show_notification("ForgeWeb", "Server is stopping...")
            GLib.timeout_add_seconds(2, self.update_status)
        except Exception as e:
            self.show_notification("ForgeWeb", f"Failed to stop: {e}")
    
    def open_admin(self, widget):
        """Open ForgeWeb admin panel"""
        try:
            subprocess.Popen([
                'xdg-open',
                f'http://localhost:{ControllerConfig.FORGEWEB_PORT}/admin/'
            ])
        except:
            try:
                subprocess.Popen([
                    'open',
                    f'http://localhost:{ControllerConfig.FORGEWEB_PORT}/admin/'
                ])
            except Exception as e:
                self.show_notification("ForgeWeb", f"Could not open browser: {e}")
    
    def open_site(self, widget):
        """Open ForgeWeb test site"""
        try:
            subprocess.Popen([
                'xdg-open',
                f'http://localhost:{ControllerConfig.FORGEWEB_PORT}/'
            ])
        except:
            try:
                subprocess.Popen([
                    'open',
                    f'http://localhost:{ControllerConfig.FORGEWEB_PORT}/'
                ])
            except Exception as e:
                self.show_notification("ForgeWeb", f"Could not open browser: {e}")
    
    def view_logs(self, widget):
        """Open logs in terminal"""
        log_file = self.forgeweb_dir / "forgeweb.log"
        if log_file.exists():
            try:
                subprocess.Popen([
                    'xdg-open', str(log_file)
                ])
            except:
                try:
                    subprocess.Popen(['open', str(log_file)])
                except:
                    self.show_notification("ForgeWeb", "Could not open log file")
        else:
            self.show_notification("ForgeWeb", "No logs found yet. Start the server first.")
    
    def show_notification(self, title, message):
        """Show system notification"""
        try:
            subprocess.run([
                'notify-send',
                title,
                message
            ])
        except:
            print(f"{title}: {message}")
    
    def quit_app(self, widget):
        """Quit the application"""
        Gtk.main_quit()
    
    def _show_error(self, message):
        """Show error and exit"""
        dialog = Gtk.MessageDialog(
            transient_for=None,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="ForgeWeb Control Error"
        )
        dialog.format_secondary_text(message)
        dialog.run()
        sys.exit(1)


if __name__ == '__main__':
    try:
        app = ForgeWebController()
        Gtk.main()
    except Exception as e:
        print(f"Error starting ForgeWeb Controller: {e}")
        import traceback
        traceback.print_exc()

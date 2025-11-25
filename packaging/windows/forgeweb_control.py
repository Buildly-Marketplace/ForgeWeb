#!/usr/bin/env python3
"""
ForgeWeb Control App - Windows System Tray Version (Integrated with Dashboard)
A system tray application to control ForgeWeb admin server
Can integrate with existing Dashboard controller or run standalone
"""

import sys
import os
import signal
import subprocess
import webbrowser
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QMessageBox
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
import requests

# Add parent packaging dir to path for control_integration import
sys.path.insert(0, str(Path(__file__).parent.parent))
from control_integration import DashboardIntegration, ControllerConfig, get_startup_script, get_pid_file, get_logo_path


class ForgeWebController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        
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
            self.show_error("ForgeWeb startup script not found")
        
        # Update config
        self.integration.add_forgeweb_service()
        
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self.app)
        self.tray_icon.setToolTip("ForgeWeb Controller")
        
        # Set icon if available
        if self.logo and Path(self.logo).exists():
            self.tray_icon.setIcon(QIcon(str(self.logo)))
        
        # Create menu
        self.menu = QMenu()
        self.build_menu()
        
        # Set menu and show tray icon
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()
        
        # Start status update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(5000)  # Update every 5 seconds
        self.update_status()
        
        # Log startup mode
        print(f"ForgeWeb Controller started in {self.mode} mode")
    
    def build_menu(self):
        """Build the system tray menu"""
        # ForgeWeb section header (if integrated)
        if self.mode == "integrated":
            header = QAction("🔧 ForgeWeb Controls", self.app)
            header.setEnabled(False)
            self.menu.addAction(header)
        
        # Status item (disabled)
        self.status_action = QAction("⭕ Checking status...", self.app)
        self.status_action.setEnabled(False)
        self.menu.addAction(self.status_action)
        
        self.menu.addSeparator()
        
        # Control actions
        self.start_action = QAction("▶️ Start ForgeWeb", self.app)
        self.start_action.triggered.connect(self.start_forgeweb)
        self.menu.addAction(self.start_action)
        
        self.restart_action = QAction("🔄 Restart ForgeWeb", self.app)
        self.restart_action.triggered.connect(self.restart_forgeweb)
        self.menu.addAction(self.restart_action)
        
        self.stop_action = QAction("⏹️ Stop ForgeWeb", self.app)
        self.stop_action.triggered.connect(self.stop_forgeweb)
        self.menu.addAction(self.stop_action)
        
        self.menu.addSeparator()
        
        # Open admin action
        self.admin_action = QAction("🔧 Open Admin Panel", self.app)
        self.admin_action.triggered.connect(self.open_admin)
        self.menu.addAction(self.admin_action)
        
        # Open site action
        self.site_action = QAction("🌐 Open ForgeWeb Site", self.app)
        self.site_action.triggered.connect(self.open_site)
        self.menu.addAction(self.site_action)
        
        # View logs action
        self.logs_action = QAction("📋 View Logs", self.app)
        self.logs_action.triggered.connect(self.view_logs)
        self.menu.addAction(self.logs_action)
        
        self.menu.addSeparator()
        
        # Quit action
        quit_action = QAction("❌ Quit", self.app)
        quit_action.triggered.connect(self.quit_app)
        self.menu.addAction(quit_action)
    
    def get_server_status(self):
        """Check if ForgeWeb server is running"""
        try:
            if self.pid_file.exists():
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                # On Windows, check if process exists differently
                try:
                    # Try using tasklist on Windows
                    result = subprocess.run(
                        ['tasklist', '/FI', f'PID eq {pid}'],
                        capture_output=True,
                        text=True
                    )
                    
                    if str(pid) in result.stdout:
                        # Process exists, check if responding
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
                except:
                    pass
            
            return 'stopped', None
        except Exception as e:
            print(f"Error checking status: {e}")
            return 'unknown', None
    
    def update_status(self):
        """Update status display"""
        status, pid = self.get_server_status()
        
        if status == 'running':
            self.status_action.setText(f"✅ Running (PID: {pid})")
            self.start_action.setEnabled(False)
            self.restart_action.setEnabled(True)
            self.stop_action.setEnabled(True)
            self.admin_action.setEnabled(True)
            self.site_action.setEnabled(True)
        elif status == 'starting':
            self.status_action.setText(f"⏳ Starting (PID: {pid})")
            self.start_action.setEnabled(False)
            self.restart_action.setEnabled(True)
            self.stop_action.setEnabled(True)
            self.admin_action.setEnabled(False)
            self.site_action.setEnabled(False)
        else:
            self.status_action.setText("⭕ Stopped")
            self.start_action.setEnabled(True)
            self.restart_action.setEnabled(False)
            self.stop_action.setEnabled(False)
            self.admin_action.setEnabled(False)
            self.site_action.setEnabled(False)
    
    def kill_existing_server(self):
        """Kill any existing ForgeWeb server process"""
        try:
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq python.exe'],
                capture_output=True,
                text=True
            )
            
            # Look for forgeweb processes and kill them
            if 'python.exe' in result.stdout:
                try:
                    result = subprocess.run(
                        ['taskkill', '/F', '/IM', 'python.exe'],
                        capture_output=True,
                        text=True
                    )
                except:
                    pass
        except Exception as e:
            print(f"Error killing existing server: {e}")
    
    def start_forgeweb(self):
        """Start ForgeWeb server"""
        try:
            self.kill_existing_server()
            subprocess.Popen(
                [str(self.startup_script)],
                cwd=str(self.forgeweb_dir),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.tray_icon.showMessage(
                "ForgeWeb",
                "Server is starting...",
                QSystemTrayIcon.Information,
                2000
            )
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to start ForgeWeb: {e}")
    
    def restart_forgeweb(self):
        """Restart ForgeWeb server"""
        try:
            self.kill_existing_server()
            subprocess.Popen(
                [str(self.startup_script), 'restart'],
                cwd=str(self.forgeweb_dir),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.tray_icon.showMessage(
                "ForgeWeb",
                "Server is restarting...",
                QSystemTrayIcon.Information,
                2000
            )
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to restart ForgeWeb: {e}")
    
    def stop_forgeweb(self):
        """Stop ForgeWeb server"""
        try:
            subprocess.Popen(
                [str(self.startup_script), 'stop'],
                cwd=str(self.forgeweb_dir),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.tray_icon.showMessage(
                "ForgeWeb",
                "Server is stopping...",
                QSystemTrayIcon.Information,
                2000
            )
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to stop ForgeWeb: {e}")
    
    def open_admin(self):
        """Open ForgeWeb admin panel"""
        webbrowser.open(f'http://localhost:{ControllerConfig.FORGEWEB_PORT}/admin/')
    
    def open_site(self):
        """Open ForgeWeb test site"""
        webbrowser.open(f'http://localhost:{ControllerConfig.FORGEWEB_PORT}/')
    
    def view_logs(self):
        """Open logs in default viewer"""
        log_file = self.forgeweb_dir / "forgeweb.log"
        if log_file.exists():
            os.startfile(str(log_file))
        else:
            QMessageBox.information(
                None,
                "ForgeWeb",
                "No logs found yet. Start the server first."
            )
    
    def quit_app(self):
        """Quit the application"""
        self.app.quit()
    
    def show_error(self, message):
        """Show error and exit"""
        QMessageBox.critical(None, "ForgeWeb Control Error", message)
        sys.exit(1)
    
    def run(self):
        """Run the application"""
        sys.exit(self.app.exec_())


if __name__ == '__main__':
    try:
        controller = ForgeWebController()
        controller.run()
    except Exception as e:
        print(f"Error starting ForgeWeb Controller: {e}")
        import traceback
        traceback.print_exc()

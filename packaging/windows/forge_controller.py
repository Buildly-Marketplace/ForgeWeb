#!/usr/bin/env python3
"""
Forge Controller - Universal Service Monitor (Windows)
Discovers and manages services across ports 80-90 and 8000-9000
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
import subprocess
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from service_discovery import ServiceDiscovery, Service


class ForgeController(QSystemTrayIcon):
    """Universal Forge Controller for Windows"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Find and set icon
        logo_path = self._find_logo()
        if logo_path:
            self.setIcon(QIcon(logo_path))
        
        # Initialize service discovery
        self.discovery = ServiceDiscovery(search_root=Path.cwd().parent)
        self.services = {}
        
        # Create menu
        self.menu = QMenu()
        self.setContextMenu(self.menu)
        
        # Discover services
        self.discover_services()
        
        # Refresh timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_services)
        self.timer.start(5000)  # 5 second refresh
        
        # Show in system tray
        self.show()
    
    def _find_logo(self) -> str:
        """Find the Forge logo"""
        candidates = [
            Path(__file__).parent / "forge-logo.png",
            Path(__file__).parent.parent / "forge-logo.png",
            Path(__file__).parent.parent.parent / "forgeweb" / "assets" / "images" / "forge-logo.png",
        ]
        
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)
        
        return None
    
    def discover_services(self):
        """Discover available services"""
        try:
            discovered = self.discovery.discover()
            self.services = {s.name: s for s in discovered}
            self._rebuild_menu(discovered)
        except Exception as e:
            print(f"Error discovering services: {e}")
    
    def refresh_services(self):
        """Refresh service statuses"""
        try:
            for service in self.services.values():
                self.discovery._update_service_status(service)
                # Update menu item
                self._update_menu_status(service)
        except Exception as e:
            print(f"Error refreshing services: {e}")
    
    def _rebuild_menu(self, services):
        """Rebuild menu with discovered services"""
        self.menu.clear()
        
        if not services:
            action = self.menu.addAction("No services found")
            action.setEnabled(False)
        else:
            for i, service in enumerate(services):
                if i > 0:
                    self.menu.addSeparator()
                
                # Status
                status_icon = self._get_status_icon(service.status)
                status_action = self.menu.addAction(f"{status_icon} {service.name} (:{service.port})")
                status_action.setEnabled(False)
                status_action.setObjectName(f"status_{service.name}")
                
                # Start
                start_action = self.menu.addAction("  ▶ Start")
                start_action.triggered.connect(lambda checked, s=service: self.start_service(s))
                
                # Stop
                stop_action = self.menu.addAction("  ⏸ Stop")
                stop_action.triggered.connect(lambda checked, s=service: self.stop_service(s))
                
                # Restart
                restart_action = self.menu.addAction("  🔄 Restart")
                restart_action.triggered.connect(lambda checked, s=service: self.restart_service(s))
                
                # Logs
                logs_action = self.menu.addAction("  📖 Logs")
                logs_action.triggered.connect(lambda checked, s=service: self.show_logs(s))
                
                # Browser
                browser_action = self.menu.addAction("  🌐 Open Browser")
                browser_action.triggered.connect(lambda checked, s=service: self.open_browser(s))
        
        # Separator
        self.menu.addSeparator()
        
        # Quit
        quit_action = self.menu.addAction("Quit")
        quit_action.triggered.connect(QApplication.quit)
    
    def _update_menu_status(self, service: Service):
        """Update a service's status in menu"""
        status_icon = self._get_status_icon(service.status)
        pid_info = f" (PID: {service.pid})" if service.pid else ""
        new_text = f"{status_icon} {service.name} (:{service.port}){pid_info}"
        
        # Find and update the action
        for action in self.menu.actions():
            if action.objectName() == f"status_{service.name}":
                action.setText(new_text)
                break
    
    def _get_status_icon(self, status: str) -> str:
        """Get icon for service status"""
        if status == "running":
            return "✅"
        elif status == "starting":
            return "⏳"
        else:
            return "⭕"
    
    def start_service(self, service: Service):
        """Start a service"""
        try:
            self.discovery.start_service(service)
            self.discovery._update_service_status(service)
            self._update_menu_status(service)
        except Exception as e:
            print(f"Error starting service: {e}")
    
    def stop_service(self, service: Service):
        """Stop a service"""
        try:
            self.discovery.stop_service(service)
            time.sleep(1)
            self.discovery._update_service_status(service)
            self._update_menu_status(service)
        except Exception as e:
            print(f"Error stopping service: {e}")
    
    def restart_service(self, service: Service):
        """Restart a service"""
        try:
            self.discovery.restart_service(service)
            time.sleep(2)
            self.discovery._update_service_status(service)
            self._update_menu_status(service)
        except Exception as e:
            print(f"Error restarting service: {e}")
    
    def show_logs(self, service: Service):
        """Show service logs"""
        try:
            logs = self.discovery.tail_logs(service)
            if logs:
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
                    f.write(logs)
                    subprocess.Popen(['notepad', f.name])
            else:
                print(f"No logs found for {service.name}")
        except Exception as e:
            print(f"Error showing logs: {e}")
    
    def open_browser(self, service: Service):
        """Open service in browser"""
        try:
            if service.browser_url:
                import webbrowser
                webbrowser.open(service.browser_url)
        except Exception as e:
            print(f"Error opening browser: {e}")


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        controller = ForgeController()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error starting Forge Controller: {e}")
        import traceback
        traceback.print_exc()

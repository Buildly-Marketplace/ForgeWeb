#!/usr/bin/env python3
"""
Forge Controller - Universal Service Monitor (macOS)
Discovers and manages services across ports 80-90 and 8000-9000
"""

import rumps
import subprocess
import time
from pathlib import Path
import sys

# Add parent directory to path to import service_discovery
sys.path.insert(0, str(Path(__file__).parent.parent))
from service_discovery import ServiceDiscovery, Service


class ForgeController(rumps.App):
    """Universal Forge Controller for macOS"""
    
    def __init__(self):
        super(ForgeController, self).__init__("Forge Controller")
        
        # Find logo
        self.logo_path = self._find_logo()
        if self.logo_path:
            self.icon = self.logo_path
        
        # Initialize service discovery
        self.discovery = ServiceDiscovery(search_root=Path.cwd().parent)
        self.services = {}
        
        # Discover services immediately
        discovered = self._discover_services_sync()
        
        # Build initial menu
        menu_items = self._build_menu_items(discovered)
        menu_items.extend([None, "Quit"])
        
        # Set the menu
        self.menu = menu_items
        
        # Start refresh timer
        self.timer = rumps.Timer(self.refresh_services, 5)
        self.timer.start()
    
    def _find_logo(self) -> str:
        """Find the Forge logo"""
        candidates = [
            Path(__file__).parent / "forge-logo.png",
            Path(__file__).parent / "macos" / "forge-logo.png",
            Path(__file__).parent.parent / "forgeweb" / "assets" / "images" / "forge-logo.png",
        ]
        
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)
        
        return None
    
    def discover_services(self, sender):
        """Discover available services"""
        discovered = self._discover_services_sync()
        menu_items = self._build_menu_items(discovered)
        menu_items.extend([None, "Quit"])
        self.menu = menu_items
    
    def _discover_services_sync(self):
        """Synchronously discover services"""
        try:
            discovered = self.discovery.discover()
            self.services = {s.name: s for s in discovered}
            return discovered
        except Exception as e:
            print(f"Error discovering services: {e}")
            return []
    
    def _build_menu_items(self, services):
        """Build menu items from services"""
        if not services:
            return [
                rumps.MenuItem("No services found", callback=None),
                None,
            ]
        
        menu_items = []
        for service in services:
            # Add separator between services
            if menu_items:
                menu_items.append(None)
            
            # Status item
            status_icon = self._get_status_icon(service.status)
            menu_items.append(
                rumps.MenuItem(
                    f"{status_icon} {service.name} (:{service.port})",
                    callback=None,
                    key=f"status_{service.name}"
                )
            )
            
            # Service controls
            menu_items.append(
                rumps.MenuItem(
                    "  ▶ Start",
                    callback=lambda sender, s=service: self.start_service_callback(sender, s),
                    key=f"start_{service.name}"
                )
            )
            menu_items.append(
                rumps.MenuItem(
                    "  ⏸ Stop",
                    callback=lambda sender, s=service: self.stop_service_callback(sender, s),
                    key=f"stop_{service.name}"
                )
            )
            menu_items.append(
                rumps.MenuItem(
                    "  🔄 Restart",
                    callback=lambda sender, s=service: self.restart_service_callback(sender, s),
                    key=f"restart_{service.name}"
                )
            )
            menu_items.append(
                rumps.MenuItem(
                    "  📖 Logs",
                    callback=lambda sender, s=service: self.show_logs_callback(sender, s),
                    key=f"logs_{service.name}"
                )
            )
            menu_items.append(
                rumps.MenuItem(
                    "  🌐 Open Browser",
                    callback=lambda sender, s=service: self.open_browser_callback(sender, s),
                    key=f"browser_{service.name}"
                )
            )
        
        return menu_items
    
    def refresh_services(self, sender):
        """Refresh service statuses"""
        try:
            # Update status for all services
            for service in self.services.values():
                self.discovery._update_service_status(service)
            
            # Rebuild entire menu with updated statuses
            menu_items = self._build_menu_items(list(self.services.values()))
            menu_items.extend([None, "Quit"])
            self.menu = menu_items
            
            # Update title bar icon
            if any(s.status == "running" for s in self.services.values()):
                self.title = "✅"
            elif any(s.status == "starting" for s in self.services.values()):
                self.title = "⏳"
            else:
                self.title = "⭕"
        except Exception as e:
            print(f"Error refreshing services: {e}")
    
    def _get_status_icon(self, status: str) -> str:
        """Get icon for service status"""
        if status == "running":
            return "✅"
        elif status == "starting":
            return "⏳"
        else:
            return "⭕"
    
    def start_service_callback(self, sender, service: Service):
        """Handle start service click"""
        try:
            if self.discovery.start_service(service):
                rumps.notification(service.name, "Starting", f"Service starting on port {service.port}")
                self.discovery._update_service_status(service)
                self._update_service_menu_item(service)
            else:
                rumps.alert(service.name, "Failed to start service")
        except Exception as e:
            rumps.alert(service.name, f"Error: {e}")
    
    def stop_service_callback(self, sender, service: Service):
        """Handle stop service click"""
        try:
            if self.discovery.stop_service(service):
                rumps.notification(service.name, "Stopping", f"Service stopping on port {service.port}")
                time.sleep(1)
                self.discovery._update_service_status(service)
                self._update_service_menu_item(service)
            else:
                rumps.alert(service.name, "Failed to stop service")
        except Exception as e:
            rumps.alert(service.name, f"Error: {e}")
    
    def restart_service_callback(self, sender, service: Service):
        """Handle restart service click"""
        try:
            if self.discovery.restart_service(service):
                rumps.notification(service.name, "Restarting", f"Service restarting on port {service.port}")
                time.sleep(2)
                self.discovery._update_service_status(service)
                self._update_service_menu_item(service)
            else:
                rumps.alert(service.name, "Failed to restart service")
        except Exception as e:
            rumps.alert(service.name, f"Error: {e}")
    
    def show_logs_callback(self, sender, service: Service):
        """Show service logs"""
        try:
            logs = self.discovery.tail_logs(service)
            if logs:
                rumps.notification(service.name, "Logs", "Opening logs in terminal...")
                # Create temp log file and open in terminal
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
                    f.write(logs)
                    subprocess.run(['open', '-a', 'Terminal', f.name])
            else:
                rumps.alert(service.name, "No logs found for this service")
        except Exception as e:
            rumps.alert(service.name, f"Error: {e}")
    
    def open_browser_callback(self, sender, service: Service):
        """Open service in browser"""
        try:
            if service.browser_url:
                subprocess.run(['open', service.browser_url])
            else:
                rumps.alert(service.name, "No browser URL available")
        except Exception as e:
            rumps.alert(service.name, f"Error: {e}")


if __name__ == '__main__':
    try:
        app = ForgeController()
        app.run()
    except Exception as e:
        print(f"Error starting Forge Controller: {e}")
        import traceback
        traceback.print_exc()

#!/usr/bin/env python3
"""
Forge Controller - Universal Service Monitor (Linux)
Discovers and manages services across ports 80-90 and 8000-9000
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gtk, AppIndicator3, GLib
import subprocess
from pathlib import Path
import sys
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from service_discovery import ServiceDiscovery, Service


class ForgeController:
    """Universal Forge Controller for Linux"""
    
    def __init__(self):
        self.app_menu = Gtk.Menu()
        
        # Initialize service discovery
        self.discovery = ServiceDiscovery(search_root=Path.cwd().parent)
        self.services = {}
        
        # Find logo
        logo_path = self._find_logo()
        
        # Create indicator
        self.indicator = AppIndicator3.Indicator.new(
            "forge-controller",
            logo_path or "dialog-information",
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_menu(self.app_menu)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        
        # Discover services
        self.discover_services()
        
        # Refresh timer
        GLib.timeout_add_seconds(5, self.refresh_services)
    
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
        except Exception as e:
            print(f"Error refreshing services: {e}")
        
        return True  # Continue timer
    
    def _rebuild_menu(self, services):
        """Rebuild menu with discovered services"""
        # Clear menu
        for item in self.app_menu.get_children():
            self.app_menu.remove(item)
        
        if not services:
            item = Gtk.MenuItem(label="No services found")
            item.set_sensitive(False)
            self.app_menu.append(item)
        else:
            for i, service in enumerate(services):
                if i > 0:
                    self.app_menu.append(Gtk.SeparatorMenuItem())
                
                # Status
                status_icon = self._get_status_icon(service.status)
                status_item = Gtk.MenuItem(label=f"{status_icon} {service.name} (:{service.port})")
                status_item.set_sensitive(False)
                self.app_menu.append(status_item)
                
                # Start
                start_item = Gtk.MenuItem(label="  ▶ Start")
                start_item.connect("activate", lambda w, s=service: self.start_service(s))
                self.app_menu.append(start_item)
                
                # Stop
                stop_item = Gtk.MenuItem(label="  ⏸ Stop")
                stop_item.connect("activate", lambda w, s=service: self.stop_service(s))
                self.app_menu.append(stop_item)
                
                # Restart
                restart_item = Gtk.MenuItem(label="  🔄 Restart")
                restart_item.connect("activate", lambda w, s=service: self.restart_service(s))
                self.app_menu.append(restart_item)
                
                # Logs
                logs_item = Gtk.MenuItem(label="  📖 Logs")
                logs_item.connect("activate", lambda w, s=service: self.show_logs(s))
                self.app_menu.append(logs_item)
                
                # Browser
                browser_item = Gtk.MenuItem(label="  🌐 Open Browser")
                browser_item.connect("activate", lambda w, s=service: self.open_browser(s))
                self.app_menu.append(browser_item)
        
        # Separator
        self.app_menu.append(Gtk.SeparatorMenuItem())
        
        # Quit
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.quit_callback)
        self.app_menu.append(quit_item)
        
        self.app_menu.show_all()
    
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
            self._rebuild_menu(list(self.services.values()))
        except Exception as e:
            print(f"Error starting service: {e}")
    
    def stop_service(self, service: Service):
        """Stop a service"""
        try:
            self.discovery.stop_service(service)
            time.sleep(1)
            self.discovery._update_service_status(service)
            self._rebuild_menu(list(self.services.values()))
        except Exception as e:
            print(f"Error stopping service: {e}")
    
    def restart_service(self, service: Service):
        """Restart a service"""
        try:
            self.discovery.restart_service(service)
            time.sleep(2)
            self.discovery._update_service_status(service)
            self._rebuild_menu(list(self.services.values()))
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
                    subprocess.run(['xdg-open', f.name])
            else:
                print(f"No logs found for {service.name}")
        except Exception as e:
            print(f"Error showing logs: {e}")
    
    def open_browser(self, service: Service):
        """Open service in browser"""
        try:
            if service.browser_url:
                subprocess.run(['xdg-open', service.browser_url])
        except Exception as e:
            print(f"Error opening browser: {e}")
    
    def quit_callback(self, widget):
        """Quit application"""
        Gtk.main_quit()
    
    def run(self):
        """Run the application"""
        Gtk.main()


if __name__ == '__main__':
    try:
        controller = ForgeController()
        controller.run()
    except Exception as e:
        print(f"Error starting Forge Controller: {e}")
        import traceback
        traceback.print_exc()

#!/usr/bin/env python3
"""
Shared Utilities for ForgeWeb Control Integration
Provides common functionality for detecting and integrating with Dashboard controller
"""

import json
import subprocess
from pathlib import Path
from typing import Tuple, Optional, Dict


class ControllerConfig:
    """Configuration for control app integration"""
    
    # ForgeWeb settings
    FORGEWEB_APP_NAME = "ForgeWeb"
    FORGEWEB_PORT = 8000
    FORGEWEB_HEALTH_ENDPOINT = f"http://localhost:{FORGEWEB_PORT}/api/health"
    
    # Dashboard settings (if it exists)
    DASHBOARD_PORT = 8008
    DASHBOARD_HEALTH_ENDPOINT = f"http://localhost:{DASHBOARD_PORT}/api/health"
    
    # Config file to store integration info
    CONFIG_FILENAME = ".forgeweb_control_config.json"


class DashboardIntegration:
    """Detect and manage integration with Dashboard controller"""
    
    def __init__(self, script_dir: Path):
        self.script_dir = Path(script_dir)
        self.forgeweb_dir = self._find_forgeweb_dir()
        self.config_file = self.forgeweb_dir / ControllerConfig.CONFIG_FILENAME if self.forgeweb_dir else None
        
    def _find_forgeweb_dir(self) -> Optional[Path]:
        """Find ForgeWeb root directory"""
        # Usually: packaging/macos (or linux/windows) -> parent -> parent
        try:
            path = self.script_dir
            for _ in range(3):
                if (path / "start.sh").exists() or (path / "start.bat").exists():
                    return path
                path = path.parent
        except:
            pass
        return None
    
    def is_dashboard_installed(self) -> bool:
        """Check if Dashboard controller is already installed/running"""
        try:
            # PRIMARY: Try to find dashboard process first (more reliable)
            dashboard_process = self._find_dashboard_process()
            if dashboard_process:
                print(f"DEBUG: Found Dashboard process: {dashboard_process}")
                return True
            print(f"DEBUG: No Dashboard process found")
            
        except Exception as e:
            print(f"DEBUG: Process detection error: {e}")
        
        try:
            # SECONDARY: Check if we can connect to dashboard health endpoint
            import requests
            response = requests.get(
                ControllerConfig.DASHBOARD_HEALTH_ENDPOINT,
                timeout=5
            )
            if response.status_code == 200:
                print(f"DEBUG: Dashboard health check succeeded")
                return True
        except Exception as e:
            print(f"DEBUG: Dashboard health check failed: {e}")
        
        print(f"DEBUG: Dashboard not detected")
        return False
    
    def _find_dashboard_process(self) -> Optional[int]:
        """Find running dashboard controller process"""
        try:
            # Try to find process by name
            result = subprocess.run(
                ['pgrep', '-f', 'dashboard_control'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.stdout.strip():
                pid_str = result.stdout.strip().split('\n')[0]
                return int(pid_str)
        except Exception as e:
            print(f"DEBUG: pgrep failed: {e}")
            pass
        
        try:
            # Windows fallback
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq dashboard_control.py'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if 'dashboard_control.py' in result.stdout:
                return True
        except:
            pass
        
        return None
    
    def get_installation_mode(self) -> str:
        """
        Determine installation mode:
        - "integrated": Dashboard controller exists, add ForgeWeb controls to it
        - "standalone": Dashboard controller not found, run ForgeWeb controller standalone
        """
        if self.is_dashboard_installed():
            return "integrated"
        return "standalone"
    
    def load_config(self) -> Dict:
        """Load existing control configuration"""
        if self.config_file and self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"mode": "standalone", "services": []}
    
    def save_config(self, config: Dict) -> bool:
        """Save control configuration"""
        if not self.config_file or not self.forgeweb_dir:
            return False
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except:
            return False
    
    def add_forgeweb_service(self) -> bool:
        """Add ForgeWeb as a managed service"""
        config = self.load_config()
        
        forgeweb_service = {
            "name": ControllerConfig.FORGEWEB_APP_NAME,
            "port": ControllerConfig.FORGEWEB_PORT,
            "health_endpoint": ControllerConfig.FORGEWEB_HEALTH_ENDPOINT,
            "enabled": True
        }
        
        # Check if already in services
        existing = [s for s in config.get("services", []) if s.get("name") == "ForgeWeb"]
        if not existing:
            config.setdefault("services", []).append(forgeweb_service)
            return self.save_config(config)
        
        return True


def get_startup_script(forgeweb_dir: Path) -> Optional[Path]:
    """Get the startup script path for the platform"""
    if (forgeweb_dir / "start.sh").exists():
        return forgeweb_dir / "start.sh"
    elif (forgeweb_dir / "start.bat").exists():
        return forgeweb_dir / "start.bat"
    return None


def get_pid_file(forgeweb_dir: Path) -> Path:
    """Get the PID file path for ForgeWeb"""
    return forgeweb_dir / "forgeweb.pid"


def get_logo_path(packaging_dir: Path) -> Optional[Path]:
    """Get the best available logo for the platform"""
    # Try different logo options (Buildly icon first, then forge logo)
    candidates = [
        packaging_dir / "buildly_icon.png",
        packaging_dir / "buildly_icon.icns",
        packaging_dir / "forge-logo.png",
    ]
    
    for logo in candidates:
        if logo.exists():
            return logo
    
    return None

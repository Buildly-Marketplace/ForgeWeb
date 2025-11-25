#!/usr/bin/env python3
"""
Universal Service Discovery for Forge Controller
Discovers and monitors services running on common ports
"""

import subprocess
import socket
import json
import time
import requests
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Service:
    """Represents a discovered service"""
    name: str
    port: int
    pid: Optional[int] = None
    status: str = "unknown"  # running, stopped, starting
    script_path: Optional[Path] = None
    health_endpoint: Optional[str] = None
    browser_url: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "port": self.port,
            "pid": self.pid,
            "status": self.status,
            "script_path": str(self.script_path) if self.script_path else None,
            "health_endpoint": self.health_endpoint,
            "browser_url": self.browser_url,
        }


class ServiceDiscovery:
    """Discovers services running on common ports"""
    
    # Port ranges to scan - only development ports (not system ports)
    PORT_RANGES = [
        (8000, 9000),  # Development/app services only
    ]
    
    # Ports to explicitly ignore (system services, VPNs, etc.)
    IGNORE_PORTS = {
        80,    # HTTP
        88,    # Kerberos
        443,   # HTTPS
        445,   # SMB
        3306,  # MySQL
        5432,  # PostgreSQL
    }
    
    # Known service patterns
    SERVICE_PATTERNS = {
        "forgeweb": {
            "port": 8000,
            "health": "/api/health",
            "process_pattern": "file-api.py",
            "browser_path": "/admin/",
        },
        "dashboard": {
            "port": 8008,
            "health": "/api/health",
            "process_pattern": "main.py",
            "browser_path": "/",
        },
    }
    
    def __init__(self, search_root: Optional[Path] = None):
        """
        Initialize service discovery
        
        Args:
            search_root: Root directory to search for start scripts (default: current directory)
        """
        self.search_root = search_root or Path.cwd()
        self.services: Dict[int, Service] = {}
    
    def discover(self) -> List[Service]:
        """Discover all services and return them"""
        self.services.clear()
        
        # First check for known patterns in common locations
        self._find_services_by_pattern()
        
        # Then scan ports for services that match known patterns
        # (but only if we found the pattern, don't discover random services)
        self._scan_ports()
        
        return sorted(self.services.values(), key=lambda s: s.port)
    
    def _find_services_by_pattern(self):
        """Find services based on known patterns"""
        for service_name, pattern in self.SERVICE_PATTERNS.items():
            port = pattern.get("port")
            script = self._find_start_script(service_name)
            
            if script:
                service = Service(
                    name=service_name.capitalize(),
                    port=port,
                    script_path=script,
                    health_endpoint=f"http://localhost:{port}{pattern.get('health', '')}",
                    browser_url=f"http://localhost:{port}{pattern.get('browser_path', '/')}",
                )
                self.services[port] = service
                self._update_service_status(service)
    
    def _find_start_script(self, service_name: str) -> Optional[Path]:
        """Find start.sh or startup script for a service"""
        candidates = [
            self.search_root / "ops" / "startup.sh",  # New unified script
            self.search_root / "start.sh",
            self.search_root / f"{service_name}" / "start.sh",
            self.search_root / "packaging" / "start.sh",
            self.search_root / "ops" / "start.sh",
        ]
        
        for candidate in candidates:
            if candidate.exists() and candidate.is_file():
                return candidate
        
        return None
    
    def _scan_ports(self):
        """Scan for known services on their expected ports"""
        for service_name, pattern in self.SERVICE_PATTERNS.items():
            port = pattern.get("port")
            
            # Skip if already found
            if port in self.services:
                continue
            
            # Skip ignored ports
            if port in self.IGNORE_PORTS:
                continue
            
            # Only check the specific port for this service
            if self._is_port_open(port):
                health_ep = f"http://localhost:{port}{pattern.get('health', '')}"
                try:
                    resp = requests.get(health_ep, timeout=1)
                    if resp.status_code == 200:
                        script = self._find_start_script(service_name)
                        service = Service(
                            name=service_name.capitalize(),
                            port=port,
                            script_path=script,
                            health_endpoint=health_ep,
                            browser_url=f"http://localhost:{port}{pattern.get('browser_path', '/')}",
                        )
                        self._update_service_status(service)
                        self.services[port] = service
                except:
                    pass
    
    def _is_port_open(self, port: int) -> bool:
        """Check if port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except:
            return False
    
    def _identify_service(self, port: int) -> Optional[Service]:
        """Try to identify what service is running on a port"""
        try:
            # Try health endpoint for known services first
            for service_name, pattern in self.SERVICE_PATTERNS.items():
                if pattern.get("port") != port:
                    continue
                
                health_ep = f"http://localhost:{port}{pattern.get('health', '')}"
                try:
                    resp = requests.get(health_ep, timeout=1)
                    if resp.status_code == 200:
                        script = self._find_start_script(service_name)
                        service = Service(
                            name=service_name.capitalize(),
                            port=port,
                            script_path=script,
                            health_endpoint=health_ep,
                            browser_url=f"http://localhost:{port}{pattern.get('browser_path', '/')}",
                        )
                        self._update_service_status(service)
                        return service
                except:
                    pass
            
            # For other ports, try generic API endpoints to identify services
            service_name = self._probe_service_name(port)
            if service_name and service_name.lower() != "unknown":
                service = Service(
                    name=service_name,
                    port=port,
                    health_endpoint=f"http://localhost:{port}/api/health",
                    browser_url=f"http://localhost:{port}/",
                )
                self._update_service_status(service)
                return service
            
            return None
        except:
            return None
    
    def _probe_service_name(self, port: int) -> Optional[str]:
        """Try to determine service name from response headers/content"""
        try:
            # Check common endpoints
            endpoints = [
                "/api/health",
                "/health",
                "/",
                "/api/",
            ]
            
            for endpoint in endpoints:
                try:
                    resp = requests.get(f"http://localhost:{port}{endpoint}", timeout=1)
                    
                    # Check server header
                    server = resp.headers.get("Server", "").lower()
                    if "flask" in server or "werkzeug" in server:
                        return f"Flask App"
                    if "django" in server:
                        return f"Django App"
                    if "node" in server or "express" in server:
                        return f"Node.js App"
                    
                    # Check content type
                    content_type = resp.headers.get("Content-Type", "").lower()
                    if "application/json" in content_type:
                        try:
                            data = resp.json()
                            # Check for common API responses
                            if "service" in data:
                                return data.get("service", f"Service")
                            if "name" in data:
                                return data.get("name", f"Service")
                        except:
                            pass
                    
                    # If we got a successful response from an endpoint, it's likely a web service
                    if resp.status_code < 400:
                        return f"Web Service (:{port})"
                except:
                    continue
            
            return None
        except:
            return None
    
    def _update_service_status(self, service: Service):
        """Update service status"""
        # Check if process is running
        pid = self._find_process(service)
        if pid:
            service.pid = pid
            
            # Check health endpoint
            if service.health_endpoint:
                try:
                    resp = requests.get(service.health_endpoint, timeout=1)
                    if resp.status_code == 200:
                        service.status = "running"
                    else:
                        service.status = "starting"
                except:
                    service.status = "starting"
            else:
                service.status = "running"
        else:
            service.status = "stopped"
    
    def _find_process(self, service: Service) -> Optional[int]:
        """Find process ID for a service"""
        try:
            # Try by port
            result = subprocess.run(
                ['lsof', '-i', f':{service.port}', '-t'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.stdout.strip():
                return int(result.stdout.strip().split('\n')[0])
        except:
            pass
        
        try:
            # Try by process pattern
            for pattern_name, pattern in self.SERVICE_PATTERNS.items():
                if pattern_name.lower() in service.name.lower():
                    result = subprocess.run(
                        ['pgrep', '-f', pattern.get('process_pattern', '')],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    if result.stdout.strip():
                        return int(result.stdout.strip().split('\n')[0])
        except:
            pass
        
        return None
    
    def start_service(self, service: Service) -> bool:
        """Start a service"""
        if not service.script_path or not service.script_path.exists():
            return False
        
        try:
            subprocess.Popen(
                [str(service.script_path), 'start'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except:
            return False
    
    def stop_service(self, service: Service) -> bool:
        """Stop a service"""
        # Try by PID first (most reliable)
        if service.pid:
            try:
                import signal
                import os
                os.kill(service.pid, signal.SIGTERM)
                time.sleep(0.5)
                return True
            except Exception as e:
                print(f"Failed to kill process {service.pid}: {e}")
        
        # Try by script
        if service.script_path and service.script_path.exists():
            try:
                result = subprocess.run(
                    [str(service.script_path), 'stop'],
                    capture_output=True,
                    timeout=5
                )
                return result.returncode == 0
            except Exception as e:
                print(f"Failed to stop via script: {e}")
        
        return False
    
    def restart_service(self, service: Service) -> bool:
        """Restart a service"""
        if service.script_path and service.script_path.exists():
            try:
                subprocess.Popen(
                    [str(service.script_path), 'restart'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return True
            except:
                pass
        
        # Fallback: stop then start
        return self.stop_service(service) and self.start_service(service)
    
    def tail_logs(self, service: Service) -> Optional[str]:
        """Get recent log lines for a service"""
        log_candidates = [
            service.script_path.parent / f"{service.name.lower()}.log" if service.script_path else None,
            Path.home() / f".{service.name.lower()}.log",
            Path("/var/log") / f"{service.name.lower()}.log",
        ]
        
        for log_file in log_candidates:
            if log_file and log_file.exists():
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        return ''.join(lines[-50:])  # Last 50 lines
                except:
                    pass
        
        return None

# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""رجیستری قابلیت‌های سیستم - کشف برنامه‌ها، ابزارها و سخت‌افزار.

این ماژول اطلاعات سیستم را کشف و کش می‌کند تا AI بتواند تصمیمات بهتری بگیرد.
شامل: برنامه‌های نصب‌شده، مدیران بسته، مشخصات سخت‌افزار، و متغیرهای محیطی.
"""

from __future__ import annotations

import json
import logging
import importlib.util
import platform
import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# تلاش برای import کتابخانه‌های اختیاری
PSUTIL_AVAILABLE = importlib.util.find_spec("psutil") is not None
if not PSUTIL_AVAILABLE:
    logger.warning("psutil is unavailable - some functionality will be limited")


class SystemCapability:
    """اطلاعات یک قابلیت سیستم (برنامه، ابزار، یا ویژگی)."""
    
    def __init__(
        self,
        name: str,
        type: str,  # app, tool, hardware, feature
        path: Optional[str] = None,
        version: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ):
        self.name = name
        self.type = type
        self.path = path
        self.version = version
        self.metadata = metadata or {}
        self.discovered_at = datetime.now()
    
    def to_dict(self) -> dict[str, Any]:
        """تبدیل به دیکشنری."""
        return {
            "name": self.name,
            "type": self.type,
            "path": self.path,
            "version": self.version,
            "metadata": self.metadata,
            "discovered_at": self.discovered_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SystemCapability:
        """ساخت از دیکشنری."""
        cap = cls(
            name=data["name"],
            type=data["type"],
            path=data.get("path"),
            version=data.get("version"),
            metadata=data.get("metadata", {}),
        )
        if "discovered_at" in data:
            cap.discovered_at = datetime.fromisoformat(data["discovered_at"])
        return cap


class SystemCapabilityRegistry:
    """رجیستری مرکزی برای ذخیره و مدیریت قابلیت‌های سیستم."""
    
    def __init__(self, cache_file: Optional[Path] = None, cache_ttl_hours: int = 24):
        """
        Args:
            cache_file: مسیر فایل کش (اگر None باشد، در data ذخیره می‌شود)
            cache_ttl_hours: مدت اعتبار کش به ساعت
        """
        self.cache_file = cache_file or Path("data/system_capabilities.json")
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self.capabilities: dict[str, SystemCapability] = {}
        self.last_scan: Optional[datetime] = None
        
        # بارگذاری کش موجود
        self._load_cache()
    
    def _load_cache(self) -> None:
        """بارگذاری کش از فایل."""
        if not self.cache_file.exists():
            logger.info("Cache file not found: %s", self.cache_file)
            return
        
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.last_scan = (
                datetime.fromisoformat(data["last_scan"]) if "last_scan" in data else None
            )
            
            for cap_data in data.get("capabilities", []):
                cap = SystemCapability.from_dict(cap_data)
                self.capabilities[cap.name] = cap
            
            logger.info("Cache loaded: %d capabilities", len(self.capabilities))
        
        except Exception as e:
            logger.exception("Error loading cache: %s", e)
    
    def _save_cache(self) -> None:
        """ذخیره کش در فایل."""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "last_scan": self.last_scan.isoformat() if self.last_scan else None,
                "capabilities": [cap.to_dict() for cap in self.capabilities.values()],
            }
            
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info("Cache saved: %d capabilities", len(self.capabilities))
        
        except Exception as e:
            logger.exception("Error saving cache: %s", e)
    
    def needs_refresh(self) -> bool:
        """آیا نیاز به refresh دارد؟"""
        if not self.last_scan:
            return True
        return datetime.now() - self.last_scan > self.cache_ttl
    
    def scan_system(self, force: bool = False) -> None:
        """اسکن کامل سیستم برای کشف قابلیت‌ها.
        
        Args:
            force: اگر True باشد، حتی اگر کش معتبر است، اسکن می‌کند
        """
        if not force and not self.needs_refresh():
            logger.info("Cache is still valid - skipping scan")
            return
        
        logger.info("Starting system scan...")
        
        # کشف برنامه‌های رایج
        self._discover_common_apps()
        
        # کشف مدیران بسته
        self._discover_package_managers()
        
        # کشف اطلاعات سخت‌افزار
        self._discover_hardware()
        
        # کشف ابزارهای توسعه
        self._discover_dev_tools()
        
        self.last_scan = datetime.now()
        self._save_cache()
        
        logger.info("System scan complete: %d capabilities discovered", len(self.capabilities))
    
    def _discover_common_apps(self) -> None:
        """کشف برنامه‌های رایج نصب‌شده."""
        common_apps = [
            "notepad.exe", "calc.exe", "mspaint.exe",
            "code.exe", "chrome.exe", "firefox.exe", "msedge.exe",
            "photoshop.exe", "illustrator.exe",
            "winword.exe", "excel.exe", "powerpnt.exe",
        ]
        
        for app in common_apps:
            path = shutil.which(app)
            if path:
                self.capabilities[app] = SystemCapability(
                    name=app,
                    type="app",
                    path=path,
                )
                logger.debug("Discovered program: %s at %s", app, path)
    
    def _discover_package_managers(self) -> None:
        """کشف مدیران بسته نصب‌شده."""
        managers = {
            "winget": "winget.exe",
            "choco": "choco.exe",
            "pip": "pip.exe",
            "npm": "npm.cmd",
            "conda": "conda.exe",
        }
        
        for name, executable in managers.items():
            path = shutil.which(executable)
            if path:
                # تلاش برای دریافت نسخه
                version = self._get_tool_version(executable)
                
                self.capabilities[name] = SystemCapability(
                    name=name,
                    type="tool",
                    path=path,
                    version=version,
                    metadata={"category": "package_manager"},
                )
                logger.debug("Package manager detected: %s version %s", name, version or "unknown")
    
    def _get_tool_version(self, tool: str) -> Optional[str]:
        """دریافت نسخه یک ابزار."""
        version_commands = [
            [tool, "--version"],
            [tool, "-v"],
            [tool, "version"],
        ]
        
        for cmd in version_commands:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    # اولین خط معمولاً شامل نسخه است
                    version_line = result.stdout.split("\n")[0].strip()
                    return version_line[:100]  # محدود به 100 کاراکتر
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        return None
    
    def _discover_hardware(self) -> None:
        """کشف اطلاعات سخت‌افزار."""
        # اطلاعات پایه سیستم‌عامل
        self.capabilities["os"] = SystemCapability(
            name="operating_system",
            type="hardware",
            version=platform.version(),
            metadata={
                "system": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
                "processor": platform.processor(),
            },
        )
        
        if not PSUTIL_AVAILABLE:
            logger.warning("psutil is not available - hardware information will be limited")
            return
        
        try:
            import psutil as ps
            
            # CPU
            cpu_info = {
                "physical_cores": ps.cpu_count(logical=False),
                "logical_cores": ps.cpu_count(logical=True),
                "frequency_mhz": ps.cpu_freq().current if ps.cpu_freq() else None,
            }
            self.capabilities["cpu"] = SystemCapability(
                name="cpu",
                type="hardware",
                metadata=cpu_info,
            )
            
            # RAM
            mem = ps.virtual_memory()
            mem_info = {
                "total_gb": round(mem.total / (1024**3), 2),
                "available_gb": round(mem.available / (1024**3), 2),
            }
            self.capabilities["memory"] = SystemCapability(
                name="memory",
                type="hardware",
                metadata=mem_info,
            )
            
            # Disk
            partitions = ps.disk_partitions()
            disk_info = []
            for partition in partitions:
                try:
                    usage = ps.disk_usage(partition.mountpoint)
                    disk_info.append({
                        "device": partition.device,
                        "total_gb": round(usage.total / (1024**3), 2),
                        "free_gb": round(usage.free / (1024**3), 2),
                    })
                except PermissionError:
                    continue
            
            self.capabilities["disk"] = SystemCapability(
                name="disk",
                type="hardware",
                metadata={"partitions": disk_info},
            )
        
        except Exception as e:
            logger.exception("خطا در کشف سخت‌افزار: %s", e)
    
    def _discover_dev_tools(self) -> None:
        """کشف ابزارهای توسعه."""
        dev_tools = {
            "python": "python.exe",
            "node": "node.exe",
            "git": "git.exe",
            "java": "java.exe",
            "dotnet": "dotnet.exe",
        }
        
        for name, executable in dev_tools.items():
            path = shutil.which(executable)
            if path:
                version = self._get_tool_version(executable)
                
                self.capabilities[name] = SystemCapability(
                    name=name,
                    type="tool",
                    path=path,
                    version=version,
                    metadata={"category": "development"},
                )
                logger.debug("Development tool detected: %s version %s", name, version or "unknown")
    
    def get_capability(self, name: str) -> Optional[SystemCapability]:
        """دریافت یک قابلیت با نام."""
        return self.capabilities.get(name)
    
    def has_capability(self, name: str) -> bool:
        """بررسی وجود قابلیت."""
        return name in self.capabilities
    
    def list_capabilities(self, type_filter: Optional[str] = None) -> list[SystemCapability]:
        """لیست قابلیت‌ها با فیلتر اختیاری.
        
        Args:
            type_filter: فیلتر بر اساس نوع (app, tool, hardware, feature)
        """
        if type_filter:
            return [cap for cap in self.capabilities.values() if cap.type == type_filter]
        return list(self.capabilities.values())
    
    def get_summary(self) -> str:
        """خلاصه‌ای از قابلیت‌های سیستم برای نمایش یا تغذیه به AI."""
        apps = len([c for c in self.capabilities.values() if c.type == "app"])
        tools = len([c for c in self.capabilities.values() if c.type == "tool"])
        hardware = len([c for c in self.capabilities.values() if c.type == "hardware"])
        
        summary_parts = [
            f"System capabilities:",
            f"  - Applications: {apps}",
            f"  - Tools: {tools}",
            f"  - Hardware: {hardware}",
        ]
        
        # اضافه کردن اطلاعات کلیدی سخت‌افزار
        if "os" in self.capabilities:
            os_cap = self.capabilities["os"]
            summary_parts.append(f"  - Operating System: {os_cap.metadata.get('system')} {os_cap.version}")
        
        if "cpu" in self.capabilities:
            cpu_cap = self.capabilities["cpu"]
            cores = cpu_cap.metadata.get("logical_cores")
            summary_parts.append(f"  - CPU: {cores} cores")
        
        if "memory" in self.capabilities:
            mem_cap = self.capabilities["memory"]
            total_gb = mem_cap.metadata.get("total_gb")
            summary_parts.append(f"  - Memory: {total_gb} GB")
        
        return "\n".join(summary_parts)


__all__ = ["SystemCapability", "SystemCapabilityRegistry"]

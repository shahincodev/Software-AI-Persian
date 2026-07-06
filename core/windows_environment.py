# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
Windows Environment - درک محیط ویندوز

این ماژول مسئول شناسایی و درک محیط ویندوز است شامل:
- مسیرهای رایج ویندوز (Desktop, Downloads, Documents)
- نام‌های محلی‌شده (فارسی و انگلیسی)
- شناسایی برنامه‌های نصب شده
- کشف مسیرهای اجرایی
- اطلاعات درایوها
"""

import json
import logging
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════════════════

class AppCategory(Enum):
    """دسته‌بندی برنامه‌ها"""
    BROWSER = "browser"
    EDITOR = "editor"
    OFFICE = "office"
    MEDIA = "media"
    DEV = "dev"
    SYSTEM = "system"
    GAME = "game"
    UTILITY = "utility"
    UNKNOWN = "unknown"


# ═══════════════════════════════════════════════════════════════════════════════
# Data Classes
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AppInfo:
    """اطلاعات یک برنامه"""
    name: str
    path: str
    version: Optional[str] = None
    publisher: Optional[str] = None
    category: AppCategory = AppCategory.UNKNOWN


@dataclass
class DriveInfo:
    """اطلاعات یک درایو"""
    letter: str
    label: str
    total_gb: float
    free_gb: float
    filesystem: str


@dataclass
class WindowsLocation:
    """اطلاعات یک مکان ویندوز"""
    name: str
    path: Path
    exists: bool
    item_count: Optional[int] = None


# ═══════════════════════════════════════════════════════════════════════════════
# Localized Names
# ═══════════════════════════════════════════════════════════════════════════════

LOCALIZED_NAMES = {
    "desktop": {
        "en": ["Desktop", "desktop"],
        "fa": ["دسکتاپ", "رو‌میزی"],
    },
    "downloads": {
        "en": ["Downloads", "download"],
        "fa": ["دانلودها", "بارگذاری‌ها", "دانلود"],
    },
    "documents": {
        "en": ["Documents", "document"],
        "fa": ["مستندات", "اسناد", "سند"],
    },
    "pictures": {
        "en": ["Pictures", "picture", "photos"],
        "fa": ["تصاویر", "عکس‌ها", "عکس"],
    },
    "music": {
        "en": ["Music", "music"],
        "fa": ["موسیقی", "آهنگ‌ها", "آهنگ"],
    },
    "videos": {
        "en": ["Videos", "video", "movies"],
        "fa": ["ویدیوها", "فیلم‌ها", "فیلم", "ویدیو"],
    },
    "favorites": {
        "en": ["Favorites", "favorite"],
        "fa": ["علاقه‌مندی‌ها", "برگزیده‌ها"],
    },
    "templates": {
        "en": ["Templates", "template"],
        "fa": ["قالب‌ها", "الگوها"],
    },
}

KNOWN_APPS = {
    "chrome": AppInfo(name="Google Chrome", path="", category=AppCategory.BROWSER),
    "firefox": AppInfo(name="Mozilla Firefox", path="", category=AppCategory.BROWSER),
    "edge": AppInfo(name="Microsoft Edge", path="", category=AppCategory.BROWSER),
    "msedge": AppInfo(name="Microsoft Edge", path="", category=AppCategory.BROWSER),
    "code": AppInfo(name="Visual Studio Code", path="", category=AppCategory.EDITOR),
    "vscode": AppInfo(name="Visual Studio Code", path="", category=AppCategory.EDITOR),
    "notepad": AppInfo(name="Notepad", path="", category=AppCategory.EDITOR),
    "notepad++": AppInfo(name="Notepad++", path="", category=AppCategory.EDITOR),
    "wordpad": AppInfo(name="WordPad", path="", category=AppCategory.EDITOR),
    "calc": AppInfo(name="Calculator", path="", category=AppCategory.UTILITY),
    "calculator": AppInfo(name="Calculator", path="", category=AppCategory.UTILITY),
    "mspaint": AppInfo(name="Paint", path="", category=AppCategory.MEDIA),
    "paint": AppInfo(name="Paint", path="", category=AppCategory.MEDIA),
    "explorer": AppInfo(name="File Explorer", path="", category=AppCategory.SYSTEM),
    "cmd": AppInfo(name="Command Prompt", path="", category=AppCategory.SYSTEM),
    "powershell": AppInfo(name="PowerShell", path="", category=AppCategory.SYSTEM),
    "terminal": AppInfo(name="Windows Terminal", path="", category=AppCategory.SYSTEM),
    "winword": AppInfo(name="Microsoft Word", path="", category=AppCategory.OFFICE),
    "excel": AppInfo(name="Microsoft Excel", path="", category=AppCategory.OFFICE),
    "powerpnt": AppInfo(name="Microsoft PowerPoint", path="", category=AppCategory.OFFICE),
    "python": AppInfo(name="Python", path="", category=AppCategory.DEV),
    "python3": AppInfo(name="Python 3", path="", category=AppCategory.DEV),
    "node": AppInfo(name="Node.js", path="", category=AppCategory.DEV),
    "git": AppInfo(name="Git", path="", category=AppCategory.DEV),
    "java": AppInfo(name="Java", path="", category=AppCategory.DEV),
    "dotnet": AppInfo(name=".NET", path="", category=AppCategory.DEV),
    "docker": AppInfo(name="Docker", path="", category=AppCategory.DEV),
}


# ═══════════════════════════════════════════════════════════════════════════════
# Path Resolver
# ═══════════════════════════════════════════════════════════════════════════════

class PathResolver:
    """
    مسیریاب متمرکز ویندوز

    تبدیل نام‌های طبیعی به مسیرهای فایل سیستم
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._user_profile = Path(os.environ.get("USERPROFILE", Path.home()))
        self._drives_cache: Optional[List[DriveInfo]] = None

    def resolve(self, name: str) -> Optional[Path]:
        """
        تبدیل نام به مسیر فایل

        مثال‌ها:
        - "Desktop" -> C:\\Users\\<user>\\Desktop
        - "Downloads" -> C:\\Users\\<user>\\Downloads
        - "D drive" -> D:\\
        - "D:" -> D:\\
        - "C:\\Projects" -> C:\\Projects
        - "دسکتاپ" -> C:\\Users\\<user>\\Desktop
        """
        name = name.strip()
        if not name:
            return None

        # Check for absolute path
        if os.path.isabs(name):
            path = Path(name)
            return path if path.exists() else None

        # Check for drive letter
        if len(name) == 2 and name[1] == ":":
            letter = name[0].upper()
            drive = Path(f"{letter}:\\")
            return drive if drive.exists() else None

        if len(name) > 2 and name[1] == ":" and name[2] == "\\":
            path = Path(name)
            return path if path.exists() else None

        # Check for "X drive" pattern
        name_lower = name.lower()
        if name_lower.endswith(" drive"):
            drive_letter = name_lower[0]
            if drive_letter.isalpha():
                drive = Path(f"{drive_letter.upper()}:\\")
                return drive if drive.exists() else None

        # Check localized folder names
        for folder_key, names in LOCALIZED_NAMES.items():
            all_names = names["en"] + names["fa"]
            if name in all_names or name_lower in [n.lower() for n in all_names]:
                folder_path = self._get_user_folder(folder_key)
                if folder_path and folder_path.exists():
                    return folder_path

        # Try as relative path in user profile
        relative = self._user_profile / name
        if relative.exists():
            return relative

        return None

    def resolve_app(self, name: str) -> Optional[str]:
        """
        تبدیل نام برنامه به مسیر اجرایی

        مثال‌ها:
        - "Chrome" -> C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe
        - "VS Code" -> C:\\Users\\<user>\\AppData\\Local\\Programs\\...\\code.exe
        - "notepad" -> C:\\Windows\\System32\\notepad.exe
        """
        name_lower = name.lower().strip()

        # Check known apps
        if name_lower in KNOWN_APPS:
            known = KNOWN_APPS[name_lower]
            if known.path and Path(known.path).exists():
                return known.path

        # Try shutil.which
        result = shutil.which(name)
        if result:
            return result

        result = shutil.which(f"{name}.exe")
        if result:
            return result

        # Search in common locations
        search_dirs = []
        program_files = os.environ.get("PROGRAMFILES", "C:\\Program Files")
        program_files_x86 = os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)")
        local_app_data = os.environ.get("LOCALAPPDATA", str(self._user_profile / "AppData" / "Local"))

        search_dirs.extend([
            Path(program_files),
            Path(program_files_x86),
            Path(local_app_data) / "Programs",
            self._user_profile / "AppData" / "Local" / "Programs",
        ])

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            try:
                for item in search_dir.rglob("*.exe"):
                    if name_lower in item.stem.lower():
                        return str(item)
            except PermissionError:
                continue

        return None

    def get_user_folders(self) -> Dict[str, WindowsLocation]:
        """دریافت مکان‌های کاربر"""
        folders = {}
        for folder_key in LOCALIZED_NAMES.keys():
            path = self._get_user_folder(folder_key)
            if path:
                exists = path.exists()
                item_count = None
                if exists:
                    try:
                        item_count = len(list(path.iterdir()))
                    except PermissionError:
                        pass
                folders[folder_key] = WindowsLocation(
                    name=folder_key,
                    path=path,
                    exists=exists,
                    item_count=item_count,
                )
        return folders

    def _get_user_folder(self, folder_key: str) -> Optional[Path]:
        """دریافت مسیر یک پوشه کاربر"""
        folder_map = {
            "desktop": "Desktop",
            "downloads": "Downloads",
            "documents": "Documents",
            "pictures": "Pictures",
            "music": "Music",
            "videos": "Videos",
            "favorites": "Favorites",
            "templates": "Templates",
        }
        folder_name = folder_map.get(folder_key)
        if folder_name:
            return self._user_profile / folder_name
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# App Detector
# ═══════════════════════════════════════════════════════════════════════════════

class AppDetector:
    """
    شناسایی برنامه‌های نصب شده

    شناسایی از طریق:
    - رجیستری ویندوز
    - منوی Start
    - متغیر PATH
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._cache: Optional[List[AppInfo]] = None
        self._cache_time: Optional[datetime] = None
        self._cache_ttl_hours = 24

    def find_app(self, name: str) -> Optional[AppInfo]:
        """پیدا کردن یک برنامه با نام"""
        apps = self.get_all_apps()
        name_lower = name.lower().strip()

        for app in apps:
            if name_lower in app.name.lower() or name_lower == app.name.lower():
                return app

        # Try partial match
        for app in apps:
            if name_lower in app.name.lower():
                return app

        return None

    def get_all_apps(self) -> List[AppInfo]:
        """دریافت لیست تمام برنامه‌ها"""
        if self._cache and self._cache_time:
            elapsed = datetime.now() - self._cache_time
            if elapsed.total_seconds() < self._cache_ttl_hours * 3600:
                return self._cache

        apps = []
        apps.extend(self._scan_registry())
        apps.extend(self._scan_path())
        apps = self._deduplicate(apps)

        self._cache = apps
        self._cache_time = datetime.now()

        self.logger.info("Identified %d programs", len(apps))
        return apps

    def _scan_registry(self) -> List[AppInfo]:
        """اسکن رجیستری ویندوز"""
        apps = []
        try:
            import winreg
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            try:
                                name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                install_loc = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                version = None
                                publisher = None
                                try:
                                    version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                                except FileNotFoundError:
                                    pass
                                try:
                                    publisher = winreg.QueryValueEx(subkey, "Publisher")[0]
                                except FileNotFoundError:
                                    pass

                                if install_loc and Path(install_loc).exists():
                                    apps.append(AppInfo(
                                        name=name,
                                        path=install_loc,
                                        version=version,
                                        publisher=publisher,
                                        category=AppCategory.UNKNOWN,
                                    ))
                            except FileNotFoundError:
                                pass
                        i += 1
                    except OSError:
                        break
        except ImportError:
            self.logger.warning("winreg not available, skipping registry scan")
        except Exception as e:
            self.logger.warning("Registry scan failed: %s", e)

        return apps

    def _scan_path(self) -> List[AppInfo]:
        """اسکن متغیر PATH"""
        apps = []
        path_dirs = os.environ.get("PATH", "").split(os.pathsep)

        for path_dir in path_dirs:
            path = Path(path_dir)
            if not path.exists():
                continue
            try:
                for exe in path.glob("*.exe"):
                    if exe.stem.lower() in KNOWN_APPS:
                        known = KNOWN_APPS[exe.stem.lower()]
                        apps.append(AppInfo(
                            name=known.name,
                            path=str(exe),
                            category=known.category,
                        ))
            except PermissionError:
                continue

        return apps

    def _deduplicate(self, apps: List[AppInfo]) -> List[AppInfo]:
        """حذف برنامه‌های تکراری"""
        seen = set()
        unique = []
        for app in apps:
            key = app.name.lower()
            if key not in seen:
                seen.add(key)
                unique.append(app)
        return unique


# ═══════════════════════════════════════════════════════════════════════════════
# Drive Enumerator
# ═══════════════════════════════════════════════════════════════════════════════

class DriveEnumerator:
    """
    شناسایی درایوهای موجود

    اطلاعات هر درایو شامل:
    - حرف درایو
    - برچسب
    - فضای کل
    - فضای خالی
    - فایل‌سیستم
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_drives(self) -> List[DriveInfo]:
        """دریافت لیست درایوها"""
        drives = []
        for letter in "CDEFGH":
            drive_path = Path(f"{letter}:\\")
            if drive_path.exists():
                try:
                    usage = shutil.disk_usage(f"{letter}:\\")
                    total_gb = usage.total / (1024 ** 3)
                    free_gb = usage.free / (1024 ** 3)

                    label = self._get_drive_label(letter)
                    filesystem = self._get_filesystem(letter)

                    drives.append(DriveInfo(
                        letter=f"{letter}:",
                        label=label,
                        total_gb=round(total_gb, 1),
                        free_gb=round(free_gb, 1),
                        filesystem=filesystem,
                    ))
                except Exception as e:
                    self.logger.warning("Failed to get info for drive %s: %s", letter, e)

        return drives

    def _get_drive_label(self, letter: str) -> str:
        """دریافت برچسب درایو"""
        try:
            import ctypes
            buffer = ctypes.create_unicode_buffer(256)
            ctypes.windll.kernel32.GetVolumeInformationW(
                f"{letter}:\\", buffer, 256, None, None, None, None, 0
            )
            return buffer.value or f"Drive {letter}"
        except Exception:
            return f"Drive {letter}"

    def _get_filesystem(self, letter: str) -> str:
        """دریافت فایل‌سیستم درایو"""
        try:
            import ctypes
            buffer = ctypes.create_unicode_buffer(256)
            ctypes.windll.kernel32.GetVolumeInformationW(
                f"{letter}:\\", None, 0, None, None, None, buffer, 256
            )
            return buffer.value or "Unknown"
        except Exception:
            return "Unknown"


# ═══════════════════════════════════════════════════════════════════════════════
# Environment Context
# ═══════════════════════════════════════════════════════════════════════════════

class EnvironmentContext:
    """
    زمینه محیط برای تزریق به پرامپت AI

    اطلاعات محیط شامل:
    - سیستم‌عامل
    - درایوها
    - مکان‌های کاربر
    - برنامه‌های نصب شده
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.path_resolver = PathResolver()
        self.app_detector = AppDetector()
        self.drive_enumerator = DriveEnumerator()

    def get_context_summary(self) -> str:
        """تولید خلاصه زمینه برای تزریق به پرامپت AI"""
        sections = []

        # System info
        import platform
        system = platform.system()
        release = platform.release()
        version = platform.version()
        sections.append(f"System: {system} {release} ({version})")

        # User
        user_profile = os.environ.get("USERPROFILE", "")
        username = os.path.basename(user_profile) if user_profile else "Unknown"
        sections.append(f"User: {username}")

        # Drives
        drives = self.drive_enumerator.get_drives()
        if drives:
            drive_strs = [f"{d.letter} ({d.free_gb}GB free/{d.total_gb}GB)" for d in drives]
            sections.append(f"Drives: {', '.join(drive_strs)}")

        # User folders
        folders = self.path_resolver.get_user_folders()
        folder_strs = []
        for key, loc in folders.items():
            if loc.exists:
                folder_strs.append(f"{key}={loc.path}")
        if folder_strs:
            sections.append(f"Folders: {', '.join(folder_strs)}")

        # Installed apps
        apps = self.app_detector.get_all_apps()
        if apps:
            app_names = [a.name for a in apps[:15]]
            sections.append(f"Installed Apps: {', '.join(app_names)}")

        return "\n".join(sections)

    def get_quick_paths(self) -> Dict[str, str]:
        """دریافت مسیرهای رایج برای مرجع AI"""
        paths = {}
        folders = self.path_resolver.get_user_folders()
        for key, loc in folders.items():
            if loc.exists:
                paths[key] = str(loc.path)
        return paths


# ═══════════════════════════════════════════════════════════════════════════════
# Windows Environment (Main Class)
# ═══════════════════════════════════════════════════════════════════════════════

class WindowsEnvironment:
    """
    کلاس اصلی درک محیط ویندوز

    ترکیب تمامی ماژول‌های محیطی در یک رابط یکپارچه
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.path_resolver = PathResolver()
        self.app_detector = AppDetector()
        self.drive_enumerator = DriveEnumerator()
        self.context = EnvironmentContext()

    def resolve_path(self, name: str) -> Optional[Path]:
        """تبدیل نام به مسیر"""
        return self.path_resolver.resolve(name)

    def resolve_app(self, name: str) -> Optional[str]:
        """تبدیل نام برنامه به مسیر اجرایی"""
        return self.path_resolver.resolve_app(name)

    def get_user_folders(self) -> Dict[str, WindowsLocation]:
        """دریافت مکان‌های کاربر"""
        return self.path_resolver.get_user_folders()

    def get_drives(self) -> List[DriveInfo]:
        """دریافت درایوها"""
        return self.drive_enumerator.get_drives()

    def find_app(self, name: str) -> Optional[AppInfo]:
        """پیدا کردن برنامه"""
        return self.app_detector.find_app(name)

    def get_all_apps(self) -> List[AppInfo]:
        """دریافت تمام برنامه‌ها"""
        return self.app_detector.get_all_apps()

    def get_context_summary(self) -> str:
        """تولید خلاصه زمینه"""
        return self.context.get_context_summary()

    def get_quick_paths(self) -> Dict[str, str]:
        """دریافت مسیرهای رایج"""
        return self.context.get_quick_paths()

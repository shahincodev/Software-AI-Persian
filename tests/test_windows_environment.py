# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
Tests for Windows Environment (Phase 7)

Tests cover:
- PathResolver: localized names, drive resolution, app resolution
- AppDetector: app finding, registry scan
- DriveEnumerator: drive discovery
- EnvironmentContext: context summary generation
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from core.windows_environment import (
    WindowsEnvironment,
    PathResolver,
    AppDetector,
    DriveEnumerator,
    EnvironmentContext,
    AppInfo,
    DriveInfo,
    WindowsLocation,
    AppCategory,
    LOCALIZED_NAMES,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def path_resolver():
    """Create a PathResolver instance."""
    return PathResolver()


@pytest.fixture
def app_detector():
    """Create an AppDetector instance."""
    return AppDetector()


@pytest.fixture
def drive_enumerator():
    """Create a DriveEnumerator instance."""
    return DriveEnumerator()


@pytest.fixture
def windows_env():
    """Create a WindowsEnvironment instance."""
    return WindowsEnvironment()


# ═══════════════════════════════════════════════════════════════════════════════
# PathResolver Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestPathResolver:
    """Tests for PathResolver."""

    def test_resolve_desktop_english(self, path_resolver):
        """Test resolving 'Desktop' to the user's Desktop folder."""
        result = path_resolver.resolve("Desktop")
        assert result is not None
        assert result.exists()
        assert "Desktop" in str(result)

    def test_resolve_downloads_english(self, path_resolver):
        """Test resolving 'Downloads' to the user's Downloads folder."""
        result = path_resolver.resolve("Downloads")
        assert result is not None
        assert result.exists()
        assert "Downloads" in str(result)

    def test_resolve_documents_english(self, path_resolver):
        """Test resolving 'Documents' to the user's Documents folder."""
        result = path_resolver.resolve("Documents")
        assert result is not None
        assert result.exists()
        assert "Documents" in str(result)

    def test_resolve_drive_letter(self, path_resolver):
        """Test resolving drive letters like 'C:' or 'D:'."""
        result = path_resolver.resolve("C:")
        assert result is not None
        assert result.exists()
        assert str(result) == "C:\\"

    def test_resolve_drive_with_space(self, path_resolver):
        """Test resolving 'C drive' pattern."""
        result = path_resolver.resolve("C drive")
        assert result is not None
        assert result.exists()

    def test_resolve_absolute_path(self, path_resolver):
        """Test resolving absolute paths."""
        result = path_resolver.resolve("C:\\Windows")
        assert result is not None
        assert result.exists()

    def test_resolve_nonexistent_returns_none(self, path_resolver):
        """Test that non-existent paths return None."""
        result = path_resolver.resolve("NonExistentFolder12345")
        assert result is None

    def test_resolve_empty_string(self, path_resolver):
        """Test that empty string returns None."""
        result = path_resolver.resolve("")
        assert result is None

    def test_get_user_folders(self, path_resolver):
        """Test getting user folders."""
        folders = path_resolver.get_user_folders()
        assert "desktop" in folders
        assert "downloads" in folders
        assert "documents" in folders
        for key, loc in folders.items():
            assert isinstance(loc, WindowsLocation)


# ═══════════════════════════════════════════════════════════════════════════════
# Localized Names Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestLocalizedNames:
    """Tests for localized folder names."""

    def test_localized_names_has_all_keys(self):
        """Test that all expected folder keys exist."""
        expected_keys = ["desktop", "downloads", "documents", "pictures", "music", "videos"]
        for key in expected_keys:
            assert key in LOCALIZED_NAMES

    def test_localized_names_has_english(self):
        """Test that English names are defined."""
        for key, names in LOCALIZED_NAMES.items():
            assert "en" in names
            assert len(names["en"]) > 0

    def test_localized_names_has_persian(self):
        """Test that Persian names are defined."""
        for key, names in LOCALIZED_NAMES.items():
            assert "fa" in names
            assert len(names["fa"]) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# AppDetector Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestAppDetector:
    """Tests for AppDetector."""

    def test_get_all_apps_returns_list(self, app_detector):
        """Test that get_all_apps returns a list."""
        apps = app_detector.get_all_apps()
        assert isinstance(apps, list)

    def test_find_app_notepad(self, app_detector):
        """Test finding Notepad."""
        result = app_detector.find_app("notepad")
        if result:
            assert isinstance(result, AppInfo)
            assert "notepad" in result.name.lower() or "Notepad" in result.name

    def test_find_app_nonexistent(self, app_detector):
        """Test finding a non-existent app returns None."""
        result = app_detector.find_app("NonExistentApp12345XYZ")
        assert result is None

    def test_deduplication(self, app_detector):
        """Test that apps are deduplicated."""
        apps = app_detector.get_all_apps()
        names = [a.name.lower() for a in apps]
        assert len(names) == len(set(names))


# ═══════════════════════════════════════════════════════════════════════════════
# DriveEnumerator Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestDriveEnumerator:
    """Tests for DriveEnumerator."""

    def test_get_drives_returns_list(self, drive_enumerator):
        """Test that get_drives returns a list."""
        drives = drive_enumerator.get_drives()
        assert isinstance(drives, list)

    def test_drives_have_required_fields(self, drive_enumerator):
        """Test that drives have all required fields."""
        drives = drive_enumerator.get_drives()
        for drive in drives:
            assert isinstance(drive, DriveInfo)
            assert drive.letter
            assert drive.total_gb > 0
            assert drive.free_gb >= 0

    def test_c_drive_exists(self, drive_enumerator):
        """Test that C: drive exists."""
        drives = drive_enumerator.get_drives()
        c_drives = [d for d in drives if d.letter == "C:"]
        assert len(c_drives) == 1


# ═══════════════════════════════════════════════════════════════════════════════
# EnvironmentContext Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestEnvironmentContext:
    """Tests for EnvironmentContext."""

    def test_get_context_summary_returns_string(self):
        """Test that get_context_summary returns a string."""
        ctx = EnvironmentContext()
        summary = ctx.get_context_summary()
        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_context_summary_contains_system_info(self):
        """Test that context summary contains system info."""
        ctx = EnvironmentContext()
        summary = ctx.get_context_summary()
        assert "System:" in summary

    def test_context_summary_contains_drives(self):
        """Test that context summary contains drive info."""
        ctx = EnvironmentContext()
        summary = ctx.get_context_summary()
        assert "Drives:" in summary

    def test_get_quick_paths_returns_dict(self):
        """Test that get_quick_paths returns a dict."""
        ctx = EnvironmentContext()
        paths = ctx.get_quick_paths()
        assert isinstance(paths, dict)


# ═══════════════════════════════════════════════════════════════════════════════
# WindowsEnvironment Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestWindowsEnvironment:
    """Tests for WindowsEnvironment (main class)."""

    def test_resolve_path(self, windows_env):
        """Test resolving a path."""
        result = windows_env.resolve_path("Desktop")
        assert result is not None

    def test_resolve_app(self, windows_env):
        """Test resolving an app."""
        result = windows_env.resolve_app("notepad")
        if result:
            assert isinstance(result, str)

    def test_get_user_folders(self, windows_env):
        """Test getting user folders."""
        folders = windows_env.get_user_folders()
        assert isinstance(folders, dict)
        assert "desktop" in folders

    def test_get_drives(self, windows_env):
        """Test getting drives."""
        drives = windows_env.get_drives()
        assert isinstance(drives, list)
        assert len(drives) > 0

    def test_get_context_summary(self, windows_env):
        """Test getting context summary."""
        summary = windows_env.get_context_summary()
        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_get_quick_paths(self, windows_env):
        """Test getting quick paths."""
        paths = windows_env.get_quick_paths()
        assert isinstance(paths, dict)


# ═══════════════════════════════════════════════════════════════════════════════
# Data Model Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestDataModels:
    """Tests for data classes."""

    def test_app_info_creation(self):
        """Test creating an AppInfo."""
        app = AppInfo(name="Test", path="/test", category=AppCategory.BROWSER)
        assert app.name == "Test"
        assert app.category == AppCategory.BROWSER

    def test_drive_info_creation(self):
        """Test creating a DriveInfo."""
        drive = DriveInfo(
            letter="C:", label="Windows",
            total_gb=256.0, free_gb=100.0, filesystem="NTFS"
        )
        assert drive.letter == "C:"
        assert drive.free_gb == 100.0

    def test_windows_location_creation(self):
        """Test creating a WindowsLocation."""
        loc = WindowsLocation(
            name="desktop",
            path=Path("C:\\Users\\test\\Desktop"),
            exists=True,
            item_count=10,
        )
        assert loc.name == "desktop"
        assert loc.exists is True

    def test_app_category_enum(self):
        """Test AppCategory enum values."""
        assert AppCategory.BROWSER.value == "browser"
        assert AppCategory.EDITOR.value == "editor"
        assert AppCategory.DEV.value == "dev"

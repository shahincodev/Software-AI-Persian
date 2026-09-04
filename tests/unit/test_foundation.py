"""Smoke tests for the repository foundation."""

import software_ai


def test_package_exposes_version() -> None:
    assert software_ai.__version__ == "0.1.0"

# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
ماژول سیستم حافظه - Backward Compatible Wrapper

تذکر: این ماژول برای سازگاری با عقب حفظ شده است.
تمامی قابلیت‌ها به core.memory_integrator منتقل شده‌اند.

مثال جدید:
    >>> from core.memory_integrator import MemoryManager, MemoryIntegrator
"""

import warnings
from .memory_integrator import (
    MemoryItem,
    ShortTermMemory,
    LongTermMemory,
    MemoryManager,
)

warnings.warn(
    "core.memory_system is deprecated. Use core.memory_integrator.MemoryManager instead.",
    DeprecationWarning,
    stacklevel=2,
)

# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
Backward-compatible re-export wrapper for IntelligentSystemAgent.

Functionality has been consolidated:
  - SystemActionParser  → core.intent_analyzer
  - IntelligentSystemAgent process_request/create_action → core.action_controller.ActionController

This module re-exports the public API with a DeprecationWarning.
"""

from __future__ import annotations

import logging
import warnings
from typing import Optional

from core.action_controller import ActionController
from core.execution_manager import ExecutionManager
from core.system_action_parser import SystemActionParser
from core.system_capabilities import SystemCapabilityRegistry

logger = logging.getLogger(__name__)


class IntelligentSystemAgent:
    """Backward-compatible wrapper — delegates to ActionController.
    
    Deprecated: Use ActionController directly for action execution
    and SystemActionParser from core.intent_analyzer for parsing.
    """

    def __init__(self, dry_run: bool = False, action_controller: Optional[ActionController] = None):
        warnings.warn(
            "IntelligentSystemAgent is deprecated. Use ActionController directly.",
            DeprecationWarning, stacklevel=2,
        )
        self.dry_run = dry_run
        self.registry = SystemCapabilityRegistry()
        self.parser = SystemActionParser(self.registry)
        self.executor = ExecutionManager(dry_run=dry_run)
        self.action_controller = action_controller or ActionController(dry_run=dry_run)

        if self.registry.needs_refresh():
            logger.info("Scanning system for capabilities...")
            self.registry.scan_system()

    async def process_request(self, user_request: str) -> str:
        """Delegates to ActionController.process_request."""
        return await self.action_controller.process_request(user_request)

    def get_system_summary(self) -> str:
        """Get system summary from capability registry."""
        return self.registry.get_summary()


__all__ = ["IntelligentSystemAgent", "SystemActionParser"]

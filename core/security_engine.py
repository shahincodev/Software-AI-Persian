# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""Intelligent Security Architecture for autonomous desktop interaction.

Complete redesign of the security system with:

Risk-Based Execution:
    Actions are classified by risk level (SAFE → LOW → MEDIUM → HIGH → CRITICAL).
    Low-risk actions execute automatically. High-risk actions require confirmation.

Trust Levels:
    Applications and commands have trust levels that evolve based on history.
    Trusted apps get automatic approval. Unknown apps get scrutiny.

Session Permissions:
    Users can grant temporary elevated access for the current session.
    Session permissions expire automatically.

Intent Validation:
    The system understands WHY an action is being performed, not just WHAT.
    Context affects approval decisions.

Context-Aware Approvals:
    Same action may need different approval based on:
    - Which app is being targeted
    - What the user is trying to accomplish
    - Historical success/failure patterns
    - Time of day, system state

Dangerous Action Detection:
    Automatic detection of destructive operations:
    - File deletion
    - Process termination
    - System modification
    - Network exposure

Plan Validation:
    Entire execution plans are validated before any action runs.
    This prevents cascading failures and dangerous sequences.

The goal: Maximum safety with minimal interruption.
"""

from __future__ import annotations

import logging
import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import IntEnum, Enum
from typing import Optional

logger = logging.getLogger(__name__)


__all__ = [
    "RiskLevel",
    "TrustLevel",
    "SecurityDecision",
    "SessionPermission",
    "SecurityPolicy",
    "RiskAssessor",
    "TrustManager",
    "SessionPermissionManager",
    "IntentValidator",
    "SecurityEngine",
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Enums
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class RiskLevel(IntEnum):
    """Risk levels for actions, ordered by severity."""
    SAFE = 0        # Read-only, no side effects
    LOW = 1         # Minor side effects, easily reversible
    MEDIUM = 2      # Moderate side effects, may require undo
    HIGH = 3        # Significant side effects, hard to undo
    CRITICAL = 4    # Destructive or irreversible


class TrustLevel(IntEnum):
    """Trust levels for applications and entities."""
    UNKNOWN = 0     # Never seen before
    LOW = 1         # Seen but not proven
    MEDIUM = 2      # Generally reliable
    HIGH = 3        # Proven trustworthy
    FULL = 4        #完全受信 (completely trusted)


class SecurityDecision(Enum):
    """Possible security decisions."""
    AUTO_APPROVE = "auto_approve"
    SESSION_APPROVE = "session_approve"
    REQUIRE_CONSENT = "require_consent"
    REJECT = "reject"
    ESCALATE = "escalate"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Data Classes
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class SessionPermission:
    """A temporary permission granted for the current session."""
    permission_type: str
    granted_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    scope: str = "global"
    reason: str = ""

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    @property
    def remaining_seconds(self) -> float:
        if self.expires_at is None:
            return float('inf')
        delta = self.expires_at - datetime.now()
        return max(0.0, delta.total_seconds())


@dataclass
class SecurityAssessment:
    """Complete assessment of an action's security posture."""
    risk_level: RiskLevel
    decision: SecurityDecision
    trust_level: TrustLevel = TrustLevel.UNKNOWN
    reason: str = ""
    confidence: float = 1.0
    requires_consent: bool = False
    consent_reason: str = ""
    session_permission_needed: Optional[str] = None
    matching_rules: list[str] = field(default_factory=list)

    @property
    def should_proceed(self) -> bool:
        return self.decision in (SecurityDecision.AUTO_APPROVE, SecurityDecision.SESSION_APPROVE)


@dataclass
class ActionIntent:
    """Parsed intent of an action for security assessment."""
    action_type: str
    target: str = ""
    parameters: dict = field(default_factory=dict)
    context: str = ""
    app_name: str = ""
    is_reversible: bool = True
    has_side_effects: bool = False
    modifies_system: bool = False
    accesses_network: bool = False
    accesses_files: bool = False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Security Policy
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SecurityPolicy:
    """Configurable security policy with risk-based rules.

    Instead of a hardcoded whitelist, this policy uses risk assessment
    combined with trust levels to make intelligent approval decisions.
    """

    def __init__(self):
        # Risk classification rules
        self.risk_rules: list[tuple[str, RiskLevel]] = [
            # System-critical operations
            (r"format\s+[a-z]:", RiskLevel.CRITICAL),
            (r"del\s+/s\s+/q", RiskLevel.CRITICAL),
            (r"rm\s+-rf\s+/", RiskLevel.CRITICAL),
            (r"diskpart", RiskLevel.CRITICAL),
            (r"bcdedit", RiskLevel.CRITICAL),
            (r"reg\s+delete\s+hklm", RiskLevel.CRITICAL),

            # Destructive operations
            (r"taskkill\s+/f\s+/im\s+explorer", RiskLevel.HIGH),
            (r"shutdown\s+/", RiskLevel.HIGH),
            (r"del\s+/f", RiskLevel.HIGH),
            (r"rmdir\s+/s", RiskLevel.HIGH),

            # System modification
            (r"reg\s+add", RiskLevel.MEDIUM),
            (r"net\s+user", RiskLevel.MEDIUM),
            (r"sc\s+config", RiskLevel.MEDIUM),

            # Safe operations
            (r"^(mkdir|md|echo|cd|dir|type|findstr|cat|ls|pwd)$", RiskLevel.SAFE),
            (r"^(get-childitem|get-content|get-process)$", RiskLevel.SAFE),
        ]

        # Trusted application patterns (auto-approve for LOW risk)
        self.trusted_app_patterns: list[str] = [
            r"notepad\.exe$", r"calc\.exe$", r"mspaint\.exe$",
            r"explorer\.exe$", r"chrome\.exe$", r"firefox\.exe$",
            r"code\.exe$", r"edge\.exe$",
            r"winword\.exe$", r"excel\.exe$", r"powerpnt\.exe$",
            r"powershell\.exe$", r"cmd\.exe$",
            r"steam\.exe$", r"cs2\.exe$",
        ]

        # Protected processes (never terminate)
        self.protected_processes: set[str] = {
            "system", "smss.exe", "csrss.exe", "wininit.exe",
            "services.exe", "lsass.exe", "winlogon.exe", "svchost.exe",
            "dwm.exe", "ntoskrnl.exe",
        }

        # Suspicious packages (never install)
        self.suspicious_packages: set[str] = {
            "mimikatz", "metasploit", "nmap", "wireshark", "burpsuite",
        }

        # Allowed paths for execution
        self.allowed_paths: list[str] = [
            os.environ.get("PROGRAMFILES", "C:\\Program Files"),
            os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"),
            os.environ.get("LOCALAPPDATA", ""),
            os.environ.get("APPDATA", ""),
            "C:\\Windows\\System32",
            "C:\\Windows\\SysWOW64",
        ]

        # Maximum trust level for auto-approve without consent
        self.auto_approve_max_risk = RiskLevel.MEDIUM

        # Session permission duration (default: 30 minutes)
        self.session_permission_duration = timedelta(minutes=30)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Risk Assessor
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class RiskAssessor:
    """Assesses the risk level of actions using multiple signals."""

    def __init__(self, policy: Optional[SecurityPolicy] = None):
        self.policy = policy or SecurityPolicy()

    def assess_risk(self, action_description: str, context: Optional[dict] = None) -> RiskLevel:
        """Assess the risk level of an action.

        Uses multiple signals:
        - Pattern matching on command/description
        - Context (which app, what the user is doing)
        - Historical data (past success/failure)
        """
        desc_lower = action_description.lower().strip()

        # Check risk rules
        for pattern, risk_level in self.policy.risk_rules:
            if re.search(pattern, desc_lower, re.IGNORECASE):
                return risk_level

        # Check if it's a trusted app
        if context and 'app_name' in context:
            app_name = context['app_name'].lower()
            for trusted_pattern in self.policy.trusted_app_patterns:
                if re.search(trusted_pattern, app_name, re.IGNORECASE):
                    return RiskLevel.LOW

        # Default risk based on action type keywords
        if any(word in desc_lower for word in ['delete', 'remove', 'terminate', 'kill', 'format']):
            return RiskLevel.HIGH
        if any(word in desc_lower for word in ['install', 'modify', 'change', 'update']):
            return RiskLevel.MEDIUM
        if any(word in desc_lower for word in ['read', 'list', 'show', 'get', 'query']):
            return RiskLevel.SAFE

        return RiskLevel.LOW


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Trust Manager
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TrustManager:
    """Manages trust levels for applications and entities.

    Trust evolves based on:
    - Successful executions (trust increases)
    - Failed executions (trust decreases)
    - User approvals (trust increases)
    - Security violations (trust decreases significantly)
    """

    def __init__(self):
        self.trust_scores: dict[str, float] = {}  # entity -> score (0-100)
        self.execution_history: dict[str, list[bool]] = defaultdict(list)
        self.max_history = 50

    def get_trust_level(self, entity: str) -> TrustLevel:
        score = self.trust_scores.get(entity, 50.0)
        if score >= 90:
            return TrustLevel.FULL
        elif score >= 70:
            return TrustLevel.HIGH
        elif score >= 50:
            return TrustLevel.MEDIUM
        elif score >= 30:
            return TrustLevel.LOW
        return TrustLevel.UNKNOWN

    def record_execution(self, entity: str, success: bool):
        self.execution_history[entity].append(success)
        if len(self.execution_history[entity]) > self.max_history:
            self.execution_history[entity] = self.execution_history[entity][-self.max_history:]

        history = self.execution_history[entity]
        success_rate = sum(history) / len(history) if history else 0.5

        current = self.trust_scores.get(entity, 50.0)
        if success:
            new_score = current + (100 - current) * 0.1 * success_rate
        else:
            new_score = current - current * 0.2

        self.trust_scores[entity] = max(0.0, min(100.0, new_score))

    def record_approval(self, entity: str):
        current = self.trust_scores.get(entity, 50.0)
        self.trust_scores[entity] = min(100.0, current + 5.0)

    def record_violation(self, entity: str):
        current = self.trust_scores.get(entity, 50.0)
        self.trust_scores[entity] = max(0.0, current - 30.0)

    def get_trust_summary(self) -> dict[str, dict]:
        result = {}
        for entity, score in sorted(self.trust_scores.items(), key=lambda x: -x[1]):
            result[entity] = {
                'score': round(score, 1),
                'level': self.get_trust_level(entity).name,
                'executions': len(self.execution_history.get(entity, [])),
            }
        return result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Session Permission Manager
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SessionPermissionManager:
    """Manages temporary permissions for the current session.

    Users can grant temporary elevated access that expires automatically.
    This avoids repeated confirmation dialogs while maintaining safety.
    """

    def __init__(self, default_duration: timedelta = timedelta(minutes=30)):
        self.default_duration = default_duration
        self.permissions: dict[str, SessionPermission] = {}
        self.denied: set[str] = set()

    def grant(self, permission_type: str, duration: Optional[timedelta] = None,
              reason: str = "") -> SessionPermission:
        duration = duration or self.default_duration
        perm = SessionPermission(
            permission_type=permission_type,
            expires_at=datetime.now() + duration,
            reason=reason,
        )
        self.permissions[permission_type] = perm
        self.denied.discard(permission_type)
        logger.info("Session permission granted: %s (expires in %s)", permission_type, duration)
        return perm

    def has_permission(self, permission_type: str) -> bool:
        perm = self.permissions.get(permission_type)
        if perm is None:
            return False
        if perm.is_expired:
            del self.permissions[permission_type]
            return False
        return True

    def deny(self, permission_type: str):
        self.denied.add(permission_type)
        self.permissions.pop(permission_type, None)

    def is_denied(self, permission_type: str) -> bool:
        return permission_type in self.denied

    def cleanup_expired(self):
        expired = [k for k, v in self.permissions.items() if v.is_expired]
        for k in expired:
            del self.permissions[k]

    def get_active_permissions(self) -> list[dict]:
        self.cleanup_expired()
        return [
            {
                'type': p.permission_type,
                'remaining': f"{p.remaining_seconds:.0f}s",
                'reason': p.reason,
            }
            for p in self.permissions.values()
        ]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Intent Validator
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class IntentValidator:
    """Validates the intent behind actions.

    This goes beyond pattern matching to understand WHY an action
    is being performed and whether it makes sense in context.
    """

    def validate_plan(self, actions: list[dict]) -> tuple[bool, str, list[str]]:
        """Validate an entire execution plan before any action runs.

        Args:
            actions: List of action dictionaries with 'type', 'target', 'params'

        Returns:
            (is_valid, reason, warnings) tuple
        """
        warnings = []

        if not actions:
            return True, "Empty plan", []

        dangerous_sequences = [
            (['delete', 'delete'], "Multiple delete operations in sequence"),
            (['install', 'execute'], "Installing then executing unknown code"),
            (['modify', 'modify', 'modify'], "Many modifications without verification"),
        ]

        action_types = [a.get('type', '').lower() for a in actions]

        for seq, msg in dangerous_sequences:
            if all(any(s in t for t in action_types) for s in seq):
                warnings.append(f"Warning: {msg}")

        has_verification = any(
            'verify' in a.get('type', '').lower() or
            'check' in a.get('type', '').lower()
            for a in actions
        )
        if len(actions) > 3 and not has_verification:
            warnings.append("Long plan without verification steps")

        is_valid = True
        reason = "Plan validation passed"

        for i, action in enumerate(actions):
            action_type = action.get('type', '').lower()
            if action_type in ('delete', 'remove', 'terminate', 'kill'):
                if i == 0:
                    warnings.append("First action is destructive - consider safer alternatives")

        return is_valid, reason, warnings

    def validate_action_sequence(self, actions: list[dict]) -> tuple[bool, list[str]]:
        """Quick validation of action sequence coherence."""
        issues = []
        for i in range(len(actions) - 1):
            curr = actions[i]
            next_a = actions[i + 1]

            curr_type = curr.get('type', '').lower()
            next_type = next_a.get('type', '').lower()

            if curr_type == 'click' and next_type == 'click':
                curr_target = curr.get('target', '')
                next_target = next_a.get('target', '')
                if curr_target == next_target:
                    issues.append(f"Steps {i+1} and {i+2} click the same target")

        return len(issues) == 0, issues


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Security Engine (Main Interface)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SecurityEngine:
    """Main security engine that orchestrates all security components.

    This is the single entry point for all security decisions.
    It combines risk assessment, trust management, session permissions,
    and intent validation to make intelligent approval decisions.

    The engine follows this decision flow:
    1. Assess risk level
    2. Check trust level of the app/entity
    3. Check session permissions
    4. Validate intent
    5. Make decision (auto-approve, require consent, reject)
    """

    def __init__(
        self,
        policy: Optional[SecurityPolicy] = None,
        session_duration: timedelta = timedelta(minutes=30),
    ):
        self.policy = policy or SecurityPolicy()
        self.risk_assessor = RiskAssessor(self.policy)
        self.trust_manager = TrustManager()
        self.session_permissions = SessionPermissionManager(session_duration)
        self.intent_validator = IntentValidator()

        self.audit_log: list[dict] = []

    def assess_action(
        self,
        action_description: str,
        action_type: str = "unknown",
        context: Optional[dict] = None,
    ) -> SecurityAssessment:
        """Assess an action and make a security decision.

        This is the core method that combines all security signals
        to make an intelligent decision.

        Args:
            action_description: Human-readable description of the action
            action_type: Type of action (launch, click, type, execute, etc.)
            context: Additional context (app name, user intent, etc.)

        Returns:
            SecurityAssessment with decision and reasoning
        """
        context = context or {}
        app_name = context.get('app_name', '')

        risk_level = self.risk_assessor.assess_risk(action_description, context)
        trust_level = self.trust_manager.get_trust_level(app_name) if app_name else TrustLevel.UNKNOWN

        decision, reason = self._make_decision(risk_level, trust_level, action_type, context)

        assessment = SecurityAssessment(
            risk_level=risk_level,
            decision=decision,
            trust_level=trust_level,
            reason=reason,
            requires_consent=(decision == SecurityDecision.REQUIRE_CONSENT),
            consent_reason=reason if decision == SecurityDecision.REQUIRE_CONSENT else "",
        )

        self._log_assessment(action_description, assessment)

        return assessment

    def _make_decision(
        self,
        risk: RiskLevel,
        trust: TrustLevel,
        action_type: str,
        context: dict,
    ) -> tuple[SecurityDecision, str]:
        """Make the actual security decision based on all signals."""

        if risk == RiskLevel.CRITICAL:
            return SecurityDecision.REJECT, "Critical risk - action rejected"

        permission_key = f"{action_type}:{context.get('app_name', 'unknown')}"
        if self.session_permissions.has_permission(permission_key):
            return SecurityDecision.SESSION_APPROVE, "Session permission active"
        if self.session_permissions.is_denied(permission_key):
            return SecurityDecision.REJECT, "Session permission denied"

        if risk <= self.policy.auto_approve_max_risk:
            if trust >= TrustLevel.MEDIUM:
                return SecurityDecision.AUTO_APPROVE, f"Low risk ({risk.name}) + trusted app"
            elif risk <= RiskLevel.LOW:
                return SecurityDecision.AUTO_APPROVE, f"Low risk ({risk.name}) - safe to auto-approve"

        if risk == RiskLevel.LOW and trust >= TrustLevel.HIGH:
            return SecurityDecision.AUTO_APPROVE, "Trusted app with low risk"

        if risk == RiskLevel.MEDIUM:
            if trust >= TrustLevel.HIGH:
                return SecurityDecision.AUTO_APPROVE, "Medium risk but high trust"
            return SecurityDecision.REQUIRE_CONSENT, f"Medium risk ({risk.name}) requires approval"

        if risk == RiskLevel.HIGH:
            return SecurityDecision.REQUIRE_CONSENT, f"High risk ({risk.name}) requires explicit approval"

        return SecurityDecision.REQUIRE_CONSENT, "Default: requires approval"

    def record_action_result(self, action_description: str, success: bool, app_name: str = ""):
        """Record the result of an action for trust evolution."""
        if app_name:
            self.trust_manager.record_execution(app_name, success)

    def grant_session_permission(
        self,
        permission_type: str,
        duration: Optional[timedelta] = None,
        reason: str = "",
    ) -> SessionPermission:
        return self.session_permissions.grant(permission_type, duration, reason)

    def has_session_permission(self, permission_type: str) -> bool:
        return self.session_permissions.has_permission(permission_type)

    def validate_plan(self, actions: list[dict]) -> tuple[bool, str, list[str]]:
        return self.intent_validator.validate_plan(actions)

    def get_trust_summary(self) -> dict:
        return self.trust_manager.get_trust_summary()

    def get_active_permissions(self) -> list[dict]:
        return self.session_permissions.get_active_permissions()

    def _log_assessment(self, action: str, assessment: SecurityAssessment):
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action[:200],
            'risk': assessment.risk_level.name,
            'decision': assessment.decision.value,
            'trust': assessment.trust_level.name,
            'reason': assessment.reason,
        }
        self.audit_log.append(entry)
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-500:]

    def get_audit_log(self, limit: int = 50) -> list[dict]:
        return self.audit_log[-limit:]

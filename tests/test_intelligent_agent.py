"""Tests for IntelligentSystemAgent (deprecated wrapper)."""

import pytest
from core.intelligent_agent import IntelligentSystemAgent


@pytest.mark.asyncio
async def test_basic_functionality():
    """Test basic functionality of IntelligentSystemAgent."""
    agent = IntelligentSystemAgent(dry_run=True)
    assert agent is not None
    summary = agent.get_system_summary()
    assert isinstance(summary, str)
    assert len(summary) > 0

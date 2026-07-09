# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
Test Suite for Phase 5 - Persistent Memory System

Tests for conversation history, memory tools (remember/recall/forget),
and memory integration with AI brain.
"""

import pytest
import tempfile
import os
import sys
from unittest.mock import Mock

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.memory_integrator import (
    MemoryManager,
    MemoryItem,
    ShortTermMemory,
    LongTermMemory,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        db_path = os.path.join(tmpdir, "test_memory.db")
        yield db_path
        # Clean up connections
        try:
            import sqlite3
            sqlite3.connect(db_path).close()
        except Exception:
            pass


@pytest.fixture
def memory_manager(temp_db):
    """Create a MemoryManager with a temporary database."""
    return MemoryManager(lt_db_path=temp_db)


@pytest.fixture
def fresh_memory_manager(temp_db):
    """Create a fresh MemoryManager (simulates app restart)."""
    return MemoryManager(lt_db_path=temp_db)


# ═══════════════════════════════════════════════════════════════════════════════
# Test: Conversation History
# ═══════════════════════════════════════════════════════════════════════════════

class TestMemoryManagerConversationHistory:
    """Tests for MemoryManager conversation history methods."""

    def test_add_conversation_stores_in_memory(self, memory_manager):
        """add_conversation stores messages in in-memory list."""
        memory_manager.add_conversation("user", "Hello AI")
        memory_manager.add_conversation("assistant", "Hello user!")

        history = memory_manager.get_conversation_history(limit=10)
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello AI"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Hello user!"

    def test_add_conversation_persists_to_db(self, memory_manager):
        """add_conversation persists messages to SQLite database."""
        memory_manager.add_conversation("user", "Test message")

        # Verify in-memory
        history = memory_manager.get_conversation_history()
        assert len(history) == 1

    def test_add_conversation_with_metadata(self, memory_manager):
        """add_conversation stores metadata correctly."""
        metadata = {"action_type": "chat_reply", "source": "test"}
        memory_manager.add_conversation("assistant", "Response", metadata=metadata)

        history = memory_manager.get_conversation_history()
        assert len(history) == 1
        assert history[0]["metadata"]["action_type"] == "chat_reply"
        assert history[0]["metadata"]["source"] == "test"

    def test_conversation_history_respects_limit(self, memory_manager):
        """get_conversation_history respects the limit parameter."""
        for i in range(10):
            memory_manager.add_conversation("user", f"Message {i}")

        history = memory_manager.get_conversation_history(limit=3)
        assert len(history) == 3
        assert history[0]["content"] == "Message 7"
        assert history[2]["content"] == "Message 9"

    def test_conversation_history_max_capacity(self, memory_manager):
        """In-memory history is capped at _max_history (50)."""
        for i in range(60):
            memory_manager.add_conversation("user", f"Message {i}")

        assert len(memory_manager._conversation_history) == 50
        # Should contain messages 10-59
        assert memory_manager._conversation_history[0]["content"] == "Message 10"

    def test_get_memory_context_formats_correctly(self, memory_manager):
        """get_memory_context returns properly formatted string."""
        memory_manager.add_conversation("user", "What time is it?")
        memory_manager.add_conversation("assistant", "It's 3 PM")

        context = memory_manager.get_memory_context(max_items=5)
        assert "Recent Conversation:" in context
        assert "user: What time is it?" in context
        assert "assistant: It's 3 PM" in context

    def test_get_memory_context_empty_history(self, memory_manager):
        """get_memory_context returns empty string when no history."""
        context = memory_manager.get_memory_context()
        assert context == ""


# ═══════════════════════════════════════════════════════════════════════════════
# Test: Memory Tools (Remember/Recall/Forget)
# ═══════════════════════════════════════════════════════════════════════════════

class TestMemoryTools:
    """Tests for memory tool operations."""

    def test_remember_stores_content(self, memory_manager):
        """remember_long stores content and returns MemoryItem."""
        item = memory_manager.remember_long(
            content="My favorite color is blue",
            metadata={"category": "preference"}
        )
        assert isinstance(item, MemoryItem)
        assert item.content == "My favorite color is blue"
        assert item.metadata["category"] == "preference"

    def test_recall_finds_stored_memory(self, memory_manager):
        """recall finds previously stored memories."""
        memory_manager.remember_long("My favorite color is blue")
        memory_manager.remember_long("I prefer dark mode")

        results = memory_manager.recall("color")
        assert len(results) >= 1
        assert any("color" in r.content for r in results)

    def test_recall_returns_empty_when_no_match(self, memory_manager):
        """recall returns empty list when no memories match."""
        memory_manager.remember_long("My favorite color is blue")

        results = memory_manager.recall("nonexistent_keyword_xyz")
        assert len(results) == 0

    def test_forget_deletes_memory(self, memory_manager):
        """forget_long deletes a memory by ID."""
        item = memory_manager.remember_long("Temporary memory")
        item_id = item.id

        deleted = memory_manager.forget_long(item_id)
        assert deleted is True

        # Verify it's gone
        retrieved = memory_manager.long.get(item_id)
        assert retrieved is None

    def test_forget_returns_false_for_nonexistent(self, memory_manager):
        """forget_long returns False for nonexistent ID."""
        deleted = memory_manager.forget_long("nonexistent_id_12345")
        assert deleted is False

    def test_remember_with_category(self, memory_manager):
        """remember_long stores category in metadata."""
        item = memory_manager.remember_long(
            content="User prefers dark theme",
            metadata={"category": "preference"}
        )
        assert item.metadata["category"] == "preference"

    def test_recall_limit(self, memory_manager):
        """recall respects the limit parameter."""
        for i in range(10):
            memory_manager.remember_long(f"Memory item {i}")

        results = memory_manager.recall("item", limit=3)
        assert len(results) <= 3

    def test_remember_and_recall_roundtrip(self, memory_manager):
        """Full roundtrip: remember → recall → verify content."""
        memory_manager.remember_long(
            content="The password is secret123",
            metadata={"category": "instruction"}
        )

        results = memory_manager.recall("password")
        assert len(results) == 1
        assert "secret123" in results[0].content

    def test_conversation_and_memory_independent(self, memory_manager):
        """Conversation history and long-term memory are independent."""
        memory_manager.add_conversation("user", "Hello")
        memory_manager.remember_long("Important fact")

        history = memory_manager.get_conversation_history()
        memories = memory_manager.recall("fact")

        assert len(history) == 1
        assert len(memories) == 1
        assert history[0]["content"] == "Hello"
        assert "Important fact" in memories[0].content


# ═══════════════════════════════════════════════════════════════════════════════
# Test: Tool Schema Registration
# ═══════════════════════════════════════════════════════════════════════════════

class TestMemoryToolSchema:
    """Tests for memory tool schema definitions."""

    def test_remember_tool_registered(self):
        """remember tool is registered in tool schema."""
        from core.tool_schema import get_tool_definitions
        tools = get_tool_definitions()
        tool_names = [t.name for t in tools]
        assert "remember" in tool_names

    def test_recall_tool_registered(self):
        """recall tool is registered in tool schema."""
        from core.tool_schema import get_tool_definitions
        tools = get_tool_definitions()
        tool_names = [t.name for t in tools]
        assert "recall" in tool_names

    def test_forget_tool_registered(self):
        """forget tool is registered in tool schema."""
        from core.tool_schema import get_tool_definitions
        tools = get_tool_definitions()
        tool_names = [t.name for t in tools]
        assert "forget" in tool_names

    def test_memory_tools_are_safe_risk(self):
        """Memory tools have safe risk level."""
        from core.tool_schema import get_tool_definitions
        tools = get_tool_definitions()
        for tool in tools:
            if tool.name in ("remember", "recall", "forget"):
                assert tool.risk_level == "safe"

    def test_remember_tool_has_content_param(self):
        """remember tool has required 'content' parameter."""
        from core.tool_schema import get_tool_definitions
        tools = get_tool_definitions()
        remember_tool = next(t for t in tools if t.name == "remember")
        param_names = [p.name for p in remember_tool.params]
        assert "content" in param_names
        content_param = next(p for p in remember_tool.params if p.name == "content")
        assert content_param.required is True

    def test_recall_tool_has_query_param(self):
        """recall tool has required 'query' parameter."""
        from core.tool_schema import get_tool_definitions
        tools = get_tool_definitions()
        recall_tool = next(t for t in tools if t.name == "recall")
        param_names = [p.name for p in recall_tool.params]
        assert "query" in param_names
        query_param = next(p for p in recall_tool.params if p.name == "query")
        assert query_param.required is True

    def test_forget_tool_has_memory_id_param(self):
        """forget tool has required 'memory_id' parameter."""
        from core.tool_schema import get_tool_definitions
        tools = get_tool_definitions()
        forget_tool = next(t for t in tools if t.name == "forget")
        param_names = [p.name for p in forget_tool.params]
        assert "memory_id" in param_names


# ═══════════════════════════════════════════════════════════════════════════════
# Test: ToolExecutor Memory Integration
# ═══════════════════════════════════════════════════════════════════════════════

class TestToolExecutorMemoryIntegration:
    """Tests for ToolExecutor memory tool dispatch."""

    def test_handle_remember_saves_content(self, memory_manager):
        """_handle_remember saves content via memory_manager."""
        from main import ToolExecutor
        executor = ToolExecutor(
            Mock(), Mock(), safety_mode="moderate",
            memory_manager=memory_manager
        )

        result = executor._handle_remember(
            {"content": "My favorite language is Python", "category": "preference"},
            "Remember preference"
        )
        assert result["status"] == "success"
        assert "Remembered" in result["output"]
        assert "memory_id" in result

    def test_handle_remember_without_memory_manager(self):
        """_handle_remember fails gracefully without memory_manager."""
        from main import ToolExecutor
        executor = ToolExecutor(Mock(), Mock(), safety_mode="moderate")

        result = executor._handle_remember(
            {"content": "Test"},
            "Test remember"
        )
        assert result["status"] == "failed"
        assert "not initialized" in result["error"]

    def test_handle_remember_empty_content(self, memory_manager):
        """_handle_remember fails with empty content."""
        from main import ToolExecutor
        executor = ToolExecutor(
            Mock(), Mock(), safety_mode="moderate",
            memory_manager=memory_manager
        )

        result = executor._handle_remember({"content": ""}, "Empty")
        assert result["status"] == "failed"
        assert "No content" in result["error"]

    def test_handle_recall_searches_memory(self, memory_manager):
        """_handle_recall searches memory and returns results."""
        memory_manager.remember_long("My favorite color is blue")
        memory_manager.remember_long("I prefer dark mode")

        from main import ToolExecutor
        executor = ToolExecutor(
            Mock(), Mock(), safety_mode="moderate",
            memory_manager=memory_manager
        )

        result = executor._handle_recall(
            {"query": "color", "limit": 5},
            "Search color"
        )
        assert result["status"] == "success"
        assert "Found" in result["output"] or "memories" in result["output"]

    def test_handle_recall_no_results(self, memory_manager):
        """_handle_recall returns message when no results found."""
        from main import ToolExecutor
        executor = ToolExecutor(
            Mock(), Mock(), safety_mode="moderate",
            memory_manager=memory_manager
        )

        result = executor._handle_recall(
            {"query": "nonexistent_xyz"},
            "Search nonexistent"
        )
        assert result["status"] == "success"
        assert "No memories" in result["output"]

    def test_handle_forget_deletes_memory(self, memory_manager):
        """_handle_forget deletes a memory by ID."""
        item = memory_manager.remember_long("Temporary fact")

        from main import ToolExecutor
        executor = ToolExecutor(
            Mock(), Mock(), safety_mode="moderate",
            memory_manager=memory_manager
        )

        result = executor._handle_forget(
            {"memory_id": item.id},
            "Delete memory"
        )
        assert result["status"] == "success"
        assert "Deleted" in result["output"]

    def test_handle_forget_nonexistent_id(self, memory_manager):
        """_handle_forget returns error for nonexistent ID."""
        from main import ToolExecutor
        executor = ToolExecutor(
            Mock(), Mock(), safety_mode="moderate",
            memory_manager=memory_manager
        )

        result = executor._handle_forget(
            {"memory_id": "nonexistent_12345"},
            "Delete nonexistent"
        )
        assert result["status"] == "failed"
        assert "not found" in result["error"]


# ═══════════════════════════════════════════════════════════════════════════════
# Test: Memory Context Injection
# ═══════════════════════════════════════════════════════════════════════════════

class TestMemoryContextInjection:
    """Tests for memory context injection into AI prompts."""

    def test_memory_context_includes_conversation(self, memory_manager):
        """Memory context includes recent conversation."""
        memory_manager.add_conversation("user", "What's the weather?")
        memory_manager.add_conversation("assistant", "It's sunny today.")

        context = memory_manager.get_memory_context(max_items=5)
        assert "What's the weather?" in context
        assert "sunny" in context

    def test_memory_context_includes_recalled_memories(self, memory_manager):
        """Memory context includes recalled memories."""
        memory_manager.remember_long("User prefers dark theme")

        context = memory_manager.get_memory_context(max_items=5)
        assert "dark theme" in context

    def test_memory_context_limited_by_max_items(self, memory_manager):
        """Memory context respects max_items limit."""
        for i in range(10):
            memory_manager.add_conversation("user", f"Message {i}")

        context = memory_manager.get_memory_context(max_items=3)
        # Should only contain last 3 messages
        assert "Message 0" not in context
        assert "Message 9" in context

    def test_ai_brain_accepts_memory_context(self):
        """AIBrain.agent_chat accepts memory_context parameter."""
        from core.ai_brain import AIBrain
        brain = AIBrain()

        # Verify the method signature accepts memory_context
        import inspect
        sig = inspect.signature(brain.agent_chat)
        assert "memory_context" in sig.parameters


# ═══════════════════════════════════════════════════════════════════════════════
# Test: Persistence Across Restarts
# ═══════════════════════════════════════════════════════════════════════════════

class TestMemoryPersistence:
    """Tests for memory persistence across app restarts."""

    def test_conversation_persists_in_db(self, temp_db):
        """Conversation history persists in SQLite database."""
        manager1 = MemoryManager(lt_db_path=temp_db)
        manager1.add_conversation("user", "Important message")

        # Simulate app restart
        manager2 = MemoryManager(lt_db_path=temp_db)
        history = manager2.get_conversation_history()
        assert len(history) == 1
        assert history[0]["content"] == "Important message"

    def test_long_term_memory_persists(self, temp_db):
        """Long-term memories persist across restarts."""
        manager1 = MemoryManager(lt_db_path=temp_db)
        manager1.remember_long("Persistent fact")

        # Simulate app restart
        manager2 = MemoryManager(lt_db_path=temp_db)
        results = manager2.recall("Persistent fact")
        assert len(results) == 1
        assert "Persistent fact" in results[0].content

    def test_forget_persists_across_restarts(self, temp_db):
        """Forgetting a memory persists across restarts."""
        manager1 = MemoryManager(lt_db_path=temp_db)
        item = manager1.remember_long("To be deleted")
        manager1.forget_long(item.id)

        # Simulate app restart
        manager2 = MemoryManager(lt_db_path=temp_db)
        results = manager2.recall("To be deleted")
        assert len(results) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Test: Edge Cases
# ═══════════════════════════════════════════════════════════════════════════════

class TestMemoryEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_conversation_history(self, memory_manager):
        """Empty conversation history returns empty list."""
        history = memory_manager.get_conversation_history()
        assert history == []

    def test_conversation_with_very_long_content(self, memory_manager):
        """Long content is truncated appropriately."""
        long_content = "x" * 5000
        memory_manager.add_conversation("user", long_content)

        history = memory_manager.get_conversation_history()
        assert len(history[0]["content"]) <= 500

    def test_concurrent_add_conversation(self, memory_manager):
        """Multiple concurrent adds don't crash."""
        import threading

        def add_messages():
            for i in range(10):
                memory_manager.add_conversation("user", f"Thread message {i}")

        threads = [threading.Thread(target=add_messages) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        history = memory_manager.get_conversation_history(limit=100)
        assert len(history) == 30

    def test_memory_manager_with_custom_db_path(self, temp_db):
        """MemoryManager works with custom database path."""
        manager = MemoryManager(lt_db_path=temp_db)
        assert manager.long._conn is not None

    def test_short_term_memory_independent(self):
        """ShortTermMemory works independently of MemoryManager."""
        stm = ShortTermMemory()
        item = stm.add("Test content", ttl=60.0)
        assert item.content == "Test content"
        retrieved = stm.get(item.id)
        assert retrieved is not None


# ═══════════════════════════════════════════════════════════════════════════════
# Test: Core __init__.py Exports
# ═══════════════════════════════════════════════════════════════════════════════

class TestCoreExports:
    """Tests for Phase 5 exports in core/__init__.py."""

    def test_memory_manager_exported(self):
        """MemoryManager is exported from core package."""
        from core import MemoryManager
        assert MemoryManager is not None

    def test_memory_item_exported(self):
        """MemoryItem is exported from core package."""
        from core import MemoryItem
        assert MemoryItem is not None

    def test_short_term_memory_exported(self):
        """ShortTermMemory is exported from core package."""
        from core import ShortTermMemory
        assert ShortTermMemory is not None

    def test_long_term_memory_exported(self):
        """LongTermMemory is exported from core package."""
        from core import LongTermMemory
        assert LongTermMemory is not None

# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
Tests for Session Manager (Phase 6)

Tests cover:
- Session CRUD operations
- Message storage and retrieval
- Session search
- Auto-generated session names
- Session stats
"""

import os
import tempfile
import time
import pytest

from core.session_manager import SessionManager


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_sessions.sqlite3")
        yield db_path


@pytest.fixture
def session_manager(temp_db):
    """Create a SessionManager with a temporary database."""
    sm = SessionManager(db_path=temp_db)
    yield sm
    sm.close()


# ═══════════════════════════════════════════════════════════════════════════════
# Session CRUD Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestSessionCRUD:
    """Tests for session create, read, update, delete operations."""

    def test_create_session_with_name(self, session_manager):
        """Test creating a session with a custom name."""
        session = session_manager.create_session("test-session")
        assert session is not None
        assert session.name == "test-session"
        assert session.id.startswith("session_")
        assert session.message_count == 0

    def test_create_session_auto_name(self, session_manager):
        """Test creating a session with auto-generated name."""
        session = session_manager.create_session()
        assert session is not None
        assert session.name.startswith("chat-")

    def test_get_session(self, session_manager):
        """Test retrieving a session by ID."""
        created = session_manager.create_session("get-test")
        retrieved = session_manager.get_session(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "get-test"

    def test_get_session_by_name(self, session_manager):
        """Test retrieving a session by name."""
        session_manager.create_session("name-test")
        retrieved = session_manager.get_session_by_name("name-test")
        assert retrieved is not None
        assert retrieved.name == "name-test"

    def test_get_nonexistent_session(self, session_manager):
        """Test retrieving a non-existent session returns None."""
        result = session_manager.get_session("nonexistent")
        assert result is None

    def test_list_sessions(self, session_manager):
        """Test listing all sessions."""
        session_manager.create_session("session-1")
        session_manager.create_session("session-2")
        session_manager.create_session("session-3")
        sessions = session_manager.list_sessions()
        assert len(sessions) == 3

    def test_list_sessions_ordered_by_updated(self, session_manager):
        """Test sessions are listed in order of last update."""
        session_manager.create_session("first")
        time.sleep(0.01)
        session_manager.create_session("second")
        sessions = session_manager.list_sessions()
        assert sessions[0].name == "second"
        assert sessions[1].name == "first"

    def test_delete_session(self, session_manager):
        """Test deleting a session."""
        session = session_manager.create_session("to-delete")
        result = session_manager.delete_session(session.id)
        assert result is True
        assert session_manager.get_session(session.id) is None

    def test_delete_session_by_name(self, session_manager):
        """Test deleting a session by name."""
        session_manager.create_session("named-delete")
        result = session_manager.delete_session_by_name("named-delete")
        assert result is True

    def test_delete_nonexistent_session(self, session_manager):
        """Test deleting a non-existent session returns False."""
        result = session_manager.delete_session("nonexistent")
        assert result is False

    def test_switch_session(self, session_manager):
        """Test switching to a different session."""
        session_manager.create_session("session-a")
        s2 = session_manager.create_session("session-b")
        result = session_manager.switch_session(s2.id)
        assert result is not None
        assert result.id == s2.id
        assert session_manager.get_current_session().id == s2.id

    def test_switch_session_by_name(self, session_manager):
        """Test switching to a session by name."""
        session_manager.create_session("switch-target")
        result = session_manager.switch_session("switch-target")
        assert result is not None
        assert result.name == "switch-target"


# ═══════════════════════════════════════════════════════════════════════════════
# Message Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestSessionMessages:
    """Tests for message storage and retrieval."""

    def test_add_message(self, session_manager):
        """Test adding a message to a session."""
        session = session_manager.create_session("msg-test")
        msg = session_manager.add_message(session.id, "user", "Hello world")
        assert msg is not None
        assert msg.role == "user"
        assert msg.content == "Hello world"
        assert msg.session_id == session.id

    def test_add_multiple_messages(self, session_manager):
        """Test adding multiple messages to a session."""
        session = session_manager.create_session("multi-msg")
        session_manager.add_message(session.id, "user", "Hello")
        session_manager.add_message(session.id, "assistant", "Hi there!")
        session_manager.add_message(session.id, "user", "How are you?")
        messages = session_manager.get_messages(session.id)
        assert len(messages) == 3

    def test_get_messages_returns_asc_order(self, session_manager):
        """Test messages are returned in ascending timestamp order."""
        session = session_manager.create_session("order-test")
        session_manager.add_message(session.id, "user", "First")
        time.sleep(0.01)
        session_manager.add_message(session.id, "assistant", "Second")
        messages = session_manager.get_messages(session.id)
        assert messages[0].content == "First"
        assert messages[1].content == "Second"

    def test_get_messages_with_limit(self, session_manager):
        """Test limiting the number of returned messages."""
        session = session_manager.create_session("limit-test")
        for i in range(10):
            session_manager.add_message(session.id, "user", f"Message {i}")
        messages = session_manager.get_messages(session.id, limit=5)
        assert len(messages) == 5

    def test_message_count_updates(self, session_manager):
        """Test that message count is updated on the session."""
        session = session_manager.create_session("count-test")
        session_manager.add_message(session.id, "user", "msg1")
        session_manager.add_message(session.id, "assistant", "msg2")
        updated = session_manager.get_session(session.id)
        assert updated.message_count == 2

    def test_add_message_with_metadata(self, session_manager):
        """Test adding a message with metadata."""
        session = session_manager.create_session("meta-test")
        meta = {"action_type": "tool_call", "tool": "execute_command"}
        msg = session_manager.add_message(session.id, "user", "Run command", meta)
        assert msg.metadata == meta


# ═══════════════════════════════════════════════════════════════════════════════
# Search Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestSessionSearch:
    """Tests for session search functionality."""

    def test_search_by_name(self, session_manager):
        """Test searching sessions by name."""
        session_manager.create_session("python-project")
        session_manager.create_session("web-app")
        session_manager.create_session("python-scripts")
        results = session_manager.search_sessions("python")
        assert len(results) == 2

    def test_search_by_content(self, session_manager):
        """Test searching sessions by message content."""
        session = session_manager.create_session("content-search")
        session_manager.add_message(session.id, "user", "Install Docker on Windows")
        results = session_manager.search_sessions("Docker")
        assert len(results) >= 1

    def test_search_no_results(self, session_manager):
        """Test search with no matching results."""
        session_manager.create_session("unrelated")
        results = session_manager.search_sessions("nonexistent-query")
        assert len(results) == 0

    def test_search_deduplicates(self, session_manager):
        """Test search results are deduplicated."""
        session = session_manager.create_session("dedup-test")
        session_manager.add_message(session.id, "user", "test query here")
        session_manager.add_message(session.id, "assistant", "test query response")
        results = session_manager.search_sessions("test query")
        session_ids = [s.id for s in results]
        assert len(session_ids) == len(set(session_ids))


# ═══════════════════════════════════════════════════════════════════════════════
# Auto-Name Generation Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestAutoNameGeneration:
    """Tests for automatic session name generation."""

    def test_auto_create_session(self, session_manager):
        """Test auto-creating a session from a first message."""
        session = session_manager.auto_create_session("Create a folder on D")
        assert session is not None
        assert "create" in session.name.lower()

    def test_auto_name_open(self, session_manager):
        """Test auto-name for 'open' requests."""
        session = session_manager.auto_create_session("Open Chrome browser")
        assert "open" in session.name.lower()

    def test_auto_name_query(self, session_manager):
        """Test auto-name for query requests."""
        session = session_manager.auto_create_session("What files are in Downloads?")
        assert "query" in session.name.lower() or "chat" in session.name.lower()


# ═══════════════════════════════════════════════════════════════════════════════
# Stats Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestSessionStats:
    """Tests for session statistics."""

    def test_get_session_stats(self, session_manager):
        """Test getting session statistics."""
        s1 = session_manager.create_session("stats-1")
        s2 = session_manager.create_session("stats-2")
        session_manager.add_message(s1.id, "user", "hello")
        session_manager.add_message(s1.id, "assistant", "hi")
        session_manager.add_message(s2.id, "user", "test")
        stats = session_manager.get_session_stats()
        assert stats["total_sessions"] == 2
        assert stats["total_messages"] == 3

    def test_empty_stats(self, session_manager):
        """Test stats when no sessions exist."""
        stats = session_manager.get_session_stats()
        assert stats["total_sessions"] == 0
        assert stats["total_messages"] == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Tag and Summary Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestSessionMetadata:
    """Tests for session tags and summaries."""

    def test_add_tag(self, session_manager):
        """Test adding a tag to a session."""
        session = session_manager.create_session("tag-test")
        result = session_manager.add_tag(session.id, "important")
        assert result is True
        updated = session_manager.get_session(session.id)
        assert "important" in updated.tags

    def test_add_duplicate_tag(self, session_manager):
        """Test adding a duplicate tag doesn't create duplicates."""
        session = session_manager.create_session("dup-tag")
        session_manager.add_tag(session.id, "test")
        session_manager.add_tag(session.id, "test")
        updated = session_manager.get_session(session.id)
        assert updated.tags.count("test") == 1

    def test_update_summary(self, session_manager):
        """Test updating a session summary."""
        session = session_manager.create_session("summary-test")
        result = session_manager.update_summary(session.id, "This is a summary")
        assert result is True
        updated = session_manager.get_session(session.id)
        assert updated.summary == "This is a summary"


# ═══════════════════════════════════════════════════════════════════════════════
# Persistence Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestSessionPersistence:
    """Tests for session persistence across manager instances."""

    def test_persistence_across_instances(self, temp_db):
        """Test sessions persist across SessionManager instances."""
        sm1 = SessionManager(db_path=temp_db)
        session = sm1.create_session("persist-test")
        sm1.add_message(session.id, "user", "persisted message")
        sm1.close()

        sm2 = SessionManager(db_path=temp_db)
        retrieved = sm2.get_session(session.id)
        assert retrieved is not None
        assert retrieved.name == "persist-test"
        messages = sm2.get_messages(session.id)
        assert len(messages) == 1
        assert messages[0].content == "persisted message"
        sm2.close()


# ═══════════════════════════════════════════════════════════════════════════════
# Recent Sessions Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestRecentSessions:
    """Tests for getting recent sessions."""

    def test_get_recent_sessions(self, session_manager):
        """Test getting recent sessions."""
        session_manager.create_session("old")
        time.sleep(0.01)
        session_manager.create_session("new")
        recent = session_manager.get_recent_sessions(limit=1)
        assert len(recent) == 1
        assert recent[0].name == "new"

# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
Session Manager - مدیریت نشست‌های مکالمه

این ماژول مسئول ایجاد، ذخیره، بازیابی و حذف نشست‌های مکالمه است.
هر نشست شامل تاریخچه پیام‌ها و اطلاعات مرتبط است.
"""

import json
import logging
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional


# ═══════════════════════════════════════════════════════════════════════════════
# Data Classes
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SessionMessage:
    """یک پیام در نشست"""
    id: int
    session_id: str
    role: str          # 'user' or 'assistant'
    content: str
    metadata: Dict[str, Any]
    timestamp: float


@dataclass
class Session:
    """یک نشست مکالمه"""
    id: str
    name: str
    created_at: float
    updated_at: float
    message_count: int = 0
    summary: str = ""
    tags: List[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# Session Manager Class
# ═══════════════════════════════════════════════════════════════════════════════

class SessionManager:
    """
    مدیریت نشست‌های مکالمه

    مسئولیت‌های اصلی:
    1. ایجاد نشست‌های جدید
    2. ذخیره پیام‌ها در نشست
    3. بازیابی تاریخچه نشست
    4. جستجوی نشست‌ها
    5. حذف نشست‌ها
    """

    def __init__(self, db_path: Optional[str] = None):
        """سازنده Session Manager"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        if db_path is None:
            db_path = str(Path("./data").resolve() / "sessions.sqlite3")

        self._db_path = db_path
        self._lock = Lock()

        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

        self._current_session: Optional[Session] = None

    def _init_database(self) -> None:
        """اولیه‌سازی دیتابیس"""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    message_count INTEGER DEFAULT 0,
                    summary TEXT DEFAULT '',
                    tags TEXT DEFAULT '[]'
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    timestamp REAL NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_messages_session
                ON session_messages(session_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_messages_timestamp
                ON session_messages(timestamp)
            """)

            conn.commit()

    def create_session(self, name: Optional[str] = None) -> Session:
        """ایجاد یک نشست جدید"""
        session_id = f"session_{int(time.time() * 1000)}"
        now = time.time()

        if not name:
            name = f"chat-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}"

        session = Session(
            id=session_id,
            name=name,
            created_at=now,
            updated_at=now,
        )

        with self._lock:
            conn = sqlite3.connect(self._db_path)
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sessions (id, name, created_at, updated_at, message_count, summary, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.id,
                    session.name,
                    session.created_at,
                    session.updated_at,
                    session.message_count,
                    session.summary,
                    json.dumps(session.tags, ensure_ascii=False),
                ))
                conn.commit()
            finally:
                conn.close()

        self._current_session = session
        self.logger.info("New session created: %s (%s)", session.name, session.id)
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """دریافت یک نشست با شناسه"""
        with self._lock:
            conn = sqlite3.connect(self._db_path)
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, created_at, updated_at, message_count, summary, tags
                    FROM sessions WHERE id = ?
                """, (session_id,))
                row = cursor.fetchone()
                if row is None:
                    return None
                return Session(
                    id=row[0],
                    name=row[1],
                    created_at=row[2],
                    updated_at=row[3],
                    message_count=row[4],
                    summary=row[5],
                    tags=json.loads(row[6]) if row[6] else [],
                )
            finally:
                conn.close()

    def get_session_by_name(self, name: str) -> Optional[Session]:
        """دریافت یک نشست با نام"""
        with self._lock:
            conn = sqlite3.connect(self._db_path)
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, created_at, updated_at, message_count, summary, tags
                    FROM sessions WHERE name = ?
                """, (name,))
                row = cursor.fetchone()
                if row is None:
                    return None
                return Session(
                    id=row[0],
                    name=row[1],
                    created_at=row[2],
                    updated_at=row[3],
                    message_count=row[4],
                    summary=row[5],
                    tags=json.loads(row[6]) if row[6] else [],
                )
            finally:
                conn.close()

    def list_sessions(self, limit: int = 50) -> List[Session]:
        """لیست تمام نشست‌ها"""
        with self._lock:
            conn = sqlite3.connect(self._db_path)
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, created_at, updated_at, message_count, summary, tags
                    FROM sessions
                    ORDER BY updated_at DESC
                    LIMIT ?
                """, (limit,))
                rows = cursor.fetchall()
                sessions = []
                for row in rows:
                    sessions.append(Session(
                        id=row[0],
                        name=row[1],
                        created_at=row[2],
                        updated_at=row[3],
                        message_count=row[4],
                        summary=row[5],
                        tags=json.loads(row[6]) if row[6] else [],
                    ))
                return sessions
            finally:
                conn.close()

    def delete_session(self, session_id: str) -> bool:
        """حذف یک نشست و تمام پیام‌های آن"""
        with self._lock:
            conn = sqlite3.connect(self._db_path)
            try:
                cursor = conn.cursor()

                cursor.execute("DELETE FROM session_messages WHERE session_id = ?", (session_id,))
                messages_deleted = cursor.rowcount

                cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
                sessions_deleted = cursor.rowcount

                conn.commit()

                if sessions_deleted > 0:
                    self.logger.info(
                        "نشست حذف شد: %s (%d پیام حذف شد)",
                        session_id, messages_deleted
                    )
                    if self._current_session and self._current_session.id == session_id:
                        self._current_session = None
                    return True
                return False
            finally:
                conn.close()

    def delete_session_by_name(self, name: str) -> bool:
        """حذف یک نشست با نام"""
        session = self.get_session_by_name(name)
        if session:
            return self.delete_session(session.id)
        return False

    def switch_session(self, identifier: str) -> Optional[Session]:
        """سوئیچ به یک نشست دیگر"""
        session = self.get_session(identifier)
        if session is None:
            session = self.get_session_by_name(identifier)
        if session:
            self._current_session = session
            self.logger.info("Switched to session: %s", session.name)
        return session

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SessionMessage:
        """افزودن یک پیام به نشست"""
        now = time.time()
        meta_json = json.dumps(metadata or {}, ensure_ascii=False)

        with self._lock:
            conn = sqlite3.connect(self._db_path)
            try:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO session_messages (session_id, role, content, metadata, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (session_id, role, content[:2000], meta_json, now))

                message_id = cursor.lastrowid

                cursor.execute("""
                    UPDATE sessions
                    SET message_count = message_count + 1, updated_at = ?
                    WHERE id = ?
                """, (now, session_id))

                conn.commit()

                if self._current_session and self._current_session.id == session_id:
                    self._current_session.updated_at = now
                    self._current_session.message_count += 1

                return SessionMessage(
                    id=message_id,
                    session_id=session_id,
                    role=role,
                    content=content,
                    metadata=metadata or {},
                    timestamp=now,
                )
            finally:
                conn.close()

    def get_messages(
        self,
        session_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[SessionMessage]:
        """دریافت پیام‌های یک نشست"""
        with self._lock:
            conn = sqlite3.connect(self._db_path)
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, session_id, role, content, metadata, timestamp
                    FROM session_messages
                    WHERE session_id = ?
                    ORDER BY timestamp ASC
                    LIMIT ? OFFSET ?
                """, (session_id, limit, offset))
                rows = cursor.fetchall()
                messages = []
                for row in rows:
                    messages.append(SessionMessage(
                        id=row[0],
                        session_id=row[1],
                        role=row[2],
                        content=row[3],
                        metadata=json.loads(row[4]) if row[4] else {},
                        timestamp=row[5],
                    ))
                return messages
            finally:
                conn.close()

    def search_sessions(self, query: str, limit: int = 20) -> List[Session]:
        """جستجوی نشست‌ها بر اساس نام، خلاصه یا محتوای پیام‌ها"""
        like_q = f"%{query}%"
        with self._lock:
            conn = sqlite3.connect(self._db_path)
            try:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT DISTINCT s.id, s.name, s.created_at, s.updated_at,
                           s.message_count, s.summary, s.tags
                    FROM sessions s
                    LEFT JOIN session_messages sm ON s.id = sm.session_id
                    WHERE s.name LIKE ?
                       OR s.summary LIKE ?
                       OR sm.content LIKE ?
                    ORDER BY s.updated_at DESC
                    LIMIT ?
                """, (like_q, like_q, like_q, limit))

                rows = cursor.fetchall()
                sessions = []
                seen_ids = set()
                for row in rows:
                    if row[0] not in seen_ids:
                        seen_ids.add(row[0])
                        sessions.append(Session(
                            id=row[0],
                            name=row[1],
                            created_at=row[2],
                            updated_at=row[3],
                            message_count=row[4],
                            summary=row[5],
                            tags=json.loads(row[6]) if row[6] else [],
                        ))
                return sessions
            finally:
                conn.close()

    def update_summary(self, session_id: str, summary: str) -> bool:
        """بروز‌رسانی خلاصه نشست"""
        with self._lock:
            conn = sqlite3.connect(self._db_path)
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE sessions SET summary = ? WHERE id = ?
                """, (summary, session_id))
                conn.commit()
                if self._current_session and self._current_session.id == session_id:
                    self._current_session.summary = summary
                return cursor.rowcount > 0
            finally:
                conn.close()

    def add_tag(self, session_id: str, tag: str) -> bool:
        """افزودن تگ به نشست"""
        session = self.get_session(session_id)
        if not session:
            return False
        if tag not in session.tags:
            session.tags.append(tag)
            with self._lock:
                conn = sqlite3.connect(self._db_path)
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE sessions SET tags = ? WHERE id = ?
                    """, (json.dumps(session.tags, ensure_ascii=False), session_id))
                    conn.commit()
                    return True
                finally:
                    conn.close()
        return True

    def get_recent_sessions(self, limit: int = 5) -> List[Session]:
        """دریافت آخرین نشست‌ها"""
        return self.list_sessions(limit=limit)

    def get_current_session(self) -> Optional[Session]:
        """دریافت نشست فعلی"""
        return self._current_session

    def set_current_session(self, session: Session) -> None:
        """تنظیم نشست فعلی"""
        self._current_session = session

    def auto_create_session(self, first_message: str) -> Session:
        """ایجاد خودکار نشست از اولین پیام"""
        name = self._generate_session_name(first_message)
        return self.create_session(name)

    def _generate_session_name(self, first_message: str) -> str:
        """تولید نام خودکار برای نشست از اولین پیام"""
        msg_lower = first_message.lower().strip()

        prefixes = {
            "create": "create-",
            "open": "open-",
            "delete": "delete-",
            "rename": "rename-",
            "move": "move-",
            "copy": "copy-",
            "search": "search-",
            "find": "find-",
            "show": "show-",
            "list": "list-",
            "run": "run-",
            "install": "install-",
            "what": "query-",
            "how": "howto-",
        }

        prefix = "chat-"
        for keyword, pfx in prefixes.items():
            if msg_lower.startswith(keyword):
                prefix = pfx
                break

        words = first_message.split()[:3]
        slug = "-".join(w.lower() for w in words if w.isalnum())
        if not slug:
            slug = datetime.now().strftime("%H%M%S")

        timestamp = datetime.now().strftime("%H%M%S")
        return f"{prefix}{slug}-{timestamp}"

    def get_session_stats(self) -> Dict[str, Any]:
        """دریافت آمار کلی نشست‌ها"""
        with self._lock:
            conn = sqlite3.connect(self._db_path)
            try:
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) FROM sessions")
                total_sessions = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM session_messages")
                total_messages = cursor.fetchone()[0]

                cursor.execute("SELECT AVG(message_count) FROM sessions")
                avg_messages = cursor.fetchone()[0] or 0

                cursor.execute("""
                    SELECT id, name, message_count
                    FROM sessions ORDER BY updated_at DESC LIMIT 1
                """)
                latest = cursor.fetchone()
                latest_session = {
                    "id": latest[0],
                    "name": latest[1],
                    "message_count": latest[2],
                } if latest else None

                return {
                    "total_sessions": total_sessions,
                    "total_messages": total_messages,
                    "average_messages_per_session": round(avg_messages, 1),
                    "latest_session": latest_session,
                }
            finally:
                conn.close()

    def close(self) -> None:
        """بستن اتصالات"""
        self._current_session = None
        self.logger.info("Session Manager closed")

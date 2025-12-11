# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""تنظیمات متمرکز لاگ‌گیری برای Software-AI

این ماژول تابع setup_logging() رو ارائه می‌کنه که یه handler برای نمایش لاگ‌ها تو کنسول
و یه handler چرخشی برای فایل (data/logs/app.log) تنظیم می‌کنه.
همچنین یه هوک استثنا نصب می‌کنه تا خطاهای گرفته‌نشده هم لاگ بشن.

ویژگی‌های جدید:
- Session-based logging: هر اجرا یک فایل لاگ جداگانه با timestamp
- Comprehensive logging: تمام لاگ‌های کنسول + فایل در یک session log
- Master log file: یک فایل اصلی که همه چیز را ضبط می‌کند
"""
from __future__ import annotations

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


DEFAULT_LOG_FILE = Path("data") / "logs" / "app.log"
MASTER_LOG_FILE = Path("data") / "logs" / "master.log"  # فایل لاگ اصلی
SESSION_LOG_DIR = Path("data") / "logs" / "sessions"  # پوشه session logs


def ensure_logs_dir(path: Path) -> None:
    """ایجاد دایرکتوری لاگ در صورت عدم وجود"""
    path.parent.mkdir(parents=True, exist_ok=True)


def get_session_log_file() -> Path:
    """ایجاد فایل لاگ با timestamp برای این session
    
    فرمت: data/logs/sessions/session_YYYYMMDD_HHMMSS.log
    """
    SESSION_LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return SESSION_LOG_DIR / f"session_{timestamp}.log"


class ComprehensiveFormatter(logging.Formatter):
    """فرمتر پیشرفته که اطلاعات کامل را نمایش می‌دهد"""
    
    def format(self, record: logging.LogRecord) -> str:
        # فرمت اصلی
        original = super().format(record)
        
        # اضافه کردن اطلاعات اضافی برای فایل لاگ
        extra_info = []
        
        # اضافه کردن نام thread اگر multi-threading باشد
        if hasattr(record, 'threadName') and record.threadName != 'MainThread':
            extra_info.append(f"Thread:{record.threadName}")
        
        # اضافه کردن نام process اگر multi-processing باشد
        if hasattr(record, 'processName') and record.processName != 'MainProcess':
            extra_info.append(f"Process:{record.processName}")
        
        if extra_info:
            return f"{original} [{', '.join(extra_info)}]"
        
        return original


def setup_logging(log_file: Optional[str] = None, level: Optional[int] = None, session_mode: bool = True) -> tuple[Path, Path]:
    """تنظیم لاگر اصلی برنامه با قابلیت session-based logging

    Args:
        log_file: مسیر فایل لاگ (پیش‌فرض: app.log)
        level: سطح لاگ‌گیری (پیش‌فرض: INFO)
        session_mode: ایجاد فایل لاگ جداگانه برای هر session (پیش‌فرض: True)
    
    Returns:
        tuple[Path, Path]: (session_log_file, master_log_file)
    
    ویژگی‌ها:
    - RotatingFileHandler -> app.log (چرخشی)
    - FileHandler -> master.log (فایل اصلی بدون محدودیت)
    - FileHandler -> session_TIMESTAMP.log (لاگ این اجرا)
    - StreamHandler -> نمایش در کنسول
    """
    log_path = Path(log_file) if log_file else DEFAULT_LOG_FILE
    ensure_logs_dir(log_path)
    ensure_logs_dir(MASTER_LOG_FILE)

    # تعیین سطح لاگ
    env_level = os.getenv("LOG_LEVEL")
    if level is None:
        if env_level:
            try:
                level = int(env_level)
            except Exception:
                level_name = env_level.upper()
                level = getattr(logging, level_name, logging.INFO)
        else:
            level = logging.INFO

    root = logging.getLogger()
    lvl = level
    if not isinstance(lvl, int):
        try:
            lvl = int(lvl)  # type: ignore[arg-type]
        except Exception:
            lvl = getattr(logging, str(lvl).upper(), logging.INFO)
    root.setLevel(lvl)

    # حذف handler های قبلی
    for h in list(root.handlers):
        root.removeHandler(h)

    # فرمتر جامع
    comprehensive_formatter = ComprehensiveFormatter(
        "%(asctime)s | %(levelname)-7s | [%(name)s:%(lineno)d] | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # فرمتر ساده برای کنسول
    console_formatter = logging.Formatter(
        "%(levelname)-7s | [%(name)s] %(message)s"
    )

    # 1. کنترل کننده کنسول (خروجی ساده)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(lvl)
    ch.setFormatter(console_formatter)
    root.addHandler(ch)

    # 2. گرداننده فایل چرخشی (app.log)
    fh_rotating = logging.handlers.RotatingFileHandler(
        filename=str(log_path), 
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=10, 
        encoding="utf-8"
    )
    fh_rotating.setLevel(lvl)
    fh_rotating.setFormatter(comprehensive_formatter)
    root.addHandler(fh_rotating)

    # 3. فایل لاگ اصلی (master.log) - همه چیز را ذخیره می‌کند
    fh_master = logging.FileHandler(
        filename=str(MASTER_LOG_FILE),
        mode='a',  # append mode
        encoding='utf-8'
    )
    fh_master.setLevel(logging.DEBUG)  # همه سطوح را ثبت کن
    fh_master.setFormatter(comprehensive_formatter)
    root.addHandler(fh_master)

    # 4. فایل لاگ Session (session_TIMESTAMP.log)
    session_log_file = None
    if session_mode:
        session_log_file = get_session_log_file()
        fh_session = logging.FileHandler(
            filename=str(session_log_file),
            mode='w',  # overwrite mode - فایل جدید برای هر session
            encoding='utf-8'
        )
        fh_session.setLevel(logging.DEBUG)  # همه چیز را ثبت کن
        fh_session.setFormatter(comprehensive_formatter)
        root.addHandler(fh_session)
        
        # نوشتن header برای session log
        root.info("="*80)
        root.info(f"🚀 NEW SESSION STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        root.info(f"📝 Session Log: {session_log_file}")
        root.info(f"📊 Master Log: {MASTER_LOG_FILE}")
        root.info("="*80)
    
    return session_log_file or log_path, MASTER_LOG_FILE


def install_exception_hook() -> None:
    """برای ثبت استثنائات مدیریت نشده، sys.excepthook را نصب کنید."""

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # اجازه دهید KeyboardInterrupt عبور کند تا امکان خروج تمیز فراهم شود
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.getLogger().exception("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception


__all__ = ["setup_logging", "install_exception_hook"]
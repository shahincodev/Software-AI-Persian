# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""سیستم لاگ‌گیری پیشرفته برای Software-AI

این ماژول یک سیستم لاگ‌گیری کامل و جامع فراهم می‌کند که:
- همه اقدامات کاربر را ثبت می‌کند
- همه خطاها و استثناها را با جزئیات کامل ذخیره می‌کند
- لاگ‌های جداگانه برای انواع مختلف رویدادها
- قابلیت جستجو و فیلتر در لاگ‌ها
- گزارش‌گیری خودکار از خطاها
- ذخیره‌سازی ساختاریافته (JSON)
"""

import logging
import logging.handlers
import json
import traceback
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Any, Optional, Dict, List
from enum import Enum
import threading


class LogLevel(Enum):
    """سطوح لاگ‌گیری."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class LogCategory(Enum):
    """دسته‌بندی لاگ‌ها."""
    SYSTEM = "system"           # رویدادهای سیستمی
    USER_ACTION = "user_action" # اقدامات کاربر
    AI_REQUEST = "ai_request"   # درخواست‌های AI
    AI_RESPONSE = "ai_response" # پاسخ‌های AI
    ERROR = "error"             # خطاها
    SECURITY = "security"       # رویدادهای امنیتی
    PERFORMANCE = "performance" # عملکرد
    NETWORK = "network"         # شبکه
    DATABASE = "database"       # پایگاه داده
    FILE_IO = "file_io"         # عملیات فایل


class AdvancedLogger:
    """لاگر پیشرفته با قابلیت‌های گسترده."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern برای یک instance واحد."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """مقداردهی اولیه سیستم لاگ‌گیری."""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.base_dir = Path("data/logs")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # فایل‌های لاگ مختلف
        self.log_files = {
            "main": self.base_dir / "app.log",
            "error": self.base_dir / "errors.log",
            "user_actions": self.base_dir / "user_actions.jsonl",
            "ai_logs": self.base_dir / "ai_interactions.jsonl",
            "security": self.base_dir / "security.jsonl",
            "debug": self.base_dir / "debug.log",
            "full_trace": self.base_dir / "full_trace.jsonl",
        }
        
        # Session tracking
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_log = self.base_dir / f"session_{self.session_id}.jsonl"
        
        # آمار
        self.stats = {
            "total_logs": 0,
            "errors": 0,
            "warnings": 0,
            "user_actions": 0,
            "ai_requests": 0,
            "start_time": datetime.now().isoformat(),
        }
        
        self._setup_loggers()
        self._install_hooks()
        
        self.log_system("Advanced logging system initialized", {
            "session_id": self.session_id,
            "log_directory": str(self.base_dir),
        })
    
    def _setup_loggers(self):
        """تنظیم تمام لاگرها."""
        # فرمت‌های مختلف
        self.detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        self.simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Main logger
        self.main_logger = self._create_logger(
            "main",
            self.log_files["main"],
            logging.INFO,
            self.detailed_formatter
        )
        
        # Error logger (فقط خطاها)
        self.error_logger = self._create_logger(
            "error",
            self.log_files["error"],
            logging.ERROR,
            self.detailed_formatter
        )
        
        # Debug logger (همه چیز با جزئیات)
        self.debug_logger = self._create_logger(
            "debug",
            self.log_files["debug"],
            logging.DEBUG,
            self.detailed_formatter
        )
    
    def _create_logger(
        self,
        name: str,
        log_file: Path,
        level: int,
        formatter: logging.Formatter,
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 10
    ) -> logging.Logger:
        """ایجاد یک logger با تنظیمات مشخص."""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.propagate = False
        
        # حذف handler های قبلی
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # File handler با rotation
        file_handler = logging.handlers.RotatingFileHandler(
            filename=str(log_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        
        # Force flush برای ذخیره فوری (حتی با Ctrl+C)
        class FlushingHandler(logging.handlers.RotatingFileHandler):
            def emit(self, record):
                super().emit(record)
                self.flush()  # فوری ذخیره می‌شه
        
        # جایگزین کردن با handler که flush می‌کنه
        file_handler = FlushingHandler(
            filename=str(log_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Console handler برای خطاها
        if level >= logging.ERROR:
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def _install_hooks(self):
        """نصب hook ها برای گرفتن تمام رویدادها."""
        # Exception hook
        def exception_hook(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            self.log_exception(
                exc_value,
                "Uncaught exception",
                {"type": exc_type.__name__}
            )
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
        
        sys.excepthook = exception_hook
        
        # Threading exception hook (Python 3.8+)
        if hasattr(threading, 'excepthook'):
            def thread_exception_hook(args):
                self.log_exception(
                    args.exc_value,
                    f"Uncaught exception in thread {args.thread.name}",
                    {
                        "thread": args.thread.name,
                        "type": args.exc_type.__name__ if args.exc_type else "Unknown"
                    }
                )
            threading.excepthook = thread_exception_hook
    
    def _write_jsonl(self, file_path: Path, data: Dict[str, Any]):
        """نوشتن یک خط JSON در فایل JSONL."""
        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, default=str)
                f.write('\n')
        except Exception as e:
            self.error_logger.error(f"Failed to write JSONL: {e}")
    
    def log_system(
        self,
        message: str,
        extra_data: Optional[Dict[str, Any]] = None,
        level: LogLevel = LogLevel.INFO
    ):
        """ثبت رویداد سیستمی."""
        self.stats["total_logs"] += 1
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "category": LogCategory.SYSTEM.value,
            "level": level.name,
            "message": message,
            "extra": extra_data or {},
        }
        
        # ثبت در فایل‌های مختلف
        self.main_logger.log(level.value, message)
        self._write_jsonl(self.session_log, log_entry)
        self._write_jsonl(self.log_files["full_trace"], log_entry)
    
    def log_user_action(
        self,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True
    ):
        """ثبت اقدام کاربر."""
        self.stats["total_logs"] += 1
        self.stats["user_actions"] += 1
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "category": LogCategory.USER_ACTION.value,
            "action": action,
            "success": success,
            "details": details or {},
        }
        
        self.main_logger.info(f"User action: {action} (success={success})")
        self._write_jsonl(self.log_files["user_actions"], log_entry)
        self._write_jsonl(self.session_log, log_entry)
        self._write_jsonl(self.log_files["full_trace"], log_entry)
    
    def log_ai_request(
        self,
        prompt: str,
        model: str,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """ثبت درخواست به AI."""
        self.stats["total_logs"] += 1
        self.stats["ai_requests"] += 1
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "category": LogCategory.AI_REQUEST.value,
            "prompt": prompt[:500],  # محدود کردن طول
            "prompt_length": len(prompt),
            "model": model,
            "parameters": parameters or {},
        }
        
        self.main_logger.info(f"AI request to {model} (prompt length: {len(prompt)})")
        self._write_jsonl(self.log_files["ai_logs"], log_entry)
        self._write_jsonl(self.session_log, log_entry)
        self._write_jsonl(self.log_files["full_trace"], log_entry)
    
    def log_ai_response(
        self,
        response: str,
        model: str,
        success: bool = True,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """ثبت پاسخ AI."""
        self.stats["total_logs"] += 1
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "category": LogCategory.AI_RESPONSE.value,
            "response": response[:500] if response else None,
            "response_length": len(response) if response else 0,
            "model": model,
            "success": success,
            "error": error,
            "metadata": metadata or {},
        }
        
        if success:
            self.main_logger.info(f"AI response from {model} (length: {len(response) if response else 0})")
        else:
            self.stats["errors"] += 1
            self.error_logger.error(f"AI response failed from {model}: {error}")
        
        self._write_jsonl(self.log_files["ai_logs"], log_entry)
        self._write_jsonl(self.session_log, log_entry)
        self._write_jsonl(self.log_files["full_trace"], log_entry)
    
    def log_error(
        self,
        message: str,
        error_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """ثبت خطا."""
        self.stats["total_logs"] += 1
        self.stats["errors"] += 1
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "category": LogCategory.ERROR.value,
            "message": message,
            "error_type": error_type,
            "details": details or {},
            "stack_trace": self._get_stack_trace(),
        }
        
        self.error_logger.error(f"{error_type}: {message}" if error_type else message)
        self._write_jsonl(self.log_files["error"], log_entry)
        self._write_jsonl(self.session_log, log_entry)
        self._write_jsonl(self.log_files["full_trace"], log_entry)
    
    def log_exception(
        self,
        exception: Exception,
        context: str = "",
        extra_data: Optional[Dict[str, Any]] = None
    ):
        """ثبت استثنا با جزئیات کامل."""
        self.stats["total_logs"] += 1
        self.stats["errors"] += 1
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "category": LogCategory.ERROR.value,
            "context": context,
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "stack_trace": traceback.format_exc(),
            "extra": extra_data or {},
        }
        
        self.error_logger.exception(f"{context}: {exception}" if context else str(exception))
        self._write_jsonl(self.log_files["error"], log_entry)
        self._write_jsonl(self.session_log, log_entry)
        self._write_jsonl(self.log_files["full_trace"], log_entry)
    
    def log_security(
        self,
        event: str,
        severity: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """ثبت رویداد امنیتی."""
        self.stats["total_logs"] += 1
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "category": LogCategory.SECURITY.value,
            "event": event,
            "severity": severity,
            "details": details or {},
        }
        
        level = logging.WARNING if severity == "high" else logging.INFO
        self.main_logger.log(level, f"Security event: {event} (severity: {severity})")
        self._write_jsonl(self.log_files["security"], log_entry)
        self._write_jsonl(self.session_log, log_entry)
        self._write_jsonl(self.log_files["full_trace"], log_entry)
    
    def log_performance(
        self,
        operation: str,
        duration: float,
        details: Optional[Dict[str, Any]] = None
    ):
        """ثبت اطلاعات عملکرد."""
        self.stats["total_logs"] += 1
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "category": LogCategory.PERFORMANCE.value,
            "operation": operation,
            "duration_seconds": duration,
            "details": details or {},
        }
        
        self.debug_logger.debug(f"Performance: {operation} took {duration:.3f}s")
        self._write_jsonl(self.session_log, log_entry)
        self._write_jsonl(self.log_files["full_trace"], log_entry)
    
    def _get_stack_trace(self) -> str:
        """دریافت stack trace فعلی."""
        return ''.join(traceback.format_stack()[:-1])
    
    def generate_error_report(self) -> str:
        """تولید گزارش خطاها."""
        report_file = self.base_dir / f"error_report_{self.session_id}.txt"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"ERROR REPORT - Session {self.session_id}\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write("=" * 80 + "\n\n")
                
                # خلاصه آمار
                f.write("STATISTICS:\n")
                f.write("-" * 40 + "\n")
                for key, value in self.stats.items():
                    f.write(f"{key}: {value}\n")
                f.write("\n")
                
                # خواندن تمام خطاها از فایل error
                f.write("DETAILED ERRORS:\n")
                f.write("-" * 40 + "\n")
                
                if self.log_files["error"].exists():
                    with open(self.log_files["error"], 'r', encoding='utf-8') as error_file:
                        errors = [json.loads(line) for line in error_file if line.strip()]
                        
                        for i, error in enumerate(errors, 1):
                            f.write(f"\nError #{i}:\n")
                            f.write(f"Time: {error.get('timestamp', 'Unknown')}\n")
                            f.write(f"Type: {error.get('exception_type', error.get('error_type', 'Unknown'))}\n")
                            f.write(f"Message: {error.get('exception_message', error.get('message', 'Unknown'))}\n")
                            
                            if 'stack_trace' in error:
                                f.write(f"\nStack Trace:\n{error['stack_trace']}\n")
                            
                            if 'details' in error or 'extra' in error:
                                f.write(f"\nDetails: {json.dumps(error.get('details', error.get('extra', {})), indent=2)}\n")
                            
                            f.write("-" * 40 + "\n")
                
                f.write("\n" + "=" * 80 + "\n")
                f.write("END OF REPORT\n")
                f.write("=" * 80 + "\n")
            
            return str(report_file)
        
        except Exception as e:
            self.error_logger.error(f"Failed to generate error report: {e}")
            return ""
    
    def get_stats(self) -> Dict[str, Any]:
        """دریافت آمار لاگ‌گیری."""
        self.stats["session_duration"] = (
            datetime.now() - datetime.fromisoformat(self.stats["start_time"])
        ).total_seconds()
        return self.stats.copy()
    
    def close(self):
        """بستن تمام handler ها و تولید گزارش نهایی."""
        self.log_system("Logging system shutting down", self.get_stats())
        
        # تولید گزارش خطا اگر خطایی وجود داشته باشد
        if self.stats["errors"] > 0:
            report_path = self.generate_error_report()
            if report_path:
                print(f"\n📊 Error report generated: {report_path}")
        
        # بستن تمام handler ها
        for logger in [self.main_logger, self.error_logger, self.debug_logger]:
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)


# Singleton instance
_advanced_logger: Optional[AdvancedLogger] = None


def get_advanced_logger() -> AdvancedLogger:
    """دریافت instance لاگر پیشرفته."""
    global _advanced_logger
    if _advanced_logger is None:
        _advanced_logger = AdvancedLogger()
    return _advanced_logger


def close_advanced_logger():
    """بستن لاگر پیشرفته."""
    global _advanced_logger
    if _advanced_logger is not None:
        _advanced_logger.close()
        _advanced_logger = None


__all__ = [
    "AdvancedLogger",
    "get_advanced_logger",
    "close_advanced_logger",
    "LogLevel",
    "LogCategory",
]

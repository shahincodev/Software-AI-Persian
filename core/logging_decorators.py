# SPDX-License-Identifier: NOASSERTION
# Copyright (c) 2025 Shahin

"""Decorator ها و ابزارهای کمکی برای لاگ‌گیری خودکار.

این ماژول شامل decorator هایی است که به طور خودکار:
- ورودی و خروجی توابع را لاگ می‌کند
- زمان اجرا را اندازه‌گیری می‌کند
- خطاها را گرفته و لاگ می‌کند
- اقدامات کاربر را ثبت می‌کند
"""

import functools
import time
import inspect
from typing import Any, Callable, Optional
from .advanced_logging import get_advanced_logger, LogLevel


def log_function_call(
    category: str = "function_call",
    log_args: bool = True,
    log_result: bool = True,
    log_errors: bool = True
):
    """Decorator برای لاگ کردن خودکار فراخوانی توابع.
    
    Args:
        category: دسته‌بندی لاگ
        log_args: آیا آرگومان‌ها لاگ شوند؟
        log_result: آیا نتیجه لاگ شود؟
        log_errors: آیا خطاها لاگ شوند؟
    
    Example:
        @log_function_call(category="user_action")
        def process_command(cmd: str):
            return f"Processed: {cmd}"
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_advanced_logger()
            func_name = f"{func.__module__}.{func.__qualname__}"
            
            # آماده‌سازی اطلاعات آرگومان‌ها
            call_info = {"function": func_name}
            if log_args:
                # گرفتن نام پارامترها
                sig = inspect.signature(func)
                bound_args = sig.bind_partial(*args, **kwargs)
                bound_args.apply_defaults()
                
                call_info["arguments"] = {
                    k: str(v)[:200] for k, v in bound_args.arguments.items()
                }
            
            start_time = time.time()
            
            try:
                # فراخوانی تابع
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # لاگ موفقیت
                if log_result:
                    result_str = str(result)[:200] if result is not None else "None"
                    call_info["result"] = result_str
                
                call_info["duration"] = duration
                call_info["success"] = True
                
                logger.log_system(
                    f"Function call: {func_name}",
                    call_info,
                    LogLevel.DEBUG
                )
                
                logger.log_performance(func_name, duration, call_info)
                
                return result
            
            except Exception as e:
                duration = time.time() - start_time
                
                if log_errors:
                    call_info["duration"] = duration
                    call_info["success"] = False
                    call_info["error"] = str(e)
                    
                    logger.log_exception(e, f"Error in {func_name}", call_info)
                
                raise
        
        return wrapper
    
    return decorator


def log_async_function_call(
    category: str = "async_function_call",
    log_args: bool = True,
    log_result: bool = True,
    log_errors: bool = True
):
    """Decorator برای لاگ کردن خودکار توابع async.
    
    Args:
        category: دسته‌بندی لاگ
        log_args: آیا آرگومان‌ها لاگ شوند؟
        log_result: آیا نتیجه لاگ شود؟
        log_errors: آیا خطاها لاگ شوند؟
    
    Example:
        @log_async_function_call(category="ai_request")
        async def ask_ai(prompt: str):
            return await ai.ask(prompt)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger = get_advanced_logger()
            func_name = f"{func.__module__}.{func.__qualname__}"
            
            # آماده‌سازی اطلاعات آرگومان‌ها
            call_info = {"function": func_name}
            if log_args:
                sig = inspect.signature(func)
                bound_args = sig.bind_partial(*args, **kwargs)
                bound_args.apply_defaults()
                
                call_info["arguments"] = {
                    k: str(v)[:200] for k, v in bound_args.arguments.items()
                }
            
            start_time = time.time()
            
            try:
                # فراخوانی تابع async
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # لاگ موفقیت
                if log_result:
                    result_str = str(result)[:200] if result is not None else "None"
                    call_info["result"] = result_str
                
                call_info["duration"] = duration
                call_info["success"] = True
                
                logger.log_system(
                    f"Async function call: {func_name}",
                    call_info,
                    LogLevel.DEBUG
                )
                
                logger.log_performance(func_name, duration, call_info)
                
                return result
            
            except Exception as e:
                duration = time.time() - start_time
                
                if log_errors:
                    call_info["duration"] = duration
                    call_info["success"] = False
                    call_info["error"] = str(e)
                    
                    logger.log_exception(e, f"Error in async {func_name}", call_info)
                
                raise
        
        return wrapper
    
    return decorator


def log_user_action(action_name: Optional[str] = None):
    """Decorator برای لاگ کردن اقدامات کاربر.
    
    Args:
        action_name: نام اقدام (اگر None باشد، از نام تابع استفاده می‌شود)
    
    Example:
        @log_user_action("open_notepad")
        def open_notepad():
            subprocess.run(["notepad.exe"])
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_advanced_logger()
            action = action_name or func.__name__
            
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.log_user_action(
                    action,
                    {
                        "function": f"{func.__module__}.{func.__qualname__}",
                        "duration": duration,
                    },
                    success=True
                )
                
                return result
            
            except Exception as e:
                duration = time.time() - start_time
                
                logger.log_user_action(
                    action,
                    {
                        "function": f"{func.__module__}.{func.__qualname__}",
                        "duration": duration,
                        "error": str(e),
                    },
                    success=False
                )
                
                raise
        
        return wrapper
    
    return decorator


class LogContext:
    """Context manager برای لاگ کردن یک بلوک از کد.
    
    Example:
        with LogContext("processing_data", {"file": "data.csv"}):
            # کد شما
            process_data()
    """
    
    def __init__(self, operation: str, details: Optional[dict] = None):
        self.operation = operation
        self.details = details or {}
        self.logger = get_advanced_logger()
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.log_system(
            f"Starting operation: {self.operation}",
            self.details,
            LogLevel.DEBUG
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is None:
            # موفقیت
            self.logger.log_system(
                f"Completed operation: {self.operation}",
                {**self.details, "duration": duration},
                LogLevel.DEBUG
            )
            self.logger.log_performance(self.operation, duration, self.details)
        else:
            # خطا
            self.logger.log_exception(
                exc_val,
                f"Failed operation: {self.operation}",
                {**self.details, "duration": duration}
            )
        
        return False  # Don't suppress exceptions


def log_ai_interaction(model: str):
    """Decorator برای لاگ کردن تعاملات AI.
    
    Args:
        model: نام مدل AI
    
    Example:
        @log_ai_interaction("gpt-4")
        async def ask_gpt(prompt: str):
            return await openai.chat.completions.create(...)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger = get_advanced_logger()
            
            # استخراج prompt از آرگومان‌ها
            prompt = ""
            if args:
                prompt = str(args[0])[:500]
            elif 'prompt' in kwargs:
                prompt = str(kwargs['prompt'])[:500]
            
            # لاگ درخواست
            logger.log_ai_request(prompt, model, {
                "function": f"{func.__module__}.{func.__qualname__}",
            })
            
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # لاگ پاسخ موفق
                logger.log_ai_response(
                    str(result)[:500] if result else "",
                    model,
                    success=True,
                    metadata={"duration": duration}
                )
                
                return result
            
            except Exception as e:
                duration = time.time() - start_time
                
                # لاگ پاسخ ناموفق
                logger.log_ai_response(
                    "",
                    model,
                    success=False,
                    error=str(e),
                    metadata={"duration": duration}
                )
                
                raise
        
        return wrapper
    
    return decorator


__all__ = [
    "log_function_call",
    "log_async_function_call",
    "log_user_action",
    "log_ai_interaction",
    "LogContext",
]

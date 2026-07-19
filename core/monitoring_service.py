# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""سرویس نظارت بر منابع سیستم و فرآیندها.

این ماژول به صورت مداوم وضعیت سیستم را زیر نظر دارد و می‌تواند:
- مصرف CPU, RAM, Disk را گزارش دهد
- فرآیندهای پرمصرف را شناسایی کند
- هشدار دهد اگر منابع به حد بحرانی برسند
- تاریخچه استفاده از منابع را ذخیره کند
"""

from __future__ import annotations

import logging
import importlib.util
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from threading import Event, Thread
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

# تلاش برای import psutil
PSUTIL_AVAILABLE = importlib.util.find_spec("psutil") is not None
if not PSUTIL_AVAILABLE:
    logger.warning("psutil unavailable - monitoring service is disabled")


@dataclass
class SystemSnapshot:
    """یک نما از وضعیت سیستم در یک لحظه."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float = 0.0
    top_processes: list[dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        """تبدیل به دیکشنری."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "memory_used_gb": self.memory_used_gb,
            "memory_total_gb": self.memory_total_gb,
            "disk_percent": self.disk_percent,
            "top_processes": self.top_processes,
        }
    
    def is_critical(self, cpu_threshold: float = 90, mem_threshold: float = 90) -> bool:
        """آیا وضعیت سیستم بحرانی است؟"""
        return self.cpu_percent > cpu_threshold or self.memory_percent > mem_threshold


class MonitoringService:
    """سرویس نظارت مداوم بر سیستم."""
    
    def __init__(
        self,
        interval_seconds: float = 5.0,
        history_size: int = 100,
        alert_callback: Optional[Callable[[str], None]] = None,
    ):
        """
        Args:
            interval_seconds: فاصله زمانی بین هر بررسی
            history_size: تعداد نماهای ذخیره‌شده در تاریخچه
            alert_callback: تابع برای دریافت هشدارها
        """
        if not PSUTIL_AVAILABLE:
            raise RuntimeError("psutil is not installed - monitoring service cannot be started")
        
        self.interval = interval_seconds
        self.history: deque[SystemSnapshot] = deque(maxlen=history_size)
        self.alert_callback = alert_callback
        
        # کنترل thread
        self._thread: Optional[Thread] = None
        self._stop_event = Event()
        self._running = False
        
        # آستانه‌های هشدار
        self.cpu_warning_threshold = 70.0
        self.cpu_critical_threshold = 90.0
        self.memory_warning_threshold = 70.0
        self.memory_critical_threshold = 90.0
        
        # وضعیت هشدارها
        self._cpu_alert_sent = False
        self._memory_alert_sent = False
    
    def start(self) -> None:
        """شروع نظارت در یک thread جداگانه."""
        if self._running:
            logger.warning("Monitoring service is already running")
            return
        
        self._stop_event.clear()
        self._running = True
        self._thread = Thread(target=self._monitor_loop, daemon=True, name="SystemMonitor")
        self._thread.start()
        
        logger.info("Monitoring service started (interval: %.1f seconds)", self.interval)
    
    def stop(self, timeout: float = 5.0) -> None:
        """نظارت را متوقف کنید."""
        if not self._running:
            return
        
        logger.info("Request to stop monitoring service...")
        self._stop_event.set()
        
        if self._thread:
            self._thread.join(timeout=timeout)
            if self._thread.is_alive():
                logger.warning("Monitoring thread is still alive after %s seconds", timeout)
        
        self._running = False
        logger.info("Monitoring service stopped")
    
    def _monitor_loop(self) -> None:
        """حلقه اصلی نظارت."""
        import psutil as ps
        
        while not self._stop_event.is_set():
            try:
                # گرفتن نمای فعلی
                snapshot = self._take_snapshot(ps)
                self.history.append(snapshot)
                
                # بررسی برای هشدار
                self._check_alerts(snapshot)
                
            except Exception as e:
                logger.exception("Error in monitoring loop: %s", e)
            
            # صبر برای دور بعدی
            self._stop_event.wait(self.interval)
    
    def _take_snapshot(self, ps: Any) -> SystemSnapshot:
        """گرفتن یک نما از وضعیت فعلی سیستم."""
        # CPU
        cpu_percent = ps.cpu_percent(interval=0.1)
        
        # Memory
        mem = ps.virtual_memory()
        memory_percent = mem.percent
        memory_used_gb = round(mem.used / (1024**3), 2)
        memory_total_gb = round(mem.total / (1024**3), 2)
        
        # Disk (فقط درایو اصلی)
        try:
            disk = ps.disk_usage("/")
            disk_percent = disk.percent
        except Exception:
            disk_percent = 0.0
        
        # فرآیندهای پرمصرف (۵ تای اول)
        top_processes = []
        try:
            processes = []
            for proc in ps.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
                try:
                    processes.append(proc.info)
                except (ps.NoSuchProcess, ps.AccessDenied):
                    continue
            
            # مرتب‌سازی بر اساس CPU
            processes.sort(key=lambda x: x.get("cpu_percent", 0), reverse=True)
            top_processes = processes[:5]
        
        except Exception as e:
            logger.debug("Error getting process list: %s", e)
        
        return SystemSnapshot(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_gb=memory_used_gb,
            memory_total_gb=memory_total_gb,
            disk_percent=disk_percent,
            top_processes=top_processes,
        )
    
    def _check_alerts(self, snapshot: SystemSnapshot) -> None:
        """بررسی و ارسال هشدارها."""
        # هشدار CPU
        if snapshot.cpu_percent > self.cpu_critical_threshold:
            if not self._cpu_alert_sent:
                self._send_alert(
                    f"🔴 Critical alert: CPU at {snapshot.cpu_percent:.1f}%!"
                )
                self._cpu_alert_sent = True
        elif snapshot.cpu_percent > self.cpu_warning_threshold:
            if not self._cpu_alert_sent:
                self._send_alert(
                    f"🟡 Warning: CPU at {snapshot.cpu_percent:.1f}%"
                )
                self._cpu_alert_sent = True
        else:
            # ریست کردن وضعیت هشدار اگر به حالت عادی برگشت
            if self._cpu_alert_sent:
                self._send_alert(f"✅ CPU returned to normal: {snapshot.cpu_percent:.1f}%")
                self._cpu_alert_sent = False
        
        # هشدار Memory
        if snapshot.memory_percent > self.memory_critical_threshold:
            if not self._memory_alert_sent:
                self._send_alert(
                    f"🔴 Critical alert: RAM at {snapshot.memory_percent:.1f}% "
                    f"({snapshot.memory_used_gb}/{snapshot.memory_total_gb} GB)"
                )
                self._memory_alert_sent = True
        elif snapshot.memory_percent > self.memory_warning_threshold:
            if not self._memory_alert_sent:
                self._send_alert(
                    f"🟡 Warning: RAM at {snapshot.memory_percent:.1f}%"
                )
                self._memory_alert_sent = True
        else:
            if self._memory_alert_sent:
                self._send_alert(
                    f"✅ RAM returned to normal: {snapshot.memory_percent:.1f}%"
                )
                self._memory_alert_sent = False
    
    def _send_alert(self, message: str) -> None:
        """ارسال هشدار."""
        logger.warning("ALERT: %s", message)
        
        if self.alert_callback:
            try:
                self.alert_callback(message)
            except Exception as e:
                logger.exception("Error executing alert callback: %s", e)
    
    def get_current_snapshot(self) -> Optional[SystemSnapshot]:
        """دریافت آخرین نما."""
        if not PSUTIL_AVAILABLE:
            return None
        
        import psutil as ps
        return self._take_snapshot(ps)
    
    def get_latest_snapshot(self) -> Optional[SystemSnapshot]:
        """دریافت آخرین نمای ذخیره‌شده در تاریخچه."""
        if not self.history:
            return None
        return self.history[-1]
    
    def get_history(self, last_n: Optional[int] = None) -> list[SystemSnapshot]:
        """دریافت تاریخچه نماها.
        
        Args:
            last_n: تعداد آخرین نماها (اگر None باشد، همه برگردانده می‌شود)
        """
        if last_n is None:
            return list(self.history)
        return list(self.history)[-last_n:]
    
    def get_average_usage(self, last_n: int = 10) -> dict[str, float]:
        """میانگین استفاده از منابع در n نمای اخیر."""
        snapshots = self.get_history(last_n)
        if not snapshots:
            return {"cpu_percent": 0.0, "memory_percent": 0.0, "disk_percent": 0.0}
        
        avg_cpu = sum(s.cpu_percent for s in snapshots) / len(snapshots)
        avg_mem = sum(s.memory_percent for s in snapshots) / len(snapshots)
        avg_disk = sum(s.disk_percent for s in snapshots) / len(snapshots)
        
        return {
            "cpu_percent": round(avg_cpu, 2),
            "memory_percent": round(avg_mem, 2),
            "disk_percent": round(avg_disk, 2),
        }
    
    def get_summary(self) -> str:
        """خلاصه‌ای از وضعیت فعلی سیستم."""
        snapshot = self.get_latest_snapshot()
        if not snapshot:
            return "No data available"
        
        lines = [
            "📊 System Status:",
            f"  CPU: {snapshot.cpu_percent:.1f}%",
            f"  RAM: {snapshot.memory_percent:.1f}% ({snapshot.memory_used_gb}/{snapshot.memory_total_gb} GB)",
            f"  Disk: {snapshot.disk_percent:.1f}%",
        ]
        
        if snapshot.top_processes:
            lines.append("High-consuming processes:")
            for proc in snapshot.top_processes[:3]:
                lines.append(
                    f"    - {proc.get('name')}: CPU {proc.get('cpu_percent', 0):.1f}%"
                )
        
        return "\n".join(lines)
    
    @property
    def is_running(self) -> bool:
        """آیا سرویس در حال اجراست؟"""
        return self._running


__all__ = ["MonitoringService", "SystemSnapshot"]

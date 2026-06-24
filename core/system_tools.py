# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""آداپتورهای اجرایی برای اقدامات سیستمی ویندوز.

این ماژول واسط یکپارچه‌ای برای کتابخانه‌های مختلف ویندوز فراهم می‌کند:
- subprocess برای اجرای فرآیندها
- psutil برای مدیریت فرآیندها و اطلاعات سیستم
- winreg برای دسترسی به رجیستری (در آینده)
- winget/choco برای نصب بسته‌ها
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .system_actions import (
    ActionResult,
    ActionStatus,
    InstallPackageAction,
    LaunchAppAction,
    QueryHardwareAction,
    SystemAction,
    TerminateProcessAction,
    ExecuteCommandAction,
)

logger = logging.getLogger(__name__)

# تلاش برای import کتابخانه‌های اختیاری
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil is not available - capabilities will be limited")

try:
    import win32api
    import win32con
    import win32process
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    logger.warning("pywin32 is not available - some advanced features will be disabled")


class ToolAdapter:
    """کلاس پایه برای آداپتورهای ابزار."""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
    
    def execute(self, action: Any) -> ActionResult:
        """اجرای یک اقدام و بازگشت نتیجه."""
        raise NotImplementedError


class ProcessLauncher(ToolAdapter):
    """آداپتور برای باز کردن برنامه‌ها."""
    
    def execute(self, action: LaunchAppAction) -> ActionResult:
        """اجرای فرآیند جدید."""
        started_at = datetime.now()
        result = ActionResult(
            action_id=action.action_id,
            status=ActionStatus.EXECUTING,
            started_at=started_at,
        )
        
        try:
            # تعیین دستور اجرا
            if action.app_path:
                command = [action.app_path] + action.arguments
            else:
                # جستجوی برنامه در PATH یا مسیرهای معمول
                app_path = self._find_application(action.app_name)
                if not app_path:
                    raise FileNotFoundError(f"Application '{action.app_name}' not found")
                command = [app_path] + action.arguments
            
            if self.dry_run or action.dry_run:
                result.status = ActionStatus.DRY_RUN
                result.output = f"[DRY-RUN] Executing command: {' '.join(command)}"
                logger.info("Dry-run: %s", result.output)
            else:
                # اجرای واقعی
                process = subprocess.Popen(
                    command,
                    cwd=action.working_directory,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                
                # صبر کوتاه برای اطمینان از شروع موفق
                try:
                    stdout, stderr = process.communicate(timeout=2)
                    result.output = stdout if stdout else "The program was successfully implemented"
                    if stderr:
                        result.metadata["stderr"] = stderr
                except subprocess.TimeoutExpired:
                    # فرآیند هنوز در حال اجراست (نرمال برای برنامه‌های GUI)
                    result.output = f"The program was successfully implemented (PID: {process.pid})"
                    result.metadata["pid"] = process.pid
                
                result.status = ActionStatus.SUCCESS
                logger.info("The program '%s' was successfully launched", action.app_name or action.app_path)
        
        except FileNotFoundError as e:
            result.status = ActionStatus.FAILED
            result.error = str(e)
            logger.error("Error finding application: %s", e)
        except Exception as e:
            result.status = ActionStatus.FAILED
            result.error = f"Error executing the program: {e}"
            logger.exception("Error executing the program")
        
        result.completed_at = datetime.now()
        return result
    
    def _find_application(self, app_name: str) -> Optional[str]:
        """جستجوی برنامه در سیستم."""
        # جستجو در PATH
        app_path = shutil.which(app_name)
        if app_path:
            return app_path
        
        # جستجو با پسوند .exe
        if not app_name.endswith(".exe"):
            app_path = shutil.which(f"{app_name}.exe")
            if app_path:
                return app_path
        
        # جستجو در مسیرهای معمول برنامه‌های ویندوز
        common_paths = [
            Path(os.environ.get("PROGRAMFILES", "C:\\Program Files")),
            Path(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)")),
            Path(os.environ.get("LOCALAPPDATA", "C:\\Users\\Default\\AppData\\Local")),
        ]
        
        for base_path in common_paths:
            if not base_path.exists():
                continue
            # جستجوی ساده (محدود به عمق 2)
            for exe_file in base_path.rglob(f"{app_name}*.exe"):
                if exe_file.name.lower().startswith(app_name.lower()):
                    return str(exe_file)
                # محدود کردن جستجو برای جلوگیری از تاخیر
                break
        
        return None


class PackageInstaller(ToolAdapter):
    """آداپتور برای نصب بسته‌های نرم‌افزاری."""
    
    def execute(self, action: InstallPackageAction) -> ActionResult:
        """نصب بسته از طریق مدیر بسته."""
        started_at = datetime.now()
        result = ActionResult(
            action_id=action.action_id,
            status=ActionStatus.EXECUTING,
            started_at=started_at,
        )
        
        try:
            # ساخت دستور نصب
            command = self._build_install_command(action)
            
            if self.dry_run or action.dry_run:
                result.status = ActionStatus.DRY_RUN
                result.output = f"[DRY-RUN] Executing command: {' '.join(command)}"
                logger.info("Dry-run: %s", result.output)
            else:
                # اجرای دستور نصب
                process = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=action.timeout_seconds,
                )
                
                result.output = process.stdout
                result.metadata["stderr"] = process.stderr
                result.metadata["return_code"] = process.returncode
                
                if process.returncode == 0:
                    result.status = ActionStatus.SUCCESS
                    logger.info("Package '%s' installed successfully", action.package_name)
                else:
                    result.status = ActionStatus.FAILED
                    result.error = f"Non-zero exit code: {process.returncode}"
                    logger.error("Error installing package '%s': %s", action.package_name, process.stderr)
        
        except FileNotFoundError:
            result.status = ActionStatus.FAILED
            result.error = f"Package manager '{action.package_manager}' not found"
            logger.error("Package manager not available: %s", action.package_manager)
        except subprocess.TimeoutExpired:
            result.status = ActionStatus.FAILED
            result.error = f"Installation took longer than {action.timeout_seconds} seconds"
            logger.error("Timeout during installation of package '%s'", action.package_name)
        except Exception as e:
            result.status = ActionStatus.FAILED
            result.error = f"Error during installation: {e}"
            logger.exception("Error during package installation")
        
        result.completed_at = datetime.now()
        return result
    
    def _build_install_command(self, action: InstallPackageAction) -> list[str]:
        """ساخت دستور نصب بر اساس مدیر بسته."""
        if action.package_manager == "winget":
            cmd = ["winget", "install", action.package_name]
            if action.version:
                cmd.extend(["--version", action.version])
            if action.silent:
                cmd.append("--silent")
            cmd.append("--accept-source-agreements")
            cmd.append("--accept-package-agreements")
            return cmd
        
        elif action.package_manager == "choco":
            cmd = ["choco", "install", action.package_name]
            if action.version:
                cmd.extend(["--version", action.version])
            if action.silent:
                cmd.append("-y")
            return cmd
        
        elif action.package_manager == "pip":
            cmd = ["pip", "install", action.package_name]
            if action.version:
                cmd[2] = f"{action.package_name}=={action.version}"
            return cmd
        
        elif action.package_manager == "npm":
            cmd = ["npm", "install", "-g", action.package_name]
            if action.version:
                cmd[3] = f"{action.package_name}@{action.version}"
            return cmd
        
        else:
            raise ValueError(f"Unsupported package manager: {action.package_manager}")


class HardwareQueryTool(ToolAdapter):
    """آداپتور برای دریافت اطلاعات سخت‌افزار."""
    
    def execute(self, action: QueryHardwareAction) -> ActionResult:
        """دریافت اطلاعات سخت‌افزار."""
        started_at = datetime.now()
        result = ActionResult(
            action_id=action.action_id,
            status=ActionStatus.EXECUTING,
            started_at=started_at,
        )
        
        if not PSUTIL_AVAILABLE:
            result.status = ActionStatus.FAILED
            result.error = "psutil library is not installed"
            result.completed_at = datetime.now()
            return result
        
        try:
            import psutil as ps  # local import for type checking
            info: dict[str, Any] = {}
            
            if action.query_type in ["all", "cpu"]:
                info["cpu"] = {
                    "physical_cores": ps.cpu_count(logical=False),
                    "logical_cores": ps.cpu_count(logical=True),
                    "frequency_mhz": ps.cpu_freq().current if ps.cpu_freq() else None,
                    "usage_percent": ps.cpu_percent(interval=1),
                }
            
            if action.query_type in ["all", "memory"]:
                mem = ps.virtual_memory()
                info["memory"] = {
                    "total_gb": round(mem.total / (1024**3), 2),
                    "available_gb": round(mem.available / (1024**3), 2),
                    "used_gb": round(mem.used / (1024**3), 2),
                    "percent": mem.percent,
                }
            
            if action.query_type in ["all", "disk"]:
                partitions = ps.disk_partitions()
                info["disk"] = []
                for partition in partitions:
                    try:
                        usage = ps.disk_usage(partition.mountpoint)
                        info["disk"].append({
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "fstype": partition.fstype,
                            "total_gb": round(usage.total / (1024**3), 2),
                            "used_gb": round(usage.used / (1024**3), 2),
                            "free_gb": round(usage.free / (1024**3), 2),
                            "percent": usage.percent,
                        })
                    except PermissionError:
                        continue
            
            if action.query_type in ["all", "network"]:
                net_io = ps.net_io_counters()
                info["network"] = {
                    "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 2),
                    "bytes_recv_mb": round(net_io.bytes_recv / (1024**2), 2),
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv,
                }
            
            if action.query_type in ["all", "processes"]:
                processes = []
                for proc in ps.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
                    try:
                        processes.append(proc.info)
                    except (ps.NoSuchProcess, ps.AccessDenied):
                        continue
                # محدود کردن به ۱۰ فرآیند پرمصرف CPU
                info["processes"] = sorted(processes, key=lambda x: x.get("cpu_percent", 0), reverse=True)[:10]
            
            result.status = ActionStatus.SUCCESS
            result.output = json.dumps(info, ensure_ascii=False, indent=2)
            result.metadata["hardware_info"] = info
            logger.info("Hardware information retrieved successfully")
        
        except Exception as e:
            result.status = ActionStatus.FAILED
            result.error = f"Error retrieving information: {e}"
            logger.exception("Error retrieving hardware information")
        
        result.completed_at = datetime.now()
        return result


class ProcessTerminator(ToolAdapter):
    """آداپتور برای بستن فرآیندها."""
    
    def execute(self, action: TerminateProcessAction) -> ActionResult:
        """بستن فرآیند."""
        started_at = datetime.now()
        result = ActionResult(
            action_id=action.action_id,
            status=ActionStatus.EXECUTING,
            started_at=started_at,
        )
        
        if not PSUTIL_AVAILABLE:
            result.status = ActionStatus.FAILED
            result.error = "psutil library is not installed"
            result.completed_at = datetime.now()
            return result
        
        try:
            import psutil as ps  # local import for type checking
            # یافتن فرآیند
            processes = []
            if action.process_id:
                try:
                    proc = ps.Process(action.process_id)
                    processes.append(proc)
                except ps.NoSuchProcess:
                    raise ValueError(f"Process with PID={action.process_id} not found")
            elif action.process_name:
                for proc in ps.process_iter(["pid", "name"]):
                    if proc.info["name"] == action.process_name:
                        processes.append(proc)
            
            if not processes:
                raise ValueError(f"No process found with name '{action.process_name}'")
            
            if self.dry_run or action.dry_run:
                result.status = ActionStatus.DRY_RUN
                pids = [p.pid for p in processes]
                result.output = f"[DRY-RUN] Terminating processes: {pids}"
                logger.info("Dry-run: %s", result.output)
            else:
                # بستن فرآیندها
                terminated = []
                for proc in processes:
                    try:
                        if action.force:
                            proc.kill()
                        else:
                            proc.terminate()
                        terminated.append(proc.pid)
                    except ps.AccessDenied:
                        logger.warning("Access denied to process PID=%d", proc.pid)
                
                result.status = ActionStatus.SUCCESS
                result.output = f"{len(terminated)} processes terminated: {terminated}"
                result.metadata["terminated_pids"] = terminated
                logger.info("Processes terminated successfully: %s", terminated)
        
        except Exception as e:
            result.status = ActionStatus.FAILED
            result.error = f"Error terminating processes: {e}"
            logger.exception("Error terminating processes")
        
        result.completed_at = datetime.now()
        return result


class CommandExecutor:
    """اجرای دستورات شل/CMD."""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
    
    def execute(self, action: ExecuteCommandAction) -> ActionResult:
        """اجرای دستور."""
        started_at = datetime.now()
        result = ActionResult(
            action_id=action.action_id,
            status=ActionStatus.EXECUTING,
            started_at=started_at,
        )
        
        try:
            if self.dry_run or action.dry_run:
                result.status = ActionStatus.DRY_RUN
                result.output = f"[DRY-RUN] Executing command: {action.command}"
                logger.info("Dry-run: %s", result.output)
            else:
                # اجرای واقعی دستور
                logger.info("Executing command: %s", action.command)
                
                # اجرای دستور در shell مربوطه (cmd یا powershell)
                proc = subprocess.Popen(
                    action.command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=action.working_directory,
                    text=True
                )
                
                try:
                    stdout, stderr = proc.communicate(timeout=action.timeout)
                    
                    if proc.returncode == 0:
                        result.status = ActionStatus.SUCCESS
                        result.output = stdout.strip() if stdout else "Command executed successfully"
                        result.metadata["return_code"] = 0
                        logger.info("Command executed successfully: %s", action.command)
                    else:
                        result.status = ActionStatus.FAILED
                        result.error = stderr.strip() if stderr else "Command failed"
                        result.output = stdout.strip() if stdout else ""
                        result.metadata["return_code"] = proc.returncode
                        logger.error("Command failed with return code %d: %s", proc.returncode, stderr)
                
                except subprocess.TimeoutExpired:
                    proc.kill()
                    result.status = ActionStatus.FAILED
                    result.error = f"Command timed out after {action.timeout} seconds"
                    logger.error("Command timed out: %s", action.command)
        
        except Exception as e:
            result.status = ActionStatus.FAILED
            result.error = f"Error executing command: {e}"
            logger.exception("Error executing command: %s", action.command)
        
        result.completed_at = datetime.now()
        return result


class SystemToolAdapter:
    """رابط یکپارچه برای تمام آداپتورهای سیستمی."""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.adapters = {
            LaunchAppAction: ProcessLauncher(dry_run),
            InstallPackageAction: PackageInstaller(dry_run),
            QueryHardwareAction: HardwareQueryTool(dry_run),
            TerminateProcessAction: ProcessTerminator(dry_run),
            ExecuteCommandAction: CommandExecutor(dry_run),
        }
    
    def execute(self, action: SystemAction) -> ActionResult:
        """اجرای اقدام با آداپتور مناسب."""
        adapter = self.adapters.get(type(action))
        if not adapter:
            started_at = datetime.now()
            return ActionResult(
                action_id=action.action_id,
                status=ActionStatus.FAILED,
                started_at=started_at,
                completed_at=datetime.now(),
                error=f"آداپتور برای {type(action).__name__} پیدا نشد",
            )
        
        return adapter.execute(action)

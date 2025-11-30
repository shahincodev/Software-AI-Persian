# 🚀 شروع سریع - Windows Automation

## نصب سریع

```powershell
# نصب وابستگی‌ها
pip install psutil>=5.9.0

# یا
pip install -r requirements.txt
```

## اولین اجرا

```python
import asyncio
from core import (
    QueryHardwareAction,
    ExecutionManager,
)

async def main():
    # دریافت اطلاعات سخت‌افزار
    action = QueryHardwareAction(query_type="all")
    
    manager = ExecutionManager()
    manager.submit(action)
    
    result = await manager.execute_next()
    print(result.output)

asyncio.run(main())
```

## اجرای نمونه کامل

```powershell
python examples/windows_automation_demo.py
```

## مستندات کامل

📖 [راهنمای کامل Windows Automation](docs/WINDOWS_AUTOMATION.md)

## قابلیت‌های اصلی

✅ باز کردن برنامه‌ها  
✅ نصب نرم‌افزار  
✅ دریافت اطلاعات سخت‌افزار  
✅ مدیریت فرآیندها  
✅ نظارت real-time  
✅ فیلتر امنیتی هوشمند  
✅ یکپارچگی با AI  

---

**💡 نکته**: همیشه ابتدا با `dry_run=True` تست کنید!

---

**توسعه‌دهندگان**: Shahin  
**نسخه**: 1.0  
**تاریخ**: November 2025  
**وضعیت**: Production Ready ✅

---

## 📄 مجوز

Copyright (c) 2025 Shahin - SPDX-License-Identifier: NOASSERTION

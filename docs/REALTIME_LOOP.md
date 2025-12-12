# Realtime Loop (Lightweight)

حلقه زمان‌واقعی سبک برای مشاهده صفحه، تفسیر ساده، و اقدام محدود در حالت Power.

## اهداف
- فراهم‌کردن حلقه capture → interpret → act با مصرف کم (۱–۲ fps).
- احترام به پروفایل ایمنی (Safe/Power) و kill-switch.
- امکان تزریق callback برای تست و سفارشی‌سازی.

## ساختار
- فایل: `core/realtime_loop.py`
- کلاس‌ها:
  - `RealtimeSnapshot`: خروجی مرحله capture
  - `RealtimeDecision`: تصمیم مرحله interpret
  - `RealtimeLoop`: حلقه اصلی

## رفتار پیش‌فرض
- Safe: فقط observe/hint، بدون اقدام واقعی.
- Power: تصمیم `act` محافظه‌کارانه، سقف اقدام متوالی (`max_actions`) برای جلوگیری از اسپم.
- Capture: تلاش برای ذخیره اسکرین در `data/logs/cache/realtime_last.png` (در صورت پشتیبانی Vision).

## استفاده
- نمونه‌سازی:
```python
loop = RealtimeLoop(
    vision=vision,
    session_control=session_control,
    action_controller=action_controller,
    fps=1.0,
    max_actions=3,
    action_callback=custom_cb,  # اختیاری
)
```
- اجرا:
```python
asyncio.create_task(loop.run_loop())
# برای توقف نرم:
loop.stop()
```

## پارامترها
- `fps`: نرخ حلقه (پیشنهاد 1–2 برای مصرف کم)
- `max_actions`: سقف اقدام متوالی قبل از ارزیابی مجدد
- `action_callback`: تابع اختیاری برای اجرای اکشن (برای تست یا سفارشی‌سازی)

## ایمنی
- از `SessionControl` (main.py) برای pause/resume/stop و آستانه ریسک استفاده می‌شود.
- در Safe هیچ اکشن واقعی اجرا نمی‌شود.
- در Power، اگر callback یا کنترل‌کننده اکشن تزریق شود، با سقف اقدام عمل می‌کند.

## تست
- فایل: `tests/test_realtime_loop.py`
- پوشش:
  - حالت Safe (observe-only)
  - حالت Power با محدودیت `max_actions`
  - pause/resume/stop در حلقه

## نکات توسعه آینده
- افزودن تفسیر پیشرفته (OCR، تشخیص پنجره فعال، الگوهای UI).
- بودجه‌بندی زمان/ریسک پویا.
- ثبت وقایع دقیق برای دیباگ حلقه.

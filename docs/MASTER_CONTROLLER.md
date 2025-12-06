<div dir="rtl">

# 🧠 Master AI Controller - راهنمای کامل

**مغز اصلی سیستم Software-AI**

---

## 📖 معرفی

**Master AI Controller** قلب تپنده سیستم Software-AI است. این ماژول تمام درخواست‌های کاربر را دریافت می‌کند، به صورت هوشمند آن‌ها را تحلیل می‌کند، به ابزار مناسب هدایت می‌کند و در نهایت پاسخ‌های انسانی و قابل فهم تولید می‌کند.

### چرا Master Controller؟

قبل از Master Controller:
```
کاربر: "CPU چقدره؟"
سیستم: {"cpu_percent": 45.2, "cores": 24}  ❌ خروجی فنی و غیرقابل فهم
```

بعد از Master Controller:
```
کاربر: "CPU چقدره؟"
سیستم: "پردازنده شما ۴۵٪ مشغول است و ۲۴ هسته دارید. وضعیت خوبی است!"  ✅
```

---

## 🎯 معماری

```
┌─────────────────────────────────────────────────┐
│          🧠 Master AI Controller                │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  1️⃣  REQUEST ANALYSIS                   │   │
│  │  تحلیل عمیق درخواست کاربر با AI        │   │
│  └─────────────────────────────────────────┘   │
│               ▼                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  2️⃣  INTELLIGENT ROUTING                │   │
│  │  تشخیص ابزار مناسب برای اجرا            │   │
│  └─────────────────────────────────────────┘   │
│               ▼                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  3️⃣  TOOL EXECUTION                     │   │
│  │  اجرای درخواست با ابزار انتخابی         │   │
│  └─────────────────────────────────────────┘   │
│               ▼                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  4️⃣  RESPONSE HUMANIZATION              │   │
│  │  تبدیل پاسخ فنی به زبان انسانی         │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
             │
             ├──────────┬──────────┬──────────┐
             ▼          ▼          ▼          ▼
      ┌──────────┐ ┌─────────┐ ┌─────────┐ ┌──────┐
      │ Desktop  │ │ System  │ │ Browser │ │ Chat │
      │ Actions  │ │  Tools  │ │   Use   │ │  AI  │
      └──────────┘ └─────────┘ └─────────┘ └──────┘
```

---

## 🚀 استفاده سریع

### نصب

Master Controller به صورت خودکار در `main.py` فعال می‌شود:

```bash
python main.py --enable-automation
```

### مثال ساده

```python
import asyncio
from core.master_controller import MasterAIController
from core.intelligent_agent import IntelligentSystemAgent

async def main():
    # مقداردهی اولیه
    system_agent = IntelligentSystemAgent()
    master = MasterAIController(system_agent=system_agent)
    
    # پردازش درخواست
    result = await master.process_request("چقدر RAM دارم؟")
    
    print(result.human_response)
    # "شما ۶۴ گیگابایت حافظه دارید که ۳۰ گیگابایت آن آزاد است."

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🔧 قابلیت‌ها

### 1️⃣ Intelligent Routing

Master Controller به صورت خودکار تشخیص می‌دهد که درخواست به کدام ابزار نیاز دارد:

```python
# درخواست‌های مختلف → ابزارهای مختلف

"باز کن نوت‌پد"          → ToolType.DESKTOP
"CPU چقدره؟"             → ToolType.SYSTEM  
"هوا امروز چطوره؟"      → ToolType.BROWSER
"هوش مصنوعی چیست؟"      → ToolType.CHAT
"پوشه MyDocs بساز"      → ToolType.FILE
"برو سایت X و..."       → ToolType.AUTONOMOUS
```

**نحوه کار:**

1. **AI-Based Routing**: از مدل‌های هوش مصنوعی برای تحلیل عمیق استفاده می‌کند
2. **Confidence Score**: اطمینان از تصمیم را محاسبه می‌کند (0.0 - 1.0)
3. **Fallback**: اگر AI در دسترس نباشد، از الگوریتم‌های ساده استفاده می‌کند

### 2️⃣ Response Humanization

تبدیل خروجی‌های فنی به پاسخ‌های انسانی:

```python
# ورودی: خروجی فنی
raw = {
    "cpu": {"usage_percent": 45.2, "cores": 24},
    "ram": {"total_gb": 63.69, "available_gb": 30.5, "used_percent": 52.1}
}

# خروجی: پاسخ انسانی
human = """
پردازنده شما ۴۵٪ مشغول است و ۲۴ هسته دارد.
حافظه سیستم: ۶۴ گیگابایت (۳۰ گیگابایت آزاد)
وضعیت کلی: خوب ✅
"""
```

### 3️⃣ Multi-Language Support

پاسخ به زبان درخواست کاربر:

```python
# فارسی
await master.process_request("CPU چقدره؟")
# "پردازنده شما ۴۵٪ مشغول است..."

# English
await master.process_request("How much RAM do I have?")
# "You have 64GB of RAM with 30GB available..."
```

### 4️⃣ Context-Aware

در نظر گرفتن زمینه و تاریخچه:

```python
result = await master.process_request(
    user_request="باز کن",
    context={
        "previous_request": "نوت‌پد",
        "user_lang": "fa"
    }
)
# AI می‌فهمد که کاربر می‌خواهد نوت‌پد را باز کند
```

---

## 📊 انواع ابزارها (ToolType)

Master Controller از ۶ نوع ابزار پشتیبانی می‌کند:

### 1. CHAT - گفتگو

برای سوالات عمومی و گفتگو:

```python
"هوش مصنوعی چیست؟"
"چطوری برنامه‌نویسی یاد بگیرم؟"
"تفاوت Python و JavaScript چیه؟"
```

### 2. SYSTEM - اطلاعات سیستم

برای دریافت اطلاعات سخت‌افزار و سیستم:

```python
"CPU چقدره؟"
"RAM آزاد چقدر دارم؟"
"فضای دیسک چقدر باقی مونده؟"
```

**اطلاعات قابل دریافت:**
- 🖥️ CPU: درصد استفاده، تعداد هسته‌ها
- 💾 RAM: کل، در دسترس، درصد استفاده
- 💿 Disk: کل، آزاد، درصد استفاده

### 3. DESKTOP - کنترل دسکتاپ

برای باز کردن برنامه‌ها و کنترل رابط کاربری:

```python
"باز کن نوت‌پد"
"اجرا کن Calculator"
"روی دکمه OK کلیک کن"
"تایپ کن سلام"
```

### 4. BROWSER - اتوماسیون وب

برای جستجو و دریافت اطلاعات آنلاین:

```python
"هوا امروز چطوره؟"
"قیمت بیت‌کوین"
"آخرین اخبار تهران"
```

⚠️ **توجه**: این قابلیت هنوز در حال توسعه است.

### 5. FILE - عملیات فایل

برای کار با فایل‌ها و پوشه‌ها:

```python
"فایل test.txt بساز"
"پوشه MyDocs باز کن"
"فایل report.pdf رو پاک کن"
```

⚠️ **توجه**: این قابلیت هنوز در حال توسعه است.

### 6. AUTONOMOUS - عامل خودمختار

برای کارهای پیچیده چند مرحله‌ای:

```python
"برو This PC، باز کن E:، فولدر MyDocs بساز"
"برو به سایت example.com و فرم رو پر کن"
```

---

## 💻 API Reference

### MasterAIController

```python
class MasterAIController:
    def __init__(
        self,
        system_agent: Optional[IntelligentSystemAgent] = None,
        autonomous_agent: Optional[AutonomousAgent] = None
    )
```

**پارامترها:**
- `system_agent`: عامل سیستمی برای Desktop Actions
- `autonomous_agent`: عامل خودمختار برای کارهای پیچیده

### process_request()

```python
async def process_request(
    self,
    user_request: str,
    context: Optional[Dict[str, Any]] = None
) -> ExecutionResult
```

**پارامترها:**
- `user_request`: درخواست کاربر به زبان طبیعی
- `context`: اطلاعات زمینه‌ای (اختیاری)

**بازگشتی:**
```python
@dataclass
class ExecutionResult:
    success: bool              # موفقیت اجرا
    raw_output: Any           # خروجی خام از ابزار
    human_response: str       # پاسخ انسانی نهایی
    tool_used: ToolType       # ابزار استفاده شده
    execution_time: float     # زمان اجرا
```

---

## 🎨 مثال‌های کاربردی

### مثال ۱: مانیتورینگ سیستم

```python
import asyncio
from core.master_controller import MasterAIController
from core.intelligent_agent import IntelligentSystemAgent

async def system_monitor():
    system_agent = IntelligentSystemAgent()
    master = MasterAIController(system_agent=system_agent)
    
    # چک کردن CPU
    result = await master.process_request("CPU چقدره؟")
    print(f"🖥️ {result.human_response}")
    
    # چک کردن RAM
    result = await master.process_request("RAM آزاد چقدر دارم؟")
    print(f"💾 {result.human_response}")
    
    # چک کردن Disk
    result = await master.process_request("فضای دیسک چقدره؟")
    print(f"💿 {result.human_response}")

asyncio.run(system_monitor())
```

**خروجی:**
```
🖥️ پردازنده شما ۴۵٪ مشغول است و ۲۴ هسته دارد. وضعیت خوبی است!
💾 شما ۶۴ گیگابایت حافظه دارید که ۳۰ گیگابایت آن آزاد است.
💿 دیسک شما ۵۱۲ گیگابایت است که ۲۰۰ گیگابایت آزاد دارید.
```

### مثال ۲: دستیار هوشمند

```python
async def smart_assistant():
    master = MasterAIController(
        system_agent=IntelligentSystemAgent(),
        autonomous_agent=AutonomousAgent()
    )
    
    requests = [
        "باز کن Calculator",
        "چقدر RAM دارم؟",
        "هوش مصنوعی چیست؟",
    ]
    
    for req in requests:
        print(f"\n👤 User: {req}")
        result = await master.process_request(req)
        print(f"🤖 AI: {result.human_response}")
        print(f"📍 Tool: {result.tool_used.value}")

asyncio.run(smart_assistant())
```

**خروجی:**
```
👤 User: باز کن Calculator
🤖 AI: ماشین‌حساب با موفقیت باز شد!
📍 Tool: desktop

👤 User: چقدر RAM دارم؟
🤖 AI: شما ۶۴ گیگابایت حافظه دارید که ۳۰ گیگابایت آن آزاد است.
📍 Tool: system

👤 User: هوش مصنوعی چیست؟
🤖 AI: هوش مصنوعی شاخه‌ای از علوم کامپیوتر است که...
📍 Tool: chat
```

### مثال ۳: Error Handling

```python
async def safe_execution():
    master = MasterAIController()
    
    try:
        result = await master.process_request("یه کار غیرممکن انجام بده")
        
        if result.success:
            print(f"✅ {result.human_response}")
        else:
            print(f"❌ {result.human_response}")
    
    except Exception as e:
        print(f"💥 خطای غیرمنتظره: {e}")

asyncio.run(safe_execution())
```

---

## 🔍 Routing Algorithm

### AI-Based Routing

Master Controller از AI برای تشخیص نوع درخواست استفاده می‌کند:

```python
prompt = """
درخواست کاربر: "هوا امروز چطوره؟"

ابزارهای موجود:
- CHAT: گفتگو
- SYSTEM: اطلاعات سیستم
- DESKTOP: کنترل دسکتاپ
- BROWSER: جستجوی وب
- FILE: عملیات فایل
- AUTONOMOUS: کارهای پیچیده

تشخیص بده کدام ابزار مناسب است و دلیل بده.
"""

# AI پاسخ می‌دهد:
{
    "tool": "BROWSER",
    "confidence": 0.9,
    "reasoning": "نیاز به جستجوی اطلاعات آنلاین دارد"
}
```

### Fallback Routing

اگر AI در دسترس نباشد، از کلمات کلیدی استفاده می‌شود:

```python
# کلمات کلیدی برای هر ابزار
KEYWORDS = {
    "DESKTOP": ["باز کن", "open", "launch", "اجرا"],
    "SYSTEM": ["cpu", "ram", "memory", "disk", "حافظه"],
    "BROWSER": ["weather", "news", "price", "هوا", "خبر"],
    "CHAT": [] # پیش‌فرض
}
```

---

## 📈 Performance

### Benchmarks

| عملیات | زمان میانگین | موفقیت |
|---|---|---|
| Routing (AI) | ~2-3 ثانیه | 95% |
| Routing (Fallback) | <0.1 ثانیه | 80% |
| System Info | <0.5 ثانیه | 100% |
| Desktop Action | 1-3 ثانیه | 95% |
| Humanization | ~1-2 ثانیه | 90% |

### بهینه‌سازی

```python
# استفاده از cache برای routing
@lru_cache(maxsize=100)
async def _route_request_cached(request: str) -> RoutingDecision:
    # ...

# Timeout برای AI calls
response = await asyncio.wait_for(
    ai_brain.ask(...),
    timeout=5.0
)
```

---

## 🐛 عیب‌یابی

### مشکلات رایج

#### ❌ AI Keys موجود نیست

```python
# خطا:
ValueError: Missing key inputs argument!

# راه‌حل:
# فایل .env را چک کنید:
GOOGLE_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

#### ❌ پاسخ خالی برمی‌گردد

```python
# علت: همه مدل‌های AI fail شدند

# راه‌حل:
# 1. API Keys را بررسی کنید
# 2. اتصال اینترنت را چک کنید
# 3. از Fallback Routing استفاده کنید
```

#### ❌ Routing اشتباه

```python
# علت: AI درخواست را اشتباه تشخیص داد

# راه‌حل:
# درخواست را واضح‌تر کنید:
"باز کن notepad"  # ✅ واضح
"notepad"          # ❌ مبهم
```

### Debug Mode

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# حالا تمام تصمیمات routing لاگ می‌شود:
# 2025-12-07 | DEBUG | Routing decision: DESKTOP (confidence: 0.85)
# 2025-12-07 | DEBUG | Reasoning: Keywords "باز کن" found
```

---

## 🔮 برنامه آینده

### نسخه 1.2

- [ ] **Browser Integration**: یکپارچه‌سازی کامل با Browser-Use
- [ ] **File Operations**: سیستم کامل مدیریت فایل
- [ ] **Learning System**: یادگیری از تصمیمات قبلی
- [ ] **Multi-Request**: پردازش چند درخواست همزمان

### نسخه 2.0

- [ ] **Plugin System**: امکان اضافه کردن ابزارهای جدید
- [ ] **Voice Integration**: درک مستقیم صدا
- [ ] **Vision-Based Routing**: تصمیم‌گیری بر اساس تصویر صفحه
- [ ] **Emotional Intelligence**: تشخیص احساسات کاربر

---

## 🤝 مشارکت

برای مشارکت در توسعه Master Controller:

1. مطالعه کد در `core/master_controller.py`
2. نوشتن تست‌های جدید در `tests/test_master_controller.py`
3. ایجاد Pull Request با توضیحات کامل

**ایده‌های خوب برای مشارکت:**
- اضافه کردن ابزارهای جدید (ToolType)
- بهبود الگوریتم Routing
- بهینه‌سازی Humanization
- افزودن پشتیبانی زبان‌های جدید

---

## 📚 منابع مرتبط

- [AI Brain](AI_BRAIN.md) - مغز هوش مصنوعی
- [Intelligent Agent](INTELLIGENT_AGENT.md) - عامل سیستمی
- [Autonomous Agent](AUTONOMOUS_AGENT.md) - عامل خودمختار
- [Integration Guide](INTEGRATION_GUIDE.md) - راهنمای یکپارچه‌سازی

---

## 📞 پشتیبانی

برای سوالات و مشکلات:
- 🐙 [GitHub Issues](https://github.com/shahincodev/Software-AI-Persian/issues)
- 📧 Email: shahincodev@gmail.com
- 💬 [Discussions](https://github.com/shahincodev/Software-AI-Persian/discussions)

---

<div align="center">

**ساخته شده با ❤️ توسط تیم Software-AI**

[🏠 بازگشت به صفحه اصلی](../README.md)

</div>

</div>

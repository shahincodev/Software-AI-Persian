# گزارش بازنویسی ai_brain.py - شناسایی هوشمند ارائه‌دهندگان API

**تاریخ**: 2026-07-03  
**نسخه**: 0.5.0  
**وضعیت**: تکمیل شده

---

## خلاصه اجرایی

فایل `core/ai_brain.py` بازنویسی شد تا به‌صورت هوشمند ارائه‌دهندگان API موجود در محیط را شناسایی کرده و فقط از مدل‌های آن‌ها استفاده کند. این تغییر مشکل اصلی سیستم قبلی را حل می‌کند که سعی می‌کرد از تمام ارائه‌دهندگان به ترتیب استفاده کند، حتی اگر کلید API آن‌ها تنظیم نشده باشد.

---

## مشکل قبلی

### سیستم قدیمی
```python
# سیستم قبلی - تلاش از تمام ارائه‌دهندگان
def _load_model_legacy(self, name: str):
    if name == "reasoning":
        from browser_use.llm.google.chat import ChatGoogle
        model = ChatGoogle(model=os.getenv("GOOGLE_REASONING_MODEL", "gemini-2.5-flash"))
    elif name == "fast":
        from browser_use.llm.groq.chat import ChatGroq
        model = ChatGroq(model=os.getenv("GROQ_MODEL", "groq-1"))
    elif name == "normal":
        from browser_use.llm.openai.chat import ChatOpenAI
        model = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini"))
```

### مشکلات سیستم قدیمی:
1. **عدم تشخیص API key**: سیستم بدون بررسی وجود کلید API، سعی در استفاده از ارائه‌دهنده می‌کرد
2. **خطاهای مکرر**: هر بار که مدلی بارگذاری می‌شد و کلید API موجود نبود، خطا رخ می‌داد
3. **کندی**: تلاش متوالی برای ارائه‌دهندگان مختلف باعث کندی می‌شد
4. **پیچیدگی**: کد تکراری و پیچیده برای هر ارائه‌دهنده

---

## راه‌حل جدید

### ۱. کلاس `ProviderDetector`

```python
class ProviderDetector:
    """شناسایی خودکار ارائه‌دهندگان API موجود در محیط."""
    
    PROVIDER_KEY_MAP: dict[str, str] = {
        "google": "GOOGLE_API_KEY",
        "groq": "GROQ_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "huggingface": "HUGGINGFACE_API_KEY",
    }
    
    def _detect_providers(self) -> None:
        """شناسایی ارائه‌دهندگان فعال"""
        for provider_name, env_var in self.PROVIDER_KEY_MAP.items():
            api_key = os.getenv(env_var, "").strip()
            is_valid = bool(api_key and not api_key.startswith("your-") and 
                          not api_key.startswith("AIza-your-"))
            
            status = ProviderStatus(
                name=provider_name,
                api_key_env=env_var,
                is_available=is_valid,
                api_key_set=bool(api_key),
            )
            self._providers[provider_name] = status
```

### ۲. تغییرات در `_load_model()`

```python
def _load_model(self, name: str) -> Any:
    # بررسی کلید API و در دسترس بودن ارائه‌دهنده
    if not self._detector.is_provider_available(model_config.provider):
        logger.warning(f"❌ Provider '{model_config.provider}' not available (no API key)")
        raise ValueError(f"Provider '{model_config.provider}' not available")
    
    # بارگذاری بر اساس ارائه‌دهنده
    if model_config.provider == "openrouter":
        return self._load_openrouter_model(model_config)
    elif model_config.provider == "google":
        return self._load_google_model(model_config)
    # ...
```

### ۳. تغییرات در `_load_model_legacy()`

```python
def _load_model_legacy(self, name: str):
    # بررسی ارائه‌دهندگان فعال
    has_google = self._detector.is_provider_available("google")
    has_groq = self._detector.is_provider_available("groq")
    has_openrouter = self._detector.is_provider_available("openrouter")
    
    if name == "reasoning":
        if has_google:
            from browser_use.llm.google.chat import ChatGoogle
            model = ChatGoogle(...)
        else:
            raise ValueError("No Google API key for reasoning model")
```

---

## ویژگی‌های جدید

### ۱. شناسایی خودکار ارائه‌دهندگان

```python
# در ابتدای برنامه
brain = AIBrain()
# خروجی:
# ✅ Provider detected: google (key: GOOGLE_API_KEY)
# ✅ Provider detected: groq (key: GROQ_API_KEY)
# ❌ No API providers detected: openrouter (key: OPENROUTER_API_KEY)
```

### ۲. اطلاعات ارائه‌دهندگان

```python
info = brain.get_provider_info()
# {
#     "available_providers": ["google", "groq"],
#     "total_providers": 6,
#     "providers": {
#         "google": {"available": True, "key_env": "GOOGLE_API_KEY", "key_set": True},
#         "groq": {"available": True, "key_env": "GROQ_API_KEY", "key_set": True},
#         "openrouter": {"available": False, "key_env": "OPENROUTER_API_KEY", "key_set": False},
#         ...
#     }
# }
```

### ۳. fallback هوشمند

```python
# فقط از ارائه‌دهندگان فعال استفاده می‌کند
response = await brain.ask_with_fallback(prompt)
# خروجی:
# 🤖 Trying model 1/3: google-gemini-3-pro-preview
# ✅ Success with model: google-gemini-3-pro-preview
```

---

## ساختار جدید فایل

```
ai_brain.py
├── ProviderStatus (dataclass)
│   ├── name: str
│   ├── api_key_env: str
│   ├── is_available: bool
│   └── api_key_set: bool
├── ProviderDetector (class)
│   ├── PROVIDER_KEY_MAP: dict
│   ├── _detect_providers()
│   ├── is_provider_available()
│   ├── get_available_providers()
│   ├── get_provider_status()
│   └── log_summary()
├── AIBrain (class)
│   ├── __init__()
│   ├── _analyze_task_complexity()
│   ├── _load_model()
│   ├── _load_openrouter_model()
│   ├── _load_google_model()
│   ├── _load_groq_model()
│   ├── _load_ollama_model()
│   ├── _load_huggingface_model()
│   ├── _load_model_legacy()
│   ├── get_model()
│   ├── ask_with_fallback()
│   ├── ask()
│   ├── _sanitize_ai_response()
│   ├── interpret_system_request()
│   ├── _extract_json_actions()
│   ├── agent_chat()
│   ├── _parse_agent_response()
│   └── get_provider_info()
└── get_provider_detector()
```

---

## مقایسه عملکرد

| معیار | سیستم قبلی | سیستم جدید |
|--------|-----------|-----------|
| تشخیص API key | ❌ خیر | ✅ بله |
| تعداد تلاش‌ها | تمام ارائه‌دهندگان | فقط فعال‌ها |
| زمان شروع | کند (تلاش متوالی) | سریع (شناسایی اولیه) |
| خطاها | خطا برای هر ارائه‌دهنده بدون key | خطا فقط یک بار |
| لاگ‌ها | گیج‌کننده | شفاف و مفید |

---

## تست‌ها

### تست شناسایی ارائه‌دهندگان

```python
import os
from core.ai_brain import ProviderDetector

def test_provider_detection():
    # تنظیم متغیر محیطی
    os.environ["GOOGLE_API_KEY"] = "test-key-123"
    os.environ["GROQ_API_KEY"] = ""
    
    detector = ProviderDetector()
    
    assert detector.is_provider_available("google") == True
    assert detector.is_provider_available("groq") == False
    assert "google" in detector.get_available_providers()
```

### تست بارگذاری مدل

```python
import os
from core.ai_brain import AIBrain

def test_model_loading_with_google():
    os.environ["GOOGLE_API_KEY"] = "test-key-123"
    
    brain = AIBrain()
    info = brain.get_provider_info()
    
    assert "google" in info["available_providers"]
```

---

## راهنمای پیکربندی

### ۱. تنظیم کلیدهای API در `.env`

```bash
# Google AI Studio (رایگان)
GOOGLE_API_KEY=AIza-your-real-key

# Groq (رایگان)
GROQ_API_KEY=gsk-your-real-key

# OpenRouter (پرداخت از طریق استفاده)
OPENROUTER_API_KEY=sk-or-v1-your-real-key
```

### ۲. بررسی ارائه‌دهندگان فعال

```python
from core.ai_brain import get_provider_detector

detector = get_provider_detector()
detector.log_summary()
# خروجی:
# ✅ Provider detected: google (key: GOOGLE_API_KEY)
# ✅ Provider detected: groq (key: GROQ_API_KEY)
```

### ۳. استفاده از AIBrain

```python
from core.ai_brain import AIBrain

brain = AIBrain()

# انتخاب خودکار مدل بر اساس تسک
model = brain.get_model(task="مرورگر را باز کن")

# پرسش با fallback هوشمند
response = await brain.ask_with_fallback("سلام، حالت چطوره؟")
```

---

## نکات فنی

### اعتبارسنجی کلید API

```python
# کلید باید شرایط زیر را داشته باشد:
# 1. خالی نباشد
# 2. با "your-" شروع نشود
# 3. با "AIza-your-" شروع نشود (برای Google)

is_valid = bool(api_key and 
                not api_key.startswith("your-") and 
                not api_key.startswith("AIza-your-"))
```

### لاگ‌گیری

```python
# در ابتدای برنامه
logger.info(f"✅ Provider detected: {provider_name} (key: {env_var})")
logger.warning(f"⚠️ Provider {provider_name}: key appears placeholder")
logger.error("❌ No API providers detected! Check your .env file")
```

---

## تغییرات مرتبط

### فایل‌های تغییر یافته:
1. `core/ai_brain.py` - بازنویسی کامل
2. `docs/AI_BRAIN_REWRITE_REPORT.md` - این گزارش

### فایل‌های بدون تغییر:
1. `core/model_config.py` - از قبل از فیلتر API key پشتیبانی می‌کند
2. `main.py` - نیاز به تغییر ندارد
3. `.env.example` - الگوی پیکربندی تغییر نکرده

---

## نتیجه‌گیری

بازنویسی `ai_brain.py` با موفقیت انجام شد. سیستم جدید:

1. **هوشمندانه** ارائه‌دهندگان API موجود را شناسایی می‌کند
2. **سریع‌تر** عمل می‌کند (بدون تلاش‌های غیرضروری)
3. **شفاف‌تر** لاگ‌های مفیدتری ارائه می‌دهد
4. **قابل اعتمادتر** است (کمتر خطا می‌دهد)

این تغییر تجربه کاربری را بهبود بخشیده و مشکل اصلی سیستم قبلی را حل کرده است.

# 🤖 Copilot-Style Model Support (مانند GitHub Copilot)

## خصوصیات جدید

### 1. هزاران مدل مختلف در دسترس
سیستم جدید Software-AI اکنون مانند GitHub Copilot و Microsoft Copilot عمل می‌کند - **هزاران مدل مختلف** در دسترس دارد:

- **OpenRouter**: دسترسی به 100+ مدل (OpenAI, Claude, Mistral, و...)
- **Google AI Studio**: Gemini 3 Pro Preview و Gemini 2.5 Flash/Pro
- **Groq**: مدل‌های سریع Mixtral و Llama
- **HuggingFace**: دسترسی به هزاران مدل متن‌باز
- **Ollama**: مدل‌های محلی (بدون نیاز به API)

### 2. Fallback خودکار و ذکی
اگر یک مدل ناکام شود، خودکار **تمام مدل‌های دردسترس** را امتحان می‌کند:

```
مدل 1 (OpenAI GPT-4) ❌ خطا → 
مدل 2 (Google Gemini) ✅ موفق!
```

### 3. انتخاب ذکی مدل‌ها
تمام مدل‌ها بر اساس **اولویت** مرتب‌شده‌اند:
- مدل‌های قوی‌تر و سریع‌تر ابتدا امتحان می‌شوند
- اگر موفق نشد، مدل‌های ضعیف‌تر امتحان می‌شوند

---

## راه‌اندازی

### مرحله 1: کلیدهای API را بدست آورید

#### OpenRouter (تا 100+ مدل)
- دریافت کلید: https://openrouter.ai
- رایگان (پرداخت از طریق استفاده)
- تمام مدل‌های OpenAI، Claude، Mistral و...

```bash
# ثبت‌نام
# 1. به https://openrouter.ai بروید
# 2. ثبت‌نام کنید
# 3. API keys بروید و کلید خود را کپی کنید
```

#### Google AI Studio (رایگان!)
- دریافت کلید: https://aistudio.google.com/app/apikeys
- **کاملاً رایگان**
- Gemini 3 Pro Preview و Gemini 2.5 Flash

```bash
# ثبت‌نام
# 1. به https://aistudio.google.com بروید
# 2. "Get API Key" کلیک کنید
# 3. Google Account خود را استفاده کنید
```

#### Groq (رایگان و سریع!)
- دریافت کلید: https://console.groq.com
- **کاملاً رایگان**
- Mixtral 8x7B، Llama 3.1 70B و...

```bash
# ثبت‌نام
# 1. به https://console.groq.com بروید
# 2. API keys بروید
# 3. Create API Key کلیک کنید
```

### مرحله 2: پیکربندی

```bash
# کپی کنید
Copy-Item .env.example .env

# فایل .env را تحریر کنید و کلیدها را وارد کنید
# OPENROUTER_API_KEY=sk-or-v1-...
# GOOGLE_API_KEY=AIza-...
# GROQ_API_KEY=gsk-...
```

### مرحله 3: اجرا

```bash
python main.py
```

سیستم خودکار **تمام مدل‌های دردسترس** را تشخیص می‌دهد و از بهترین آن‌ها استفاده می‌کند! 🚀

---

## مدل‌های موجود

### OpenRouter (100+ مدل)
| مدل | قیمت | سرعت | کیفیت |
|-----|------|------|-------|
| GPT-4o | $$ | متوسط | بسیار خوب |
| GPT-4 Turbo | $$ | متوسط | عالی |
| Claude 3 Opus | $$$ | آهسته | بسیار عالی |
| Claude 3 Sonnet | $$ | متوسط | خوب |
| Mistral Large | $ | سریع | خوب |
| Llama 2 70B | $ | سریع | متوسط |

### Google (رایگان!)
| مدل | قیمت | سرعت | کیفیت |
|-----|------|------|-------|
| Gemini 3 Pro Preview | رایگان | متوسط | خیلی خوب |
| Gemini 2.5 Flash | رایگان | سریع | خوب |
| Gemini 2.5 Pro | رایگان | متوسط | بسیار خوب |

### Groq (رایگان!)
| مدل | قیمت | سرعت | کیفیت |
|-----|------|------|-------|
| Mixtral 8x7B | رایگان | بسیار سریع | خوب |
| Llama 3.1 70B | رایگان | سریع | خوب |

---

## مثال استفاده

### Python API

```python
from core.ai_brain import AIBrain

brain = AIBrain()

# استفاده خودکار از بهترین مدل
response = await brain.ask_with_fallback(
    "سلام! چطور می‌تونم Windows رو خودکار کنم؟"
)
print(response)
```

### لاگ‌ها

```
🤖 Available models (8):
   - openrouter-gpt-4o (priority: 100)
   - openrouter-claude-3-opus (priority: 98)
   - google-gemini-3-pro-preview (priority: 95)
   - openrouter-gpt-4-turbo (priority: 99)
   - google-gemini-2-pro (priority: 88)
   - groq-mixtral-8x7b (priority: 75)
   - groq-llama-3.1-70b (priority: 78)
   ... and 1 more

🤖 Trying model 1/8: openrouter-gpt-4o
✅ Success with fallback model: openrouter-gpt-4o
```

---

## ارتقاء مدل‌های جدید

### اضافه کردن مدل جدید

فایل `core/model_config.py` را تحریر کنید:

```python
def _load_default_models(self):
    # اضافه کردن مدل جدید
    self.register_model(ModelConfig(
        name="my-awesome-model",
        provider="openrouter",  # یا google, groq, ...
        api_key_env="OPENROUTER_API_KEY",
        temperature=0.7,
        priority=110,  # اولویت بالاتر = اولی‌تر تلاش می‌شود
        description="توضیح مدل من"
    ))
```

### تغییر اولویت

```python
# مدل Google را بیشتر ترجیح دهید
ModelConfig(..., priority=105)  # بالاتر از OpenAI

# یا مدل Groq را کم‌تر ترجیح دهید
ModelConfig(..., priority=50)  # پایین‌تر
```

---

## نکات مهم

### 1. کدام کلیدهای API الزام‌ی هستند؟
**خوبخبری**: **هیچکدام الزام‌ی نیست!** 🎉

- حداقل یک کلید داشته باشید (OpenRouter یا Google یا Groq)
- سیستم بقیه را نادیده می‌گیرد
- هر چه بیشتر کلید داشته باشید، بیشتر گزینه‌های fallback دارید

### 2. آیا من حتماً باید پول بپردازم؟
**خیر!** 🆓

**رایگان:**
- Google AI Studio (رایگان کاملاً)
- Groq (رایگان کاملاً)
- Ollama (محلی، بدون API)

**پرداخت ارزان:**
- OpenRouter (خیلی ارزان، فقط برای استفاده بپردازید)

### 3. کدام مدل بهترین است؟
**وابسته به نیاز شما:**
- **سرعت**: Groq Mixtral، Gemini Flash
- **کیفیت**: GPT-4o، Claude 3 Opus
- **تعادل**: Mistral Large، Gemini Pro
- **بودجه**: Google (رایگان)

### 4. آیا می‌تونم مدل‌های محلی استفاده کنم؟
**بله!** 

Ollama را نصب کنید:
```bash
# https://ollama.ai برای دانلود
ollama pull neural-chat
```

سیستم خودکار آن را تشخیص می‌دهد!

---

## ترفندهای Fallback

### Scenario 1: API موجود نیست
```
OpenAI (❌ کلید ندارم) →
Google (✅ کلید دارم) →
✅ استفاده از Google
```

### Scenario 2: مدل خراب است
```
OpenRouter (❌ خطا) →
Google (❌ quota exceeded) →
Groq (✅ موفق!)
```

### Scenario 3: اینترنت برای Groq نیست
```
Groq (❌ offline) →
Ollama (✅ محلی، موفق!)
```

---

## پیکربندی پیشرفته

### تغییر دمای مدل‌ها

```python
ModelConfig(
    name="my-model",
    temperature=0.0,  # 0 = منطقی، 1 = خلاق
    max_tokens=4000,  # حداکثر طول پاسخ
)
```

### استفاده از مدل خاص

```python
response = await brain.ask(
    prompt="سلام!",
    mode="google-gemini-3-pro-preview"  # مدل خاص
)
```

---

## مشکل‌شناسی

### خطا: API Key not found
```bash
# بررسی کنید
# 1. فایل .env وجود دارد؟
# 2. کلید در .env صحیح است؟
# 3. متغیر محیطی export شده است؟
```

### خطا: All models failed!
```bash
# بررسی کنید
# 1. حداقل یک کلید API دارید؟
# 2. اینترنت متصل است؟
# 3. سهمیه مدل پایان نیافته است؟
```

### مدل X موجود نیست
```bash
# یا نام غلط است
# یا کلید API آن را تعریف نکرده‌اید
# یا provider در .env موجود نیست
```

---

## مثال کامل (.env)

```bash
# Google (رایگان - شروع از اینجا!)
GOOGLE_API_KEY=AIza-ABC123...

# Groq (رایگان و سریع)
GROQ_API_KEY=gsk-ABC123...

# OpenRouter (100+ مدل)
OPENROUTER_API_KEY=sk-or-v1-ABC123...

# تنظیمات
MODEL_TEMPERATURE=0.5
SYSTEM_MODEL_TEMPERATURE=0.3
LOG_LEVEL=INFO
DEBUG=false
```

**آماده هستید؟** 🚀

```bash
python main.py
```

سیستم خودکار تمام مدل‌ها را تشخیص می‌دهد و بهترین آن‌ها را انتخاب می‌کند!

---

## فیدبک و بهبود

اگر مدل بهتری می‌شناسید:
1. فایل `core/model_config.py` را باز کنید
2. مدل را اضافه کنید
3. Pull request ارسال کنید! 🙌

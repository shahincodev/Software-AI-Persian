# 🚀 راهنمای سریع - سیستم مدل‌های چندگانه

**خوبخبری**: Software-AI اکنون **مانند GitHub Copilot و Microsoft Copilot** کار می‌کند! 🎉

---

## 1️⃣ نیازها

### رایگان (بدون پول)
- **Google AI Studio** ← **شروع از اینجا! رایگان 100%**
- **Groq** ← **رایگان و سریع**
- **Ollama** ← **محلی، بدون اینترنت** (اختیاری)

### ارزان
- **OpenRouter** ← **تمام مدل‌ها در یک جا**

---

## 2️⃣ راه‌اندازی 5 دقیقه‌ای

### مرحله 1: کلید Google
```bash
# 1. بروید به: https://aistudio.google.com/app/apikeys
# 2. "Get API Key" کلیک کنید
# 3. کپی کنید
```

### مرحله 2: کلید Groq (اختیاری)
```bash
# 1. بروید به: https://console.groq.com
# 2. API keys → Create API Key
# 3. کپی کنید
```

### مرحله 3: فایل .env
```bash
# PowerShell
Copy-Item .env.example .env

# فایل .env را باز کنید و جایگزین کنید:
GOOGLE_API_KEY=AIza-...       # از Google
GROQ_API_KEY=gsk-...          # از Groq (اختیاری)
OPENROUTER_API_KEY=sk-or-...  # اختیاری
```

### مرحله 4: اجرا
```bash
python main.py
```

**بس! ✅ سیستم خودکار تمام مدل‌ها را تشخیص می‌دهد!**

---

## 3️⃣ مدل‌های موجود

| ارائه‌دهنده | مدل‌ها | قیمت | سرعت | کیفیت |
|-----------|--------|------|------|-------|
| 🔵 Google | Gemini 3/2.5 | رایگان | متوسط-سریع | خوب-عالی |
| ⚡ Groq | Mixtral, Llama | رایگان | بسیار سریع | خوب |
| 🌈 OpenRouter | 100+ مدل | ارزان | متنوع | متنوع |
| 🏠 Ollama | هر مدل محلی | رایگان | سریع | متنوع |

---

## 4️⃣ چه اتفاقی می‌افتد؟

### اگر مدل 1 خراب شود:
```
مدل 1 ❌ → مدل 2 ❌ → مدل 3 ✅ (استفاده می‌شود)
```

### لاگ مثال:
```
🤖 Available models (8):
   - openrouter-gpt-4o (priority: 100)
   - google-gemini-3-pro-preview (priority: 95)
   - groq-mixtral-8x7b (priority: 75)
   ... and 5 more

🤖 Trying model 1/8: openrouter-gpt-4o
❌ Model failed
🤖 Trying model 2/8: google-gemini-3-pro-preview
✅ Success!
```

---

## 5️⃣ مثال استفاده

### CLI
```bash
python main.py
> Hello

# سیستم خودکار بهترین مدل را استفاده می‌کند ✅
```

### Python API
```python
from core.ai_brain import AIBrain

brain = AIBrain()

# اگر OpenAI fail شود، خودکار Google یا Groq استفاده می‌شود
response = await brain.ask_with_fallback("سلام!")
print(response)
```

---

## 6️⃣ نکات

- ✅ **حداقل یک کلید بدهید** (Google یا Groq)
- ✅ **بیشتر کلید = بیشتر گزینه fallback**
- ✅ **بدون کلید = استفاده از Ollama (محلی)**
- ❌ **بدون هیچ‌کدام = سیستم فیل می‌شود**

---

## 7️⃣ مشکل‌شناسی

### ❌ Error: API Key not found
```bash
# بررسی کنید:
# 1. فایل .env وجود دارد؟
# 2. کلید صحیح است؟
# 3. فایل .gitignore آن را نادیده می‌گیرد؟
```

### ❌ All models failed!
```bash
# احتمال‌ات:
# 1. تمام کلیدها غلط هستند
# 2. اینترنت برش نیست
# 3. سهمیه تمام شده
```

### ❌ Model X doesn't exist
```bash
# بررسی کنید:
# 1. نام صحیح است؟
# 2. کلید API آن را تعریف کردید؟
```

---

## 8️⃣ دریافت مدل‌های بیشتر

### OpenRouter (100+ مدل)
```bash
# 1. https://openrouter.ai
# 2. API keys
# 3. کپی کنید → OPENROUTER_API_KEY
```

### HuggingFace (هزاران مدل)
```bash
# 1. https://huggingface.co/settings/tokens
# 2. API token
# 3. کپی کنید → HUGGINGFACE_API_KEY
```

### Anthropic Claude (اختیاری)
```bash
# اگر از OpenRouter استفاده می‌کنید، نیازی نیست!
# یا: https://console.anthropic.com
```

---

## 9️⃣ تغییر اولویت مدل‌ها

فایل `core/model_config.py`:

```python
# مدل Google را ترجیح دهید
ModelConfig(
    name="google-gemini-3-pro-preview",
    priority=110  # بالاتر = اولی‌تر
)

# مدل Groq را کم‌تر ترجیح دهید
ModelConfig(
    name="groq-mixtral-8x7b",
    priority=50  # پایین‌تر
)
```

---

## 🔟 خودآپدیت

اگر مدل جدید می‌خواهید:
```python
# core/model_config.py
self.register_model(ModelConfig(
    name="my-awesome-model",
    provider="openrouter",
    api_key_env="OPENROUTER_API_KEY",
    temperature=0.7,
    priority=105,
    description="مدل عالی برای X"
))
```

---

## ✅ آماده هستید؟

```bash
# 1. Copy-Item .env.example .env
# 2. فایل .env را تحریر کنید
# 3. python main.py

# 🚀 بیاید شروع کنیم!
```

---

## 📚 اطلاعات بیشتر

- 📖 [راهنمای کامل](./COPILOT_MODELS.md)
- 🤖 [مدل‌های موجود](./COPILOT_MODELS.md#مدل‌های-موجود)
- ⚙️ [پیکربندی پیشرفته](./COPILOT_MODELS.md#پیکربندی-پیشرفته)

---

سوال داشتید؟ [GitHub Issues](https://github.com/shahincodev/Software-AI-Persian/issues) 👈

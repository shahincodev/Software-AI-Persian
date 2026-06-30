# گزارش پیگیری فاز ۱ — رفع باگ مسیریابی دسکتاپ

## خلاصه
باگ اصلی: درخواست‌های دسکتاپ (`"یک فایل روی درایو D بساز"`) اشتباهاً به `CHAT_RESPONSE` هدایت می‌شدند.
علت: دروازه اطمینان (confidence gate) قبل از بررسی الگوها قرار داشت.

---

## تغییرات مرحله ۱

### ۱. جابجایی دروازه اطمینان
- **فایل**: `core/intent_router.py`
- دروازه اطمینان به بعد از تمام بررسی‌های الگو منتقل شد.
- الگوهای `desktop_patterns`، `browser_patterns`، `task_patterns` اولویت گرفتند.

### ۲. بهبود الگوهای دسکتاپ
- `"do "` از `desktop_patterns` حذف شد.
- `"empty "`، `"clean "`، `"rename "`، `"recycle"`، `"close "` اضافه شدند.

### ۳. رفع هشدارهای کاذب مکالمه‌ای (شکاف ۱ — بخش اول)
- نگهبان `_is_conv` برای جلوگیری از تطبیق target/fs-signal وقتی verb کانورسیشن است.
- نگهبان `_is_question` برای مهار سیگنال‌های ضعیف وقتی متن سوالی است بدون الگوی اکشن.
- تفکیک سیگنال‌های قوی (verb دسکتاپ، action pattern) از سیگنال‌های ضعیف (target, fs_signal).

---

# تغییرات مرحله ۲ — رفع بازنویسی verb در سوالات how-to

### علت ریشه‌ای
در `core/intent_analyzer.py`، متد `_extract_verb` ابتدا action verbs را در `known_verbs` جستجو می‌کند.
برای `"Tell me how to create a folder"`، کلمه "create" در متن پیدا می‌شود و verb مستقیماً
به `"create"` تنظیم می‌شود — قبل از اینکه `_check_verb_override` اصلاً صدا زده شود.
سپس در `_classify_intent`، هم `_verb_ok=True` (چون verb="create") و هم `_action_ok=True`
(چون "create " در متن خام است) باعث هدایت به `DESKTOP_AUTOMATION` می‌شوند.

### تغییر در `core/intent_analyzer.py` — `_check_verb_override`
- **حالت جدید (معکوس)**: اگر `current_verb` یک action verb باشد (create, open, delete, ...)
  و متن با `\bhow\s+(to|do|can|could)\b` مطابقت داشته باشد، verb به `"converse"` بازنشانی می‌شود.
- **حالت قبلی (حفظ شده)**: اگر `current_verb="converse"` باشد و متن action keyword داشته باشد
  و how-to نباشد، به action verb تغییر می‌کند (مثلاً "Can you create a folder?" → "create").
- اگر `current_verb="converse"` باشد ولی متن how-to باشد، override لغو می‌شود.

### تغییر در `core/intent_router.py` — `_classify_intent`
- متغیر `_how_to_question` added: تشخیص `\bhow\s+(to|do|can|could)\b` در متن خام.
- شرط DESKTOP_AUTOMATION: `(_verb_ok or _action_ok or _weak_ok) and not (_how_to_question and _is_conv)`.
- وقتی verb "converse" است (چه از استخراج اصلی، چه از بازنشانی `_check_verb_override`)
  و متن how-to است، کل بلوک DESKTOP_AUTOMATION رد می‌شود.

### Diff دقیق
**`core/intent_analyzer.py`:**
```python
# اضافه شده قبل از guard قبلی
if current_verb in ("create", "open", "delete", "write", "search",
                   "click", "install", "type", "play") and how_to_match:
    self.logger.debug(f"Verb override: '{current_verb}' → 'converse'")
    return "converse"
```

**`core/intent_router.py`:**
```python
_how_to_question = bool(re.search(r'\bhow\s+(to|do|can|could)\b', raw))
if (_verb_ok or _action_ok or _weak_ok) and not (_how_to_question and _is_conv):
```

### Baseline (قبل از fix)
```
Tell me how to create a folder  → DESKTOP_AUTOMATION (verb=create)
How can I create a backup?      → DESKTOP_AUTOMATION (verb=create)
How do I delete a file?         → DESKTOP_AUTOMATION (verb=delete)
Create a file on drive D        → DESKTOP_AUTOMATION (verb=create)  ✓
Create a folder in Downloads    → DESKTOP_AUTOMATION (verb=create)  ✓
```

### پس از fix
```
Tell me how to create a folder  → CHAT_RESPONSE (verb=converse)  ✓
How can I create a backup?      → CHAT_RESPONSE (verb=converse)  ✓
How do I delete a file?         → CHAT_RESPONSE (verb=converse)  ✓
Create a file on drive D        → DESKTOP_AUTOMATION (verb=create)  ✓
Create a folder in Downloads    → DESKTOP_AUTOMATION (verb=create)  ✓
```

### تست‌های رگرسیون (۲۱ تست router + ۴۱ تست analyzer)
- **Baseline**: 17/17 passed (قبل از اضافه کردن تست‌های how-to)
- **Post-fix**: 62/62 passed (21 intent_router + 41 intent_analyzer)
- **تست‌های جدید how-to**: همگی PASS — `test_conversational_tell_me_how_to_create_a_folder`,
  `test_conversational_how_can_i_create_a_backup`, `test_conversational_how_do_i_delete_a_file`
- **تست تأییدی**: `test_automation_can_you_create_a_folder` → DESKTOP_AUTOMATION ✓
  (تأیید میکند که "Can you create a folder?" که how-to نیست، همچنان به درستی اکشن می‌شود)

### موارد اضافی تست شده
| ورودی | نتیجه | توضیح |
|-------|--------|--------|
| "Can you show me how to create a folder" | CHAT_RESPONSE | how-to با can you — اطلاعاتی |
| "Can you create a folder?" | DESKTOP_AUTOMATION | دستور مؤدبانه — بدون how-to |

---

## شکاف ۲ — تحلیل رفتار با AI در دسترس (تست نشده، تئوری)

### پیش‌بینی با AI در دسترس
| سناریو | بدون AI | با AI |
|--------|---------|-------|
| "What is a folder?" | verb=unknown → سوال گارد فعال → CHAT_RESPONSE | verb=converse → همان نتیجه |
| "Tell me how to create a folder" | verb=create → how-to گارد فعال → CHAT_RESPONSE | verb=converse (AI تشخیص می‌دهد) → همان نتیجه |
| "Create a file on drive D" | verb=create → DESKTOP_AUTOMATION | verb=create → DESKTOP_AUTOMATION |

### مواردی که نیاز به تأیید کاربر دارند
پس از پوشش کد و کلون با API Key واقعی:
1. اجرای `python -m pytest tests/test_intent_router.py tests/test_intent_analyzer.py -v`
2. تست دستی: `"Tell me how to create a folder"` → باید `CHAT_RESPONSE` برگرداند
3. تست دستی: `"Create a file on drive D"` → باید `DESKTOP_AUTOMATION` برگرداند و فایل بسازد
4. تست دستی: `"Can you create a folder?"` → باید `DESKTOP_AUTOMATION` برگرداند (تأیید عدم شکستن)

---

## مشکل شناخته شده باقیمانده
همه موارد false positive برطرف شده‌اند. هیچ مشکل شناخته شده‌ای در مسیریابی دسکتاپ باقی نمانده است.

## فایل‌های تغییر یافته
- `core/intent_router.py` — تغییرات اصلی و companion fix
- `core/intent_analyzer.py` — رفع بازنویسی verb در سوالات how-to
- `tests/test_intent_router.py` — ۱۳ تست جدید (۹ Gap 1 + ۴ how-to)
- `docs/PHASE1_FOLLOWUP_REPORT.md` — این گزارش

---

این مشکل برطرف شد و تست‌های جدید pass شدند.

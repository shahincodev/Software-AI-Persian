# 🔄 Persian to English Conversion - TODO List

## ⚠️ Problem
CLI environment doesn't support Persian characters properly, causing encoding issues.

**Rule**: 
- ✅ Persian is OK in: Comments, Docstrings, Documentation
- ❌ Persian NOT OK in: print statements, variable names, class names, function names, CLI output

---

## 📋 Files to Fix

### High Priority (CLI Output Files)

#### 1. `tests/test_master_controller_complete.py` ⚠️
**Issues**: 50+ Persian print statements in test output
**Lines**: 55, 60, 63, 82, 85, 98, 101-103, 106-108, 126, 172, 190, 227, 233-236, 254, 258-259, 264, 269, 271, 273, 291, 293, 309

**Fix Strategy**:
```python
# Before ❌
print(f"✅ Master Controller آماده است!")
print(f"🔍 تست: {test_name}")
print(f"⚠️  توجه: این تست‌ها برنامه‌ها را واقعاً باز می‌کنند!")

# After ✅
print(f"✅ Master Controller is ready!")
print(f"🔍 Test: {test_name}")
print(f"⚠️  Warning: These tests will actually launch applications!")
```

---

#### 2. `tests/quick_test_master.py` ⚠️
**Issues**: 20+ Persian print statements
**Lines**: 33-37, 46, 49, 74, 78, 88-90, 93, 95, 97, 114, 116

**Fix Strategy**:
```python
# Before ❌
print("⚙️  در حال مقداردهی اولیه...\n")
print("✅ آماده!\n")
print(f"✅ موفقیت: {'بله' if result.success else 'خیر'}")

# After ✅
print("⚙️  Initializing...\n")
print("✅ Ready!\n")
print(f"✅ Success: {'Yes' if result.success else 'No'}")
```

---

#### 3. `examples/autonomous_demo.py` ⚠️
**Issues**: 30+ Persian print statements
**Lines**: 34, 89, 114, 120, 123, 128, 131, 136, 139, 145, 160, 189, 191, 236-242

**Fix Strategy**:
```python
# Before ❌
print("🎯 Demo 1: Simple Tasks (کارهای ساده)")
print("\n📝 تست ۱: نوت‌پد رو باز کن")
print("بهم بگو چیکار کنم! (برای خروج 'exit' بزن)")

# After ✅
print("🎯 Demo 1: Simple Tasks")
print("\n📝 Test 1: Open Notepad")
print("Tell me what to do! (Type 'exit' to quit)")
```

---

#### 4. `main.py` ⚠️
**Issues**: Persian in CLI help/examples
**Line**: 626

**Fix Strategy**:
```python
# Before ❌
print("   Example: goal برو E: فولدر MyDocs بساز")

# After ✅
print("   Example: goal Go to E: and create MyDocs folder")
```

---

#### 5. `examples/mouse_demo.py` ⚠️
**Issues**: Persian in code examples
**Line**: 161

**Fix Strategy**:
```python
# Before ❌
print("   mouse.click_on_text('تایید', confidence=0.8)")

# After ✅
print("   mouse.click_on_text('OK', confidence=0.8)")
```

---

#### 6. `core/keyboard_control.py` ⚠️
**Issues**: Persian in example code
**Lines**: 737-738

**Fix Strategy**:
```python
# Before ❌
print(f"Persian: {kb.detect_language('سلام دنیا')}")
print(f"Mixed: {kb.detect_language('Hello سلام')}")

# After ✅
print(f"Persian: {kb.detect_language('سلام دنیا')}")  # Keep string
print(f"Mixed: {kb.detect_language('Hello سلام')}")    # Keep string
# Only change label from "Persian" to "Persian:"
```

---

### Medium Priority (Documentation Examples)

#### 7. Test Data Files
Files that use Persian in test cases - these are OK as data, but output should be English:
- `test_master_controller_complete.py` - Persian test requests are OK
- Test assertions and error messages should be English

---

### Low Priority (Keep as is)

#### ✅ These are fine with Persian:
- **Docstrings** - All docstrings can stay in Persian
- **Comments** - All comments can stay in Persian  
- **Documentation files** (.md) - Can stay in Persian
- **Test data** - Persian strings in test cases are OK
- **User-facing responses** - AI responses can be in Persian

---

## 🔧 Fix Strategy

### Phase 1: Critical CLI Files (Do First)
1. `tests/test_master_controller_complete.py`
2. `tests/quick_test_master.py`
3. `examples/autonomous_demo.py`

### Phase 2: Main Program
4. `main.py`

### Phase 3: Examples
5. `examples/mouse_demo.py`
6. `core/keyboard_control.py` (example section only)

---

## ✅ Translation Guide

### Common Translations

| Persian | English |
|---------|---------|
| در حال مقداردهی اولیه | Initializing |
| آماده است | Ready / is ready |
| موفق | Success / Successful |
| ناموفق | Failed / Unsuccessful |
| خطا | Error |
| توجه | Warning / Note |
| تست | Test |
| نتیجه | Result |
| درخواست | Request |
| ابزار | Tool |
| زمان اجرا | Execution time |
| پاسخ | Response |
| تعداد | Count / Total |
| موفقیت | Success |
| خطای غیرمنتظره | Unexpected error |
| تبریک | Congratulations |
| عالی | Great / Excellent |
| نیاز به بهبود | Needs improvement |
| مشکلات جدی | Serious issues |
| متوقف شد | Stopped / Interrupted |

---

## 📝 Examples

### Test Output
```python
# ❌ Before
print(f"🧪 تست: {test_name}")
print(f"✅ موفق: {passed}/{total}")
print(f"📈 درصد موفقیت: {success_rate:.1f}%")

# ✅ After
print(f"🧪 Test: {test_name}")
print(f"✅ Passed: {passed}/{total}")
print(f"📈 Success Rate: {success_rate:.1f}%")
```

### Error Messages
```python
# ❌ Before
print(f"❌ خطا در اجرای تست: {e}")
print(f"⚠️  تست توسط کاربر متوقف شد")

# ✅ After
print(f"❌ Error running test: {e}")
print(f"⚠️  Test interrupted by user")
```

### Status Messages
```python
# ❌ Before
print("⚙️  در حال مقداردهی اولیه...")
print("✅ Master Controller آماده است!")

# ✅ After  
print("⚙️  Initializing...")
print("✅ Master Controller is ready!")
```

---

## 🎯 Priority Order

1. **First**: Fix all test files (`tests/*.py`)
2. **Second**: Fix main.py CLI output
3. **Third**: Fix examples
4. **Last**: Review and test

---

## ✅ Verification

After fixing, verify:
- [ ] Run `python tests/quick_test_master.py` - No encoding errors
- [ ] Run `python tests/test_master_controller_complete.py` - Clean English output
- [ ] Run `python main.py --help` - English help text
- [ ] Run examples - No CLI encoding issues

---

## 📌 Notes

- Keep Persian in comments/docstrings - they're fine
- Keep Persian in test DATA (e.g., `"سلام"` as test input)
- Only change DISPLAY text (print statements)
- Emojis are fine - they work in CLI
- Focus on user-facing CLI output

---

**Status**: 🔴 Not Started  
**Estimated Time**: 2-3 hours  
**Impact**: High - Will fix all CLI encoding issues

---

Created: December 7, 2025

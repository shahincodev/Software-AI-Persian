#!/usr/bin/env python3
"""تست اتصال API و بررسی مشکلات احتمالی."""

import os
import sys
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()

print("=" * 80)
print("🔍 API Connection Test")
print("=" * 80)

# 1. بررسی فایل .env
print("\n1️⃣ Checking .env file...")
if os.path.exists(".env"):
    print("   ✅ .env file exists")
else:
    print("   ❌ .env file NOT FOUND!")
    sys.exit(1)

# 2. بررسی API Keys
print("\n2️⃣ Checking API Keys...")
api_keys = {
    "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
}

for key_name, key_value in api_keys.items():
    if key_value and key_value.strip() and "YOUR_" not in key_value:
        # بررسی placeholder
        print(f"   ✅ {key_name}: SET (length={len(key_value)})")
        # نمایش اولین 10 کاراکتر
        print(f"      First 10 chars: {key_value[:10]}...")
    else:
        print(f"   ❌ {key_name}: NOT SET or PLACEHOLDER")

# 3. تست Google API
print("\n3️⃣ Testing Google API...")
google_key = os.getenv("GOOGLE_API_KEY")
if not google_key or "YOUR_" in google_key:
    print("   ⏭️  Skipped (no real API key)")
else:
    try:
        # تست با browser_use
        print("   📦 Trying browser_use.llm.google.chat.ChatGoogle...")
        from browser_use.llm.google.chat import ChatGoogle
        from langchain_core.messages import HumanMessage
        
        model = ChatGoogle(model="gemini-2.0-flash-exp", temperature=0.5)
        messages = [HumanMessage(content="سلام، فقط یک کلمه بگو: تست")]
        
        print("   🔄 Sending test request...")
        import asyncio
        response = asyncio.run(model.ainvoke(messages))
        
        print(f"   ✅ Response received: {response.content[:50]}...")
        
    except ModuleNotFoundError as e:
        print(f"   ❌ Module not found: {e}")
    except Exception as e:
        print(f"   ❌ Error: {type(e).__name__}: {e}")

# 4. بررسی وضعیت Git
print("\n4️⃣ Checking Git status...")
import subprocess  # noqa: E402
try:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=True
    )
    if result.stdout.strip():
        print("   ⚠️  You have uncommitted changes:")
        for line in result.stdout.strip().split('\n')[:5]:
            print(f"      {line}")
    else:
        print("   ✅ Working directory is clean")
        
    # بررسی آخرین commit
    result = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        capture_output=True,
        text=True,
        check=True
    )
    print(f"   📝 Latest commit: {result.stdout.strip()}")
    
except Exception as e:
    print(f"   ❌ Git error: {e}")

# 5. بررسی نصب browser_use
print("\n5️⃣ Checking browser_use installation...")
try:
    import browser_use
    print(f"   ✅ browser_use installed (version: {browser_use.__version__})")
except ImportError:
    print("   ❌ browser_use NOT installed")
except AttributeError:
    print("   ✅ browser_use installed (no version info)")

# 6. بررسی Tesseract
print("\n6️⃣ Checking Tesseract OCR...")
tesseract_path = os.getenv("TESSERACT_PATH")
if tesseract_path:
    print(f"   ℹ️  TESSERACT_PATH set: {tesseract_path}")
    if os.path.exists(tesseract_path):
        print("   ✅ Tesseract executable found")
    else:
        print("   ❌ Tesseract path invalid!")
else:
    print("   ⚠️  TESSERACT_PATH not set (OCR may not work)")

print("\n" + "=" * 80)
print("✅ Diagnostic complete!")
print("=" * 80)

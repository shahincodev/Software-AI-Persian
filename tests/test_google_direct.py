"""
تست مستقیم Google API - بدون هیچ کد اضافه‌ای
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print(f"🔑 API Key: {api_key[:10]}...{api_key[-5:]} (len={len(api_key)})")

genai.configure(api_key=api_key)

# تست با مدل‌های مختلف
models_to_test = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.5-flash",
    "gemeni-2.5-pro",      
    "gemini-3-pro-preview",  
]

print("\n" + "="*80)
print("🧪 Testing Google API with different models...")
print("="*80)

for model_name in models_to_test:
    try:
        print(f"\n📡 Testing: {model_name}")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'Hello' in one word")
        print(f"   ✅ SUCCESS: {response.text.strip()}")
    except Exception as e:
        error_str = str(e)
        if "429" in error_str:
            print(f"   ❌ QUOTA ERROR: {model_name}")
            # چاپ جزئیات quota
            if "limit: 0" in error_str:
                print("      ⚠️  Limit is ZERO for this model!")
            if "retry in" in error_str.lower():
                import re
                retry_match = re.search(r'retry in ([\d.]+)s', error_str, re.IGNORECASE)
                if retry_match:
                    print(f"      ⏳ Retry after: {retry_match.group(1)} seconds")
        elif "403" in error_str or "API_KEY" in error_str.upper():
            print("   ❌ AUTH ERROR: Invalid API Key")
        else:
            print(f"   ❌ ERROR: {error_str[:100]}")

print("\n" + "="*80)
print ("💡 Recommendations:")
print("="*80)
print("1. If all models returned 429 → Daily limit exceeded")
print("2. If only one model returned 429 → It has a specific model")
print("3. If it returned 403 → API key is broken")
print("4. If one of them is SUCCESS → Your code is 100% healthy!")

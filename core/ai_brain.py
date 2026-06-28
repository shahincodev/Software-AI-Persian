# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""لایهٔ ساده برای انتخاب مدل‌های LLM.

اینجا از lazy-loading استفاده می‌کنیم تا بارگذاری ماژول‌های سنگین تنها هنگام نیاز انجام شود.
همچنین امکان پیکربندی از طریق متغیرهای محیطی فراهم است.

دارای پشتیبانی برای هزاران مدل مختلف با fallback خودکار - مانند Microsoft Copilot و GitHub Copilot
"""

from __future__ import annotations

import asyncio
import os
import logging
import json
import re
from typing import Any

from core.model_config import get_model_registry, ModelConfig

logger = logging.getLogger(__name__)


class AIBrain:
    """کلاس برای مدیریت و انتخاب مدل مناسب بر اساس منظور (purpose).

    روش کار: مدل‌ها هنگام نیاز ساخته می‌شوند تا زمان شروع برنامه سبک بماند.
    """

    def __init__(self) -> None:
        self._models: dict[str, Any] = {}

    def _analyze_task_complexity(self, task: str) -> str:
        """تحلیل خودکار پیچیدگی تسک و انتخاب بهترین مدل.
        
        این متد بر اساس کلمات کلیدی و محتوای تسک، مناسب‌ترین مدل را انتخاب می‌کند.
        """
        if not task:
            return "normal"
        
        task_lower = task.lower()
        
        # کلمات کلیدی برای عملیات سیستمی
        system_keywords = [
            "install", "open app", "launch", "run program", "photoshop", "notepad",
            "system", "hardware", "cpu", "memory", "process", "kill", "terminate",
            "نصب", "برنامه", "باز کن", "اجرا", "فتوشاپ", "سیستم", "سخت‌افزار",
            "پردازنده", "حافظه", "فرآیند", "بستن"
        ]
        
        # کلمات کلیدی برای کارهای مرورگری
        browser_keywords = [
            "browse", "search", "web", "website", "google", "click", "open",
            "مرور", "جستجو", "وب", "سایت", "گوگل", "کلیک", "باز کن"
        ]
        
        # کلمات کلیدی برای تحلیل و استدلال عمیق
        reasoning_keywords = [
            "analyze", "compare", "explain", "why", "how does", "reason",
            "evaluate", "assess", "investigate", "deep",
            "تحلیل", "مقایسه", "توضیح", "چرا", "چگونه", "دلیل", 
            "ارزیابی", "بررسی", "تحقیق"
        ]
        
        # کلمات کلیدی برای پاسخ‌های سریع
        fast_keywords = [
            "quick", "fast", "simple", "short", "brief",
            "سریع", "ساده", "کوتاه", "خلاصه"
        ]
        
        # بررسی اولویت‌دار
        if any(kw in task_lower for kw in system_keywords):
            logger.info("تشخیص نوع تسک: system")
            return "system"
        elif any(kw in task_lower for kw in browser_keywords):
            logger.info("تشخیص نوع تسک: browser_use")
            return "browse"
        elif any(kw in task_lower for kw in reasoning_keywords):
            logger.info("Task type identification: reasoning")
            return "analyze"
        elif any(kw in task_lower for kw in fast_keywords):
            logger.info("Task type detection: fast")
            return "realtime"
        else:
            # برای تسک‌های طولانی‌تر از 100 کاراکتر از مدل reasoning استفاده کن
            if len(task) > 100:
                logger.info("Task type detection: reasoning (long)")
                return "analyze"
            logger.info("Task type detection: normal")
            return "normal"

    def _load_model(self, name: str) -> Any:
        """بارگذاری مدل با نام منطقی. این توابع importهای سنگین را محصور می‌کند.
        
        پشتیبانی برای OpenRouter (OpenAI)، Google AI Studio، Groq و سایرین.
        """
        try:
            # دریافت پیکربندی مدل
            registry = get_model_registry()
            model_config = registry.get_model(name)
            
            if not model_config:
                logger.warning(f"Model config not found for {name}, using legacy mode")
                # Fallback به سیستم قدیمی
                return self._load_model_legacy(name)
            
            # بررسی کلید API
            if model_config.api_key_env:
                api_key = os.getenv(model_config.api_key_env)
                if not api_key:
                    raise ValueError(f"Missing API key: {model_config.api_key_env}")
            
            # بارگذاری بر اساس ارائه‌دهنده
            if model_config.provider == "openrouter":
                return self._load_openrouter_model(model_config)
            elif model_config.provider == "google":
                return self._load_google_model(model_config)
            elif model_config.provider == "groq":
                return self._load_groq_model(model_config)
            elif model_config.provider == "ollama":
                return self._load_ollama_model(model_config)
            elif model_config.provider == "huggingface":
                return self._load_huggingface_model(model_config)
            else:
                logger.warning(f"Unknown provider: {model_config.provider}, using legacy mode")
                return self._load_model_legacy(name)
            
        except Exception as exc:
            logger.exception("Error loading model %s: %s", name, exc)
            raise
    
    def _load_openrouter_model(self, config: ModelConfig) -> Any:
        """بارگذاری مدل از طریق OpenRouter"""
        try:
            from browser_use.llm.openai.chat import ChatOpenAI
            
            api_key = os.getenv(config.api_key_env)
            
            # OpenRouter به عنوان OpenAI compatible endpoint
            model = ChatOpenAI(
                model=config.name,
                temperature=config.temperature,
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            logger.info(f"✅ Loaded OpenRouter model: {config.name}")
            return model
        except Exception as e:
            logger.exception(f"Failed to load OpenRouter model {config.name}: {e}")
            raise
    
    def _load_google_model(self, config: ModelConfig) -> Any:
        """بارگذاری مدل از طریق Google AI Studio"""
        try:
            from browser_use.llm.google.chat import ChatGoogle
            
            # نام مدل برای Google (مثلاً: gemini-3-pro-preview)
            model_name = config.name.replace("google-", "")
            
            model = ChatGoogle(
                model=model_name,
                temperature=config.temperature
            )
            logger.info(f"✅ Loaded Google model: {model_name}")
            return model
        except Exception as e:
            logger.exception(f"Failed to load Google model {config.name}: {e}")
            raise
    
    def _load_groq_model(self, config: ModelConfig) -> Any:
        """بارگذاری مدل از طریق Groq"""
        try:
            from browser_use.llm.groq.chat import ChatGroq
            
            model_name = config.name.replace("groq-", "")
            
            model = ChatGroq(
                model=model_name,
                temperature=config.temperature
            )
            logger.info(f"✅ Loaded Groq model: {model_name}")
            return model
        except Exception as e:
            logger.exception(f"Failed to load Groq model {config.name}: {e}")
            raise
    
    def _load_ollama_model(self, config: ModelConfig) -> Any:
        """بارگذاری مدل محلی Ollama"""
        try:
            from langchain_community.llms import Ollama
            
            model_name = config.name.replace("ollama-", "")
            
            model = Ollama(
                model=model_name,
                base_url=config.base_url or "http://localhost:11434",
                temperature=config.temperature
            )
            logger.info(f"✅ Loaded Ollama model: {model_name}")
            return model
        except Exception as e:
            logger.exception(f"Failed to load Ollama model {config.name}: {e}")
            raise
    
    def _load_huggingface_model(self, config: ModelConfig) -> Any:
        """بارگذاری مدل از طریق HuggingFace Inference"""
        try:
            from langchain_huggingface import HuggingFaceEndpoint
            
            api_key = os.getenv(config.api_key_env)
            repo_id = config.name.replace("huggingface-", "")
            
            model = HuggingFaceEndpoint(
                repo_id=repo_id,
                huggingfacehub_api_token=api_key,
                temperature=config.temperature,
                model_kwargs={"max_length": config.max_tokens}
            )
            logger.info(f"✅ Loaded HuggingFace model: {repo_id}")
            return model
        except Exception as e:
            logger.exception(f"Failed to load HuggingFace model {config.name}: {e}")
            raise
    
    def _load_model_legacy(self, name: str) -> Any:
        """سیستم قدیمی برای compatibility"""
        if name == "reasoning":
            from browser_use.llm.google.chat import ChatGoogle

            model = ChatGoogle(model=os.getenv("GOOGLE_REASONING_MODEL", "gemini-2.5-flash"),
                               temperature=float(os.getenv("MODEL_TEMPERATURE", "0.5")))
        elif name == "system":
            from browser_use.llm.google.chat import ChatGoogle

            model = ChatGoogle(model=os.getenv("GOOGLE_SYSTEM_MODEL", "gemini-2.5-flash"),
                               temperature=float(os.getenv("SYSTEM_MODEL_TEMPERATURE", "0.3")))
        elif name == "browser_use":
            from browser_use.llm.browser_use.chat import ChatBrowserUse

            model = ChatBrowserUse()
        elif name == "fast":
            from browser_use.llm.groq.chat import ChatGroq

            model = ChatGroq(model=os.getenv("GROQ_MODEL", "groq-1"),
                              temperature=float(os.getenv("MODEL_TEMPERATURE", "0.7")))
        elif name == "normal":
            from browser_use.llm.openai.chat import ChatOpenAI

            model = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini"),
                                temperature=float(os.getenv("MODEL_TEMPERATURE", "0")))
        else:
            logger.warning("Invalid model name: %s - use default model", name)
            from browser_use.llm.openai.chat import ChatOpenAI

            model = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini"),
                                temperature=float(os.getenv("MODEL_TEMPERATURE", "0")))
        logger.info("Artificial intelligence model opened (legacy): %s", name)
        return model

    def get_model(self, purpose: str | None = None, task: str | None = None) -> Any:
        """انتخاب خودکار مدل بر اساس تسک یا منظور.

        پارامترها:
        - purpose: منظور دستی ('analyze', 'browse', 'realtime', 'normal')
        - task: متن تسک برای تحلیل خودکار (اگر purpose داده نشده باشد)

        اگر هیچ‌کدام داده نشود، از مدل 'normal' استفاده می‌شود.
        
        مثال:
        >>> brain.get_model(task="مرورگر را باز کن و گوگل را جستجو کن")  # auto: browse
        >>> brain.get_model(purpose="analyze")  # manual: reasoning
        >>> brain.get_model()  # default: normal
        """
        # اگر purpose داده نشده، از task تحلیل کن
        if purpose is None:
            if task:
                purpose = self._analyze_task_complexity(task)
                logger.info("Automatic model selection based on task: %s", purpose)
            else:
                purpose = "normal"
                logger.info("Use default model: normal")
        
        # تبدیل purpose به نام داخلی مدل
        key = {
            "analyze": "reasoning",
            "browse": "browser_use",
            "realtime": "fast",
            "normal": "normal",
            "system": "system",
        }.get(purpose, "normal")

        # lazy-loading: فقط در صورت نیاز مدل را بارگذاری کن
        if key not in self._models:
            self._models[key] = self._load_model(key)

        return self._models[key]
    
    async def ask_with_fallback(self, prompt: str, mode: str = "normal", max_tokens: int = 500) -> str:
        """پرسش هوشمند با fallback خودکار به مدل‌های دیگر.
        
        اگر یک مدل فیل شد، خودکار مدل‌های بعدی را امتحان می‌کند - مانند GitHub Copilot.
        از registry استفاده می‌کند تا دسترسی به هزاران مدل داشته باشیم.
        
        Args:
            prompt: سوال یا دستور
            mode: نوع مدل اولیه ('system', 'normal', 'reasoning', 'fast')
            max_tokens: حداکثر طول پاسخ
        
        Returns:
            پاسخ متنی AI (از اولین مدل موفق)
        """
        registry = get_model_registry()
        available_models = registry.get_available_models()
        
        if not available_models:
            logger.error("❌ No available models found! Check your API keys.")
            logger.info("📋 Available models: %s", json.dumps(registry.export_config(), indent=2))
            return ""
        
        # لاگ مدل‌های دردسترس
        logger.info(f"🤖 Available models ({len(available_models)}):")
        for m in available_models[:5]:  # فقط 5 تای اول
            logger.info(f"   - {m.name} (priority: {m.priority})")
        if len(available_models) > 5:
            logger.info(f"   ... and {len(available_models) - 5} more")
        
        # لیست مدل‌های قدیمی برای compatibility
        legacy_fallback_order = {
            "system": ["system", "normal", "fast", "reasoning"],
            "normal": ["normal", "fast", "system", "reasoning"],
            "fast": ["fast", "normal", "system", "reasoning"],
            "reasoning": ["reasoning", "system", "normal", "fast"]
        }
        
        # سعی اول: از registry استفاده کن
        for i, model_config in enumerate(available_models):
            try:
                logger.info(f"🤖 Trying model {i+1}/{len(available_models)}: {model_config.name}")
                
                # بارگذاری مدل
                if model_config.name not in self._models:
                    self._models[model_config.name] = self._load_model(model_config.name)
                
                model = self._models[model_config.name]
                result = await self.ask(prompt, mode=model_config.name, max_tokens=max_tokens)
                
                if result and result.strip():
                    if i > 0:
                        logger.info(f"✅ Success with fallback model: {model_config.name}")
                    return result
                else:
                    logger.warning(f"⚠️ Model {model_config.name} returned empty response")
                    
            except Exception as e:
                logger.warning(f"❌ Model {model_config.name} failed: {e}")
                if i == len(available_models) - 1:
                    logger.error("💥 All available models failed!")
                continue
        
        return ""
    
    
    async def ask(self, prompt: str, mode: str = "normal", max_tokens: int = 500) -> str:
        """پرسش ساده از AI و دریافت پاسخ متنی.
        
        Args:
            prompt: سوال یا دستور
            mode: نام مدل (می‌تواند نام registry یا نام قدیمی باشد)
            max_tokens: حداکثر طول پاسخ
        
        Returns:
            پاسخ متنی AI
        """
        try:
            # اگر mode یک نام registry است، به‌طور مستقیم لاد کن
            registry = get_model_registry()
            model_config = registry.get_model(mode)
            
            if model_config:
                # نام مدل registry
                if mode not in self._models:
                    self._models[mode] = self._load_model(mode)
                model = self._models[mode]
                logger.debug(f"Using registry model: {mode} ({model_config.provider})")
            else:
                # فرض کن که mode یک نام قدیمی است
                if mode not in self._models:
                    self._models[mode] = self._load_model(mode)
                model = self._models[mode]
                logger.debug(f"Using legacy model: {mode}")
            
            # فراخوانی مدل - ساخت پیام بر اساس provider (OpenAI/Groq/Google)
            module_name = getattr(model, "__module__", "").lower()

            def _build_provider_message(p):
                try:
                    if "openai" in module_name:
                        from browser_use.llm.openai.serializer import UserMessage  # type: ignore
                        return [UserMessage(content=p)]
                    if "groq" in module_name:
                        from browser_use.llm.groq.serializer import UserMessage  # type: ignore
                        return [UserMessage(content=p)]
                    if "google" in module_name:
                        from browser_use.llm.google.serializer import UserMessage  # type: ignore
                        return [UserMessage(content=p)]
                except Exception:
                    logger.exception("Failed to build provider-specific message; falling back to raw prompt")
                return p  # fallback: raw string

            payload = _build_provider_message(prompt)

            if hasattr(model, 'ainvoke'):
                response = await asyncio.wait_for(
                    model.ainvoke(payload),
                    timeout=60.0
                )
            elif hasattr(model, 'invoke'):
                response = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, model.invoke, payload),
                    timeout=60.0
                )
            else:
                raise ValueError("Model does not support invoke or ainvoke")

            # Extract string content from response
            if isinstance(response, str):
                return response.strip()
            if hasattr(response, 'content'):
                return str(response.content).strip()
            if hasattr(response, 'completion'):
                return str(response.completion).strip()
            logger.warning("Unexpected response type from invoke/ainvoke: %s", type(response))
            return str(response).strip()
        
        except Exception as e:
            logger.exception("AI ask failed: %s", e)
            raise  # Re-raise برای fallback
    
    def _sanitize_ai_response(self, response: str) -> str:
        """پاکسازی پاسخ AI از داده‌های مشکوک.
        
        Args:
            response: پاسخ خام AI
            
        Returns:
            پاسخ پاکسازی شده
        """
        # حذف completion= و thinking= که در لاگ‌ها دیده شده
        import re
        
        # الگوهای مشکوک - به ترتیب اولویت
        suspicious_patterns = [
            # Pattern 1: completion='app.exe'
            (r"completion\s*=\s*['\"]([^'\"]+\.exe)['\"]?", 1),
            # Pattern 2: completion=app.exe (without quotes)
            (r"completion\s*=\s*(\w+\.exe)", 1),
            # Pattern 3: thinking='...'
            (r"thinking\s*=\s*['\"]([^'\"]+)['\"]?", 0),  # 0 = remove completely
            # Pattern 4: thinking=... (without quotes)
            (r"thinking\s*=\s*(\S+)", 0),
        ]
        
        cleaned = response
        for pattern, extract_group in suspicious_patterns:
            if extract_group > 0:
                # استخراج مقدار
                matches = re.findall(pattern, cleaned, re.IGNORECASE)
                if matches:
                    logger.warning(f"⚠️ Suspicious pattern detected: {pattern[:30]}...")
                    # جایگزینی کل pattern با فقط مقدار استخراج شده
                    for match in matches:
                        if match.endswith('.exe'):
                            cleaned = match
                            logger.info(f"✅ Extracted clean app name: {cleaned}")
                            break
            else:
                # حذف کامل
                cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
                if cleaned != response:
                    logger.info(f"✅ Removed suspicious pattern: {pattern[:30]}...")
        
        return cleaned.strip()
    
    async def interpret_system_request(self, user_request: str) -> list[dict[str, Any]]:
        """تفسیر درخواست کاربر و تبدیل به لیست اقدامات.
        
        Args:
            user_request: درخواست طبیعی کاربر (فارسی یا انگلیسی)
        
        Returns:
            لیست اقدامات در قالب JSON
        """
        # پاکسازی ورودی کاربر
        user_request = self._sanitize_ai_response(user_request)
        
        prompt = f"""You are a Windows automation system. Convert the user's natural language request into structured actions.

User Request: {user_request}

IMPORTANT NOTES:
- Windows Notepad (notepad.exe) is a SIMPLE text editor with NO tabs, NO "+" button
- To create new file in Notepad: just start typing (it's already a new file)
- To save in Notepad: use Ctrl+S shortcut, NOT clicking menus
- For .bat files, save with double quotes: "filename.bat" to preserve extension
- Only use applications from the allowed list (check safety_filter.py)

Supported Actions:
1. LaunchApp: Open an application
   {{"type": "LaunchApp", "params": {{"app_name": "app.exe", "arguments": []}}, "priority": "normal", "description": "Open app"}}

2. DesktopClick: Click on UI element (use sparingly - prefer keyboard shortcuts)
   {{"type": "DesktopClick", "params": {{"target": "button text", "button": "left", "clicks": 1}}, "priority": "normal", "description": "Click button"}}

3. DesktopType: Type text or use keyboard shortcuts
   {{"type": "DesktopType", "params": {{"text": "hello", "target": null}}, "priority": "normal", "description": "Type hello"}}
   For shortcuts: {{"text": "^s"}} for Ctrl+S, {{"text": "^o"}} for Ctrl+O

4. InstallPackage: Install software
   {{"type": "InstallPackage", "params": {{"package_name": "git", "package_manager": "winget", "silent": true}}, "priority": "normal", "description": "Install git"}}

5. TerminateProcess: Close application
   {{"type": "TerminateProcess", "params": {{"process_name": "app.exe", "force": false}}, "priority": "normal", "description": "Close app"}}

6. QueryHardware: Get system info
   {{"type": "QueryHardware", "params": {{"query_type": "all"}}, "priority": "normal", "description": "Get hardware info"}}

7. ExecuteCommand: Run shell command (requires approval)
   {{"type": "ExecuteCommand", "params": {{"command": "dir", "shell": "cmd"}}, "priority": "normal", "description": "List files"}}

BEST PRACTICES:
- Use keyboard shortcuts instead of clicking menus (faster + more reliable)
- For Notepad: Ctrl+S to save, Ctrl+O to open, Ctrl+N for new
- Keep actions simple and atomic
- Avoid clicking on elements that might not exist

Return ONLY a valid JSON array of actions, nothing else. Example:
[{{"type": "LaunchApp", "params": {{"app_name": "notepad.exe", "arguments": []}}, "priority": "normal", "description": "Open Notepad"}},
 {{"type": "DesktopType", "params": {{"text": "echo hello world", "target": null}}, "priority": "normal", "description": "Type code"}},
 {{"type": "DesktopType", "params": {{"text": "^s", "target": null}}, "priority": "normal", "description": "Save (Ctrl+S)"}}]

JSON Array:"""

        try:
            # استفاده از fallback برای اطمینان از دریافت پاسخ
            response = await self.ask_with_fallback(prompt, mode="system", max_tokens=500)
            
            # Log the raw response for debugging
            logger.debug(f"📋 Raw AI response: {response[:500]}")
            
            # تلاش برای parse کردن JSON
            import json
            import re
            
            # استخراج JSON از پاسخ
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                logger.debug(f"📋 Extracted JSON: {json_str[:200]}")
                actions = json.loads(json_str)
                
                if isinstance(actions, list):
                    logger.info("✅ AI parsed %d actions successfully", len(actions))
                    return actions
            
            logger.warning("⚠️ AI response is not valid JSON: %s", response[:200])
            return []
        
        except Exception as e:
            logger.exception("❌ AI interpretation failed: %s", e)
            return []
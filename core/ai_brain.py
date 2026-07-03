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
from core.tool_schema import (
    TOOLS, validate_tool_call, get_tool_prompt_block, get_all_tool_names
)

logger = logging.getLogger(__name__)

MAX_SCHEMA_RETRIES = 2


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

            model = ChatOpenAI(
                model=os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini"),
                temperature=float(os.getenv("MODEL_TEMPERATURE", "0")),
                api_key=os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY"),
                base_url="https://openrouter.ai/api/v1",
            )
        else:
            logger.warning("Invalid model name: %s - use default model", name)
            from browser_use.llm.openai.chat import ChatOpenAI

            model = ChatOpenAI(
                model=os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini"),
                temperature=float(os.getenv("MODEL_TEMPERATURE", "0")),
                api_key=os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY"),
                base_url="https://openrouter.ai/api/v1",
            )
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
        
        # لاگ مدل‌های دردسترس (DEBUG level to reduce noise on every request)
        logger.debug(f"Available models ({len(available_models)}): {', '.join(m.name for m in available_models[:3])}...")
        
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
                continue
        
        logger.error("💥 All %d available models failed. Check your API keys in .env", len(available_models))
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
            response = await self.ask_with_fallback(prompt, mode="system", max_tokens=500)
            logger.debug("Raw AI response: %s", response[:500])
            
            actions = self._extract_json_actions(response)
            if actions:
                logger.info("AI parsed %d actions successfully", len(actions))
                return actions
            
            logger.warning("AI response is not valid JSON: %s", response[:200])
            return []
        
        except Exception as e:
            logger.exception("AI interpretation failed: %s", e)
            return []

    def _extract_json_actions(self, response: str) -> list[dict[str, Any]]:
        """Extract JSON actions from AI response with multiple fallback strategies."""
        import json as _json
        import re as _re
        
        if not response or not response.strip():
            return []
        
        # Strategy 1: Find JSON array in the response
        json_match = _re.search(r'\[[\s\S]*?\]', response)
        if json_match:
            json_str = json_match.group(0)
            for attempt in [json_str, _re.sub(r'```json|```|json', '', json_str).strip()]:
                if attempt:
                    try:
                        result = _json.loads(attempt)
                        if isinstance(result, list):
                            return result
                    except _json.JSONDecodeError:
                        continue
        
        # Strategy 2: Try to find individual JSON objects and combine
        obj_matches = _re.findall(r'\{[^{}]*\}', response)
        if obj_matches:
            items = []
            for obj_str in obj_matches:
                try:
                    obj = _json.loads(obj_str)
                    if isinstance(obj, dict) and ("type" in obj or "tool" in obj):
                        items.append(obj)
                except _json.JSONDecodeError:
                    continue
            if items:
                return items
        
        # Strategy 3: Fix common JSON issues
        cleaned = response.strip()
        # Remove markdown code blocks
        cleaned = _re.sub(r'^```(?:json)?\s*', '', cleaned)
        cleaned = _re.sub(r'\s*```$', '', cleaned)
        # Fix trailing commas
        cleaned = _re.sub(r',\s*([}\]])', r'\1', cleaned)
        # Fix single quotes to double quotes
        cleaned = cleaned.replace("'", '"')
        
        try:
            result = _json.loads(cleaned)
            if isinstance(result, list):
                return result
            if isinstance(result, dict):
                return [result]
        except _json.JSONDecodeError:
            pass
        
        return []

    async def agent_chat(self, user_message: str, system_context: str = "",
                         last_actions: list[dict[str, Any]] | None = None,
                         screen_context: str = "") -> dict[str, Any]:
        """Agent-mode chat: AI with full system access decides what to do.

        Uses unified tool schema with validation and auto-retry.

        Args:
            user_message: The user's request
            system_context: System context (files, drives, etc.)
            last_actions: Recent actions taken
            screen_context: Current screen state from VisionLoopManager

        Returns dict with:
            - "action": "tool_call" | "chat_reply" | "none"
            - "tool_calls": list of tool call dicts (if action == "tool_call")
            - "response": text response (if action == "chat_reply")
        """
        context_block = ""
        if system_context:
            context_block = f"\n## Current System Context:\n{system_context}\n"

        screen_block = ""
        if screen_context:
            screen_block = f"\n## Current Screen State:\n{screen_context}\n"

        actions_block = ""
        if last_actions:
            actions_block = "\n## Recent Actions Taken:\n"
            for a in last_actions[-5:]:
                status = a.get("status", "unknown")
                desc = a.get("description", a.get("command", "unknown"))
                actions_block += f"- [{status}] {desc}\n"

        tools_block = get_tool_prompt_block()
        tool_names = ", ".join(get_all_tool_names())

        prompt = f"""You are Software-AI, an intelligent Windows desktop agent with FULL system access.

Your job is to convert natural language requests into structured tool calls or chat replies.
You can OBSERVE the screen using vision tools to understand what is currently visible.

{context_block}
{screen_block}
{actions_block}

## Available Tools:
{tools_block}

## User Request:
{user_message}

## Response Format:
You MUST respond with ONE of the following JSON formats:

### Option A: Tool calls (for actions on the system)
```json
{{
  "action": "tool_call",
  "tool_calls": [
    {{"tool": "tool_name", "params": {{"param1": "value1"}}, "description": "what this does"}}
  ]
}}
```

### Option B: Chat reply (for questions/information)
```json
{{
  "action": "chat_reply",
  "response": "your helpful response here"
}}
```

## Rules:
1. ALWAYS return valid JSON - no extra text before or after
2. Tool names MUST be one of: {tool_names}
3. Every required parameter MUST be included
4. For file operations, use FULL paths (e.g., D:\\\\folder\\\\file.txt)
5. Respond in the same language as the user
6. Multiple tool_calls execute in sequence

Return ONLY the JSON:"""

        # Retry loop with schema validation
        last_error = None
        for attempt in range(MAX_SCHEMA_RETRIES + 1):
            try:
                # Build prompt with error context if retrying
                current_prompt = prompt
                if last_error:
                    current_prompt += f"\n\n## PREVIOUS ERROR (attempt {attempt + 1}):\n{last_error}\nPlease fix and return valid JSON."

                response = await self.ask_with_fallback(current_prompt, mode="system", max_tokens=800)
                logger.debug("Agent chat raw response (attempt %d): %s", attempt + 1, response[:500])

                parsed = self._parse_agent_response(response)
                if not parsed:
                    last_error = "Response is not valid JSON. Return a JSON object with 'action' field."
                    logger.warning("Attempt %d: Failed to parse JSON", attempt + 1)
                    continue

                # If it's a chat reply, return immediately (no validation needed)
                if parsed.get("action") == "chat_reply":
                    return parsed

                # If it's a tool_call, validate each tool call against schema
                if parsed.get("action") == "tool_call":
                    tool_calls = parsed.get("tool_calls", [])
                    if not tool_calls:
                        last_error = "tool_calls array is empty. Provide at least one tool call."
                        logger.warning("Attempt %d: Empty tool_calls", attempt + 1)
                        continue

                    all_valid = True
                    errors = []
                    for i, tc in enumerate(tool_calls):
                        is_valid, msg = validate_tool_call(tc)
                        if not is_valid:
                            all_valid = False
                            errors.append(f"Tool call {i+1}: {msg}")

                    if all_valid:
                        logger.info("Agent parsed %d valid tool calls", len(tool_calls))
                        return parsed
                    else:
                        last_error = "Invalid tool calls:\n" + "\n".join(errors)
                        logger.warning("Attempt %d: Schema validation failed: %s", attempt + 1, last_error)
                        continue

                # Unknown action type
                last_error = f"Unknown action type: {parsed.get('action')}. Use 'tool_call' or 'chat_reply'."
                logger.warning("Attempt %d: Unknown action type", attempt + 1)

            except Exception as e:
                logger.exception("Agent chat attempt %d failed: %s", attempt + 1, e)
                last_error = f"Exception: {str(e)}"

        # All retries exhausted - return error as chat reply
        logger.error("All %d attempts exhausted for agent_chat", MAX_SCHEMA_RETRIES + 1)
        return {
            "action": "chat_reply",
            "response": "I had trouble processing that request. Could you please rephrase it?"
        }

    def _parse_agent_response(self, response: str) -> dict[str, Any] | None:
        """Parse agent response as JSON action."""
        import json as _json
        import re as _re
        
        if not response or not response.strip():
            return None
        
        # Try to extract JSON object
        json_match = _re.search(r'\{[\s\S]*\}', response)
        if json_match:
            json_str = json_match.group(0)
            for attempt in [json_str, _re.sub(r'```json|```|json', '', json_str).strip()]:
                if attempt:
                    try:
                        result = _json.loads(attempt)
                        if isinstance(result, dict) and "action" in result:
                            return result
                    except _json.JSONDecodeError:
                        continue
        
        # Try cleaning common issues
        cleaned = response.strip()
        cleaned = _re.sub(r'^```(?:json)?\s*', '', cleaned)
        cleaned = _re.sub(r'\s*```$', '', cleaned)
        cleaned = _re.sub(r',\s*([}\]])', r'\1', cleaned)
        
        try:
            result = _json.loads(cleaned)
            if isinstance(result, dict) and "action" in result:
                return result
        except _json.JSONDecodeError:
            pass
        
        return None
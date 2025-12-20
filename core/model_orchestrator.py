# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System
"""
Model Orchestrator: اجرای موازی چند مدل LLM و انتخاب بهترین پاسخ
ایده: مانند Copilot X و ChatHub - پاسخ همه مدل‌ها جمع‌آوری و بهترین انتخاب می‌شود
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from core.model_config import get_model_registry, ModelConfig
from core.ai_brain import AIBrain

logger = logging.getLogger(__name__)

class ModelOrchestrator:
    def __init__(self, timeout_per_model: float = 8.0, judge_mode: bool = False):
        self.timeout_per_model = timeout_per_model
        self.judge_mode = judge_mode
        self.brain = AIBrain()
        self.registry = get_model_registry()

    async def ask_all_models(self, prompt: str, max_models: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        به همه مدل‌های فعال همزمان پرسش می‌فرستد و پاسخ‌ها را جمع می‌کند.
        خروجی: لیست دیکشنری شامل پاسخ، مدل، زمان، موفقیت/خطا
        """
        models = self.registry.get_available_models()
        if max_models:
            models = models[:max_models]
        tasks = []
        for model in models:
            tasks.append(self._ask_one_model(prompt, model))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        responses = []
        for model, result in zip(models, results):
            if isinstance(result, Exception):
                logger.warning(f"Model {model.name} failed: {result}")
                responses.append({
                    "model": model.name,
                    "success": False,
                    "error": str(result),
                    "response": None,
                    "latency": None
                })
            else:
                responses.append(result)
        return responses

    async def _ask_one_model(self, prompt: str, model: ModelConfig) -> Dict[str, Any]:
        """پرسش به یک مدل با timeout و مدیریت خطا"""
        import time
        start = time.perf_counter()
        try:
            coro = self.brain.ask(prompt, mode=model.name)
            response = await asyncio.wait_for(coro, timeout=self.timeout_per_model)
            latency = time.perf_counter() - start
            return {
                "model": model.name,
                "success": True,
                "response": response,
                "latency": latency
            }
        except Exception as e:
            latency = time.perf_counter() - start
            logger.warning(f"Model {model.name} error: {e}")
            return {
                "model": model.name,
                "success": False,
                "error": str(e),
                "response": None,
                "latency": latency
            }

    async def collect_and_select(self, prompt: str, max_models: Optional[int] = None, judge_mode: Optional[bool] = None) -> Dict[str, Any]:
        """
        اجرای موازی همه مدل‌ها و انتخاب بهترین پاسخ
        خروجی: دیکشنری شامل پاسخ برتر، همه پاسخ‌ها و متادیتا
        """
        judge = self.judge_mode if judge_mode is None else judge_mode
        responses = await self.ask_all_models(prompt, max_models=max_models)
        valid_responses = [r for r in responses if r["success"] and r["response"]]
        if not valid_responses:
            return {"best": None, "all": responses, "reason": "no valid response"}
        # حالت ساده: بهترین پاسخ بر اساس طول و latency (بعداً judge-model اضافه می‌شود)
        scored = sorted(valid_responses, key=lambda r: (-(len(r["response"]) if r["response"] else 0), r["latency"]))
        best = scored[0]
        # TODO: اگر judge_mode فعال بود، یک مدل judge برای رتبه‌بندی استفاده شود
        return {"best": best, "all": responses, "reason": "simple scoring (longest, fastest)"}

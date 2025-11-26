#!/usr/bin/env python3
"""تست سریع برای بررسی عملکرد عامل هوشمند."""

import asyncio
import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_basic_functionality():
    """تست عملکرد پایه."""
    from core.intelligent_agent import IntelligentSystemAgent
    
    print("Test: Intelligent System Agent")
    print("=" * 50)
    
    # ایجاد عامل در حالت dry_run
    agent = IntelligentSystemAgent(dry_run=True)
    print("OK: Agent created")
    
    # تست خلاصه سیستم
    summary = agent.get_system_summary()
    print("\nSystem Summary:")
    print(summary)
    
    # تست درخواست ساده
    print("\nTest request: 'open Notepad'")
    result = await agent.process_request("open Notepad")
    print(f"\n{result}")
    
    print("\n" + "=" * 50)
    print("All tests passed!")


if __name__ == "__main__":
    asyncio.run(test_basic_functionality())

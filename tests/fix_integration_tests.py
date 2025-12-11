#!/usr/bin/env python3
"""
Fix async/await in integration tests
"""
import re

# Read backup file
with open("tests/test_intent_system_integration.py.backup", "r", encoding="utf-8") as f:
    content = f.read()

# Fix 1: Replace def test_ with @pytest.mark.asyncio + async def test_
content = re.sub(
    r'(\n    )(def test_)',
    r'\1@pytest.mark.asyncio\n    async def test_',
    content
)

# Fix 2: Add await to analyzer.analyze
content = re.sub(
    r'(\s+)intent = analyzer\.analyze\(',
    r'\1intent = await analyzer.analyze(',
    content
)

# Fix 3: Add await to plan_generator.generate_plan
content = re.sub(
    r'(\s+)plan = plan_generator\.generate_plan\(',
    r'\1plan = await plan_generator.generate_plan(',
    content
)

# Fix 4: Add await to plan_validator.validate
content = re.sub(
    r'(\s+)validation = plan_validator\.validate\(',
    r'\1validation = await plan_validator.validate(',
    content
)

# Fix 5: Fix doubled asyncio decorators
content = re.sub(
    r'@pytest\.mark\.asyncio\n    @pytest\.mark\.asyncio',
    r'@pytest.mark.asyncio',
    content
)

# Write fixed file
with open("tests/test_intent_system_integration.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Fixed async/await issues in integration tests")

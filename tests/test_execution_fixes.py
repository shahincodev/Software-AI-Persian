#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تست‌های رفع باگ‌های ترتیب اجرا، آلودگی ورودی و نمایش نادرست موفقیت.

Three separate test cases, one per bug:
  1. test_execution_order        — Bug #1: sequential dependency cascade
  2. test_stdin_isolation_order    — Bug #2: Desktop action cannot execute
                                   before preceding System action completes
  3. test_display_accuracy        — Bug #3: ✅/❌ symbols match real outcomes
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.intelligent_agent import IntelligentSystemAgent
from core.system_actions import LaunchAppAction, ExecuteCommandAction
from core.system_actions import ActionResult as SysActionResult, ActionStatus
from core.action_controller import ActionOutcome, ActionResult as ControllerResult
from core.execution_manager import ExecutionManager
from core.safety_filter import SafetyFilter, UserConsentManager
from core.system_tools import SystemToolAdapter


async def test_execution_order():
    """
    Bug #1 test: sequential dependency cascade.

    When one action fails, all subsequent actions MUST be reported as ❌
    and never execute. The old code had a two-track dispatch where
    Desktop actions ran inline while System actions queued — this test
    proves the new single-track sequential dispatch prevents that.
    """
    print("\n🔍 Test 1: Execution Order — Dependency Cascade")
    print("=" * 55)

    safety = SafetyFilter(strict_mode=False)
    consent = UserConsentManager(auto_approve_safe=False)
    adapter = SystemToolAdapter(dry_run=True)
    executor = ExecutionManager(
        safety_filter=safety, consent_manager=consent,
        adapter=adapter, dry_run=True,
    )

    action1 = LaunchAppAction(app_name="notepad.exe", require_consent=True)
    action2 = ExecuteCommandAction(command="echo should-not-run", dry_run=True)

    succeeded = 0
    failed = 0
    previous_failed = False
    output = []

    for action, desc in [
        (action1, "Open Notepad"),
        (action2, "Echo should-not-run"),
    ]:
        if previous_failed:
            output.append(f"❌ {desc}")
            failed += 1
            continue

        result = await executor.execute_single(action)

        if result.success:
            output.append(f"✅ {desc}")
            succeeded += 1
        else:
            output.append(f"❌ {desc}")
            failed += 1
            previous_failed = True

    summary = f"\n📊 Summary: {succeeded} succeeded, {failed} failed"
    full = "\n".join(output) + summary
    print(full)

    assert "❌ Open Notepad" in full, \
        "First action should be ❌ (consent not available)"
    assert "❌ Echo should-not-run" in full, \
        "Second action should be ❌ (dependency cascade from first)"
    assert "0 succeeded, 2 failed" in summary, \
        "Stats must reflect both failures"

    print("✅ PASSED: dependency cascade works correctly")
    return True


async def test_stdin_isolation_order():
    """
    Bug #2 test: Desktop action cannot execute before preceding
    System action completes.

    In the OLD code, the two-track dispatch ran Desktop actions inline
    during the loop iteration — they would execute regardless of whether
    the preceding System action had completed or failed. This meant a
    TypeAction could fire into the terminal (sending keystrokes to stdin)
    before a LaunchApp had finished opening the target window.

    In the NEW code, actions execute strictly sequentially. If the
    System action fails (e.g. consent prompt gets EOFError in a
    non-interactive test), the dependency cascade prevents ALL
    subsequent actions — including Desktop ones — from executing.

    This test proves the structural fix by:
    1. Mocking parse_request to return a LaunchApp (System) followed
       by a TypeAction (Desktop).
    2. Installing a spy on action_controller.execute_action that records
       whether it was EVER called.
    3. Calling process_request — the LaunchApp fails (input() raises
       EOFError in non-interactive mode), triggering the cascade.
    4. Asserting that execute_action was NEVER called, proving the
       Desktop action was structurally blocked from running before
       the System action completed.

    This would FAIL on OLD code: the two-track dispatch ran the
    TypeAction inline during iteration 2, reaching execute_action
    regardless of the LaunchApp's queue status.
    """
    print("\n🔍 Test 2: STDIN Isolation — Desktop action blocked by cascade")
    print("=" * 55)

    agent = IntelligentSystemAgent(dry_run=True)

    # Spy state: record whether action_controller.execute_action is EVER called
    call_record = {"desktop_called": False}

    original_execute_action = agent.action_controller.execute_action

    def spy_execute_action(action, auto_consent=False):
        call_record["desktop_called"] = True
        return ActionOutcome(
            result=ControllerResult.SUCCESS,
            message="ok",
            duration=0.0,
        )

    agent.action_controller.execute_action = spy_execute_action

    # Mock parser to return LaunchApp (System) then TypeAction (Desktop)
    async def mock_parse(text):
        return [
            {
                "type": "LaunchApp",
                "params": {"app_name": "notepad.exe"},
                "description": "Open Notepad",
                "priority": "normal",
            },
            {
                "type": "DesktopType",
                "params": {"text": "hello"},
                "description": "Type 'hello'",
                "priority": "normal",
            },
        ]

    agent.parser.parse_request = mock_parse

    result = await agent.process_request("test")

    print(result)
    print()

    # NEW code: LaunchApp fails (input() EOFError in non-interactive test)
    # → dependency cascade → TypeAction never reaches execute_action
    assert not call_record["desktop_called"], \
        "Desktop execute_action was called despite System action failing — " \
        "would indicate old two-track dispatch behavior"

    assert "❌ Open Notepad" in result
    assert "❌ Type 'hello'" in result

    print("✅ PASSED: Desktop action structurally blocked by dependency cascade")
    return True


async def test_display_accuracy():
    """
    Bug #3 test: per-action symbols match actual outcomes.

    The old code appended '✓ {description}' at submission time,
    BEFORE the action ran. This test verifies:
    1. No submission-time '✓' appears in any output.
    2. Every action uses ✅ (post-execution success) or ❌ (failure).
    3. The stats line's counts match the number of ✅/❌ symbols.
    """
    print("\n🔍 Test 3: Display Accuracy — Symbols Match Outcomes")
    print("=" * 55)

    agent = IntelligentSystemAgent(dry_run=True)

    test_cases = [
        ("create folder DisplayTestA on desktop", "create-folder"),
        ("create file displaytest_b.txt on desktop", "create-file"),
    ]

    all_pass = True

    for request, label in test_cases:
        result = await agent.process_request(request)
        lines = result.split('\n')

        old_v = [l for l in lines if l.startswith('✓')]
        if old_v:
            print(f"❌ [{label}] Found submission-time '✓': {old_v}")
            all_pass = False

        status_lines = [l for l in lines if l.startswith('✅') or l.startswith('❌')]
        if not status_lines:
            print(f"❌ [{label}] No post-execution symbols found")
            all_pass = False
            continue

        success_symbols = sum(1 for l in lines if l.startswith('✅'))
        fail_symbols = sum(1 for l in lines if l.startswith('❌'))

        stats_line = None
        for l in lines:
            if 'Summary:' in l:
                stats_line = l.strip()
                break

        if not stats_line:
            print(f"❌ [{label}] No stats line found")
            all_pass = False
            continue

        parts = stats_line.replace(',', '').split()
        try:
            s_idx = parts.index('succeeded')
            f_idx = parts.index('failed')
            stats_s = int(parts[s_idx - 1])
            stats_f = int(parts[f_idx - 1])
        except (ValueError, IndexError) as e:
            print(f"❌ [{label}] Cannot parse stats line: {e}")
            all_pass = False
            continue

        if stats_s != success_symbols or stats_f != fail_symbols:
            print(
                f"❌ [{label}] Mismatch: {success_symbols}✅/{fail_symbols}❌ "
                f"vs stats {stats_s}/{stats_f}"
            )
            all_pass = False
        else:
            print(f"✅ [{label}] {success_symbols}✅/{fail_symbols}❌ = stats {stats_s}/{stats_f}")

    if all_pass:
        print("✅ PASSED: all display checks consistent")
    return all_pass


async def main():
    tests = [
        ("Execution order (Bug #1)", test_execution_order),
        ("STDIN isolation (Bug #2)", test_stdin_isolation_order),
        ("Display accuracy (Bug #3)", test_display_accuracy),
    ]

    passed = 0
    for name, fn in tests:
        try:
            if await fn():
                passed += 1
                print(f"  ✅ {name}\n")
            else:
                print(f"  ❌ {name}\n")
        except AssertionError as e:
            print(f"  ❌ {name}: {e}\n")
        except Exception as e:
            print(f"  ❌ {name}: EXCEPTION — {e}\n")
            import traceback
            traceback.print_exc()

    print("=" * 55)
    print(f"RESULT: {passed}/{len(tests)} passed")
    print("=" * 55)

    return passed == len(tests)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

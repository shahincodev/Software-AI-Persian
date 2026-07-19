"""Test new architecture modules."""
import sys
sys.path.insert(0, '.')

def test_security():
    from core.security_engine import SecurityEngine, RiskLevel

    engine = SecurityEngine()

    # Test risk assessment
    a1 = engine.assess_action('Read file content', action_type='read')
    assert a1.risk_level == RiskLevel.SAFE, f"Expected SAFE, got {a1.risk_level}"
    print(f"  Read file: risk={a1.risk_level.name}, decision={a1.decision.value}")

    a2 = engine.assess_action('Delete all files in C:\\', action_type='execute')
    assert a2.risk_level >= RiskLevel.HIGH, f"Expected HIGH+, got {a2.risk_level}"
    print(f"  Delete files: risk={a2.risk_level.name}, decision={a2.decision.value}")

    a3 = engine.assess_action('Click Submit button', action_type='click')
    print(f"  Click button: risk={a3.risk_level.name}, decision={a3.decision.value}")

    a4 = engine.assess_action('format c:', action_type='execute')
    assert a4.risk_level == RiskLevel.CRITICAL, f"Expected CRITICAL, got {a4.risk_level}"
    print(f"  Format C: risk={a4.risk_level.name}, decision={a4.decision.value}")

    # Test trust manager
    engine.trust_manager.record_execution('notepad.exe', True)
    engine.trust_manager.record_execution('notepad.exe', True)
    engine.trust_manager.record_execution('notepad.exe', True)
    trust = engine.trust_manager.get_trust_level('notepad.exe')
    print(f"  Notepad trust: {trust.name}")

    # Test session permissions
    engine.grant_session_permission('launch:myapp', reason='User approved')
    assert engine.has_session_permission('launch:myapp')
    print("  Session permission: OK")

    # Test plan validation
    plan = [
        {'type': 'observe', 'target': 'screen'},
        {'type': 'click', 'target': 'OK'},
        {'type': 'verify', 'target': 'dialog_closed'},
    ]
    valid, reason, warnings = engine.validate_plan(plan)
    print(f"  Plan valid: {valid}, warnings: {len(warnings)}")

    print("  SecurityEngine: PASS")


def test_reasoning():
    from core.reasoning_pipeline import ReasoningPipeline, AgentResult

    pipeline = ReasoningPipeline()

    # Test pipeline stages
    stages = pipeline.get_pipeline_stages()
    assert 'understand' in stages
    assert 'think' in stages
    assert 'plan' in stages
    assert 'execute' in stages
    assert 'verify' in stages
    print(f"  Pipeline stages: {len(stages)}")

    # Test execution
    result = pipeline.execute("Click the OK button")
    assert isinstance(result, AgentResult)
    print(f"  Execute result: {result.summary}")

    print("  ReasoningPipeline: PASS")


def test_reliability():
    from core.reliability import ReliabilityManager

    mgr = ReliabilityManager()

    # Test diagnostics
    mgr.log_event('test', 'info', 'Test event')
    mgr.log_event('test', 'warning', 'Test warning')
    entries = mgr.get_diagnostics(limit=10)
    assert len(entries) >= 2
    print(f"  Diagnostics: {len(entries)} entries")

    # Test checkpoints
    cp = mgr.create_checkpoint('test_cp', {'key': 'value'})
    assert mgr.get_checkpoint('test_cp') is not None
    print(f"  Checkpoint: {cp.checkpoint_id}")

    # Test health
    mgr.log_error('component_a', Exception('test error'))
    health = mgr.get_system_health()
    assert 'overall' in health
    print(f"  Health: {health['overall']}")

    # Test retry
    call_count = [0]
    def flaky_func():
        call_count[0] += 1
        if call_count[0] < 3:
            raise ValueError("Not yet")
        return "success"

    success, result, error = mgr.retry_with_backoff(flaky_func, max_retries=5, component='test')
    assert success
    assert result == "success"
    print(f"  Retry: succeeded after {call_count[0]} attempts")

    print("  ReliabilityManager: PASS")


def test_uia():
    from core.uia_provider import UIAProvider, UIAElement, UIATreeSnapshot

    provider = UIAProvider()
    print(f"  UIA available: {provider.available}")

    # Test element creation
    elem = UIAElement(name='Test', control_type='Button', is_enabled=True)
    assert elem.is_clickable
    assert not elem.is_input
    print(f"  Element: {elem.name} ({elem.control_type})")

    # Test snapshot
    snapshot = UIATreeSnapshot()
    snapshot.all_elements.append(elem)
    found = snapshot.find_elements(name='Test')
    assert len(found) == 1
    print(f"  Snapshot search: found {len(found)} elements")

    interactive = snapshot.get_interactive_elements()
    assert len(interactive) == 1
    print(f"  Interactive elements: {len(interactive)}")

    print("  UIAProvider: PASS")


def test_mouse_engine():
    from core.mouse_engine import ClickResult, TargetInfo

    # Test TargetInfo
    target = TargetInfo(x=100, y=200, text='OK', confidence=0.9)
    assert target.center == (100, 200)
    assert target.is_reliable
    print(f"  TargetInfo: center={target.center}, reliable={target.is_reliable}")

    # Test ClickResult
    result = ClickResult(success=True, target=target, attempts=1, duration=0.5)
    assert result.success
    assert 'OK' in result.summary
    print(f"  ClickResult: {result.summary}")

    print("  MouseEngine: PASS")


def test_keyboard_engine():
    from core.keyboard_engine import KeyboardEngine, TypingMode, Language

    engine = KeyboardEngine()

    # Test language detection
    assert engine.detect_language("Hello") == Language.ENGLISH
    assert engine.detect_language("سلام") == Language.PERSIAN
    assert engine.detect_language("Hello سلام") == Language.MIXED
    print("  Language detection: OK")

    # Test safety
    assert engine.is_safe_text("Hello World")
    assert not engine.is_safe_text("rm -rf /")
    print("  Safety check: OK")

    # Test mode selection
    assert engine._select_mode("Hi", TypingMode.AUTO) == TypingMode.HUMAN
    assert engine._select_mode("سلام", TypingMode.AUTO) == TypingMode.INSTANT
    assert engine._select_mode("A" * 200, TypingMode.AUTO) == TypingMode.INSTANT
    print("  Mode selection: OK")

    print("  KeyboardEngine: PASS")


if __name__ == '__main__':
    print("=" * 60)
    print("NEW ARCHITECTURE MODULE TESTS")
    print("=" * 60)
    print()

    test_security()
    print()
    test_reasoning()
    print()
    test_reliability()
    print()
    test_uia()
    print()
    test_mouse_engine()
    print()
    test_keyboard_engine()

    print()
    print("=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)

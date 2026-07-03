"""Tests for Phase 3 — Vision Loop and Vision Tools."""

import sys
sys.path.insert(0, ".")

from core.tool_schema import validate_tool_call, TOOLS
from core.vision_loop import VisionLoopManager, ScreenState, VisionLoopConfig


def test_vision_tools_registered():
    """Verify all vision tools are registered in tool_schema."""
    vision_tools = ["screenshot", "read_screen", "find_element", "verify_action", "describe_screen"]
    for tool_name in vision_tools:
        assert tool_name in TOOLS, f"Vision tool '{tool_name}' not registered"
        print(f"  [PASS] {tool_name} registered")


def test_vision_tool_validation():
    """Verify vision tools validate correctly."""
    # screenshot - no required params
    valid, msg = validate_tool_call({"tool": "screenshot", "params": {}})
    assert valid, f"screenshot should be valid without params: {msg}"
    print("  [PASS] screenshot validation")

    # read_screen - no required params
    valid, msg = validate_tool_call({"tool": "read_screen", "params": {}})
    assert valid, f"read_screen should be valid without params: {msg}"
    print("  [PASS] read_screen validation")

    # find_element - requires either text or image (both optional in schema)
    valid, msg = validate_tool_call({"tool": "find_element", "params": {"text": "OK"}})
    assert valid, f"find_element with text should be valid: {msg}"
    print("  [PASS] find_element validation")

    # verify_action - requires 'expected'
    valid, msg = validate_tool_call({"tool": "verify_action", "params": {}})
    assert not valid, "verify_action should fail without 'expected'"
    valid, msg = validate_tool_call({"tool": "verify_action", "params": {"expected": "button clicked"}})
    assert valid, f"verify_action with expected should be valid: {msg}"
    print("  [PASS] verify_action validation")

    # describe_screen - no required params
    valid, msg = validate_tool_call({"tool": "describe_screen", "params": {}})
    assert valid, f"describe_screen should be valid without params: {msg}"
    print("  [PASS] describe_screen validation")


def test_screen_state():
    """Test ScreenState data class."""
    state = ScreenState(
        timestamp=1234567890.0,
        screenshot_path="/tmp/test.png",
        ocr_text="Hello World",
        visible_elements=["Hello at (10,20)", "World at (30,40)"],
        active_window="Notepad",
    )

    context = state.to_context_string()
    assert "Notepad" in context
    assert "Hello World" in context
    assert "Hello at (10,20)" in context
    print("  [PASS] ScreenState.to_context_string()")


def test_vision_loop_config():
    """Test VisionLoopConfig defaults."""
    config = VisionLoopConfig()
    assert config.max_retries == 2
    assert config.verify_after_action is True
    assert config.capture_before_action is True
    assert config.capture_after_action is True
    print("  [PASS] VisionLoopConfig defaults")


def test_vision_loop_manager_init():
    """Test VisionLoopManager initialization."""
    manager = VisionLoopManager()
    assert manager.vision is not None
    assert manager.config is not None
    assert manager.recovery is not None
    print("  [PASS] VisionLoopManager initialization")


def test_total_tool_count():
    """Verify total tool count includes vision tools."""
    assert len(TOOLS) == 18, f"Expected 18 tools, got {len(TOOLS)}"
    print(f"  [PASS] Total tools: {len(TOOLS)}")


if __name__ == "__main__":
    print("=== Phase 3 Tests ===\n")

    print("1. Vision tools registered:")
    test_vision_tools_registered()

    print("\n2. Vision tool validation:")
    test_vision_tool_validation()

    print("\n3. ScreenState:")
    test_screen_state()

    print("\n4. VisionLoopConfig:")
    test_vision_loop_config()

    print("\n5. VisionLoopManager:")
    test_vision_loop_manager_init()

    print("\n6. Total tool count:")
    test_total_tool_count()

    print("\n=== ALL TESTS PASSED ===")

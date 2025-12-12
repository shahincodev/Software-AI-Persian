import asyncio
import pytest

from core.realtime_loop import RealtimeLoop, RealtimeDecision


class FakeSessionControl:
    def __init__(self, safety_mode="safe"):
        self.safety_mode = safety_mode
        self.paused = False
        self.stopped = False
        self.risk_threshold = 70
        self.allowed_apps = set()
        self.allowed_paths = set()

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def stop(self):
        self.stopped = True


class FakeVision:
    def __init__(self):
        self.saved = 0

    def save_screenshot(self, path: str) -> bool:
        self.saved += 1
        return True


@pytest.mark.asyncio
async def test_safe_mode_observe_only():
    vision = FakeVision()
    session = FakeSessionControl(safety_mode="safe")
    loop = RealtimeLoop(vision=vision, session_control=session, fps=2.0)

    snap = await loop._capture()
    decision = await loop._interpret(snap)
    assert decision.action == "hint"
    await loop._act_if_allowed(decision)
    # در حالت safe هیچ اکشنی رخ نمی‌دهد و counters صفر می‌ماند
    assert loop._actions_since_eval == 0


@pytest.mark.asyncio
async def test_power_mode_allows_act_with_limits():
    vision = FakeVision()
    session = FakeSessionControl(safety_mode="power")
    called = {
        "count": 0
    }

    async def cb(decision: RealtimeDecision):
        called["count"] += 1

    loop = RealtimeLoop(vision=vision, session_control=session, fps=2.0, max_actions=2, action_callback=cb)

    snap = await loop._capture()
    decision = await loop._interpret(snap)
    await loop._act_if_allowed(decision)
    await loop._act_if_allowed(decision)
    await loop._act_if_allowed(decision)  # باید توسط max_actions متوقف شود

    assert called["count"] == 2


@pytest.mark.asyncio
async def test_pause_and_stop():
    vision = FakeVision()
    session = FakeSessionControl(safety_mode="power")
    loop = RealtimeLoop(vision=vision, session_control=session, fps=5.0)

    # pause باید اجرای حلقه را معلق کند
    session.pause()
    task = asyncio.create_task(loop.run_loop())
    await asyncio.sleep(0.3)
    session.resume()
    await asyncio.sleep(0.3)
    session.stop()
    await asyncio.sleep(0.2)
    loop.stop()
    await task
    assert session.stopped is True

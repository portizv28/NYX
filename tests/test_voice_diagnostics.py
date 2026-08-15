import unittest

from voice.diagnostics import VoiceDiagnostics
from voice.service import VoiceService, VoiceSessionConfig
from voice.wake_engines import WakeEvent


class ImmediateWakeEngine:
    def wait(self, cancel_event):
        return WakeEvent(engine="test", confidence=0.9)


class SilentListener:
    def listen(self, cancel_event=None, initial_timeout_seconds=20):
        return ""


class VoiceDiagnosticsTests(unittest.TestCase):
    def test_cooldown_rejects_repeated_wake_events(self):
        events = []
        diagnostics = VoiceDiagnostics()
        service = VoiceService(
            on_activated=lambda: events.append("activated"), on_command=lambda text: None,
            on_command_timeout=lambda: None, wake_engine=ImmediateWakeEngine(), listener=SilentListener(),
            config=VoiceSessionConfig(wake_cooldown_seconds=60), diagnostics=diagnostics,
        )
        service._running.set()

        service._wait_for_wake_word()
        service._session_active.clear()
        service._wait_for_wake_word()

        self.assertEqual(["activated"], events)
        self.assertEqual("wake_rejected", diagnostics.recent()[-1].name)

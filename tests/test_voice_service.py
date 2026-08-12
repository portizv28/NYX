import time
import unittest

from voice.contracts import RecognitionResult
from voice.factory import create_default_recognizer
from voice.service import VoiceService, VoiceSessionConfig
from voice.wake_engines import TranscriptionWakeEngine, create_default_wake_engine
from voice.sensitivity import adaptive_threshold
from voice.wake_detector import WakeWordDetector


class FakeListener:
    def __init__(self, transcripts):
        self.transcripts = list(transcripts)
        self.calls = 0

    def listen(self, cancel_event=None, initial_timeout_seconds=20):
        self.calls += 1
        return self.transcripts.pop(0) if self.transcripts else ""


class FakeResultListener(FakeListener):
    def listen_result(self, cancel_event=None, initial_timeout_seconds=20):
        value = self.listen(cancel_event, initial_timeout_seconds)
        return value if isinstance(value, RecognitionResult) else RecognitionResult(value)


class VoiceServiceTests(unittest.TestCase):
    def build_service(self, transcripts):
        self.events = []
        service = VoiceService(
            on_activated=lambda: self.events.append("activated"),
            on_command=lambda text: self.events.append(("command", text)),
            on_command_timeout=lambda: self.events.append("timeout"),
            on_session_started=lambda: self.events.append("session_started"),
            on_interruption=lambda: self.events.append("interruption"),
            listener=FakeListener(transcripts),
            config=VoiceSessionConfig(conversation_idle_seconds=12),
        )
        service._running.set()
        return service

    def test_wake_word_starts_conversation_session(self):
        service = self.build_service(["Nix"])

        service._wait_for_wake_word()

        self.assertTrue(service.session_active)
        self.assertEqual(["activated", "session_started"], self.events)

    def test_wake_word_with_command_sends_command_immediately(self):
        service = self.build_service(["NYX, abre Google"])

        service._wait_for_wake_word()

        self.assertEqual(["activated", ("command", "abre Google")], self.events)

    def test_active_session_accepts_follow_up_without_wake_word(self):
        service = self.build_service(["Nix", "¿Y el sábado?"])
        service._wait_for_wake_word()
        service._continue_session()

        self.assertIn(("command", "¿Y el sábado?"), self.events)

    def test_session_returns_to_sleep_after_timeout(self):
        service = self.build_service(["Nix"])
        service._wait_for_wake_word()
        service._session_deadline = time.monotonic() - 1

        service._continue_session()

        self.assertFalse(service.session_active)
        self.assertIn("timeout", self.events)

    def test_interrupt_requires_stop_expression(self):
        service = self.build_service(["Nix, para"])
        service.begin_speaking()
        service._monitor_interruption()

        self.assertIn("interruption", self.events)

    def test_ignores_unreliable_recognition_result(self):
        self.events = []
        service = VoiceService(
            on_activated=lambda: self.events.append("activated"),
            on_command=lambda text: self.events.append(("command", text)),
            on_command_timeout=lambda: self.events.append("timeout"),
            listener=FakeResultListener([RecognitionResult("Nix", no_speech_probability=0.9)]),
        )
        service._running.set()

        service._wait_for_wake_word()

        self.assertEqual([], self.events)


class WakeWordDetectorTests(unittest.TestCase):
    def test_accepts_nix_nyx_and_common_transcription(self):
        detector = WakeWordDetector()

        self.assertEqual("abre Google", detector.detect("Nix, abre Google").command)
        self.assertEqual("abre Google", detector.detect("NYX abre Google").command)
        self.assertEqual("abre Google", detector.detect("Nicks abre Google").command)

    def test_does_not_accept_unrelated_word(self):
        self.assertIsNone(WakeWordDetector().detect("mix abre Google"))

    def test_default_wake_engine_falls_back_without_credentials(self):
        engine = create_default_wake_engine(FakeListener([]), WakeWordDetector())

        self.assertIsInstance(engine, TranscriptionWakeEngine)


class VoiceSensitivityTests(unittest.TestCase):
    def test_keeps_sensitive_floor_for_quiet_microphone(self):
        self.assertEqual(0.004, adaptive_threshold([0.0005, 0.001]))

    def test_caps_threshold_in_noisy_environment(self):
        self.assertEqual(0.012, adaptive_threshold([0.02, 0.03]))

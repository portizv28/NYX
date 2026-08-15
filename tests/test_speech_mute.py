import unittest

from voice.speaker import SpeechService


class FakeProvider:
    def __init__(self):
        self.stopped = False

    def speak(self, text):
        return None

    def stop(self):
        self.stopped = True


class SpeechMuteTests(unittest.TestCase):
    def test_mute_is_independent_and_stops_current_tts(self):
        provider = FakeProvider()
        service = SpeechService(provider=provider)
        self.assertFalse(service.muted)
        self.assertTrue(service.toggle_muted())
        self.assertTrue(provider.stopped)
        self.assertFalse(service.toggle_muted())

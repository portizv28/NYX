import unittest

from core.state import AssistantState, MicrophoneState
from core.store import StateStore


class StateStoreTests(unittest.TestCase):
    def test_updates_snapshot_and_notifies_observer(self):
        store = StateStore()
        received = []
        unsubscribe = store.subscribe(received.append, emit_current=True)

        store.update(
            state=AssistantState.THINKING,
            activity="Procesando",
            microphone=MicrophoneState.INACTIVE,
            active_model="OpenAI",
            capabilities=("internet", "documents"),
            last_action="web_search",
        )
        unsubscribe()

        self.assertEqual(2, len(received))
        self.assertEqual(AssistantState.THINKING, received[-1].state)
        self.assertEqual("OpenAI", store.snapshot().active_model)
        self.assertEqual("web_search", store.snapshot().last_action)

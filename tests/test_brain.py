import unittest

from automation.registry import ActionRegistry, RegisteredAction
from brain.core import NyxBrain


class FakeRouter:
    name = "fake"

    def ask(self, text):
        self.last_text = text
        return f"IA: {text}"


class BrainTests(unittest.TestCase):
    def test_registered_action_has_priority_over_ai(self):
        actions = ActionRegistry()
        actions.register(
            RegisteredAction("test", "acción de prueba", lambda text: text == "haz algo", lambda _text: "hecho")
        )

        result = NyxBrain(router=FakeRouter(), actions=actions).procesar("haz algo")

        self.assertEqual("hecho", result)

    def test_unknown_request_uses_router(self):
        result = NyxBrain(router=FakeRouter(), actions=ActionRegistry()).procesar("pregunta libre")

        self.assertEqual("IA: pregunta libre", result)

    def test_second_question_receives_conversation_context(self):
        router = FakeRouter()
        brain = NyxBrain(router=router, actions=ActionRegistry())
        brain.procesar("Háblame de Napoleón")
        brain.procesar("¿Y cuándo murió?")

        self.assertIn("Háblame de Napoleón", router.last_text)
        self.assertIn("¿Y cuándo murió?", router.last_text)


if __name__ == "__main__":
    unittest.main()

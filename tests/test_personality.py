import unittest

from personality.adapters import PersonalityAwareProcessor, PersonalityAwareProvider
from personality.engine import PersonalityEngine
from personality.models import InteractionMode
from personality.profiles import NYX_PROFILE


class FakeProvider:
    name = "fake"

    def __init__(self):
        self.prompt = None

    def ask(self, text):
        self.prompt = text
        return "respuesta"


class FakeProcessor:
    def procesar(self, text):
        return f"hecho: {text}"


class PersonalityTests(unittest.TestCase):
    def setUp(self):
        self.engine = PersonalityEngine(NYX_PROFILE)

    def test_financial_request_uses_professional_mode(self):
        self.assertEqual(InteractionMode.PROFESSIONAL, self.engine.mode_for("Analiza esta inversión"))

    def test_normal_request_uses_everyday_mode(self):
        self.assertEqual(InteractionMode.EVERYDAY, self.engine.mode_for("Abre Spotify"))

    def test_provider_receives_identity_instruction(self):
        provider = FakeProvider()
        result = PersonalityAwareProvider(provider, self.engine).ask("Explícame esto")

        self.assertEqual("respuesta", result)
        self.assertIn("Eres NYX", provider.prompt)
        self.assertIn("Explícame esto", provider.prompt)

    def test_direct_response_gets_tone_without_changing_processor(self):
        response = PersonalityAwareProcessor(FakeProcessor(), self.engine).procesar("abre Spotify")

        self.assertEqual("Claro, Pablo.", response)

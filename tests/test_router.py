import unittest

from ai.router import HybridRouter


class FakeProvider:
    def __init__(self, name, response, error=None):
        self.name = name
        self.response = response
        self.error = error
        self.requests = []

    def ask(self, text):
        self.requests.append(text)
        if self.error:
            raise self.error
        return self.response


class HybridRouterTests(unittest.TestCase):
    def test_normal_requests_use_local_provider(self):
        local = FakeProvider("local", "respuesta local")
        external = FakeProvider("openai", "respuesta externa")

        result = HybridRouter(local, external).ask("¿Qué tiempo hace?")

        self.assertEqual("respuesta local", result)
        self.assertEqual(["¿Qué tiempo hace?"], local.requests)
        self.assertEqual([], external.requests)

    def test_complex_requests_use_external_provider(self):
        local = FakeProvider("local", "respuesta local")
        external = FakeProvider("openai", "respuesta externa")

        result = HybridRouter(local, external).ask("Analiza en detalle este algoritmo")

        self.assertEqual("respuesta externa", result)
        self.assertEqual(["Analiza en detalle este algoritmo"], external.requests)

    def test_external_error_falls_back_to_local(self):
        local = FakeProvider("local", "respuesta local")
        external = FakeProvider("openai", "no usada", error=RuntimeError("sin red"))

        router = HybridRouter(local, external)
        result = router.ask("Necesito un plan detallado")

        self.assertEqual("respuesta local", result)
        self.assertEqual("local", router.last_decision.provider)

    def test_publishes_provider_decision(self):
        router = HybridRouter(FakeProvider("local", "respuesta"))
        received = []
        router.subscribe_decisions(received.append)

        router.ask("consulta normal")

        self.assertEqual("local", received[-1].provider)


if __name__ == "__main__":
    unittest.main()

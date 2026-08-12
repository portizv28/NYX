import requests


class LocalAI:

    name = "local"

    def __init__(
        self,
        url="http://localhost:11434/api/generate",
        model="llama3.2:3b",
    ):
        self.url = url
        self.modelo = model


    def ask(self, text):

        respuesta = requests.post(
            self.url,
            json={
                "model": self.modelo,
                "prompt": text,
                "stream": False,
                "options": {
                    "num_predict": 200
                }
            },
            timeout=120
        )

        respuesta.raise_for_status()

        datos = respuesta.json()

        return datos["response"]

    def preguntar(self, texto):
        """Alias de compatibilidad para la API inicial en español."""
        return self.ask(texto)

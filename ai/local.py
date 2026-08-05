import requests


class LocalAI:

    def __init__(self):

        self.url = "http://localhost:11434/api/generate"
        self.modelo = "llama3.2:3b"


    def preguntar(self, texto):

        respuesta = requests.post(
            self.url,
            json={
                "model": self.modelo,
                "prompt": texto,
                "stream": False,
                "options": {
                    "num_predict": 200
                }
            },
            timeout=120
        )

        datos = respuesta.json()

        return datos["response"]
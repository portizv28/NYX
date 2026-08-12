from openai import OpenAI


class GPT:

    name = "openai"

    def __init__(self, api_key, model="gpt-4.1-mini"):

        self.client = OpenAI(
            api_key=api_key
        )
        self.model = model


    def ask(self, text):

        respuesta = self.client.chat.completions.create(

            model=self.model,

            messages=[
                {
                    "role": "user",
                    "content": text
                }
            ]

        )

        return respuesta.choices[0].message.content

    def preguntar(self, texto):
        """Alias de compatibilidad para la API inicial en español."""
        return self.ask(texto)

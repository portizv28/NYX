from openai import OpenAI


class GPT:

    def __init__(self, api_key):

        self.client = OpenAI(
            api_key=api_key
        )


    def preguntar(self, texto):

        respuesta = self.client.chat.completions.create(

            model="gpt-4.1-mini",

            messages=[
                {
                    "role": "user",
                    "content": texto
                }
            ]

        )

        return respuesta.choices[0].message.content
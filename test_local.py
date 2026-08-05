from ai.local import LocalAI


ia = LocalAI()


respuesta = ia.preguntar(
    "Hola, soy NYX. Preséntate."
)


print(respuesta)
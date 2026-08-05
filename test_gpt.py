from config.settings import API_KEY
from ai.gpt import GPT


ia = GPT(API_KEY)

respuesta = ia.preguntar(
    "Explícame qué es la teoría de juegos en economía"
)

print(respuesta)
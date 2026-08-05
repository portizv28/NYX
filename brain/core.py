from automation.launcher import abrir_programa
from ai.local import LocalAI


class NyxBrain:

    def __init__(self):

        self.estado = "Esperando"

        self.ia = LocalAI()


    def procesar(self, mensaje):

        mensaje = mensaje.lower()


        if mensaje.startswith("abre "):

            programa = mensaje.replace("abre ", "")

            return abrir_programa(programa)


        if "hola" in mensaje:

            return "Muy buenas, Pablo."


        if "quien eres" in mensaje:

            return "Soy NYX, tu asistente personal."


        # Si no es un comando conocido usamos IA local

        return self.ia.preguntar(mensaje)
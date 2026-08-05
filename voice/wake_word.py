import time
from voice.listener import escuchar


class WakeWord:

    def __init__(self, callback):

        self.callback = callback

        self.activo = True

    def iniciar(self):

        while self.activo:

            texto = escuchar()

            if texto == "":
                continue

            texto = texto.lower()

            if "nyx" in texto:

                self.callback()
                
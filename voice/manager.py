import threading
import time

from voice.listener import escuchar


class VoiceManager:

    def __init__(self, callback):

        self.callback = callback

        self.activo = True

        self.escuchando = False

    # ======================================

    def iniciar(self):

        hilo = threading.Thread(
            target=self.bucle,
            daemon=True
        )

        hilo.start()

    # ======================================

    def detener(self):

        self.activo = False

    # ======================================

    def bucle(self):

        while self.activo:

            # Evita lanzar varias escuchas a la vez
            if self.escuchando:

                time.sleep(0.2)

                continue

            self.escuchando = True

            try:

                texto = escuchar()

            except Exception as e:

                print("Error escuchando:", e)

                texto = ""

            self.escuchando = False

            if texto == "":

                continue

            texto = texto.lower()

            print("Escuchado:", texto)

            # -------------------------
            # Palabra de activación
            # -------------------------

            if "nyx" in texto:

                self.callback(texto)
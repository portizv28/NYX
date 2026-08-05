import threading
import time

from voice.listener import escuchar


class WakeDetector:

    def __init__(self, callback):

        self.callback = callback

        self.running = False

    # ----------------------------------

    def start(self):

        if self.running:
            return

        self.running = True

        threading.Thread(
            target=self.loop,
            daemon=True
        ).start()

    # ----------------------------------

    def stop(self):

        self.running = False

    # ----------------------------------

    def loop(self):

        while self.running:

            try:

                texto = escuchar()

            except Exception as e:

                print("Wake Error:", e)

                time.sleep(1)

                continue

            if texto == "":
                continue

            texto = texto.lower()

            print("[Wake]", texto)

            # -----------------------------
            # Despertar a NYX
            # -----------------------------

            if "nyx" in texto:

                texto = texto.replace(
                    "nyx",
                    ""
                ).strip()

                self.callback(texto)
from gui.window import NyxWindow
from gui.orb import NyxOrb

from brain.core import NyxBrain

from voice.listener import escuchar
from voice.speaker import hablar
from voice.wake import WakeDetector

import threading


class NYX:

    def __init__(self):

        # ---------------- GUI ----------------

        self.window = NyxWindow()
        self.window.root.withdraw()

        self.orb = NyxOrb()

        # ---------------- IA ----------------

        self.brain = NyxBrain()

        # ---------------- Estado ----------------

        self.estado = "sleep"

        # ---------------- Wake ----------------

        self.wake = WakeDetector(
            self.despertar
        )

        self.wake.start()

        # ---------------- Eventos ----------------

        self.window.set_callback(
            self.procesar
        )

        self.orb.set_callback(
            self.abrir
        )

        self.window.root.protocol(
            "WM_DELETE_WINDOW",
            self.cerrar
        )

        self.dormir()

    # =====================================================

    def abrir(self):

        self.window.root.deiconify()

        self.orb.ocultar()

    # =====================================================

    def cerrar(self):

        self.window.root.withdraw()

        self.orb.mostrar()

        self.dormir()

    # =====================================================

    def cambiar_estado(self, estado):

        self.estado = estado

        if estado == "sleep":

            self.orb.dormir()

        elif estado == "listen":

            self.orb.escuchar()

        elif estado == "think":

            self.orb.pensar()

        elif estado == "talk":

            self.orb.hablar()

    # =====================================================

    def despertar(self, texto):

        print("NYX ACTIVADA")

        self.abrir()

        self.cambiar_estado("listen")

        self.window.cambiar_color("orange")

        self.window.cambiar_estado(
            "Escuchando..."
        )

        texto = texto.replace(
            "nyx",
            ""
        ).strip()

        if texto == "":

            texto = escuchar()

        if texto.strip() == "":

            self.dormir()

            return

        self.procesar(texto)

    # =====================================================

    def procesar(self, texto):

        self.cambiar_estado("think")

        self.window.cambiar_color("yellow")

        self.window.cambiar_estado(
            "Pensando..."
        )

        def tarea():

            respuesta = self.brain.procesar(
                texto
            )

            self.window.root.after(
                0,
                lambda: self.mostrar_respuesta(
                    respuesta
                )
            )

        threading.Thread(
            target=tarea,
            daemon=True
        ).start()

        return "Procesando..."

    # =====================================================

    def mostrar_respuesta(self, respuesta):

        self.cambiar_estado("talk")

        self.window.cambiar_color("lime")

        self.window.cambiar_estado(
            respuesta
        )

        threading.Thread(
            target=hablar,
            args=(respuesta,),
            daemon=True
        ).start()

        self.window.root.after(
            10000,
            self.dormir
        )

    # =====================================================

    def dormir(self):

        self.window.cambiar_color(
            "#00BFFF"
        )

        self.window.cambiar_estado(
            "Esperando instrucciones..."
        )

        self.cambiar_estado("sleep")

    # =====================================================

    def run(self):

        self.window.run()

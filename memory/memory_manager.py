import json
import os


class MemoryManager:

    def __init__(self):

        self.file = "memory/memory.json"

        if not os.path.exists(self.file):

            with open(self.file, "w") as f:
                json.dump({}, f)

    def cargar(self):

        with open(self.file, "r", encoding="utf-8") as f:
            return json.load(f)

    def guardar(self, datos):

        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

    def recordar(self, clave, valor):

        datos = self.cargar()

        datos[clave] = valor

        self.guardar(datos)

    def obtener(self, clave):

        datos = self.cargar()

        return datos.get(clave, None)
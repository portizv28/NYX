"""API anterior de memoria, conservada sobre la nueva implementación."""

from memory.json_store import JsonMemoryStore
from memory.service import MemoryService


class MemoryManager:
    def __init__(self) -> None:
        self.file = "memory/memory.json"
        self._store = JsonMemoryStore(self.file)
        self._service = MemoryService(self._store)

    def cargar(self):
        return {entry.key: entry.value for entry in self._store.list_entries()}

    def guardar(self, datos):
        for clave, valor in datos.items():
            self.recordar(clave, valor)

    def recordar(self, clave, valor):
        self._service.remember(clave, valor)

    def obtener(self, clave):
        entry = self._service.recall(clave)
        return entry.value if entry else None

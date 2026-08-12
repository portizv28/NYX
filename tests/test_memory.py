import tempfile
import unittest
from pathlib import Path

from brain.memory_intents import MemoryIntentHandler
from memory.json_store import JsonMemoryStore
from memory.service import MemoryService


class MemoryTests(unittest.TestCase):
    def test_remembers_and_recalls_car(self):
        with tempfile.TemporaryDirectory() as directory:
            service = MemoryService(JsonMemoryStore(Path(directory) / "memory.json"))
            intents = MemoryIntentHandler(service)

            self.assertEqual(
                "Recordaré que tu coche es un Kia.",
                intents.respond("Recuerda que mi coche es un Kia."),
            )
            self.assertEqual("Tu coche es un Kia.", intents.respond("¿Qué coche tengo?"))

    def test_reads_legacy_json_format(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "memory.json"
            path.write_text('{"coche": "Kia"}', encoding="utf-8")
            service = MemoryService(JsonMemoryStore(path))

            self.assertEqual("Kia", service.recall("coche").value)

import unittest

from config.identity import NYX_IDENTITY


class IdentityTests(unittest.TestCase):
    def test_recognizes_written_and_spoken_wake_words(self):
        self.assertEqual("abre Google", NYX_IDENTITY.extract_command("NYX, abre Google"))
        self.assertEqual("abre Google", NYX_IDENTITY.extract_command("Nix abre Google"))

    def test_name_is_spoken_as_nix(self):
        self.assertEqual("Nix está lista", NYX_IDENTITY.for_speech("NYX está lista"))


if __name__ == "__main__":
    unittest.main()

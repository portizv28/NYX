import unittest

from integrations.windows.startup import StartupCommand


class StartupCommandTests(unittest.TestCase):
    def test_current_command_points_to_main_entrypoint(self):
        command = StartupCommand.for_current_installation()

        self.assertTrue(command.arguments[0].endswith("main.py"))
        self.assertIn("main.py", command.value)

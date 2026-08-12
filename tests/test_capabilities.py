import unittest

from capabilities.registry import CapabilityRegistry


class FakeCapability:
    identifier = "fake"
    description = "Capacidad de prueba"

    def register_actions(self, actions):
        self.installed_on = actions


class CapabilityRegistryTests(unittest.TestCase):
    def test_installs_capabilities_without_brain_dependency(self):
        capability = FakeCapability()
        registry = CapabilityRegistry()
        registry.register(capability)

        from automation.registry import ActionRegistry

        actions = ActionRegistry()
        registry.install_actions(actions)

        self.assertIs(actions, capability.installed_on)
        self.assertEqual((capability,), registry.list_capabilities())


if __name__ == "__main__":
    unittest.main()

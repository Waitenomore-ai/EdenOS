import importlib
import unittest


class LaunchCooldownTests(unittest.TestCase):
    def gate(self, now):
        try:
            module = importlib.import_module('eden_shell.launch_control')
        except ModuleNotFoundError:
            self.fail('Rapid activity launch guard is missing')
        return module.LaunchCooldown(clock=lambda:now[0])

    def test_rapid_repeat_click_is_rejected_but_other_activity_is_allowed(self):
        now = [10.0]
        gate = self.gate(now)
        self.assertTrue(gate.try_start('paint'))
        now[0] = 10.1
        self.assertFalse(gate.try_start('paint'))
        self.assertTrue(gate.try_start('read'))
        now[0] = 12.0
        self.assertTrue(gate.try_start('paint'))

    def test_failed_launch_can_be_retried_immediately(self):
        now = [10.0]
        gate = self.gate(now)
        self.assertTrue(gate.try_start('paint'))
        gate.release('paint')
        self.assertTrue(gate.try_start('paint'))

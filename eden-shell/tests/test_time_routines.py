import unittest


class TimeRoutinesTests(unittest.TestCase):
    def test_routine_starts_empty_and_finishes_after_each_step(self):
        from eden_shell.time_routines_model import Routine, STEPS

        routine = Routine()
        self.assertFalse(routine.finished)
        for index in range(len(STEPS)):
            self.assertTrue(routine.toggle(index))
        self.assertTrue(routine.finished)

    def test_routine_can_be_reset_without_saved_personal_data(self):
        from eden_shell.time_routines_model import Routine

        routine = Routine()
        routine.toggle(0)
        routine.reset()
        self.assertEqual(routine.completed, [False, False, False, False])
        self.assertNotIn("name", routine.__dict__)

import unittest

from smsurvey.schedule.task import Task


class TestTask(unittest.TestCase):

    def test_from_tuple(self):
        test_tuple = (1, '2', '3')
        task = Task.from_tuple(test_tuple)

        self.assertEqual(task.task_id, test_tuple[0])
        self.assertEqual(task.survey_id, test_tuple[1])
        self.assertEqual(task.time_rule_id, test_tuple[2])
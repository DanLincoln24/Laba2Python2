import unittest
from src.second_laba.task import Task


class TestTaskProperties(unittest.TestCase):

    def test_is_ready_true(self):
        task = Task(id=1, description="test", priority=4, status="created")
        self.assertTrue(task.is_ready)

    def test_is_ready_false_low_priority(self):
        task = Task(id=1, description="test", priority=2, status="created")
        self.assertFalse(task.is_ready)

    def test_is_ready_false_wrong_status(self):
        task = Task(id=1, description="test", priority=4, status="in_progress")
        self.assertFalse(task.is_ready)

    def test_is_ready_readonly(self):
        task = Task(id=1, description="test", priority=4, status="created")
        with self.assertRaises(AttributeError):
            task.is_ready = False

    def test_age_positive(self):
        task = Task(id=1, description="test", priority=3)
        self.assertGreaterEqual(task.age, 0)

    def test_age_increases(self):
        task = Task(id=1, description="test", priority=3)
        age1 = task.age
        import time
        time.sleep(0.1)
        age2 = task.age
        self.assertGreater(age2, age1)

    def test_age_readonly(self):
        task = Task(id=1, description="test", priority=3)
        with self.assertRaises(AttributeError):
            task.age = 100

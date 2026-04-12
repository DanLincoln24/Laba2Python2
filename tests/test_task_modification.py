import unittest
from src.second_laba.task import Task
from src.second_laba.descriptors import TaskValidationError

class TestTaskModification(unittest.TestCase):

    def test_modify_status_after_creation(self):
        task = Task(id=1, description="test", priority=3)
        task.status = "in_progress"
        self.assertEqual(task.status, "in_progress")

    def test_modify_priority_after_creation(self):
        task = Task(id=1, description="test", priority=3)
        task.priority = 5
        self.assertEqual(task.priority, 5)

    def test_modify_description_after_creation(self):
        task = Task(id=1, description="old", priority=3)
        task.description = "new description"
        self.assertEqual(task.description, "new description")

    def test_modify_status_invalid(self):
        task = Task(id=1, description="test", priority=3)
        with self.assertRaises(TaskValidationError):
            task.status = "invalid_status"

    def test_modify_priority_invalid(self):
        task = Task(id=1, description="test", priority=3)
        with self.assertRaises(TaskValidationError):
            task.priority = 10

    def test_modify_description_invalid_empty(self):
        task = Task(id=1, description="test", priority=3)
        with self.assertRaises(TaskValidationError):
            task.description = ""

    def test_modify_description_invalid_long(self):
        task = Task(id=1, description="test", priority=3)
        with self.assertRaises(TaskValidationError):
            task.description = "a" * 501

    def test_is_ready_changes_with_status(self):
        task = Task(id=1, description="test", priority=4)
        self.assertTrue(task.is_ready)
        task.status = "in_progress"
        self.assertFalse(task.is_ready)

    def test_is_ready_changes_with_priority(self):
        task = Task(id=1, description="test", priority=4)
        self.assertTrue(task.is_ready)
        task.priority = 2
        self.assertFalse(task.is_ready)


class TestTaskRepresentation(unittest.TestCase):

    def test_repr_format(self):
        task = Task(id=1, description="test", priority=3, status="created")
        repr_str = repr(task)
        self.assertIn("id=1", repr_str)
        self.assertIn("description='test'", repr_str)
        self.assertIn("priority=3", repr_str)
        self.assertIn("status='created'", repr_str)
        self.assertIn("created_at", repr_str)
import unittest
import json
import tempfile
import os
import unittest
from datetime import datetime, timedelta
from src.task import Task
from src.descriptors import TaskValidationError


class TestIdDescriptor(unittest.TestCase):

    def test_valid_int_id(self):
        task = Task(id=1, description="test", priority=3)
        self.assertEqual(task.id, 1)

    def test_valid_str_id(self):
        task = Task(id="task_001", description="test", priority=3)
        self.assertEqual(task.id, "task_001")

    def test_invalid_zero_id(self):
        with self.assertRaises(TaskValidationError) as context:
            Task(id=0, description="test", priority=3)
        self.assertIn("положительным", str(context.exception))

    def test_invalid_negative_id(self):
        with self.assertRaises(TaskValidationError) as context:
            Task(id=-5, description="test", priority=3)
        self.assertIn("положительным", str(context.exception))

    def test_invalid_empty_str_id(self):
        with self.assertRaises(TaskValidationError) as context:
            Task(id="", description="test", priority=3)
        self.assertIn("пустой строкой", str(context.exception))

    def test_invalid_whitespace_str_id(self):
        with self.assertRaises(TaskValidationError) as context:
            Task(id="   ", description="test", priority=3)
        self.assertIn("пустой строкой", str(context.exception))

    def test_invalid_none_id(self):
        with self.assertRaises(TaskValidationError) as context:
            Task(id=None, description="test", priority=3)
        self.assertIn("int или str", str(context.exception))

    def test_invalid_float_id(self):
        with self.assertRaises(TaskValidationError) as context:
            Task(id=1.5, description="test", priority=3)
        self.assertIn("int или str", str(context.exception))

    def test_invalid_list_id(self):
        with self.assertRaises(TaskValidationError) as context:
            Task(id=[1, 2], description="test", priority=3)
        self.assertIn("int или str", str(context.exception))

    def test_cannot_bypass_id_descriptor_through_dict(self):
        task = Task(id=1, description="test", priority=3)
        task.__dict__['id'] = 0
        self.assertEqual(task.id, 1)
        with self.assertRaises(TaskValidationError):
            task.id = 0


class TestDescriptionDescriptor(unittest.TestCase):

    def test_valid_description(self):
        task = Task(id=1, description="Подготовить отчёт", priority=3)
        self.assertEqual(task.description, "Подготовить отчёт")

    def test_valid_description_with_spaces(self):
        task = Task(id=1, description="Подготовить отчёт по продажам", priority=3)
        self.assertEqual(task.description, "Подготовить отчёт по продажам")

    def test_invalid_empty_string(self):
        with self.assertRaises(TaskValidationError) as context:
            Task(id=1, description="", priority=3)
        self.assertIn("пустым", str(context.exception))

    def test_invalid_whitespace_only(self):
        with self.assertRaises(TaskValidationError) as context:
            Task(id=1, description="     ", priority=3)
        self.assertIn("пустым", str(context.exception))

    def test_invalid_too_long(self):
        long_text = "a" * 501
        with self.assertRaises(TaskValidationError) as context:
            Task(id=1, description=long_text, priority=3)
        self.assertIn("500 символов", str(context.exception))

    def test_invalid_none_description(self):
        with self.assertRaises(TaskValidationError) as context:
            Task(id=1, description=None, priority=3)
        self.assertIn("строкой", str(context.exception))

    def test_invalid_int_description(self):
        with self.assertRaises(TaskValidationError) as context:
            Task(id=1, description=123, priority=3)
        self.assertIn("строкой", str(context.exception))

    def test_valid_max_length(self):
        text = "a" * 500
        task = Task(id=1, description=text, priority=3)
        self.assertEqual(len(task.description), 500)

    def test_cannot_bypass_description_descriptor_through_dict(self):
        task = Task(id=1, description="test", priority=3)
        task.__dict__['description'] = ""
        self.assertEqual(task.description, "test")
        with self.assertRaises(TaskValidationError):
            task.description = ""


class TestPriorityDescriptor(unittest.TestCase):

    def test_valid_min_priority(self):
        task = Task(id=1, description="test", priority=1)
        self.assertEqual(task.priority, 1)

    def test_valid_mid_priority(self):
        task = Task(id=1, description="test", priority=3)
        self.assertEqual(task.priority, 3)

    def test_valid_max_priority(self):
        task = Task(id=1, description="test", priority=5)
        self.assertEqual(task.priority, 5)

    def test_invalid_below_min(self):
        with self.assertRaises(TaskValidationError) as context:
            Task(id=1, description="test", priority=0)
        self.assertIn("от 1 до 5", str(context.exception))

    def test_invalid_negative(self):
        with self.assertRaises(TaskValidationError) as context:
            Task(id=1, description="test", priority=-1)
        self.assertIn("от 1 до 5", str(context.exception))

    def test_invalid_above_max(self):
        with self.assertRaises(TaskValidationError) as context:
            Task(id=1, description="test", priority=6)
        self.assertIn("от 1 до 5", str(context.exception))

    def test_invalid_high_value(self):
        with self.assertRaises(TaskValidationError) as context:
            Task(id=1, description="test", priority=100)
        self.assertIn("от 1 до 5", str(context.exception))

    def test_invalid_float_priority(self):
        with self.assertRaises(TaskValidationError) as context:
            Task(id=1, description="test", priority=3.5)
        self.assertIn("int", str(context.exception))

    def test_invalid_str_priority(self):
        with self.assertRaises(TaskValidationError) as context:
            Task(id=1, description="test", priority="high")
        self.assertIn("int", str(context.exception))


    def test_cannot_bypass_priority_descriptor_through_dict(self):
        task = Task(id=1, description="test", priority=3)
        task.__dict__['priority'] = 10
        self.assertEqual(task.priority, 3)
        with self.assertRaises(TaskValidationError):
            task.priority = 10

class TestStatusDescriptor(unittest.TestCase):

    def test_valid_status_created(self):
        task = Task(id=1, description="test", priority=3, status="created")
        self.assertEqual(task.status, "created")

    def test_valid_status_in_progress(self):
        task = Task(id=1, description="test", priority=3, status="in_progress")
        self.assertEqual(task.status, "in_progress")

    def test_valid_status_completed(self):
        task = Task(id=1, description="test", priority=3, status="completed")
        self.assertEqual(task.status, "completed")

    def test_valid_status_canceled(self):
        task = Task(id=1, description="test", priority=3, status="canceled")
        self.assertEqual(task.status, "canceled")

    def test_status_without_default_in_descriptor(self):
        task = Task(id=1, description="test", priority=3)
        self.assertEqual(task.status, "created")

    def test_invalid_status_done(self):
        with self.assertRaises(TaskValidationError) as context:
            Task(id=1, description="test", priority=3, status="done")
        self.assertIn("недопустим", str(context.exception))

    def test_invalid_status_pending(self):
        with self.assertRaises(TaskValidationError) as context:
            Task(id=1, description="test", priority=3, status="pending")
        self.assertIn("недопустим", str(context.exception))

    def test_invalid_status_empty(self):
        with self.assertRaises(TaskValidationError) as context:
            Task(id=1, description="test", priority=3, status="")
        self.assertIn("недопустим", str(context.exception))

    def test_invalid_status_none(self):
        with self.assertRaises(TaskValidationError) as context:
            Task(id=1, description="test", priority=3, status=None)
        self.assertIn("str", str(context.exception))

    def test_invalid_status_int(self):
        with self.assertRaises(TaskValidationError) as context:
            Task(id=1, description="test", priority=3, status=123)
        self.assertIn("str", str(context.exception))

    def test_cannot_bypass_status_descriptor_through_dict(self):
        task = Task(id=1, description="test", priority=3)
        task.__dict__['status'] = "invalid"
        self.assertEqual(task.status, "created")
        with self.assertRaises(TaskValidationError):
            task.status = "invalid"


class TestCreatedAtDescriptor(unittest.TestCase):

    def test_valid_current_time(self):
        now = datetime.now()
        task = Task(id=1, description="test", priority=3, created_at=now)
        self.assertEqual(task.created_at, now)

    def test_valid_past_time(self):
        past = datetime.now() - timedelta(days=1)
        task = Task(id=1, description="test", priority=3, created_at=past)
        self.assertEqual(task.created_at, past)

    def test_valid_default_created_at(self):
        before = datetime.now()
        task = Task(id=1, description="test", priority=3)
        after = datetime.now()
        self.assertTrue(before <= task.created_at <= after)

    def test_invalid_future_time(self):
        future = datetime.now() + timedelta(days=1)
        with self.assertRaises(TaskValidationError) as context:
            Task(id=1, description="test", priority=3, created_at=future)
        self.assertIn("будущем", str(context.exception))

    def test_invalid_str_time(self):
        with self.assertRaises(TaskValidationError) as context:
            Task(id=1, description="test", priority=3, created_at="2024-01-01")
        self.assertIn("datetime", str(context.exception))


    def test_cannot_bypass_created_at_descriptor_through_dict(self):
        task = Task(id=1, description="test", priority=3)
        future = datetime.now() + timedelta(days=1)
        task.__dict__['created_at'] = future
        self.assertNotEqual(task.created_at, future)
        with self.assertRaises(TaskValidationError):
            task.created_at = future




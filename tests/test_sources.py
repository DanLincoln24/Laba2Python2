import sys
import os
import unittest
import json
import tempfile
from src.first_laba.protocol import TaskSource, RawTask
from src.first_laba.random_source import RandomTaskSource
from src.first_laba.file_source import FileTaskSource
from src.first_laba.api_source import ApiStubSource
from src.task import Task
from src.descriptors import TaskValidationError


class TestIntegrationWithSources(unittest.TestCase):

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_filename = self.temp_file.name
        self.temp_file.close()

    def tearDown(self):
        if os.path.exists(self.temp_filename):
            try:
                os.unlink(self.temp_filename)
            except PermissionError:
                pass

    def test_file_source_yields_raw_tasks(self):
        data = [
            {"id": 1, "payload": "task 1"},
            {"id": 2, "payload": "task 2"}
        ]
        with open(self.temp_filename, 'w') as f:
            json.dump(data, f)

        source = FileTaskSource(self.temp_filename)
        tasks = list(source.get_tasks())

        self.assertEqual(len(tasks), 2)
        self.assertIsInstance(tasks[0], RawTask)
        self.assertEqual(tasks[0].id, 1)
        self.assertEqual(tasks[0].payload, "task 1")

    def test_random_source_yields_raw_tasks(self):
        source = RandomTaskSource(5)
        tasks = list(source.get_tasks())

        self.assertEqual(len(tasks), 5)
        for i, task in enumerate(tasks):
            self.assertIsInstance(task, RawTask)
            self.assertEqual(task.id, i)
            self.assertIsInstance(task.payload, str)

    def test_api_stub_source_yields_raw_tasks(self):
        source = ApiStubSource("https://test.com")
        tasks = list(source.get_tasks())

        self.assertEqual(len(tasks), 2)
        self.assertIsInstance(tasks[0], RawTask)
        self.assertEqual(tasks[0].id, "api_1")
        self.assertEqual(tasks[0].payload, {'source': 'stub', 'data': 'value1'})

    def test_convert_raw_task_to_valid_task(self):
        raw = RawTask(id=1, payload="some data")
        task = Task(
            id=raw.id,
            description=str(raw.payload),
            priority=3,
            status="created"
        )

        self.assertEqual(task.id, 1)
        self.assertEqual(task.description, "some data")
        self.assertEqual(task.priority, 3)

    def test_invalid_raw_task_data_raises_error(self):
        raw = RawTask(id=0, payload="")
        with self.assertRaises(TaskValidationError):
            Task(
                id=raw.id,
                description=str(raw.payload),
                priority=3
            )

    def test_process_all_sources_and_create_tasks(self):
        with open(self.temp_filename, 'w') as f:
            json.dump([
                {"id": 10, "payload": "from file"},
                {"id": 20, "payload": "another file task"}
            ], f)

        sources = [
            FileTaskSource(self.temp_filename),
            RandomTaskSource(2),
            ApiStubSource("https://test.com")
        ]

        all_tasks = []
        for source in sources:
            for raw_task in source.get_tasks():
                if isinstance(raw_task.id, int) and raw_task.id > 0:
                    try:
                        task = Task(
                            id=raw_task.id,
                            description=str(raw_task.payload),
                            priority=3,
                            status="created"
                        )
                        all_tasks.append(task)
                    except TaskValidationError:
                        pass

        self.assertGreater(len(all_tasks), 0)
        for task in all_tasks:
            self.assertIsInstance(task, Task)
            self.assertIsInstance(task.id, (int, str))
            self.assertIsInstance(task.description, str)


class TestTaskSourceProtocol(unittest.TestCase):

    def test_file_source_implements_protocol(self):
        source = FileTaskSource("test.json")
        self.assertTrue(hasattr(source, 'get_tasks'))
        self.assertTrue(callable(source.get_tasks))

    def test_random_source_implements_protocol(self):
        source = RandomTaskSource(3)
        self.assertTrue(hasattr(source, 'get_tasks'))
        self.assertTrue(callable(source.get_tasks))

    def test_api_source_implements_protocol(self):
        source = ApiStubSource("https://test.com")
        self.assertTrue(hasattr(source, 'get_tasks'))
        self.assertTrue(callable(source.get_tasks))

    def test_raw_task_is_dataclass(self):
        task = RawTask(id=1, payload="test")
        self.assertEqual(task.id, 1)
        self.assertEqual(task.payload, "test")


import unittest
import json
import tempfile
import os
from datetime import datetime
from src.first_laba.protocol import RawTask, TaskSource
from src.first_laba.random_source import RandomTaskSource
from src.first_laba.file_source import FileTaskSource
from src.first_laba.api_source import ApiStubSource
from src.second_laba.task import Task
from src.second_laba.descriptors import TaskValidationError
from src.third_laba.queue import TaskQueue


class TestIntegration(unittest.TestCase):

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

    def raw_to_task(self, raw: RawTask) -> Task:
        desc = str(raw.payload)

        if isinstance(raw.id, int) and raw.id == 0:
            task_id = raw.id + 1
        elif isinstance(raw.id, int) and raw.id > 0:
            task_id = raw.id
        else:
            task_id = raw.id

        return Task(
            id=task_id,
            description=desc,
            priority=3,
            status='created',
            created_at=datetime.now()
        )

    def test_full_cycle_file_source_to_queue(self):
        test_data = [
            {"id": 101, "payload": "Integration task 1"},
            {"id": 102, "payload": "Integration task 2"},
            {"id": 103, "payload": "Integration task 3"}
        ]
        with open(self.temp_filename, 'w') as f:
            json.dump(test_data, f)

        source = FileTaskSource(self.temp_filename)
        self.assertTrue(hasattr(source, 'get_tasks'))
        self.assertTrue(callable(source.get_tasks))

        queue = TaskQueue()
        raw_tasks = list(source.get_tasks())
        self.assertEqual(len(raw_tasks), 3)

        for raw in raw_tasks:
            self.assertIsInstance(raw, RawTask)
            task = self.raw_to_task(raw)
            queue.add_task(task)

        self.assertEqual(len(queue), 3)

        task_ids = [t.id for t in queue]
        self.assertEqual(task_ids, [101, 102, 103])

        created_tasks = list(queue.tasks_by_status("created"))
        self.assertEqual(len(created_tasks), 3)

    def test_full_cycle_random_source_to_queue(self):
        source = RandomTaskSource(count=5)
        self.assertTrue(hasattr(source, 'get_tasks'))

        queue = TaskQueue()
        raw_tasks = list(source.get_tasks())
        self.assertEqual(len(raw_tasks), 5)

        valid_tasks_count = 0
        for i, raw in enumerate(raw_tasks):
            self.assertIsInstance(raw, RawTask)
            self.assertEqual(raw.id, i)
            try:
                task = self.raw_to_task(raw)
                queue.add_task(task)
                valid_tasks_count += 1
            except TaskValidationError:
                pass

        self.assertEqual(valid_tasks_count, 5)
        self.assertEqual(len(queue), 5)

        first_pass = [t.id for t in queue]
        second_pass = [t.id for t in queue]
        self.assertEqual(first_pass, second_pass)

        high_priority_tasks = list(queue.tasks_by_priority(4))
        self.assertGreaterEqual(len(high_priority_tasks), 0)

    def test_full_cycle_api_source_to_queue(self):
        source = ApiStubSource("https://test.com")
        self.assertTrue(hasattr(source, 'get_tasks'))

        queue = TaskQueue()
        raw_tasks = list(source.get_tasks())
        self.assertEqual(len(raw_tasks), 2)

        for raw in raw_tasks:
            self.assertIsInstance(raw, RawTask)
            task = self.raw_to_task(raw)
            queue.add_task(task)

        self.assertEqual(len(queue), 2)
        self.assertEqual([t.id for t in queue], ["api_1", "api_2"])

    def test_multiple_sources_to_single_queue(self):
        with open(self.temp_filename, 'w') as f:
            json.dump([
                {"id": 201, "payload": "File task 1"},
                {"id": 202, "payload": "File task 2"}
            ], f)

        sources = [
            FileTaskSource(self.temp_filename),
            RandomTaskSource(count=3),
            ApiStubSource("https://test.com")
        ]

        queue = TaskQueue()
        total_raw_tasks = 0
        valid_tasks = 0

        for source in sources:
            self.assertTrue(hasattr(source, 'get_tasks'))
            for raw in source.get_tasks():
                total_raw_tasks += 1
                try:
                    task = self.raw_to_task(raw)
                    queue.add_task(task)
                    valid_tasks += 1
                except TaskValidationError:
                    pass

        self.assertEqual(total_raw_tasks, 7)
        self.assertEqual(valid_tasks, 7)
        self.assertEqual(len(queue), 7)

    def test_task_modification_through_queue(self):
        task = Task(id=301, description="Original", priority=3)
        queue = TaskQueue([task])

        retrieved_task = list(queue)[0]
        self.assertEqual(retrieved_task.description, "Original")
        self.assertEqual(retrieved_task.priority, 3)

        retrieved_task.description = "Modified"
        retrieved_task.priority = 5
        retrieved_task.status = "in_progress"

        self.assertEqual(queue._tasks[0].description, "Modified")
        self.assertEqual(queue._tasks[0].priority, 5)
        self.assertEqual(queue._tasks[0].status, "in_progress")

        with self.assertRaises(TaskValidationError):
            retrieved_task.priority = 10

        self.assertEqual(queue._tasks[0].priority, 5)

    def test_invalid_task_handling(self):
        with open(self.temp_filename, 'w') as f:
            json.dump([
                {"id": 0, "payload": ""},
                {"id": -1, "payload": None},
                {"id": 401, "payload": "Valid task"}
            ], f)

        source = FileTaskSource(self.temp_filename)
        queue = TaskQueue()

        valid_count = 0
        invalid_count = 0

        for raw in source.get_tasks():
            try:
                task = self.raw_to_task(raw)
                queue.add_task(task)
                valid_count += 1
            except TaskValidationError:
                invalid_count += 1

        self.assertEqual(valid_count, 1)
        self.assertEqual(invalid_count, 2)
        self.assertEqual(len(queue), 1)
        self.assertEqual(list(queue)[0].id, 401)

    def test_queue_with_complex_filtering(self):
        tasks = [
            Task(id=1, description="High priority created", priority=5, status="created"),
            Task(id=2, description="Low priority created", priority=1, status="created"),
            Task(id=3, description="High priority progress", priority=5, status="in_progress"),
            Task(id=4, description="Medium priority completed", priority=3, status="completed"),
            Task(id=5, description="Low priority canceled", priority=2, status="canceled")
        ]
        queue = TaskQueue(tasks)

        ready_tasks = [t for t in queue if t.is_ready]
        self.assertEqual(len(ready_tasks), 1)
        self.assertEqual(ready_tasks[0].id, 1)

        sorted_by_age = sorted(queue, key=lambda t: t.age)
        self.assertEqual(len(sorted_by_age), 5)

        created_high_priority = [
            t for t in queue.tasks_by_status("created")
            if t.priority >= 4
        ]
        self.assertEqual(len(created_high_priority), 1)
        self.assertEqual(created_high_priority[0].id, 1)

    def test_lazy_evaluation_with_large_dataset(self):
        large_file_data = [{"id": i, "payload": f"Task {i}"} for i in range(1, 501)]
        with open(self.temp_filename, 'w') as f:
            json.dump(large_file_data, f)

        source = FileTaskSource(self.temp_filename)
        queue = TaskQueue()

        for raw in source.get_tasks():
            task = self.raw_to_task(raw)
            queue.add_task(task)

        self.assertEqual(len(queue), 500)

        for i in range(5):
            task = Task(
                id=1000 + i,
                description=f"High priority {i}",
                priority=5
            )
            queue.add_task(task)

        filtered = queue.tasks_by_priority(4)
        first_five = []
        for i, task in enumerate(filtered):
            first_five.append(task.id)
            if i >= 4:
                break

        self.assertEqual(len(first_five), 5)
        self.assertTrue(all(tid >= 1000 for tid in first_five))

    def test_protocol_compliance_with_queue(self):
        with open(self.temp_filename, 'w') as f:
            json.dump([
                {"id": 1, "payload": "test1"},
                {"id": 2, "payload": "test2"}
            ], f)

        sources = [
            FileTaskSource(self.temp_filename),
            RandomTaskSource(3),
            ApiStubSource("https://test.com")
        ]

        for source in sources:
            self.assertTrue(isinstance(source, TaskSource))
            self.assertTrue(hasattr(source, 'get_tasks'))

        all_queues = []
        for source in sources:
            queue = TaskQueue()
            for raw in source.get_tasks():
                try:
                    task = self.raw_to_task(raw)
                    queue.add_task(task)
                except TaskValidationError:
                    pass
            all_queues.append(queue)

        total_tasks = sum(len(q) for q in all_queues)
        self.assertGreater(total_tasks, 0)

        for queue in all_queues:
            self.assertIsInstance(queue, TaskQueue)
            self.assertTrue(hasattr(queue, '__iter__'))

    def test_descriptor_validation_in_queue_context(self):
        task = Task(id=501, description="Valid task", priority=3)
        queue = TaskQueue([task])

        queued_task = list(queue)[0]

        with self.assertRaises(TaskValidationError):
            queued_task.id = 0

        with self.assertRaises(TaskValidationError):
            queued_task.description = ""

        with self.assertRaises(TaskValidationError):
            queued_task.priority = 6

        with self.assertRaises(TaskValidationError):
            queued_task.status = "invalid"

        self.assertEqual(queued_task.id, 501)
        self.assertEqual(queued_task.description, "Valid task")
        self.assertEqual(queued_task.priority, 3)
        self.assertEqual(queued_task.status, "created")

    def test_property_calculation_in_queue(self):
        tasks = [
            Task(id=1, description="Task 1", priority=5, status="created"),
            Task(id=2, description="Task 2", priority=2, status="created"),
            Task(id=3, description="Task 3", priority=4, status="in_progress")
        ]
        queue = TaskQueue(tasks)

        ready_in_queue = [t for t in queue if t.is_ready]
        self.assertEqual(len(ready_in_queue), 1)
        self.assertEqual(ready_in_queue[0].id, 1)

        for task in queue:
            self.assertGreaterEqual(task.age, 0)
            self.assertIsInstance(task.is_ready, bool)

    def test_end_to_end_workflow(self):
        with open(self.temp_filename, 'w') as f:
            json.dump([
                {"id": 601, "payload": "Urgent task"},
                {"id": 602, "payload": "Normal task"},
                {"id": 603, "payload": "Low priority task"}
            ], f)

        source = FileTaskSource(self.temp_filename)
        self.assertTrue(isinstance(source, TaskSource))

        queue = TaskQueue()
        for raw in source.get_tasks():
            task = self.raw_to_task(raw)
            if task.id == 601:
                task.priority = 5
            elif task.id == 603:
                task.priority = 1
            queue.add_task(task)

        self.assertEqual(len(queue), 3)

        ready_tasks = [t for t in queue if t.is_ready]
        self.assertEqual(len(ready_tasks), 2)

        high_priority_tasks = list(queue.tasks_by_priority(4))
        self.assertEqual(len(high_priority_tasks), 1)

        task_601 = next(t for t in queue if t.id == 601)
        task_601.status = "in_progress"
        self.assertEqual(task_601.status, "in_progress")

        in_progress_tasks = list(queue.tasks_by_status("in_progress"))
        self.assertEqual(len(in_progress_tasks), 1)

        task_601.status = "completed"
        completed_tasks = list(queue.tasks_by_status("completed"))
        self.assertEqual(len(completed_tasks), 1)

        with self.assertRaises(AttributeError):
            task_601.is_ready = False

        with self.assertRaises(AttributeError):
            task_601.age = 0


class TestIntegrationEdgeCases(unittest.TestCase):

    def test_empty_source_handling(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([], f)
            temp_filename = f.name

        try:
            source = FileTaskSource(temp_filename)
            queue = TaskQueue()

            for raw in source.get_tasks():
                task = Task(
                    id=raw.id if raw.id > 0 else 1,
                    description=str(raw.payload) if raw.payload else "empty",
                    priority=3
                )
                queue.add_task(task)

            self.assertEqual(len(queue), 0)
        finally:
            os.unlink(temp_filename)

    def test_malformed_json_handling(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{invalid json}")
            temp_filename = f.name

        try:
            source = FileTaskSource(temp_filename)
            with self.assertRaises(json.JSONDecodeError):
                list(source.get_tasks())
        finally:
            os.unlink(temp_filename)

    def test_concurrent_queue_access_simulation(self):
        tasks = [Task(id=i, description=f"Task {i}", priority=3) for i in range(1, 11)]
        queue = TaskQueue(tasks)

        iterator1 = iter(queue)
        iterator2 = iter(queue)

        self.assertEqual(next(iterator1).id, 1)
        self.assertEqual(next(iterator2).id, 1)
        self.assertEqual(next(iterator1).id, 2)
        self.assertEqual(next(iterator1).id, 3)
        self.assertEqual(next(iterator2).id, 2)

        queue.add_task(Task(id=11, description="New task", priority=3))

        iterator3 = iter(queue)
        ids = [t.id for t in iterator3]
        self.assertEqual(len(ids), 11)
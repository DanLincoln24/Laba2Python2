import unittest
from src.second_laba.task import Task
from src.third_laba.queue import TaskQueue, TaskQueueIterator


class TestTaskQueueIterator(unittest.TestCase):

    def setUp(self):
        self.tasks = [
            Task(id=1, description="Task 1", priority=3),
            Task(id=2, description="Task 2", priority=4),
            Task(id=3, description="Task 3", priority=5)
        ]

    def test_iterator_returns_all_elements(self):
        iterator = TaskQueueIterator(self.tasks)
        result = list(iterator)
        self.assertEqual(len(result), 3)
        self.assertEqual([t.id for t in result], [1, 2, 3])

    def test_iterator_raises_stop_iteration(self):
        iterator = TaskQueueIterator(self.tasks)
        next(iterator)
        next(iterator)
        next(iterator)
        with self.assertRaises(StopIteration):
            next(iterator)

    def test_iterator_is_itself(self):
        iterator = TaskQueueIterator(self.tasks)
        self.assertIs(iter(iterator), iterator)

    def test_iterator_empty_list(self):
        iterator = TaskQueueIterator([])
        self.assertEqual(list(iterator), [])


class TestTaskQueueInitialization(unittest.TestCase):

    def test_empty_queue(self):
        queue = TaskQueue()
        self.assertEqual(len(queue), 0)
        self.assertEqual(list(queue), [])

    def test_queue_with_initial_tasks(self):
        tasks = [
            Task(id=1, description="Task 1", priority=3),
            Task(id=2, description="Task 2", priority=4)
        ]
        queue = TaskQueue(tasks)
        self.assertEqual(len(queue), 2)

    def test_add_task(self):
        queue = TaskQueue()
        task = Task(id=1, description="New task", priority=3)
        queue.add_task(task)
        self.assertEqual(len(queue), 1)
        self.assertEqual(list(queue)[0], task)


class TestTaskQueueIteration(unittest.TestCase):

    def setUp(self):
        self.tasks = [
            Task(id=1, description="Task 1", priority=3),
            Task(id=2, description="Task 2", priority=4),
            Task(id=3, description="Task 3", priority=5)
        ]
        self.queue = TaskQueue(self.tasks)

    def test_multiple_iterations_independent(self):
        first_pass = [t.id for t in self.queue]
        second_pass = [t.id for t in self.queue]
        self.assertEqual(first_pass, [1, 2, 3])
        self.assertEqual(second_pass, [1, 2, 3])

    def test_for_loop_works(self):
        ids = []
        for task in self.queue:
            ids.append(task.id)
        self.assertEqual(ids, [1, 2, 3])

    def test_list_conversion(self):
        task_list = list(self.queue)
        self.assertEqual(len(task_list), 3)
        self.assertIsInstance(task_list, list)

    def test_nested_iteration(self):
        outer_ids = []
        inner_ids = []
        for outer in self.queue:
            outer_ids.append(outer.id)
            for inner in self.queue:
                inner_ids.append(inner.id)
                break
        self.assertEqual(outer_ids, [1, 2, 3])
        self.assertEqual(len(inner_ids), 3)

    def test_iteration_after_adding_tasks(self):
        first_pass = list(self.queue)
        self.queue.add_task(Task(id=4, description="Task 4", priority=3))
        second_pass = list(self.queue)
        self.assertEqual(len(first_pass), 3)
        self.assertEqual(len(second_pass), 4)


class TestTaskQueueLazyFilters(unittest.TestCase):

    def setUp(self):
        self.tasks = [
            Task(id=1, description="Task 1", priority=5, status="created"),  # изменено с 3 на 5
            Task(id=2, description="Task 2", priority=4, status="in_progress"),
            Task(id=3, description="Task 3", priority=5, status="completed"),
            Task(id=4, description="Task 4", priority=2, status="created"),
            Task(id=5, description="Task 5", priority=1, status="canceled")
        ]
        self.queue = TaskQueue(self.tasks)

    def test_filter_by_status_created(self):
        created_tasks = list(self.queue.tasks_by_status("created"))
        self.assertEqual(len(created_tasks), 2)
        self.assertEqual([t.id for t in created_tasks], [1, 4])

    def test_filter_by_status_in_progress(self):
        in_progress_tasks = list(self.queue.tasks_by_status("in_progress"))
        self.assertEqual(len(in_progress_tasks), 1)
        self.assertEqual(in_progress_tasks[0].id, 2)

    def test_filter_by_status_no_match(self):
        no_tasks = list(self.queue.tasks_by_status("nonexistent"))
        self.assertEqual(len(no_tasks), 0)

    def test_filter_by_priority_min_4(self):
        high_priority = list(self.queue.tasks_by_priority(4))
        self.assertEqual(len(high_priority), 3)  # задачи с приоритетами 5, 4, 5 (id: 1, 2, 3)
        self.assertEqual([t.id for t in high_priority], [1, 2, 3])

    def test_filter_by_priority_min_5(self):
        max_priority = list(self.queue.tasks_by_priority(5))
        self.assertEqual(len(max_priority), 2)  # задачи с приоритетом 5 (id: 1, 3)
        self.assertEqual([t.id for t in max_priority], [1, 3])

    def test_filter_by_priority_no_match(self):
        no_tasks = list(self.queue.tasks_by_priority(6))
        self.assertEqual(len(no_tasks), 0)

    def test_filters_are_lazy(self):
        filtered = self.queue.tasks_by_priority(4)
        self.assertIsNotNone(filtered)
        self.assertTrue(hasattr(filtered, '__iter__'))
        self.assertTrue(hasattr(filtered, '__next__'))

    def test_combine_filters_with_comprehension(self):
        high_priority_created = [
            t for t in self.queue.tasks_by_status("created")
            if t.priority >= 4
        ]
        self.assertEqual(len(high_priority_created), 1)  # только задача с id=1 (priority=5, status=created)
        self.assertEqual(high_priority_created[0].id, 1)


class TestTaskQueueStandardFunctions(unittest.TestCase):

    def setUp(self):
        self.tasks = [
            Task(id=1, description="Task 1", priority=3),
            Task(id=2, description="Task 2", priority=4),
            Task(id=3, description="Task 3", priority=5)
        ]
        self.queue = TaskQueue(self.tasks)

    def test_len_function(self):
        self.assertEqual(len(self.queue), 3)

    def test_sum_function(self):
        total_priority = sum(t.priority for t in self.queue)
        self.assertEqual(total_priority, 12)

    def test_max_function(self):
        max_priority = max(t.priority for t in self.queue)
        self.assertEqual(max_priority, 5)

    def test_min_function(self):
        min_priority = min(t.priority for t in self.queue)
        self.assertEqual(min_priority, 3)

    def test_sorted_function(self):
        sorted_tasks = sorted(self.queue, key=lambda t: t.priority, reverse=True)
        self.assertEqual([t.priority for t in sorted_tasks], [5, 4, 3])

    def test_any_function(self):
        has_high_priority = any(t.priority >= 4 for t in self.queue)
        self.assertTrue(has_high_priority)

    def test_all_function(self):
        all_created = all(t.status == "created" for t in self.queue)
        self.assertTrue(all_created)

    def test_filter_function(self):
        filtered = filter(lambda t: t.priority > 3, self.queue)
        result = list(filtered)
        self.assertEqual(len(result), 2)
        self.assertEqual([t.priority for t in result], [4, 5])

    def test_map_function(self):
        ids = list(map(lambda t: t.id, self.queue))
        self.assertEqual(ids, [1, 2, 3])


class TestTaskQueueEdgeCases(unittest.TestCase):

    def test_large_queue_iteration(self):
        tasks = [Task(id=i, description=f"Task {i}", priority=3) for i in range(1, 1001)]
        queue = TaskQueue(tasks)
        count = 0
        for task in queue:
            count += 1
        self.assertEqual(count, 1000)

    def test_empty_queue_filters(self):
        queue = TaskQueue()
        self.assertEqual(list(queue.tasks_by_status("created")), [])
        self.assertEqual(list(queue.tasks_by_priority(1)), [])

    def test_mixed_task_states(self):
        tasks = [
            Task(id=1, description="Created high", priority=5, status="created"),
            Task(id=2, description="Created low", priority=1, status="created"),
            Task(id=3, description="Progress high", priority=5, status="in_progress"),
            Task(id=4, description="Completed high", priority=5, status="completed"),
            Task(id=5, description="Canceled low", priority=1, status="canceled")
        ]
        queue = TaskQueue(tasks)

        high_priority_created = [
            t for t in queue.tasks_by_status("created")
            if t.priority >= 4
        ]
        self.assertEqual(len(high_priority_created), 1)
        self.assertEqual(high_priority_created[0].id, 1)

    def test_queue_repr(self):
        queue = TaskQueue()
        self.assertEqual(repr(queue), "TaskQueue(0 tasks)")

        queue.add_task(Task(id=1, description="Test", priority=3))
        self.assertEqual(repr(queue), "TaskQueue(1 tasks)")
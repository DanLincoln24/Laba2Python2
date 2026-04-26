import asyncio
import unittest
from datetime import datetime
from src.second_laba.task import Task
from src.second_laba.descriptors import TaskValidationError
from src.fourth_laba.executor import (
    AsyncTaskExecutor,
    ExecutorNotStartedError,
    TaskProcessingError,
)
from src.fourth_laba.handlers import (
    TaskHandler,
    PrintHandler,
    FailingHandler,
    PriorityBasedHandler,
)


class TestAsyncExecutor(unittest.TestCase):

    def async_test(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def test_register_handler_checks_protocol(self):
        executor = AsyncTaskExecutor()

        class NotHandler:
            pass

        with self.assertRaises(TypeError):
            executor.register_handler(NotHandler())

    def test_register_valid_handler(self):
        executor = AsyncTaskExecutor()
        try:
            executor.register_handler(PrintHandler())
        except Exception:
            self.fail("register_handler() вызвал исключение")

    def test_submit_before_start_raises(self):
        executor = AsyncTaskExecutor()
        executor.register_handler(PrintHandler())
        task = Task(id=1, description="test", priority=3)

        async def test():
            with self.assertRaises(ExecutorNotStartedError):
                await executor.submit(task)

        self.loop.run_until_complete(test())

    def test_single_task_processing(self):

        async def scenario():
            async with AsyncTaskExecutor(workers=1) as executor:
                executor.register_handler(PrintHandler())
                await executor.submit(
                    Task(id=10, description="Single", priority=2)
                )
                await executor.wait_all()
                self.assertEqual(len(executor.errors), 0)

        self.loop.run_until_complete(scenario())

    def test_multiple_tasks_concurrently(self):

        async def scenario():
            async with AsyncTaskExecutor(workers=2) as executor:
                executor.register_handler(PrintHandler())
                for i in range(5):
                    await executor.submit(
                        Task(id=100 + i, description=f"Task {i}", priority=3)
                    )
                await executor.wait_all()
                self.assertEqual(len(executor.errors), 0)

        self.loop.run_until_complete(scenario())

    def test_failing_handler_produces_errors(self):

        async def scenario():
            async with AsyncTaskExecutor(workers=1) as executor:
                executor.register_handler(FailingHandler())
                # Задача с priority=5 вызовет исключение
                await executor.submit(
                    Task(id=1, description="Will fail", priority=5)
                )
                await executor.submit(
                    Task(id=2, description="OK", priority=3)
                )
                await executor.wait_all()
                # Должна быть одна ошибка
                self.assertEqual(len(executor.errors), 1)
                err = executor.errors[0]
                self.assertIsInstance(err, TaskProcessingError)
                self.assertEqual(err.task.id, 1)

        self.loop.run_until_complete(scenario())

    def test_handler_not_found_creates_error(self):

        async def scenario():
            async with AsyncTaskExecutor(workers=1) as executor:
                executor.register_handler(PriorityBasedHandler())
                await executor.submit(
                    Task(id=99, description="Low priority", priority=2)
                )
                await executor.wait_all()
                self.assertEqual(len(executor.errors), 1)
                self.assertIn("Нет обработчика", str(executor.errors[0]))

        self.loop.run_until_complete(scenario())

    def test_multiple_handlers_chain(self):

        async def scenario():
            async with AsyncTaskExecutor(workers=1) as executor:
                executor.register_handler(FailingHandler())    # обработает всё, но падает при priority=5
                executor.register_handler(PrintHandler())     # запасной, обрабатывает всё
                await executor.submit(
                    Task(id=201, description="Test", priority=5)
                )
                await executor.wait_all()
                # FailingHandler выбросит исключение, задача не должна быть обработана PrinterHandler
                # т.к. мы ищем первый can_handle=True – это FailingHandler.
                # Поэтому будет ошибка.
                self.assertEqual(len(executor.errors), 1)
                self.assertIsInstance(executor.errors[0].cause, ValueError)

        self.loop.run_until_complete(scenario())

    def test_workers_receive_tasks_parallel(self):
        import time

        class SlowHandler:
            def can_handle(self, task):
                return True

            async def handle(self, task):
                await asyncio.sleep(0.1)

        async def scenario():
            async with AsyncTaskExecutor(workers=3) as executor:
                executor.register_handler(SlowHandler())
                for i in range(1, 7):
                    await executor.submit(
                        Task(id=i, description="Parallel", priority=1)
                    )
                start = time.perf_counter()
                await executor.wait_all()
                elapsed = time.perf_counter() - start
                # При 3 worker'ах 6 задач по 0.1c = ~0.2c
                self.assertLess(elapsed, 0.3)
                self.assertEqual(len(executor.errors), 0)

    def test_context_manager_cleanup(self):

        async def scenario():
            executor = AsyncTaskExecutor(workers=2)
            async with executor as ex:
                self.assertTrue(ex._running)
                ex.register_handler(PrintHandler())
                await ex.submit(Task(id=1, description="Cleanup", priority=1))
            self.assertFalse(ex._running)
            # Проверяем, что после выхода worker-таски отменены/завершены
            for wt in ex._worker_tasks:
                self.assertTrue(wt.done())

        self.loop.run_until_complete(scenario())


if __name__ == "__main__":
    unittest.main()
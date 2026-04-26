import asyncio
import logging
from typing import Any, List, Optional, TypeVar
from src.second_laba.task import Task
from src.fourth_laba.handlers import TaskHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
_ch = logging.StreamHandler()
_ch.setLevel(logging.DEBUG)
_formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(name)s: %(message)s")
_ch.setFormatter(_formatter)
if not logger.handlers:
    logger.addHandler(_ch)

T = TypeVar("T", bound=Task)


class ExecutorError(Exception):
    ...


class TaskProcessingError(ExecutorError):

    def __init__(self, task: Task, cause: Exception) -> None:
        self.task = task
        self.cause = cause
        super().__init__(f"[{task.id}] {cause}")


class HandlerNotFoundError(ExecutorError):

    def __init__(self, task: Task) -> None:
        super().__init__(f"Нет обработчика для задачи {task.id!r} (priority={task.priority})")


class ExecutorNotStartedError(ExecutorError):
    ...

class AsyncTaskExecutor:
    def __init__(self, workers: int = 2, log_level: int = logging.INFO) -> None:
        if workers < 1:
            raise ValueError("workers должен быть >= 1")
        self._workers = workers
        self._queue: Optional[asyncio.Queue[Optional[Task]]] = None
        self._handlers: List[TaskHandler] = []
        self._worker_tasks: List[asyncio.Task[Any]] = []
        self._running = False
        self._errors: List[TaskProcessingError] = []

        logger.setLevel(log_level)

    def register_handler(self, handler: object) -> None:
        if not isinstance(handler, TaskHandler):
            raise TypeError(
                f"Обработчик {handler!r} не реализует протокол TaskHandler"
            )
        self._handlers.append(handler)
        logger.info("Зарегистрирован обработчик: %s", type(handler).__name__)

    async def submit(self, task: Task) -> None:
        if not self._running or self._queue is None:
            raise ExecutorNotStartedError(
                "Исполнитель не запущен. Используйте 'async with'"
            )
        await self._queue.put(task)
        logger.debug("Задача %s добавлена в очередь", task.id)

    async def wait_all(self) -> None:
        if self._queue:
            await self._queue.join()

    @property
    def errors(self) -> List[TaskProcessingError]:
        return list(self._errors)

    async def __aenter__(self) -> "AsyncTaskExecutor":
        self._queue = asyncio.Queue()
        self._running = True
        self._worker_tasks = [
            asyncio.create_task(self._worker_loop(f"worker-{i}"))
            for i in range(self._workers)
        ]
        logger.info("Исполнитель запущен с %d worker-ами", self._workers)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        for _ in self._worker_tasks:
            await self._queue.put(None)
        await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        self._running = False
        logger.info("Исполнитель остановлен")
        return False


    async def _worker_loop(self, name: str) -> None:
        while True:
            task = await self._queue.get()
            if task is None:
                self._queue.task_done()
                break
            try:
                handler = next(
                    (h for h in self._handlers if h.can_handle(task)),
                    None
                )
                if handler is None:
                    raise HandlerNotFoundError(task)
                await handler.handle(task)
                logger.info("[%s] Задача %s успешно обработана", name, task.id)
            except Exception as e:
                if isinstance(e, HandlerNotFoundError):
                    processing_error = TaskProcessingError(task, e)
                else:
                    processing_error = TaskProcessingError(task, e)
                self._errors.append(processing_error)
                logger.error("[%s] Ошибка при обработке %s: %s", name, task.id, e)
            finally:
                self._queue.task_done()
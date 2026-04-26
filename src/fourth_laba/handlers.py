from typing import Protocol, runtime_checkable
from src.second_laba.task import Task


@runtime_checkable
class TaskHandler(Protocol):

    def can_handle(self, task: Task) -> bool:
        ...

    async def handle(self, task: Task) -> None:
        ...


class PrintHandler:
    def can_handle(self, task: Task) -> bool:
        return True

    async def handle(self, task: Task) -> None:
        import asyncio
        await asyncio.sleep(0.05 * task.priority)
        print(f"[PrintHandler] Задача {task.id} обработана (status={task.status}, priority={task.priority})")


class FailingHandler:
    def can_handle(self, task: Task) -> bool:
        return True

    async def handle(self, task: Task) -> None:
        import asyncio
        await asyncio.sleep(0.05)
        if task.priority >= 5:
            raise ValueError(f"Слишком высокий приоритет у задачи {task.id}")
        print(f"[FailingHandler] Задача {task.id} выполнена успешно")


class PriorityBasedHandler:
    def can_handle(self, task: Task) -> bool:
        return task.priority >= 4

    async def handle(self, task: Task) -> None:
        import asyncio
        await asyncio.sleep(0.1)
        print(f"[PriorityBasedHandler] Высокоприоритетная задача {task.id} обработана")
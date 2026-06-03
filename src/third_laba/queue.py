from typing import Iterator, List, Optional
from src.second_laba.task import Task


class TaskQueueIterator:
    def __init__(self, tasks: List[Task]):
        self._tasks = tasks
        self._index = 0

    def __iter__(self) -> Iterator[Task]:
        return self

    def __next__(self) -> Task:
        if self._index >= len(self._tasks):
            raise StopIteration
        task = self._tasks[self._index]
        self._index += 1
        return task


class TaskQueue:
    def __init__(self, tasks: List[Task] | None = None):
        self._tasks = tasks if tasks is not None else []

    def add_task(self, task: Task) -> None:
        self._tasks.append(task)

    def __iter__(self) -> Iterator[Task]:
        return TaskQueueIterator(self._tasks)

    def tasks_by_status(self, status: str) -> Iterator[Task]:
        for task in self._tasks:
            if task.status == status:
                yield task

    def tasks_by_priority(self, min_priority: int) -> Iterator[Task]:
        for task in self._tasks:
            if task.priority >= min_priority:
                yield task

    def __len__(self) -> int:
        return len(self._tasks)

    def __repr__(self) -> str:
        return f"TaskQueue({len(self._tasks)} tasks)"

task123 = Task(id = 1, description='wrkjgmer', priority=4)
task124 = Task(id = 2, description='wrыапкjgmer', priority=1)
task125 = Task(id = 3, description='wrыапкjыцпкmer', priority=5)
queue = TaskQueue()
queue.add_task(task123)
queue.add_task(task124)
queue.add_task(task125)
for t in queue.tasks_by_priority(3):
    print(t)

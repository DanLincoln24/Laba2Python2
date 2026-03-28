from typing import Iterable, Any, Protocol, runtime_checkable
from dataclasses import dataclass


@dataclass
class Task:
    id: int | str
    payload: Any


@runtime_checkable
class TaskSource(Protocol):
    def get_tasks(self) -> Iterable[Task]:
        ...
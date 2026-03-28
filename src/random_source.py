import random
import string
from typing import Iterable
from protocol import Task, TaskSource


class RandomTaskSource:
    def __init__(self, count: int):
        self.count = count

    def get_tasks(self) -> Iterable[Task]:
        for i in range(self.count):
            yield Task(
                id=i,
                payload=''.join(random.choices(string.ascii_letters, k=5))
            )
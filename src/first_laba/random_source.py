import random
import string
from typing import Iterable
from .protocol import RawTask


class RandomTaskSource:
    def __init__(self, count: int):
        self.count = count

    def get_tasks(self) -> Iterable[RawTask]:
        for i in range(self.count):
            yield RawTask(
                id=i,
                payload=''.join(random.choices(string.ascii_letters, k=5))
            )
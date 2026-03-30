import json
from typing import Iterable
from protocol import RawTask, TaskSource


class FileTaskSource:
    def __init__(self, filename: str):
        self.filename = filename

    def get_tasks(self) -> Iterable[RawTask]:
        with open(self.filename) as f:
            data = json.load(f)
        for item in data:
            yield RawTask(id=item['id'], payload=item['payload'])
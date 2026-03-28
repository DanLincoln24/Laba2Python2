import json
from typing import Iterable
from protocol import Task, TaskSource


class FileTaskSource:
    def __init__(self, filename: str):
        self.filename = filename

    def get_tasks(self) -> Iterable[Task]:
        with open(self.filename) as f:
            data = json.load(f)
        for item in data:
            yield Task(id=item['id'], payload=item['payload'])
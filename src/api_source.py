from typing import Iterable
from protocol import Task, TaskSource


class ApiStubSource:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_tasks(self) -> Iterable[Task]:
        return [
            Task(id='api_1', payload={'source': 'stub', 'data': 'value1'}),
            Task(id='api_2', payload={'source': 'stub', 'data': 'value2'}),
        ]
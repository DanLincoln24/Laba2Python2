from typing import Iterable
from protocol import RawTask, TaskSource


class ApiStubSource:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_tasks(self) -> Iterable[RawTask]:
        return [
            RawTask(id='api_1', payload={'source': 'stub', 'data': 'value1'}),
            RawTask(id='api_2', payload={'source': 'stub', 'data': 'value2'}),
        ]
import json
import tempfile
import os
from datetime import datetime

from task import Task
from descriptors import TaskValidationError
from file_source import FileTaskSource
from random_source import RandomTaskSource
from api_source import ApiStubSource
from protocol import TaskSource


def process_tasks(source):
    for task in source.get_tasks():
        print(f"Задача {task.id}: {task.payload}")


def safe_process(source):
    if isinstance(source, TaskSource):
        print(f"\nОбработка источника: {source.__class__.__name__}")
        process_tasks(source)
    else:
        print(f"Объект {source} не является источником задач")


if __name__ == "__main__":

    try:
        task1 = Task(
            id=101,
            description="Подготовить отчёт",
            priority=4,
            status="created"
        )
        print("Создана задача:")
        print(task1)
        print(f"Готовность: {task1.is_ready}")
        print(f"Возраст: {task1.age:.2f} сек")
    except TaskValidationError as e:
        print(f"Ошибка: {e}")

    try:
        task2 = Task(
            id=102,
            description="Исправить баги",
            priority=10,
            status="created"
        )
    except TaskValidationError as e:
        print(f"\nОшибка: {e}")

    try:
        task1.status = "done"
    except TaskValidationError as e:
        print(f"\nОшибка: {e}")

    try:
        task1.is_ready = False
    except AttributeError as e:
        print(f"\nСвойство только для чтения: {e}")

    print(f"\nТекущий статус: {task1.status}")
    task1.status = "in_progress"
    print(f"Новый статус: {task1.status}")
    print(f"Готовность: {task1.is_ready}")

    print("\n=== Работа с источниками ===")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tf:
        json.dump([
            {"id": 1, "payload": "file task 1"},
            {"id": 2, "payload": "file task 2"}
        ], tf)
        temp_filename = tf.name

    file_source = FileTaskSource(temp_filename)
    random_source = RandomTaskSource(3)
    api_source = ApiStubSource("https://example.com/api")

    safe_process(file_source)
    safe_process(random_source)
    safe_process(api_source)
    safe_process("not a source")

    os.unlink(temp_filename)
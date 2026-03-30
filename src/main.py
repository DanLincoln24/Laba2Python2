from src.first_laba.protocol import TaskSource


def process_tasks(source):
    for task in source.get_tasks():
        print(f"Задача {task.id}: {task.payload}")


def safe_process(source):
    if isinstance(source, TaskSource):
        print(f"\nОбработка источника: {source.__class__.__name__}")
        process_tasks(source)
    else:
        print(f"Объект {source} не является источником задач")

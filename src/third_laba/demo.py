from datetime import datetime
from src.task import Task
from src.first_laba.random_source import RandomTaskSource
from src.first_laba.file_source import FileTaskSource
from src.first_laba.protocol import RawTask
from src.third_laba.queue import TaskQueue


def raw_to_task(raw: RawTask) -> Task:
    desc = str(raw.payload)

    if isinstance(raw.id, int) and raw.id == 0:
        task_id = raw.id + 1
    elif isinstance(raw.id, int) and raw.id > 0:
        task_id = raw.id
    else:
        task_id = raw.id

    return Task(
        id=task_id,
        description=desc,
        priority=3,
        status='created',
        created_at=datetime.now()
    )


def main():
    print("1. Загрузка из RandomTaskSource (5 задач):")
    random_source = RandomTaskSource(count=5)
    queue = TaskQueue()
    for raw in random_source.get_tasks():
        task = raw_to_task(raw)
        queue.add_task(task)
        print(f"  Добавлена: {task}")

    print(f"\nОчередь: {queue}")

    print("\n2. Повторный обход:")
    print("   Первый проход:", [t.id for t in queue])
    print("   Второй проход:", [t.id for t in queue])

    print("\n3. Стандартные функции:")
    print(f"   Всего задач: {len(queue)}")
    print(f"   Сумма приоритетов: {sum(t.priority for t in queue)}")

    priorities = [t.priority for t in queue]
    if priorities:
        print(f"   Максимальный приоритет: {max(priorities)}")

    print("\n4. Ленивые фильтры:")
    print("   Задачи со статусом 'created':")
    for task in queue.tasks_by_status('created'):
        print(f"     - {task.id} (priority={task.priority})")

    print("\n   Задачи с приоритетом >= 4:")
    high_priority = list(queue.tasks_by_priority(4))
    if high_priority:
        for task in high_priority:
            print(f"     - {task.id} (priority={task.priority})")
    else:
        print("     (нет задач с таким приоритетом)")

    try:
        file_source = FileTaskSource("tasks.json")
        file_queue = TaskQueue()
        for raw in file_source.get_tasks():
            task = raw_to_task(raw)
            file_queue.add_task(task)
        print(f"\n5. Загружено из файла tasks.json: {len(file_queue)} задач")
        for task in file_queue:
            desc_preview = task.description[:30] + "..." if len(task.description) > 30 else task.description
            print(f"   {task.id}: {desc_preview}")
    except FileNotFoundError:
        print("\n5. Файл tasks.json не найден")
    except Exception as e:
        print(f"\n5. Ошибка при загрузке из файла: {e}")


if __name__ == "__main__":
    main()
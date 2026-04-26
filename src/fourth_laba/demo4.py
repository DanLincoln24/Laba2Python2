import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.first_laba.random_source import RandomTaskSource
from src.first_laba.file_source import FileTaskSource
from src.first_laba.api_source import ApiStubSource
from src.second_laba.task import Task
from src.third_laba.queue import TaskQueue
from src.fourth_laba.executor import AsyncTaskExecutor
from src.fourth_laba.handlers import PrintHandler, PriorityBasedHandler


async def main():
    logging.basicConfig(level=logging.INFO)

    sources = [
        ("RandomSource(3)", RandomTaskSource(count=3)),
        ("FileTaskSource('tasks.json')", FileTaskSource("tasks.json")),
        ("ApiStubSource", ApiStubSource("https://example.com/api")),
    ]

    all_tasks = TaskQueue()
    for src_name, src in sources:
        try:
            for raw in src.get_tasks():
                desc = str(raw.payload)
                if isinstance(raw.id, int) and raw.id <= 0:
                    task_id = abs(raw.id) + 1
                else:
                    task_id = raw.id
                task = Task(
                    id=task_id,
                    description=desc[:200],
                    priority=3,
                    status="created",
                )
                all_tasks.add_task(task)
            print(f"Из {src_name} загружено задач: {len(all_tasks)} (пока)")
        except FileNotFoundError:
            print(f"[!] Файл для {src_name} не найден, пропускаем")
        except Exception as e:
            print(f"[!] Ошибка при загрузке из {src_name}: {e}")

    print(f"Всего задач для асинхронной обработки: {len(all_tasks)}")

    async with AsyncTaskExecutor(workers=2) as executor:
        executor.register_handler(PrintHandler())
        executor.register_handler(PriorityBasedHandler())

        for task in all_tasks:
            await executor.submit(task)

        await executor.wait_all()

        if executor.errors:
            print(f"\nОбнаружены ошибки ({len(executor.errors)}):")
            for err in executor.errors:
                print(f"  {err}")
        else:
            print("\nВсе задачи обработаны без ошибок")


if __name__ == "__main__":
    asyncio.run(main())
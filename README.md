# Laba2Python2
# Гаврилов Данила 103
# Платформа обработки задач

Проект реализует платформу для приёма, хранения и обработки задач из различных источников. Состоит из трёх последовательных лабораторных работ, каждая из которых расширяет функциональность системы.

---

## Лабораторная работа №1: Источники задач и контракты

### Цель работы
Освоить duck typing и контрактное программирование на примере источников задач без использования наследования.

### Реализованные компоненты

#### Протокол TaskSource (`protocol.py`)
```python
@runtime_checkable
class TaskSource(Protocol):
    def get_tasks(self) -> Iterable[RawTask]: ...
```

#### RawTask (`protocol.py`)
Легковесная структура данных для передачи задач от источников:
- `id: int | str` — идентификатор задачи
- `payload: Any` — пользовательские данные

#### Источники задач

| Класс | Описание |
|-------|----------|
| `FileTaskSource` | Загружает задачи из JSON-файла |
| `RandomTaskSource` | Генерирует случайные задачи (id и payload) |
| `ApiStubSource` | Имитирует получение задач из внешнего API |

#### Ключевые особенности
- Источники не связаны общим базовым классом
- Контракт описан через `typing.Protocol`
- Runtime-проверка: `isinstance(source, TaskSource)`
- Ленивая генерация задач через `yield`

## Лабораторная работа №2: Модель задачи (дескрипторы и property)

### Цель работы
Освоить управление доступом к атрибутам и защиту инвариантов доменной модели с использованием дескрипторов и property.

### Реализованные компоненты

#### Дескрипторы (`descriptors.py`)

**`TaskValidationError`** — специализированное исключение для ошибок валидации.

**`ValidatedDescriptor`** — абстрактный data-дескриптор:
- `__set_name__` — автоматически создаёт приватное имя `_атрибут`
- `__get__` — возвращает значение из приватного хранилища
- `__set__` — вызывает `validate()` и сохраняет значение

**Конкретные дескрипторы:**

| Дескриптор | Назначение | Правила валидации |
|------------|------------|-------------------|
| `IdDescriptor` | Идентификатор | `int > 0` или непустая `str` |
| `DescriptionDescriptor` | Описание | `str`, непустая, ≤ 500 символов |
| `PriorityDescriptor` | Приоритет | `int` от 1 до 5 |
| `StatusDescriptor` | Статус | `created` / `in_progress` / `completed` / `canceled` |
| `CreatedAtDescriptor` | Время создания | `datetime`, не в будущем |

#### Класс `Task` (`task.py`)

**Атрибуты (через дескрипторы):**
- `id` — идентификатор задачи
- `description` — описание задачи
- `priority` — приоритет (1-5)
- `status` — статус (по умолчанию `'created'`)
- `created_at` — время создания (по умолчанию `datetime.now()`)

**Вычисляемые свойства (`@property`):**
- `is_ready: bool` — готовность к выполнению (`status == 'created'` и `priority ≥ 3`)
- `age: float` — возраст задачи в секундах

### Ключевые особенности
- Data descriptors для контроля записи атрибутов
- Non-data descriptor `@property` для вычисляемых полей
- Предотвращение некорректных состояний объекта
- Защита от обхода валидации через `__dict__`

## Лабораторная работа №3: Очередь задач (итераторы и генераторы)

### Цель работы
Научиться реализовывать пользовательские коллекции и ленивую обработку задач.

### Реализованные компоненты

#### `TaskQueueIterator` (`queue.py`)
Итератор для последовательного обхода задач в очереди:
- `__iter__` — возвращает себя
- `__next__` — возвращает следующую задачу или `raise StopIteration`

#### `TaskQueue` (`queue.py`)
Очередь задач с поддержкой протокола итерации.

**Методы:**

| Метод | Описание |
|-------|----------|
| `__init__(tasks=None)` | Создание очереди (пустой или с начальными задачами) |
| `add_task(task)` | Добавление задачи в очередь |
| `__iter__()` | Возвращает новый `TaskQueueIterator` |
| `__len__()` | Количество задач в очереди |
| `tasks_by_status(status)` | Ленивый фильтр по статусу (генератор) |
| `tasks_by_priority(min_priority)` | Ленивый фильтр по приоритету (генератор) |

### Ключевые особенности
- **Iterable vs Iterator**: очередь — Iterable, возвращает новый Iterator при каждом `__iter__`
- **Повторный обход**: `for task in queue` работает многократно
- **Ленивые фильтры**: `tasks_by_status()` и `tasks_by_priority()` — генераторы, не создают промежуточных коллекций
- **Совместимость со стандартными функциями**: `len()`, `sum()`, `max()`, `min()`, `sorted()`, `list()`, `filter()`, `map()`, `any()`, `all()`

### Пример использования
```python
from src.first_laba.task import Task
from src.third_laba.queue import TaskQueue

queue = TaskQueue()
queue.add_task(Task(id=1, description="Срочно", priority=5))
queue.add_task(Task(id=2, description="Обычная", priority=3))

# Повторный обход
print([t.id for t in queue])  # [1, 2]
print([t.id for t in queue])  # [1, 2]

# Ленивые фильтры
for task in queue.tasks_by_priority(4):
    print(f"Высокий приоритет: {task.id}")

# Стандартные функции
total_priority = sum(t.priority for t in queue)
```

## Структура проекта
```
Laba2Python2/
├── src/
│ ├── first_laba/ # Лабораторная работа №1
│ │ ├── init.py
│ │ ├── protocol.py # TaskSource и RawTask
│ │ ├── api_source.py # ApiStubSource
│ │ ├── file_source.py # FileTaskSource
│ │ └── random_source.py # RandomTaskSource
│ ├── second_laba/ # Лабораторная работа №2
│ │ ├── init.py
│ │ ├── task.py # Класс Task
│ │ ├── descriptors.py # Дескрипторы
│ │ └── runtime_check.py # Runtime-проверка протокола
│ └── third_laba/ # Лабораторная работа №3
│ ├── init.py
│ ├── queue.py # TaskQueue и TaskQueueIterator
│ └── demo.py # Демонстрация
├── tests/
│ ├── init.py
│ ├── test_descriptors.py # Тесты дескрипторов
│ ├── test_property.py # Тесты свойств Task
│ ├── test_sources.py # Тесты источников
│ ├── test_task_modification.py # Тесты модификации задач
│ ├── test_queue.py # Тесты очереди задач
│ └── test_integration.py # Интеграционные тесты
├── tasks.json # Пример файла с задачами
└── README.md
```

## Запуск всех тестов
````bash
cd C:\Users\Данила\данек\Laba2Python2
python -m unittest discover tests -v
````
## Интеграция компонентов

1. **Источник** (`FileTaskSource`, `RandomTaskSource`, `ApiStubSource`) генерирует `RawTask`
2. `RawTask` преобразуется в `Task` с валидацией через дескрипторы
3. `Task` добавляется в `TaskQueue`
4. `TaskQueue` предоставляет итерацию и ленивую фильтрацию

```python
source = FileTaskSource("tasks.json")
queue = TaskQueue()

for raw in source.get_tasks():
    task = Task(
        id=raw.id,
        description=str(raw.payload),
        priority=3
    )
    queue.add_task(task)

# Работа с очередью
for task in queue.tasks_by_status("created"):
    if task.is_ready:
        print(f"Готова к выполнению: {task.id}")
```

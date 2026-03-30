from datetime import datetime


class TaskValidationError(Exception):
    pass


class ValidatedDescriptor:
    def __set_name__(self, owner, name):
        self.private_name = '_' + name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private_name, None)

    def __set__(self, obj, value):
        self.validate(value)
        setattr(obj, self.private_name, value)

    def validate(self, value):
        raise NotImplementedError


class IdDescriptor(ValidatedDescriptor):
    def validate(self, value):
        if not isinstance(value, (int, str)):
            raise TaskValidationError(f"Id должен быть int или str, получен {type(value).__name__}")
        if isinstance(value, str) and not value.strip():
            raise TaskValidationError("Id не может быть пустой строкой")
        if isinstance(value, int) and value <= 0:
            raise TaskValidationError("Id должен быть положительным числом")


class DescriptionDescriptor(ValidatedDescriptor):
    def validate(self, value):
        if not isinstance(value, str):
            raise TaskValidationError(f"Описание должно быть строкой, получен {type(value).__name__}")
        if len(value.strip()) == 0:
            raise TaskValidationError("Описание не может быть пустым")
        if len(value) > 500:
            raise TaskValidationError("Описание не должно превышать 500 символов")


class PriorityDescriptor(ValidatedDescriptor):
    def validate(self, value):
        if not isinstance(value, int):
            raise TaskValidationError(f"Приоритет должен быть int, получен {type(value).__name__}")
        if not (1 <= value <= 5):
            raise TaskValidationError("Приоритет должен быть от 1 до 5")


class StatusDescriptor(ValidatedDescriptor):
    allowed_statuses = {'created', 'in_progress', 'completed', 'canceled'}

    def validate(self, value):
        if not isinstance(value, str):
            raise TaskValidationError(f"Статус должен быть str, получен {type(value).__name__}")
        if value not in self.allowed_statuses:
            raise TaskValidationError(f"Статус '{value}' недопустим")


class CreatedAtDescriptor(ValidatedDescriptor):
    def validate(self, value):
        if not isinstance(value, datetime):
            raise TaskValidationError(f"Время должно быть datetime, получен {type(value).__name__}")
        if value > datetime.now():
            raise TaskValidationError("Время создания не может быть в будущем")
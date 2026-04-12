from datetime import datetime
from .descriptors import (
    IdDescriptor, DescriptionDescriptor, PriorityDescriptor,
    StatusDescriptor, CreatedAtDescriptor
)


class Task:
    id = IdDescriptor()
    description = DescriptionDescriptor()
    priority = PriorityDescriptor()
    status = StatusDescriptor()
    created_at = CreatedAtDescriptor()

    def __init__(self, id: int | str, description: str, priority: int,
                 status: str = 'created', created_at: datetime = datetime.now()):
        self.id = id
        self.description = description
        self.priority = priority
        self.status = status
        self.created_at = created_at

    @property
    def is_ready(self) -> bool:
        return self.status == 'created' and self.priority >= 3

    @property
    def age(self) -> float:
        return (datetime.now() - self.created_at).total_seconds()

    def __repr__(self):
        return (f"Task(id={self.id!r}, description={self.description!r}, "
                f"priority={self.priority}, status={self.status!r}, "
                f"created_at={self.created_at.isoformat()})")
"""Модель данных проекта.

Содержит:
    - :class:`ProjectStatus` - перечисление статусов проекта
    - :class:`Project` - dataclass проекта

Статусы проекта:
    - ``planning`` - планирование
    - ``in_progress`` - в работе
    - ``on_hold`` - приостановлен
    - ``completed`` - завершён
    - ``cancelled`` - отменён

Пример:
    ::
    
        project = Project(
            project_name="EMS 2.0",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            status="in_progress"
        )
        print(project.duration_days)  # 365
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal
from enum import Enum


class ProjectStatus(Enum):
    """Статусы проекта."""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


VALID_PROJECT_STATUSES = tuple(s.value for s in ProjectStatus)
"""Допустимые строковые значения статуса проекта."""


@dataclass
class Project:
    """Модель проекта.

    Поля БД (таблица ``projects``):
        project_id, project_name, description, start_date, end_date,
        status, budget, department_id, created_at, updated_at

    Вспомогательные поля (не хранятся в БД):
        department_name — название отдела (из JOIN)
        employee_ids   — список ID сотрудников проекта
    """

    # --- поля таблицы ---
    project_id: Optional[int] = None
    project_name: str = ""
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "planning"
    budget: Optional[Decimal] = None
    department_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # --- вспомогательные поля (JOIN) ---
    department_name: Optional[str] = field(default=None, repr=False)
    employee_ids: List[int] = field(default_factory=list, repr=False)

    
    def __post_init__(self) -> None:
        """Проверяет корректность полей после создания."""
        self.project_name = self.project_name.strip() if self.project_name else ""
        if not self.project_name:
            raise ValueError("project_name не может быть пустым")
        if self.status not in VALID_PROJECT_STATUSES:
            raise ValueError(
                f"status должен быть одним из {VALID_PROJECT_STATUSES}, "
                f"получено: '{self.status}'"
            )
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError(
                f"end_date ({self.end_date}) не может быть раньше "
                f"start_date ({self.start_date})"
            )
        if self.budget is not None and self.budget < 0:
            raise ValueError(f"budget не может быть отрицательным: {self.budget}")

    
    @property
    def is_active(self) -> bool:
        """Проверяет, активен ли проект."""
        return self.status in (
            ProjectStatus.PLANNING.value,
            ProjectStatus.IN_PROGRESS.value,
        )

    @property
    def duration_days(self) -> Optional[int]:
        """Возвращает длительность проекта в днях."""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return None

    
    def to_dict(self) -> dict:
        """Конвертирует модель в словарь для сохранения в БД."""
        return {
            'project_id': self.project_id,
            'project_name': self.project_name,
            'description': self.description,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'status': self.status,
            'budget': float(self.budget) if self.budget is not None else None,
            'department_id': self.department_id,
        }

    @classmethod
    def from_db_row(cls, row: tuple) -> 'Project':
        """Создаёт экземпляр из строки БД.

        Ожидаемый порядок (SELECT * FROM projects)::

            0  project_id
            1  project_name
            2  description
            3  start_date
            4  end_date
            5  status
            6  budget
            7  department_id
            8  created_at
            9  updated_at
        """
        return cls(
            project_id=row[0],
            project_name=row[1],
            description=row[2] if len(row) > 2 else None,
            start_date=row[3] if len(row) > 3 else None,
            end_date=row[4] if len(row) > 4 else None,
            status=row[5] if len(row) > 5 and row[5] else 'planning',
            budget=(
                Decimal(str(row[6])) if len(row) > 6 and row[6] is not None
                else None
            ),
            department_id=row[7] if len(row) > 7 else None,
            created_at=row[8] if len(row) > 8 else None,
            updated_at=row[9] if len(row) > 9 else None,
        )

    
    _STATUS_MAP = {
        'planning': 'Планирование',
        'in_progress': 'В работе',
        'on_hold': 'Приостановлен',
        'completed': 'Завершён',
        'cancelled': 'Отменён',
    }

    def __str__(self) -> str:
        """Краткое строковое представление."""
        label = self._STATUS_MAP.get(self.status, self.status)
        parts = [f"[{self.project_id or '—'}] {self.project_name}"]
        parts.append(f"статус: {label}")
        if self.duration_days is not None:
            parts.append(f"{self.duration_days} дн.")
        return ' | '.join(parts)
    






    




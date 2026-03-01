"""Модель данных отдела.

Содержит dataclass :class:`Department` для представления
данных отдела компании.

Порядок столбцов в БД (таблица departments):
    department_id, department_name, manager_id,
    created_at, updated_at

Пример::

    dept = Department(
        department_name="Отдел разработки",
        manager_id=5
    )
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Department:
    """Модель отдела.

    Поля БД (таблица ``departments``):
        department_id, department_name, manager_id,
        created_at, updated_at

    Вспомогательные поля (не хранятся в БД):
        manager_name  — ФИО руководителя (из JOIN)
        employee_count — кол-во сотрудников (из COUNT)
    """

    # --- поля таблицы ---
    department_id: Optional[int] = None
    department_name: str = ""
    manager_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # --- вспомогательные поля (JOIN) ---
    manager_name: Optional[str] = field(default=None, repr=False)
    employee_count: int = field(default=0, repr=False)

    
    def __post_init__(self) -> None:
        """Проверяет корректность полей после создания."""
        self.department_name = self.department_name.strip() if self.department_name else ""
        if not self.department_name:
            raise ValueError("department_name не может быть пустым")

    
    def to_dict(self) -> dict:
        """Конвертирует модель в словарь для сохранения в БД."""
        return {
            'department_id': self.department_id,
            'department_name': self.department_name,
            'manager_id': self.manager_id,
        }

    @classmethod
    def from_db_row(cls, row: tuple) -> 'Department':
        """Создаёт экземпляр из строки БД.

        Ожидаемый порядок (SELECT * FROM departments)::

            0  department_id
            1  department_name
            2  manager_id
            3  created_at
            4  updated_at
        """
        return cls(
            department_id=row[0],
            department_name=row[1],
            manager_id=row[2] if len(row) > 2 else None,
            created_at=row[3] if len(row) > 3 else None,
            updated_at=row[4] if len(row) > 4 else None,
        )

    
    def __str__(self) -> str:
        """Краткое строковое представление."""
        parts = [f"[{self.department_id or '—'}] {self.department_name}"]
        if self.manager_name:
            parts.append(f"рук.: {self.manager_name}")
        if self.employee_count:
            parts.append(f"сотрудников: {self.employee_count}")
        return ' | '.join(parts)
    


"""Модель данных зарплаты.

Содержит dataclass :class:`Salary` для представления
записи о выплате зарплаты сотруднику.

Типы выплат:
    - ``salary``  — основная зарплата
    - ``bonus``   — премия
    - ``advance`` — аванс

Пример::

    from decimal import Decimal

    salary = Salary(
        employee_id=1,
        salary_amount=Decimal("50000.00"),
        payment_type="salary"
    )
    print(salary.formatted_amount)  # "50 000.00 ₽"
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional
from decimal import Decimal


PAYMENT_TYPES = ('salary', 'bonus', 'advance')
"""Допустимые типы выплат."""


@dataclass
class Salary:
    """Модель зарплатной записи.

    Поля БД (таблица ``salaries``):
        salary_id, employee_id, salary_amount, effective_date,
        payment_type, description, created_at, updated_at

    Вспомогательные поля (не хранятся в БД):
        employee_name  — ФИО сотрудника (из JOIN)
        department_name — название отдела (из JOIN)
    """

    # --- поля таблицы ---
    salary_id: Optional[int] = None
    employee_id: int = 0
    salary_amount: Decimal = Decimal("0.00")
    effective_date: Optional[date] = None
    payment_type: str = "salary"
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # --- вспомогательные поля (JOIN) ---
    employee_name: Optional[str] = field(default=None, repr=False)
    department_name: Optional[str] = field(default=None, repr=False)

    
    def __post_init__(self) -> None:
        """Проверяет корректность полей после создания."""
        if self.salary_amount < 0:
            raise ValueError(
                f"salary_amount не может быть отрицательной: "
                f"{self.salary_amount}"
            )
        if self.payment_type not in PAYMENT_TYPES:
            raise ValueError(
                f"payment_type должен быть одним из {PAYMENT_TYPES}, "
                f"получено: '{self.payment_type}'"
            )

   
    @property
    def formatted_amount(self) -> str:
        """Возвращает сумму в формате ``'50 000.00 ₽'``."""
        return f"{self.salary_amount:,.2f} ₽".replace(",", " ")

    
    def to_dict(self) -> dict:
        """Конвертирует модель в словарь для сохранения в БД.

        Возвращает только поля таблицы ``salaries`` (без служебных
        ``created_at`` / ``updated_at`` и вспомогательных JOIN-полей).
        """
        return {
            'salary_id': self.salary_id,
            'employee_id': self.employee_id,
            'salary_amount': float(self.salary_amount),
            'effective_date': self.effective_date,
            'payment_type': self.payment_type,
            'description': self.description,
        }

    @classmethod
    def from_db_row(cls, row: tuple) -> 'Salary':
        """Создаёт экземпляр из строки БД.

        Ожидаемый порядок столбцов (SELECT * FROM salaries)::

            0  salary_id
            1  employee_id
            2  salary_amount
            3  effective_date
            4  payment_type
            5  description
            6  created_at
            7  updated_at
        """
        return cls(
            salary_id=row[0],
            employee_id=row[1],
            salary_amount=(
                Decimal(str(row[2])) if row[2] else Decimal("0.00")
            ),
            effective_date=row[3] if len(row) > 3 else None,
            payment_type=row[4] if len(row) > 4 and row[4] else 'salary',
            description=row[5] if len(row) > 5 else None,
            created_at=row[6] if len(row) > 6 else None,
            updated_at=row[7] if len(row) > 7 else None,
        )

    
    def __str__(self) -> str:
        """Краткое строковое представление."""
        type_map = {
            'salary': 'Зарплата',
            'bonus': 'Премия',
            'advance': 'Аванс',
        }
        label = type_map.get(self.payment_type, self.payment_type)
        return (
            f"Зарплата #{self.salary_id}: "
            f"{label} {self.formatted_amount} "
            f"(сотрудник {self.employee_id}, "
            f"дата {self.effective_date})"
        )

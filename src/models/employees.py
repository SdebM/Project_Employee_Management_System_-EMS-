"""Модель данных сотрудника.

Содержит dataclass :class:`Employee` для представления
данных сотрудника в приложении.

Основные возможности:
    - Создание из строки БД: :meth:`Employee.from_db_row`
    - Конвертация в словарь: :meth:`Employee.to_dict`
    - Вычисляемые свойства: ``full_name``, ``age``
    - Валидация полей при создании: ``__post_init__``

Порядок столбцов в БД (таблица employees):
    employee_id, first_name, last_name, date_of_birth, gender,
    hire_date, department_id, phone, email, inn, snils, passport,
    status, created_at, updated_at

Пример:
    ::

        employee = Employee(
            first_name="Иван",
            last_name="Петров",
            date_of_birth=date(1990, 5, 15),
            hire_date=date.today()
        )
        print(employee.full_name)  # "Иван Петров"
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class Employee:
    """Модель сотрудника.

    Attributes:
        employee_id: Уникальный идентификатор сотрудника
        first_name: Имя
        last_name: Фамилия
        date_of_birth: Дата рождения
        gender: Пол ('М' или 'Ж')
        hire_date: Дата приема на работу
        department_id: ID отдела (опционально)
        phone: Телефон (опционально)
        email: Email (опционально)
        inn: ИНН (опционально, конфиденциально)
        snils: СНИЛС (опционально, конфиденциально)
        passport: Паспортные данные (опционально, конфиденциально)
        status: Статус ('active', 'inactive', 'fired')
        created_at: Дата создания записи
        updated_at: Дата последнего обновления
    """
    # --- Обязательные поля (NOT NULL в БД) ---
    employee_id: Optional[int] = None  # None до сохранения в БД
    first_name: str = ""
    last_name: str = ""
    date_of_birth: Optional[date] = None  # NOT NULL — Optional только до заполнения
    gender: str = "М"
    hire_date: Optional[date] = None  # NOT NULL — Optional только до заполнения

    # --- Опциональные поля ---
    department_id: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    inn: Optional[str] = None
    snils: Optional[str] = None
    passport: Optional[str] = None
    status: str = "active"

    # --- Служебные поля (генерируются БД) ---
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Дополнительные поля для отображения (не хранятся в БД)
    department_name: Optional[str] = field(default=None, repr=False)

    _VALID_GENDERS = ('М', 'Ж')
    _VALID_STATUSES = ('active', 'inactive', 'fired')

    def __post_init__(self):
        """Валидация и нормализация полей после инициализации."""
        self._validate_choice('gender', self.gender, self._VALID_GENDERS)
        self._validate_choice('status', self.status, self._VALID_STATUSES)

        # Нормализация строковых полей
        self.first_name = self.first_name.strip() if self.first_name else ""
        self.last_name = self.last_name.strip() if self.last_name else ""

    @staticmethod
    def _validate_choice(field_name: str, value: str, valid_values: tuple) -> None:
        """Проверяет, что значение входит в набор допустимых.

        Args:
            field_name: Название поля (для сообщения об ошибке).
            value: Проверяемое значение.
            valid_values: Кортеж допустимых значений.

        Raises:
            ValueError: Если значение не входит в допустимые.
        """
        if value not in valid_values:
            raise ValueError(
                f"Недопустимое значение поля '{field_name}': '{value}'. "
                f"Допустимые значения: {valid_values}"
            )

    @property
    def full_name(self) -> str:
        """Возвращает полное имя сотрудника."""
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self) -> Optional[int]:
        """Вычисляет возраст сотрудника."""
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def to_dict(self) -> dict:
        """Конвертирует модель в словарь для сохранения."""
        return {
            'employee_id': self.employee_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth,
            'gender': self.gender,
            'hire_date': self.hire_date,
            'department_id': self.department_id,
            'phone': self.phone,
            'email': self.email,
            'inn': self.inn,
            'snils': self.snils,
            'passport': self.passport,
            'status': self.status
        }

    def __str__(self) -> str:
        """Строковое представление сотрудника."""
        status_map = {'active': 'Активен', 'inactive': 'Неактивен', 'fired': 'Уволен'}
        parts = [f"[{self.employee_id or '—'}] {self.full_name}"]
        if self.department_name:
            parts.append(f"отдел: {self.department_name}")
        parts.append(f"статус: {status_map.get(self.status, self.status)}")
        return ' | '.join(parts)

    @classmethod
    def from_db_row(cls, row: tuple) -> 'Employee':
        """Создает экземпляр из строки БД.

        Args:
            row: Кортеж с данными в порядке столбцов таблицы employees:
                 (employee_id, first_name, last_name, date_of_birth, gender,
                  hire_date, department_id, phone, email, inn, snils, passport,
                  status, created_at, updated_at)

        Returns:
            Новый экземпляр Employee.

        Note:
            Метод устойчив к неполным кортежам — отсутствующие
            поля получат значения по умолчанию.
        """
        n = len(row)
        return cls(
            employee_id=row[0],
            first_name=row[1],
            last_name=row[2],
            date_of_birth=row[3],
            gender=row[4],
            hire_date=row[5],
            department_id=row[6] if n > 6 else None,
            phone=row[7] if n > 7 else None,
            email=row[8] if n > 8 else None,
            inn=row[9] if n > 9 else None,
            snils=row[10] if n > 10 else None,
            passport=row[11] if n > 11 else None,
            status=row[12] if n > 12 else 'active',
            created_at=row[13] if n > 13 else None,
            updated_at=row[14] if n > 14 else None,
        )

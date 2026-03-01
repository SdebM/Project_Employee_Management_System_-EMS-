"""Пакет моделей данных EMS.

Экспортирует основные модели:
    - :class:`Employee`   — сотрудник
    - :class:`Department` — отдел
    - :class:`Project`    — проект  (+ :class:`ProjectStatus`)
    - :class:`Salary`     — зарплата
    - :class:`User`       — пользователь (+ :class:`UserRole`)
"""

from .employees import Employee
from .departments import Department
from .projects import Project, ProjectStatus
from .salaries import Salary
from .users import User, UserRole

__all__ = [
    'Employee',
    'Department',
    'Project',
    'ProjectStatus',
    'Salary',
    'User',
    'UserRole',
]

"""Слой доступа к данным (Data Access Layer).

Репозитории инкапсулируют SQL-запросы и преобразование данных.

Доступные репозитории:
    - :class:`BaseRepository` - абстрактный базовый класс
    - :class:`EmployeeRepository` - сотрудники
    - :class:`DepartmentRepository` - отделы
    - :class:`ProjectRepository` - проекты
    - :class:`SalaryRepository` - зарплаты
    - :class:`UserRepository` - пользователи
"""

from .base_repository import BaseRepository
from .employee_repository import EmployeeRepository
from .department_repository import DepartmentRepository
from .project_repository import ProjectRepository
from .salary_repository import SalaryRepository
from .user_repository import UserRepository

__all__ = [
    'BaseRepository',
    'EmployeeRepository',
    'DepartmentRepository',
    'ProjectRepository',
    'SalaryRepository',
    'UserRepository'
]

"""Слой бизнес-логики (Business Logic Layer).

Сервисы содержат бизнес-правила, валидацию и проверку прав.

Доступные сервисы:
    - :class:`EmployeeService` - управление сотрудниками
    - :class:`DepartmentService` - управление отделами
    - :class:`ProjectService` - управление проектами
    - :class:`SalaryService` - управление зарплатами
    - :class:`AuthService` - аутентификация
    - :class:`ExportService` - экспорт в PDF/Excel
    - :class:`AnalyticsService` - аналитика
"""

from .employee_service import EmployeeService
from .department_service import DepartmentService
from .project_service import ProjectService
from .salary_service import SalaryService
from .auth_service import AuthService
from .export_service import ExportService
from .analytics_service import AnalyticsService

__all__ = [
    'EmployeeService',
    'DepartmentService',
    'ProjectService',
    'SalaryService',
    'AuthService',
    'ExportService',
    'AnalyticsService'
]

"""Вкладки приложения.

Содержит все вкладки интерфейса:
- EmployeesTabNew - управление сотрудниками
- DepartmentsTab - управление отделами
- ProjectsTab - управление проектами
- SalariesTab - управление зарплатами
- AnalyticsTab - аналитика и графики
"""

from .employees_tab import EmployeesTabNew
from .departments_tab import DepartmentsTab
from .projects_tab import ProjectsTab
from .salaries_tab import SalariesTab
from .analytics_tab import AnalyticsTab

__all__ = [
    'EmployeesTabNew',
    'DepartmentsTab',
    'ProjectsTab',
    'SalariesTab',
    'AnalyticsTab'
]

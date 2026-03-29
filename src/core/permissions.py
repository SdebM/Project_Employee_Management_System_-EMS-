"""Система контроля доступа и разрешений.

Содержит:
    - :class:`Permission` - перечисление разрешений
    - :func:`check_permission` - проверка прав доступа
    - :func:`get_user_permissions` - получение всех разрешений пользователя

Логика доступа:
    - ``admin`` - полный доступ ко всему (``'all'``)
    - ``manager`` - управление подчиненными и отчеты
    - ``employee`` - просмотр только своих данных

Пример:
    ::
    
        user = {'role': 'manager', 'department_id': 5}
        check_permission(user, Permission.VIEW_EMPLOYEES)  # OK
        check_permission(user, Permission.DELETE_EMPLOYEE)  # Raises PermissionDeniedError
"""

from enum import Enum
from typing import Dict, List, Set

from core.exceptions import PermissionDeniedError


class Permission(Enum):
    """Перечисление разрешений в системе."""
    
    # Права на сотрудников
    VIEW_EMPLOYEES = "view_employees"
    CREATE_EMPLOYEE = "create_employee"
    EDIT_EMPLOYEE = "edit_employee"
    DELETE_EMPLOYEE = "delete_employee"
    
    # Права на отделы
    VIEW_DEPARTMENTS = "view_departments"
    CREATE_DEPARTMENT = "create_department"
    EDIT_DEPARTMENT = "edit_department"
    DELETE_DEPARTMENT = "delete_department"
    
    # Права на проекты
    VIEW_PROJECTS = "view_projects"
    CREATE_PROJECT = "create_project"
    EDIT_PROJECT = "edit_project"
    DELETE_PROJECT = "delete_project"
    
    # Права на зарплаты
    VIEW_SALARIES = "view_salaries"
    EDIT_SALARIES = "edit_salaries"
    
    # Права на пользователей
    MANAGE_USERS = "manage_users"
    
    # Права на экспорт и аналитику
    EXPORT_DATA = "export_data"
    VIEW_ANALYTICS = "view_analytics"
    
    # Право на просмотр своих данных
    VIEW_OWN_DATA = "view_own_data"


# Матрица разрешений по ролям
ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    'admin': {'all'},  # Администратор имеет доступ ко всему
    'manager': {
        Permission.VIEW_EMPLOYEES.value,
        Permission.VIEW_DEPARTMENTS.value,
        Permission.VIEW_PROJECTS.value,
        Permission.VIEW_SALARIES.value,
        Permission.EXPORT_DATA.value,
        Permission.VIEW_ANALYTICS.value,
    },
    'employee': {
        Permission.VIEW_OWN_DATA.value,
    },
}


def get_user_permissions(user: dict) -> Set[str]:
    """Получает набор разрешений для пользователя.
    
    Args:
        user: Словарь с данными пользователя (поля: role, is_active, ...)
        
    Returns:
        Множество строк разрешений пользователя
        
    Raises:
        ValueError: Если роль пользователя не найдена
    """
    if not user.get('is_active', False):
        return set()
    
    role = user.get('role', 'employee')
    
    if role not in ROLE_PERMISSIONS:
        raise ValueError(f"Неизвестная роль: {role}")
    
    return ROLE_PERMISSIONS[role].copy()


def check_permission(user: dict, permission: Permission) -> bool:
    """Проверяет наличие разрешения у пользователя.
    
    Администратор имеет доступ ко всему (возвращает True на любое разрешение).
    
    Args:
        user: Словарь с данными пользователя (поля: role, is_active, ...)
        permission: Объект Permission для проверки
        
    Returns:
        True если пользователь имеет разрешение
        
    Raises:
        PermissionDeniedError: Если пользователь не имеет разрешение
        ValueError: Если роль пользователя неизвестна
        
    Пример:
        ::
        
            user = {'role': 'manager', 'is_active': True}
            check_permission(user, Permission.VIEW_EMPLOYEES)  # OK
    """
    if not user.get('is_active', False):
        raise PermissionDeniedError(
            f"Доступ запрещен: пользователь неактивен"
        )
    
    role = user.get('role', 'employee')
    
    if role not in ROLE_PERMISSIONS:
        raise ValueError(f"Неизвестная роль: {role}")
    
    user_permissions = ROLE_PERMISSIONS[role]
    
    # Администратор имеет доступ ко всему
    if 'all' in user_permissions:
        return True
    
    permission_value = permission.value
    
    if permission_value not in user_permissions:
        raise PermissionDeniedError(
            f"Доступ запрещен: требуется разрешение '{permission_value}', "
            f"роль '{role}' не имеет этого разрешения"
        )
    
    return True


def has_permission(user: dict, permission: Permission) -> bool:
    """Проверяет наличие разрешения (мягкая версия, без исключений).
    
    Args:
        user: Словарь с данными пользователя
        permission: Объект Permission для проверки
        
    Returns:
        True если пользователь имеет разрешение, иначе False
        
    Пример:
        ::
        
            if has_permission(user, Permission.DELETE_EMPLOYEE):
                # Показать кнопку удаления
            else:
                # Скрыть кнопку удаления
    """
    try:
        return check_permission(user, permission)
    except (PermissionDeniedError, ValueError):
        return False

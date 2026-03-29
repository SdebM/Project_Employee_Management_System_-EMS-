"""Сервис бизнес-логики для работы с отделами."""

from typing import List, Optional, Dict, Any
import logging

from models.departments import Department
from repositories.department_repository import DepartmentRepository
from core.database import Database
from core.permissions import Permission, check_permission
from core.exceptions import ValidationError, EntityNotFoundError


class DepartmentService:
    """Сервис для управления отделами."""

    def __init__(self, db: Database):
        self._db = db
        self._repository = DepartmentRepository(db)

    def get_departments(
        self, 
        user: dict, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Department]:
        """Получает список отделов с учетом прав доступа."""
        check_permission(user, Permission.VIEW_DEPARTMENTS)
        
        filters = filters or {}
        
        # Менеджер видит только свой отдел
        if user.get('role') == 'manager' and user.get('department_id'):
            return [self._repository.get_by_id(user['department_id'])]
        
        return self._repository.get_all(filters)

    def get_department_by_id(self, user: dict, department_id: int) -> Optional[Department]:
        """Получает отдел по ID."""
        check_permission(user, Permission.VIEW_DEPARTMENTS)
        return self._repository.get_by_id(department_id)

    def create_department(self, user: dict, data: Dict[str, Any]) -> int:
        """Создает новый отдел."""
        check_permission(user, Permission.CREATE_DEPARTMENT)
        
        self._validate_department_data(data)
        
        department = Department(
            department_name=data['department_name'],
            description=data.get('description'),
            manager_id=data.get('manager_id')
        )
        
        department_id = self._repository.create(department)
        
        self._db.log_action(
            user['id'],
            'CREATE_DEPARTMENT',
            f"Создан отдел: {department.department_name} (ID: {department_id})"
        )
        
        return department_id

    def update_department(
        self, 
        user: dict, 
        department_id: int, 
        data: Dict[str, Any]
    ) -> bool:
        """Обновляет данные отдела."""
        check_permission(user, Permission.EDIT_DEPARTMENT)
        
        department = self._repository.get_by_id(department_id)
        if not department:
            raise EntityNotFoundError("Отдел", department_id)
        
        self._validate_department_data(data, is_update=True)
        
        for field, value in data.items():
            if hasattr(department, field):
                setattr(department, field, value)
        
        result = self._repository.update(department)
        
        if result:
            self._db.log_action(
                user['id'],
                'UPDATE_DEPARTMENT',
                f"Обновлен отдел: {department.department_name} (ID: {department_id})"
            )
        
        return result

    def delete_department(self, user: dict, department_id: int) -> bool:
        """Удаляет отдел."""
        check_permission(user, Permission.DELETE_DEPARTMENT)
        
        department = self._repository.get_by_id(department_id)
        if not department:
            raise EntityNotFoundError("Отдел", department_id)
        
        # Проверка наличия сотрудников
        if department.employee_count > 0:
            raise ValidationError(
                f"Невозможно удалить отдел: в нем числится {department.employee_count} сотрудников"
            )
        
        result = self._repository.delete(department_id)
        
        if result:
            self._db.log_action(
                user['id'],
                'DELETE_DEPARTMENT',
                f"Удален отдел: {department.department_name} (ID: {department_id})"
            )
        
        return result

    def get_departments_for_dropdown(self) -> List[tuple]:
        """Возвращает список отделов для выпадающего списка."""
        return self._repository.get_for_dropdown()

    def get_department_statistics(self) -> List[Dict]:
        """Возвращает статистику по отделам."""
        return self._repository.get_department_statistics()

    def _validate_department_data(self, data: dict, is_update: bool = False) -> None:
        """Валидирует данные отдела."""
        if not is_update:
            if not data.get('department_name'):
                raise ValidationError("Название отдела обязательно", "department_name")
        
        if data.get('department_name') and len(data['department_name']) < 2:
            raise ValidationError("Название отдела слишком короткое", "department_name")

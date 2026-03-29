"""Репозиторий для работы с проектами."""

from typing import List, Optional, Dict, Any
from .base_repository import BaseRepository
from models.projects import Project
from core.database import Database


class ProjectRepository(BaseRepository[Project]):
    """Репозиторий для CRUD-операций с проектами."""

    def __init__(self, db: Database):
        super().__init__(db, 'projects')

    def _map_to_entity(self, row: tuple) -> Project:
        """Преобразует строку БД в объект Project."""
        return Project.from_db_row(row)

    def _entity_to_params(self, entity: Project) -> tuple:
        """Преобразует Project в параметры SQL."""
        return (
            entity.project_name,
            entity.description,
            entity.start_date,
            entity.end_date,
            entity.status,
            entity.budget,
            entity.department_id
        )

    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Project]:
        """Получает список проектов с фильтрацией.
        
        Args:
            filters: Фильтры поиска:
                - project_name (str): Поиск по названию (ILIKE)
                - status (str): Фильтр по статусу
                - department_id (int): Фильтр по отделу
                
        Returns:
            Список объектов Project
        """
        query = """
            SELECT 
                p.project_id, p.project_name, p.description,
                p.start_date, p.end_date, p.status,
                p.budget, p.department_id,
                p.created_at, p.updated_at,
                d.department_name
            FROM projects p
            LEFT JOIN departments d ON p.department_id = d.department_id
            WHERE 1=1
        """
        params = []

        if filters:
            if filters.get('project_name'):
                query += " AND p.project_name ILIKE %s"
                params.append(f"%{filters['project_name']}%")
            if filters.get('status'):
                query += " AND p.status = %s"
                params.append(filters['status'])
            if filters.get('department_id'):
                query += " AND p.department_id = %s"
                params.append(filters['department_id'])

        query += " ORDER BY p.start_date DESC"

        rows = self._db.fetch_all(query, tuple(params))
        projects = []
        for row in rows:
            proj = Project.from_db_row(row[:10])
            proj.department_name = row[10] if len(row) > 10 else None
            projects.append(proj)
        return projects

    def get_by_id(self, project_id: int) -> Optional[Project]:
        """Получает проект по ID."""
        query = """
            SELECT 
                p.project_id, p.project_name, p.description,
                p.start_date, p.end_date, p.status,
                p.budget, p.department_id,
                p.created_at, p.updated_at,
                d.department_name
            FROM projects p
            LEFT JOIN departments d ON p.department_id = d.department_id
            WHERE p.project_id = %s
        """
        row = self._db.fetch_one(query, (project_id,))
        if row:
            proj = Project.from_db_row(row[:10])
            proj.department_name = row[10] if len(row) > 10 else None
            return proj
        return None

    def create(self, project: Project) -> int:
        """Создает новый проект."""
        query = """
            INSERT INTO projects (
                project_name, description, start_date, end_date,
                status, budget, department_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING project_id
        """
        params = self._entity_to_params(project)
        result = self._db.execute_query(query, params, return_result=True)
        return result[0][0] if result else None

    def update(self, project: Project) -> bool:
        """Обновляет данные проекта."""
        query = """
            UPDATE projects SET
                project_name = %s, description = %s,
                start_date = %s, end_date = %s,
                status = %s, budget = %s, department_id = %s,
                updated_at = NOW()
            WHERE project_id = %s
        """
        params = self._entity_to_params(project) + (project.project_id,)
        return self._db.execute_query(query, params)

    def delete(self, project_id: int) -> bool:
        """Удаляет проект."""
        query = "DELETE FROM projects WHERE project_id = %s"
        return self._db.execute_query(query, (project_id,))

    def count_by_status(self) -> List[tuple]:
        """Возвращает количество проектов по статусам.
        
        Returns:
            Список кортежей (status, count)
        """
        query = """
            SELECT status, COUNT(*) as count
            FROM projects
            GROUP BY status
            ORDER BY count DESC
        """
        return self._db.fetch_all(query)

    def get_active_projects(self) -> List[Project]:
        """Возвращает активные проекты."""
        return self.get_all({'status': 'in_progress'})

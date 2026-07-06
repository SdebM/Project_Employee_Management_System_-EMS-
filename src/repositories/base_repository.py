"""Базовый класс репозитория.

Содержит абстрактный класс :class:`BaseRepository`, который
определяет интерфейс CRUD-операций для всех репозиториев.

Репозитории инкапсулируют всю логику доступа к данным,
отделяя её от бизнес-логики в сервисах.

Основные методы:
    - :meth:`get_all` - получение всех записей с фильтрацией
    - :meth:`get_by_id` - получение по ID
    - :meth:`count` - подсчёт записей
    - :meth:`exists` - проверка существования


"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional, Any
import re
from core.database import Database

T = TypeVar('T')
_VALID_COLUMN_RE = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_.]*$')

def _validate_column_name(name: str) -> str:
    if not _VALID_COLUMN_RE.match(name):
        raise ValueError(f"Недопустимое имя колонки: {name}")
    return name

class BaseRepository(ABC, Generic[T]):
    """Абстрактный базовый репозиторий с поддержкой мягкого удаления."""
    
    _table_name: str
    
    # --- Настройки мягкого удаления (Soft Delete) ---
    soft_delete_column: Optional[str] = None  # Имя колонки (например, 'is_active' или 'status')
    soft_delete_value: Optional[Any] = None   # Значение "удалено" (например, False или 'fired')
    active_value: Optional[Any] = None        # Значение "активно" (например, True или 'active')

    def __init__(self, db: Database, table_name: str):
        self._db = db
        self._table_name = table_name

    @abstractmethod
    def _map_to_entity(self, row: dict) -> T: pass

    @abstractmethod
    def _entity_to_params(self, entity: T) -> tuple: pass

    def get_all(self, filters: Optional[dict] = None) -> List[T]:
        """Получает записи с фильтрацией. 
        Автоматически исключает мягко удаленные записи, если не указан флаг show_deleted."""
        query = f"SELECT * FROM {self._table_name} WHERE 1=1"
        params = []

        filters = filters or {}
        if self.soft_delete_column and not filters.pop('show_deleted', False):
            query += f" AND {self.soft_delete_column} = %s"
            params.append(self.active_value)

        if filters:
            for field, value in filters.items():
                if value is not None:
                    field = _validate_column_name(field)
                    if isinstance(value, str) and '%' in value:
                        query += f" AND {field} ILIKE %s"
                    else:
                        query += f" AND {field} = %s"
                    params.append(value)

        rows = self._db.fetch_all(query, tuple(params))
        return [self._map_to_entity(row) for row in rows]

    def get_by_id(self, entity_id: int, id_column: str = None) -> Optional[T]:
        if id_column is None:
            base_name = self._table_name.rstrip('s')
            id_column = f"{base_name}_id"
        query = f"SELECT * FROM {self._table_name} WHERE {id_column} = %s"
        row = self._db.fetch_one(query, (entity_id,))
        return self._map_to_entity(row) if row else None

    def count(self, filters: Optional[dict] = None) -> int:
        query = f"SELECT COUNT(*) FROM {self._table_name} WHERE 1=1"
        params = []
        filters = filters or {}
        
        if self.soft_delete_column and not filters.pop('show_deleted', False):
            query += f" AND {self.soft_delete_column} = %s"
            params.append(self.active_value)

        if filters:
            for field, value in filters.items():
                if value is not None:
                    field = _validate_column_name(field)
                    query += f" AND {field} = %s"
                    params.append(value)

        result = self._db.fetch_one(query, tuple(params))
        return result['count'] if result else 0

    def delete(self, entity_id: int, id_column: str = None) -> bool:
        """Удаляет запись. Если настроен Soft Delete, делает UPDATE, иначе DELETE."""
        if id_column is None:
            base_name = self._table_name.rstrip('s')
            id_column = f"{base_name}_id"

        if self.soft_delete_column:
            # ИЗМЕНЕНИЕ: Мягкое удаление (UPDATE)
            query = f"UPDATE {self._table_name} SET {self.soft_delete_column} = %s WHERE {id_column} = %s"
            return self._db.execute_query(query, (self.soft_delete_value, entity_id))
        else:
            # Жесткое удаление (для справочников, где это разрешено)
            query = f"DELETE FROM {self._table_name} WHERE {id_column} = %s"
            return self._db.execute_query(query, (entity_id,))
        

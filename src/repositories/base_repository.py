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

# Регулярное выражение для проверки допустимых имён колонок
_VALID_COLUMN_RE = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_.]*$')


def _validate_column_name(name: str) -> str:
    """Проверяет имя колонки на допустимость (защита от SQL-инъекции).
    
    Args:
        name: Имя колонки
        
    Returns:
        Имя колонки, если оно допустимо
        
    Raises:
        ValueError: Если имя колонки содержит недопустимые символы
    """
    if not _VALID_COLUMN_RE.match(name):
        raise ValueError(f"Недопустимое имя колонки: {name}")
    return name


class BaseRepository(ABC, Generic[T]):
    """Абстрактный базовый репозиторий.
    
    Определяет интерфейс CRUD-операций для всех репозиториев.
    
    Attributes:
        _db: Объект подключения к БД
        _table_name: Имя таблицы в БД
    """

    def __init__(self, db: Database, table_name: str):
        """
        Args:
            db: Объект Database для работы с БД
            table_name: Имя таблицы сущности
        """
        self._db = db
        self._table_name = table_name

    @abstractmethod
    def _map_to_entity(self, row: tuple) -> T:
        """Преобразует строку БД в объект сущности.
        
        Args:
            row: Кортеж данных из БД
            
        Returns:
            Объект сущности
        """
        pass

    @abstractmethod
    def _entity_to_params(self, entity: T) -> tuple:
        """Преобразует сущность в параметры для SQL.
        
        Args:
            entity: Объект сущности
            
        Returns:
            Кортеж параметров
        """
        pass

    def get_all(self, filters: Optional[dict] = None) -> List[T]:
        """Получает все записи с опциональной фильтрацией.
        
        Args:
            filters: Словарь фильтров {поле: значение}
            
        Returns:
            Список сущностей
        """
        query = f"SELECT * FROM {self._table_name} WHERE 1=1"
        params = []

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
        """Получает сущность по ID.
        
        Args:
            entity_id: Идентификатор записи
            id_column: Название колонки ID (по умолчанию: table_name + '_id')
            
        Returns:
            Сущность или None если не найдена
        """
        if id_column is None:
            # Убираем 's' в конце если есть (employees -> employee_id)
            base_name = self._table_name.rstrip('s')
            id_column = f"{base_name}_id"

        query = f"SELECT * FROM {self._table_name} WHERE {id_column} = %s"
        row = self._db.fetch_one(query, (entity_id,))
        return self._map_to_entity(row) if row else None

    def count(self, filters: Optional[dict] = None) -> int:
        """Подсчитывает количество записей.
        
        Args:
            filters: Словарь фильтров
            
        Returns:
            Количество записей
        """
        query = f"SELECT COUNT(*) FROM {self._table_name} WHERE 1=1"
        params = []

        if filters:
            for field, value in filters.items():
                if value is not None:
                    field = _validate_column_name(field)
                    query += f" AND {field} = %s"
                    params.append(value)

        result = self._db.fetch_one(query, tuple(params))
        return result[0] if result else 0

    def exists(self, entity_id: int, id_column: str = None) -> bool:
        """Проверяет существование записи.
        
        Args:
            entity_id: Идентификатор записи
            id_column: Название колонки ID
            
        Returns:
            True если запись существует
        """
        if id_column is None:
            base_name = self._table_name.rstrip('s')
            id_column = f"{base_name}_id"

        query = f"SELECT 1 FROM {self._table_name} WHERE {id_column} = %s LIMIT 1"
        result = self._db.fetch_one(query, (entity_id,))
        return result is not None

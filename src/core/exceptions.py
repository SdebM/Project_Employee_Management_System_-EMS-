"""Кастомные исключения приложения.

Модуль содержит иерархию исключений для обработки ошибок:

.. code-block:: text

    AppException (базовый класс)
    ├── DatabaseError - ошибки БД
    ├── ValidationError - ошибки валидации
    ├── AuthenticationError - ошибки аутентификации
    ├── PermissionDeniedError - ошибки доступа
    ├── EntityNotFoundError - сущность не найдена
    └── DuplicateEntityError - дубликат сущности


"""


class AppException(Exception):
    """Базовое исключение приложения.
    
    Все кастомные исключения наследуются от этого класса.
    
    Attributes:
        message: Краткое описание ошибки
        details: Дополнительная информация об ошибке
    
    Args:
        message: Текст сообщения
        details: Дополнительные детали (опционально)
    """
    
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class DatabaseError(AppException):
    """Ошибки работы с базой данных.
    
    Возникает при ошибках подключения, выполнения запросов
    или транзакций в PostgreSQL.
    """
    pass


class ValidationError(AppException):
    """Ошибки валидации данных.
    
    Возникает при некорректных входных данных.
    
    Attributes:
        field: Имя поля, в котором ошибка
    
    Args:
        message: Описание ошибки
        field: Имя поля (опционально)
        details: Дополнительные детали (опционально)
    """
    
    def __init__(self, message: str, field: str = None, details: str = None):
        self.field = field
        super().__init__(message, details)


class AuthenticationError(AppException):
    """Ошибки аутентификации.
    
    Возникает при отсутствии или неверных учетных данных.
    """
    pass


class PermissionDeniedError(AppException):
    """Ошибки доступа/авторизации.
    
    Возникает когда пользователь не имеет прав на выполнение операции.
    """
    pass


class EntityNotFoundError(AppException):
    """Сущность не найдена.
    
    Возникает при попытке получить несуществующую сущность.
    
    Attributes:
        entity_type: Тип сущности (например 'Сотрудник')
        entity_id: ID сущности
    
    Args:
        entity_type: Тип сущности
        entity_id: ID сущности (опционально)
        details: Дополнительные детали (опционально)
    """
    
    def __init__(self, entity_type: str, entity_id = None, details: str = None):
        self.entity_type = entity_type
        self.entity_id = entity_id
        if entity_id is not None:
            message = f"{entity_type} с ID {entity_id} не найден(а)"
        else:
            message = f"{entity_type} не найден(а)"
        super().__init__(message, details)


class DuplicateEntityError(AppException):
    """Дубликат сущности.
    
    Возникает при попытке создать сущность с уникальным полем,
    которое уже существует.
    
    Attributes:
        entity_type: Тип сущности
        field: Поле с дубликатом
    
    Args:
        entity_type: Тип сущности
        field: Уникальное поле (опционально)
        details: Дополнительные детали (опционально)
    """
    
    def __init__(self, entity_type: str, field: str = None, details: str = None):
        self.entity_type = entity_type
        self.field = field
        if field:
            message = f"{entity_type} с таким '{field}' уже существует"
        else:
            message = f"{entity_type} с такими параметрами уже существует"
        super().__init__(message, details)






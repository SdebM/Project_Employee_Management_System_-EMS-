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

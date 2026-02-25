"""Конфигурация приложения.

Этот модуль содержит классы для управления конфигурацией:

- :class:`DatabaseConfig` - настройки подключения к PostgreSQL
- :class:`AppConfig` - общие настройки приложения
- :class:`Config` - главный класс конфигурации (Singleton)

Переменные окружения:
    - ``DB_HOST`` - хост БД (по умолчанию: localhost)
    - ``DB_PORT`` - порт БД (по умолчанию: 5432)
    - ``DB_NAME`` - имя базы данных
    - ``DB_USER`` - пользователь БД
    - ``DB_PASSWORD`` - пароль БД
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv
load_dotenv()

@dataclass
class DatabaseConfig:
    """Настройки подключения к базе данных PostgreSQL.
    
    Attributes:
        dbname: Имя базы данных
        user: Имя пользователя
        password: Пароль
        host: Хост сервера
        port: Порт подключения
    
    Example:
        ::
        
            # Загрузка из переменных окружения
            config = DatabaseConfig.from_env()
            
            # Или явное создание
            config = DatabaseConfig(
                dbname='mydb',
                user='admin',
                password='secret'
            )
    """
    dbname: str = "empls_db"
    user: str = "postgres"
    password: str = "0123"
    host: str = "localhost"
    port: str = "5432"

    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Загружает конфигурацию из переменных окружения.
        
        Использует переменные DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT.
        Если переменная не задана, используется значение по умолчанию.
        
        Returns:
            Новый экземпляр DatabaseConfig
        """
        return cls(
            dbname=os.getenv('DB_NAME', cls.dbname),
            user=os.getenv('DB_USER', cls.user),
            password=os.getenv('DB_PASSWORD', cls.password),
            host=os.getenv('DB_HOST', cls.host),
            port=os.getenv('DB_PORT', cls.port)
        )


@dataclass
class AppConfig:
    """Общие настройки приложения.
    
    Attributes:
        app_name: Название приложения
        version: Текущая версия
        debug: Режим отладки
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR)
        log_file_pattern: Шаблон имени файла логов
    """
    app_name: str = "Employee Systems"
    version: str = "1.01"
    debug: bool = False
    log_level: str = "INFO"
    log_file_pattern: str = "app_errors_{date}.log"


class Config:
    """Главный класс конфигурации приложения.
    
    Реализует паттерн Singleton для единой точки доступа к настройкам.
    """
    _instance: Optional['Config'] = None

    def __init__(self):
        self.database = DatabaseConfig.from_env()
        self.app = AppConfig()

    @classmethod
    def get_instance(cls) -> 'Config':
        """Возвращает единственный экземпляр конфигурации."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        """Сбрасывает экземпляр (для тестов)."""
        cls._instance = None

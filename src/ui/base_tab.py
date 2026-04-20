"""Базовый класс для вкладок приложения.

Содержит класс :class:`BaseTab`, который предоставляет
общий функционал для всех вкладок:

- Контроль доступа на основе роли
- Экспорт данных в PDF/Excel
- Отложенный поиск (debounce)
- Диалоги сообщений

Паттерн Template Method:
    Наследники должны реализовать:
    
    - :meth:`init_ui` - создание интерфейса
    - :meth:`load_data` - загрузка данных

Пример создания вкладки:
    ::
    
        class EmployeesTab(BaseTab):
            def __init__(self, service, user):
                super().__init__(service, user)
                self.init_ui()
                self.load_data()
            
            def init_ui(self):
                # создание виджетов
                pass
            
            def load_data(self):
                # загрузка данных из сервиса
                pass

См. также:
    - :mod:`ui.widgets` - переиспользуемые виджеты
    - :mod:`core.permissions` - контроль доступа
"""

from typing import Dict, List, Optional, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QMessageBox, QLineEdit
)
from PyQt6.QtCore import QTimer

from core.permissions import PermissionManager, Permission
from services.export_service import ExportService


class BaseTab(QWidget):
    """Базовый класс для всех вкладок приложения.
    
    Предоставляет общий функционал:
    - Настройка контроля доступа
    - Экспорт данных
    - Отложенный поиск
    - Обновление данных
    
    Наследники должны реализовать:
    - init_ui(): Создание интерфейса
    - load_data(): Загрузка данных
    
    Пример использования:
        class EmployeesTab(BaseTab):
            def __init__(self, service, user):
                super().__init__(service, user)
                self.init_ui()
                self.load_data()
    """
    
    # Маппинг кнопок на разрешения (переопределять в наследниках)
    BUTTON_PERMISSIONS: Dict[str, str] = {
        'btn_add': Permission.CREATE_EMPLOYEE,
        'btn_edit': Permission.EDIT_EMPLOYEE,
        'btn_delete': Permission.DELETE_EMPLOYEE,
        'btn_export_excel': Permission.EXPORT_DATA,
        'btn_export_pdf': Permission.EXPORT_DATA,
    }

    def __init__(self, service: Any, user: dict):
        """
        Args:
            service: Сервис бизнес-логики для данной вкладки
            user: Данные текущего пользователя
        """
        super().__init__()
        self.service = service
        self.user = user
        self.permission_manager = PermissionManager(user)
        
        # Таймер для отложенного поиска
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.load_data)
        
        # Основные виджеты (инициализируются в наследниках)
        self.main_table: Optional[QTableWidget] = None
        self.btn_add: Optional[QPushButton] = None
        self.btn_edit: Optional[QPushButton] = None
        self.btn_delete: Optional[QPushButton] = None
        self.btn_export_excel: Optional[QPushButton] = None
        self.btn_export_pdf: Optional[QPushButton] = None
        self.btn_refresh: Optional[QPushButton] = None

    def init_ui(self):
        """Инициализирует интерфейс вкладки.
        
        Должен быть переопределен в наследниках.
        """
        raise NotImplementedError("Метод init_ui() должен быть реализован")

    def load_data(self):
        """Загружает данные для отображения.
        
        Должен быть переопределен в наследниках.
        """
        raise NotImplementedError("Метод load_data() должен быть реализован")

    def setup_access_control(self):
        """Настраивает видимость элементов на основе прав пользователя."""
        for btn_name, permission in self.BUTTON_PERMISSIONS.items():
            button = getattr(self, btn_name, None)
            if button:
                has_permission = self.permission_manager.has_permission(permission)
                button.setVisible(has_permission)

    def trigger_search(self):
        """Запускает отложенный поиск (300мс задержка)."""
        self.search_timer.stop()
        self.search_timer.start(300)

    def export_to_pdf(self):
        """Экспортирует данные таблицы в PDF."""
        if not self.main_table:
            return
        
        default_name = self._get_export_filename('pdf')
        title = self._get_export_title()
        
        ExportService.export_to_pdf(
            self, self.main_table, default_name, title
        )

    def export_to_excel(self):
        """Экспортирует данные таблицы в Excel."""
        if not self.main_table:
            return
        
        default_name = self._get_export_filename('xlsx')
        sheet_name = self._get_export_title()
        
        ExportService.export_to_excel(
            self, self.main_table, default_name, sheet_name
        )

    def show_error(self, title: str, message: str):
        """Показывает диалог ошибки."""
        QMessageBox.critical(self, title, message)

    def show_warning(self, title: str, message: str):
        """Показывает предупреждение."""
        QMessageBox.warning(self, title, message)

    def show_info(self, title: str, message: str):
        """Показывает информационное сообщение."""
        QMessageBox.information(self, title, message)

    def confirm_action(self, title: str, message: str) -> bool:
        """Показывает диалог подтверждения.
        
        Returns:
            True если пользователь подтвердил действие
        """
        reply = QMessageBox.question(
            self, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes

    def get_selected_row_id(self, id_column: int = 0) -> Optional[int]:
        """Возвращает ID выбранной строки в таблице.
        
        Args:
            id_column: Индекс колонки с ID (по умолчанию 0)
            
        Returns:
            ID выбранной строки или None
        """
        if not self.main_table:
            return None
        
        selected_row = self.main_table.currentRow()
        if selected_row == -1:
            self.show_warning("Внимание", "Выберите запись в таблице")
            return None
        
        item = self.main_table.item(selected_row, id_column)
        if item:
            try:
                return int(item.text())
            except ValueError:
                return None
        return None

    def _get_export_filename(self, extension: str) -> str:
        """Возвращает имя файла для экспорта.
        
        Переопределить в наследниках для кастомных имён.
        """
        return f"export.{extension}"

    def _get_export_title(self) -> str:
        """Возвращает заголовок документа для экспорта.
        
        Переопределить в наследниках.
        """
        return "Экспорт данных"

    def _create_control_panel(self) -> QHBoxLayout:
        """Создает стандартную панель управления с кнопками."""
        panel = QHBoxLayout()
        
        self.btn_add = QPushButton("Добавить")
        self.btn_edit = QPushButton("Редактировать")
        self.btn_delete = QPushButton("Удалить")
        
        panel.addWidget(self.btn_add)
        panel.addWidget(self.btn_edit)
        panel.addWidget(self.btn_delete)
        panel.addStretch()
        
        return panel

    def _create_export_panel(self) -> QHBoxLayout:
        """Создает панель экспорта."""
        panel = QHBoxLayout()
        
        self.btn_export_excel = QPushButton("Экспорт в Excel")
        self.btn_export_pdf = QPushButton("Экспорт в PDF")
        
        panel.addStretch()
        panel.addWidget(self.btn_export_excel)
        panel.addWidget(self.btn_export_pdf)
        
        # Подключение сигналов
        self.btn_export_excel.clicked.connect(self.export_to_excel)
        self.btn_export_pdf.clicked.connect(self.export_to_pdf)
        
        return panel

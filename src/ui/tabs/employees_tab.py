"""Вкладка сотрудников.

Пример реализации вкладки с разделением слоёв:
- UI отвечает только за отображение
- Бизнес-логика в EmployeeService
- Данные через EmployeeRepository
"""

from typing import Optional, List
from datetime import datetime, date
import logging

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLineEdit, QComboBox, QLabel,
    QMessageBox, QDialog, QFormLayout, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon

from ui.base_tab import BaseTab
from ui.widgets import DataTableWidget, SearchPanel, ExportPanel, ControlPanel
from services.employee_service import EmployeeService
from services.department_service import DepartmentService
from core.permissions import Permission
from core.exceptions import ValidationError, EntityNotFoundError, PermissionDeniedError
from models.employees import Employee
from styles import TABLE_STYLES, BUTTON_STYLES
from utils.formatters import Formatters



class EmployeeDialog(QDialog):
    def __init__(self, parent, departments, employee: Optional[Employee] = None):
        super().__init__(parent)
        self.setWindowTitle("Добавить сотрудника" if not employee else "Редактировать сотрудника")
        self.layout = QFormLayout(self)

        self.first_name = QLineEdit()
        self.last_name = QLineEdit()
        self.date_of_birth = QLineEdit()
        self.date_of_birth.setPlaceholderText("дд.мм.гггг")
        self.gender = QComboBox()
        self.gender.addItems(["М", "Ж"])
        self.hire_date = QLineEdit()
        self.hire_date.setPlaceholderText("дд.мм.гггг")
        self.department = QComboBox()
        self.department.addItem("Не указан", None)
        for d_id, d_name in departments:
            self.department.addItem(d_name, d_id)
            
        self.phone = QLineEdit()
        self.email = QLineEdit()
        self.inn = QLineEdit()
        self.snils = QLineEdit()
        self.passport = QLineEdit()

        self.layout.addRow("Имя:", self.first_name)
        self.layout.addRow("Фамилия:", self.last_name)
        self.layout.addRow("Дата рождения:", self.date_of_birth)
        self.layout.addRow("Пол:", self.gender)
        self.layout.addRow("Дата приема:", self.hire_date)
        self.layout.addRow("Отдел:", self.department)
        self.layout.addRow("Телефон:", self.phone)
        self.layout.addRow("Email:", self.email)
        self.layout.addRow("ИНН:", self.inn)
        self.layout.addRow("СНИЛС:", self.snils)
        self.layout.addRow("Паспорт:", self.passport)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addRow(buttons)

        if employee:
            self._load_data(employee)

    def _load_data(self, emp: Employee):
        self.first_name.setText(emp.first_name)
        self.last_name.setText(emp.last_name)
        self.date_of_birth.setText(Formatters.format_date(emp.date_of_birth))
        self.gender.setCurrentText(emp.gender or "М")
        self.hire_date.setText(Formatters.format_date(emp.hire_date))
        if emp.department_id:
            for i in range(self.department.count()):
                if self.department.itemData(i) == emp.department_id:
                    self.department.setCurrentIndex(i)
                    break
        self.phone.setText(emp.phone or "")
        self.email.setText(emp.email or "")
        self.inn.setText(emp.inn or "")
        self.snils.setText(emp.snils or "")
        self.passport.setText(emp.passport or "")

    def get_data(self):
        data = {
            'first_name': self.first_name.text().strip(),
            'last_name': self.last_name.text().strip(),
            'gender': self.gender.currentText(),
            'department_id': self.department.currentData(),
            'phone': self.phone.text().strip() or None,
            'email': self.email.text().strip() or None,
            'inn': self.inn.text().strip() or None,
            'snils': self.snils.text().strip() or None,
            'passport': self.passport.text().strip() or None,
        }
        def _parse(d):
            if not d: return None
            for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
                try: return datetime.strptime(d, fmt).date()
                except Exception: continue
            return None

        dob = _parse(self.date_of_birth.text().strip())
        hd = _parse(self.hire_date.text().strip())
        if dob: data['date_of_birth'] = dob
        if hd: data['hire_date'] = hd
        return data


class EmployeesTabNew(BaseTab):
    """Вкладка управления сотрудниками (новая архитектура).
    
    Использует:
    - EmployeeService для бизнес-логики
    - BaseTab для общего функционала
    - Компоненты из ui.widgets
    """
    
    BUTTON_PERMISSIONS = {
        'btn_add': Permission.CREATE_EMPLOYEE,
        'btn_edit': Permission.EDIT_EMPLOYEE,
        'btn_delete': Permission.DELETE_EMPLOYEE,
        'btn_export_excel': Permission.EXPORT_DATA,
        'btn_export_pdf': Permission.EXPORT_DATA,
    }

    def __init__(
        self, 
        employee_service: EmployeeService,
        department_service: DepartmentService,
        user: dict
    ):
        """
        Args:
            employee_service: Сервис работы с сотрудниками
            department_service: Сервис работы с отделами
            user: Данные текущего пользователя
        """
        super().__init__(employee_service, user)
        self.employee_service = employee_service
        self.department_service = department_service
        
        self.init_ui()
        self.setup_access_control()
        self.load_data()

    def init_ui(self):
        """Инициализирует интерфейс вкладки."""
        main_layout = QVBoxLayout()
        main_layout.addLayout(self._create_control_panel())
        main_layout.addLayout(self._create_search_panel())
        self.main_table = self._create_table()
        main_layout.addWidget(self.main_table)
        main_layout.addLayout(self._create_bottom_panel())
        self.setLayout(main_layout)
        self._connect_signals()

    def _create_control_panel(self) -> QHBoxLayout:
        """Создает панель с кнопками управления."""
        panel = QHBoxLayout()
        self.btn_add = QPushButton("Добавить")
        self.btn_edit = QPushButton("Редактировать")
        self.btn_delete = QPushButton("Удалить")
        for btn in [self.btn_add, self.btn_edit, self.btn_delete]:
            btn.setStyleSheet(BUTTON_STYLES.get("secondary", ""))
        self.btn_add.setStyleSheet(BUTTON_STYLES.get("primary", ""))
        panel.addWidget(self.btn_add)
        panel.addWidget(self.btn_edit)
        panel.addWidget(self.btn_delete)
        panel.addStretch()
        return panel

    def _create_search_panel(self) -> QHBoxLayout:
        """Создает панель поиска."""
        panel = QHBoxLayout()
        self.search_first_name = QLineEdit()
        self.search_first_name.setPlaceholderText("Имя")
        self.search_last_name = QLineEdit()
        self.search_last_name.setPlaceholderText("Фамилия")
        self.department_combo = QComboBox()
        self._load_departments()
        panel.addWidget(QLabel("Фильтры:"))
        panel.addWidget(self.search_first_name)
        panel.addWidget(self.search_last_name)
        panel.addWidget(self.department_combo)
        panel.addStretch()
        return panel

    def _create_table(self) -> QTableWidget:
        """Создает таблицу сотрудников."""
        table = QTableWidget()
        columns = ["ID", "Имя", "Фамилия", "Дата рождения", "Пол", "Дата приема", "Отдел", "Статус", "Дата создания", "Дата обновления"]
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        header = table.horizontalHeader()
        header.setStretchLastSection(True)
        table.setStyleSheet(TABLE_STYLES.get("base", ""))
        header.setStyleSheet(TABLE_STYLES.get("header", ""))
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setMinimumHeight(400)
        return table

    def _create_bottom_panel(self) -> QHBoxLayout:
        """Создает нижнюю панель с кнопками."""
        panel = QHBoxLayout()
        self.btn_refresh = QPushButton()
        self.btn_refresh.setIcon(QIcon.fromTheme("view-refresh"))
        self.btn_refresh.setToolTip("Обновить данные")
        self.btn_refresh.setFixedSize(32, 32)
        self.btn_export_excel = QPushButton("Экспорт в Excel")
        self.btn_export_pdf = QPushButton("Экспорт в PDF")
        self.btn_export_excel.setStyleSheet(BUTTON_STYLES.get("export", ""))
        self.btn_export_pdf.setStyleSheet(BUTTON_STYLES.get("pdf", ""))
        panel.addWidget(self.btn_refresh)
        panel.addStretch()
        panel.addWidget(self.btn_export_excel)
        panel.addWidget(self.btn_export_pdf)
        return panel

    def _connect_signals(self):
        """Подключает сигналы к слотам."""
        self.btn_add.clicked.connect(self.add_employee)
        self.btn_edit.clicked.connect(self.edit_employee)
        self.btn_delete.clicked.connect(self.delete_employee)
        self.btn_refresh.clicked.connect(self.load_data)
        self.btn_export_excel.clicked.connect(self.export_to_excel)
        self.btn_export_pdf.clicked.connect(self.export_to_pdf)
        self.search_first_name.textChanged.connect(self.trigger_search)
        self.search_last_name.textChanged.connect(self.trigger_search)
        self.department_combo.currentIndexChanged.connect(self.trigger_search)
        self.main_table.doubleClicked.connect(self.show_employee_details)

    def _load_departments(self):
        """Загружает отделы в комбобокс."""
        try:
            departments = self.department_service.get_departments_for_dropdown()
            self.department_combo.clear()
            self.department_combo.addItem("Все отделы", None)
            for dept_id, dept_name in departments:
                self.department_combo.addItem(dept_name, dept_id)
        except Exception as e:
            logging.error(f"Ошибка загрузки отделов: {e}")

    def load_data(self):
        """Загружает список сотрудников из сервиса."""
        try:
            filters = {}
            if self.search_first_name.text().strip(): filters['first_name'] = self.search_first_name.text().strip()
            if self.search_last_name.text().strip(): filters['last_name'] = self.search_last_name.text().strip()
            if self.department_combo.currentData(): filters['department_id'] = self.department_combo.currentData()
            
            employees = self.employee_service.get_employees(self.user, filters)
            self._populate_table(employees)
        except PermissionDeniedError as e:
            self.show_error("Доступ запрещен", str(e))
        except Exception as e:
            logging.error(f"Ошибка загрузки сотрудников: {e}")
            self.show_error("Ошибка", "Не удалось загрузить список сотрудников")


    def _populate_table(self, employees: List[Employee]):
        """Заполняет таблицу данными."""
        self.main_table.setRowCount(len(employees))
        for row, emp in enumerate(employees):
            self.main_table.setItem(row, 0, QTableWidgetItem(str(emp.employee_id)))
            self.main_table.setItem(row, 1, QTableWidgetItem(emp.first_name))
            self.main_table.setItem(row, 2, QTableWidgetItem(emp.last_name))
            self.main_table.setItem(row, 3, QTableWidgetItem(Formatters.format_date(emp.date_of_birth)))
            self.main_table.setItem(row, 4, QTableWidgetItem(emp.gender))
            self.main_table.setItem(row, 5, QTableWidgetItem(Formatters.format_date(emp.hire_date)))
            self.main_table.setItem(row, 6, QTableWidgetItem(emp.department_name or ""))
            self.main_table.setItem(row, 7, QTableWidgetItem(Formatters.format_status(emp.status)))
            self.main_table.setItem(row, 8, QTableWidgetItem(Formatters.format_datetime(emp.created_at)))
            self.main_table.setItem(row, 9, QTableWidgetItem(Formatters.format_datetime(emp.updated_at)))
            for col in range(self.main_table.columnCount()):
                item = self.main_table.item(row, col)
                if item: item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    def add_employee(self):
        """Открывает диалог добавления сотрудника."""
        try:
            departments = self.department_service.get_departments_for_dropdown()
            dialog = EmployeeDialog(self, departments)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                employee_id = self.employee_service.create_employee(self.user, data)
                self.show_info("Успех", f"Сотрудник добавлен (ID: {employee_id})")
                self.load_data()
        except ValidationError as e:
            self.show_error("Ошибка валидации", e.message)
        except PermissionDeniedError as e:
            self.show_error("Доступ запрещен", str(e))
        except Exception as e:
            logging.error(f"Ошибка добавления: {e}")
            self.show_error("Ошибка", "Не удалось добавить сотрудника")

    def edit_employee(self):
        """Открывает диалог редактирования сотрудника."""
        employee_id = self.get_selected_row_id()
        if not employee_id: return
        try:
            employee = self.employee_service.get_employee_by_id(self.user, employee_id)
            if not employee:
                self.show_error("Ошибка", "Сотрудник не найден")
                return
            departments = self.department_service.get_departments_for_dropdown()
            dialog = EmployeeDialog(self, departments, employee=employee)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                self.employee_service.update_employee(self.user, employee_id, data)
                self.show_info("Успех", "Данные сотрудника обновлены")
                self.load_data()
        except ValidationError as e:
            self.show_error("Ошибка валидации", e.message)
        except Exception as e:
            logging.error(f"Ошибка редактирования: {e}")
            self.show_error("Ошибка", "Не удалось обновить данные")

    def delete_employee(self):
        """Удаляет выбранного сотрудника."""
        employee_id = self.get_selected_row_id()
        if not employee_id: return
        if not self.confirm_action("Подтверждение", f"Вы уверены, что хотите удалить сотрудника с ID {employee_id}?"): return
        try:
            self.employee_service.delete_employee(self.user, employee_id)
            self.show_info("Успех", "Сотрудник удален")
            self.load_data()
        except EntityNotFoundError:
            self.show_error("Ошибка", "Сотрудник не найден")
        except PermissionDeniedError as e:
            self.show_error("Доступ запрещен", str(e))
        except Exception as e:
            logging.error(f"Ошибка удаления: {e}")
            self.show_error("Ошибка", "Не удалось удалить сотрудника")

    def show_employee_details(self):
        """Показывает детальную информацию о сотруднике через QMessageBox."""
        employee_id = self.get_selected_row_id()
        if not employee_id: return
        try:
            employee = self.employee_service.get_employee_by_id(self.user, employee_id)
            if employee:
                details = (
                    f"<b>ID:</b> {employee.employee_id}<br>"
                    f"<b>Имя:</b> {employee.first_name}<br>"
                    f"<b>Фамилия:</b> {employee.last_name}<br>"
                    f"<b>Дата рождения:</b> {Formatters.format_date(employee.date_of_birth)}<br>"
                    f"<b>Пол:</b> {employee.gender}<br>"
                    f"<b>Дата приема:</b> {Formatters.format_date(employee.hire_date)}<br>"
                    f"<b>Отдел:</b> {employee.department_name or ''}<br>"
                    f"<b>Статус:</b> {Formatters.format_status(employee.status)}<br>"
                )
                QMessageBox.information(self, "Детали сотрудника", details)
        except Exception as e:
            logging.error(f"Ошибка просмотра: {e}")

    def _get_export_filename(self, extension: str) -> str:
        return f"employees.{extension}"

    def _get_export_title(self) -> str:
        return "Список сотрудников"

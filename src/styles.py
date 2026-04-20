"""Стили оформления интерфейса.

Содержит константы стилей для виджетов PyQt6.
"""

# Стили таблиц
TABLE_STYLES = {
    "base": """
        QTableWidget {
            background-color: #ffffff;
            alternate-background-color: #f8f9fa;
            gridline-color: #dee2e6;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 13px;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QTableWidget::item {
            padding: 8px 12px;
            border-bottom: 1px solid #e9ecef;
        }
        QTableWidget::item:selected {
            background-color: #0d6efd;
            color: white;
        }
        QTableWidget::item:hover {
            background-color: #e7f1ff;
        }
    """,
    "header": """
        QHeaderView::section {
            background-color: #495057;
            color: white;
            padding: 10px 12px;
            border: none;
            border-right: 1px solid #6c757d;
            font-weight: bold;
            font-size: 13px;
        }
        QHeaderView::section:hover {
            background-color: #5a6268;
        }
    """
}

# Стили кнопок
BUTTON_STYLES = {
    "primary": """
        QPushButton {
            background-color: #1976d2;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 13px;
            min-width: 80px;
        }
        QPushButton:hover {
            background-color: #1565c0;
        }
        QPushButton:pressed {
            background-color: #0d47a1;
        }
        QPushButton:disabled {
            background-color: #bdbdbd;
        }
    """,
    "danger": """
        QPushButton {
            background-color: #d32f2f;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #c62828;
        }
    """,
    "success": """
        QPushButton {
            background-color: #388e3c;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #2e7d32;
        }
    """,
    "secondary": """
        QPushButton {
            background-color: #757575;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #616161;
        }
    """,
    "export": """
        QPushButton {
            background-color: #198754;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 13px;
            min-width: 120px;
        }
        QPushButton:hover {
            background-color: #157347;
        }
        QPushButton:disabled {
            background-color: #6c757d;
        }
    """,
    "pdf": """
        QPushButton {
            background-color: #dc3545;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 13px;
            min-width: 120px;
        }
        QPushButton:hover {
            background-color: #bb2d3b;
        }
        QPushButton:disabled {
            background-color: #6c757d;
        }
    """
}

# Стили полей ввода
INPUT_STYLES = """
    QLineEdit {
        border: 1px solid #bdbdbd;
        border-radius: 4px;
        padding: 8px;
        font-size: 13px;
    }
    QLineEdit:focus {
        border: 2px solid #1976d2;
    }
    QComboBox {
        border: 1px solid #bdbdbd;
        border-radius: 4px;
        padding: 8px;
        font-size: 13px;
    }
"""

# Стили вкладок
TAB_STYLES = """
    QTabWidget::pane {
        border: 1px solid #d0d0d0;
        border-radius: 4px;
        background: white;
    }
    QTabBar::tab {
        background: #f0f0f0;
        border: 1px solid #d0d0d0;
        padding: 10px 20px;
        margin-right: 2px;
    }
    QTabBar::tab:selected {
        background: white;
        border-bottom: 2px solid #1976d2;
    }
"""

"""Сервис экспорта данных."""

import logging
from typing import List, Any
from PyQt6.QtWidgets import QWidget, QTableWidget, QFileDialog, QMessageBox

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm

import pandas as pd

from core.permissions import Permission, check_permission


class ExportService:
    """Сервис для экспорта данных в различные форматы.
    
    Поддерживает:
    - Экспорт в PDF
    - Экспорт в Excel
    - Настройка стилей и форматирования
    """

    @staticmethod
    def check_export_permission(user: dict) -> bool:
        """Проверяет право на экспорт данных."""
        try:
            check_permission(user, Permission.EXPORT_DATA)
            return True
        except Exception:
            return False

    @staticmethod
    def export_to_pdf(
        parent: QWidget,
        table_widget: QTableWidget,
        default_filename: str,
        document_title: str
    ) -> bool:
        """Экспортирует таблицу в PDF.
        
        Args:
            parent: Родительское окно для диалогов
            table_widget: Таблица с данными
            default_filename: Имя файла по умолчанию
            document_title: Заголовок документа
            
        Returns:
            True если экспорт успешен
        """
        try:
            if table_widget.rowCount() == 0:
                QMessageBox.warning(parent, "Ошибка", "Нет данных для экспорта")
                return False

            # Регистрация шрифтов
            font_name = ExportService._register_fonts()

            # Создание стилей
            styles = ExportService._create_styles(font_name)

            # Подготовка данных
            headers, table_data = ExportService._prepare_table_data(table_widget, styles)

            # Диалог сохранения
            file_path, _ = QFileDialog.getSaveFileName(
                parent,
                "Экспорт в PDF",
                default_filename,
                "PDF Files (*.pdf)"
            )
            if not file_path:
                return False

            # Создание документа
            doc = SimpleDocTemplate(
                file_path,
                pagesize=landscape(A4),
                leftMargin=10 * mm,
                rightMargin=10 * mm,
                topMargin=15 * mm,
                bottomMargin=15 * mm
            )

            elements = []
            elements.append(Paragraph(document_title, styles['CustomTitle']))
            elements.append(Spacer(1, 5 * mm))

            # Создание таблицы
            pdf_table = Table(
                table_data,
                colWidths=ExportService._calculate_column_widths(len(headers))
            )
            pdf_table.setStyle(ExportService._create_table_style(font_name))

            elements.append(pdf_table)
            doc.build(elements)

            QMessageBox.information(
                parent,
                "Успех",
                f"PDF-документ сохранен:\n{file_path}"
            )
            return True

        except PermissionError:
            QMessageBox.critical(parent, "Ошибка", "Нет прав для записи в выбранную директорию")
            return False
        except Exception as e:
            logging.error(f"PDF Export Error: {str(e)}")
            QMessageBox.critical(parent, "Ошибка", f"Не удалось создать PDF:\n{str(e)}")
            return False

    @staticmethod
    def export_to_excel(
        parent: QWidget,
        table_widget: QTableWidget,
        default_filename: str,
        sheet_name: str = "Данные"
    ) -> bool:
        """Экспортирует таблицу в Excel.
        
        Args:
            parent: Родительское окно
            table_widget: Таблица с данными
            default_filename: Имя файла по умолчанию
            sheet_name: Название листа
            
        Returns:
            True если экспорт успешен
        """
        try:
            if table_widget.rowCount() == 0:
                QMessageBox.warning(parent, "Ошибка", "Нет данных для экспорта")
                return False

            # Сбор данных из таблицы
            headers = []
            for col in range(table_widget.columnCount()):
                header = table_widget.horizontalHeaderItem(col)
                headers.append(header.text() if header else f"Column {col}")

            data = []
            for row in range(table_widget.rowCount()):
                row_data = []
                for col in range(table_widget.columnCount()):
                    item = table_widget.item(row, col)
                    row_data.append(item.text() if item else "")
                data.append(row_data)

            # Создание DataFrame
            df = pd.DataFrame(data, columns=headers)

            # Диалог сохранения
            file_path, _ = QFileDialog.getSaveFileName(
                parent,
                "Экспорт в Excel",
                default_filename,
                "Excel Files (*.xlsx)"
            )
            if not file_path:
                return False

            # Сохранение в Excel
            df.to_excel(file_path, sheet_name=sheet_name, index=False)

            QMessageBox.information(
                parent,
                "Успех",
                f"Excel-файл сохранен:\n{file_path}"
            )
            return True

        except PermissionError:
            QMessageBox.critical(parent, "Ошибка", "Нет прав для записи в выбранную директорию")
            return False
        except Exception as e:
            logging.error(f"Excel Export Error: {str(e)}")
            QMessageBox.critical(parent, "Ошибка", f"Не удалось создать Excel:\n{str(e)}")
            return False

    @staticmethod
    def _register_fonts() -> str:
        """Регистрирует шрифты для PDF."""
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
            return 'DejaVuSans'
        except Exception:
            return 'Helvetica'

    @staticmethod
    def _create_styles(font_name: str) -> dict:
        """Создает стили для PDF документа."""
        styles = getSampleStyleSheet()
        
        styles.add(ParagraphStyle(
            name='CustomTitle',
            fontName=font_name,
            fontSize=16,
            alignment=1,
            spaceAfter=12
        ))
        
        styles.add(ParagraphStyle(
            name='CustomHeader',
            fontName=font_name,
            fontSize=10,
            alignment=1
        ))
        
        styles.add(ParagraphStyle(
            name='CustomBody',
            fontName=font_name,
            fontSize=9,
            alignment=1
        ))
        
        return styles

    @staticmethod
    def _prepare_table_data(table_widget: QTableWidget, styles: dict) -> tuple:
        """Подготавливает данные таблицы для PDF."""
        headers = []
        for col in range(table_widget.columnCount()):
            header = table_widget.horizontalHeaderItem(col)
            text = header.text() if header else ""
            headers.append(Paragraph(f"<b>{text}</b>", styles['CustomHeader']))

        table_data = [headers]
        
        for row in range(table_widget.rowCount()):
            row_data = []
            for col in range(table_widget.columnCount()):
                item = table_widget.item(row, col)
                text = item.text() if item else ""
                row_data.append(Paragraph(text, styles['CustomBody']))
            table_data.append(row_data)

        return headers, table_data

    @staticmethod
    def _calculate_column_widths(num_columns: int) -> List[float]:
        """Рассчитывает ширину колонок."""
        page_width = landscape(A4)[0] - 20 * mm
        return [page_width / num_columns] * num_columns

    @staticmethod
    def _create_table_style(font_name: str) -> TableStyle:
        """Создает стиль таблицы для PDF."""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ])

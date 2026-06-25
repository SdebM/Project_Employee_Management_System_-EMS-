"""Сервис экспорта данных."""

import logging
from typing import List, Any
from PyQt6.QtWidgets import QWidget, QTableWidget, QFileDialog, QMessageBox

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm

import pandas as pd

from core.permissions import Permission, check_permission


class PDFExporter:
    """Класс для экспорта данных таблицы в PDF-формат."""

    @staticmethod
    def export_to_pdf(parent, table_widget, default_filename, document_title) -> bool:
        try:
            if table_widget.rowCount() == 0:
                QMessageBox.warning(parent, "Ошибка", "Нет данных для экспорта")
                return False

            font_name = PDFExporter.register_fonts()
            styles = PDFExporter.create_styles(font_name)
            headers, table_data = PDFExporter.prepare_data(table_widget, styles)

            file_path, _ = QFileDialog.getSaveFileName(
                parent,
                "Экспорт в PDF",
                default_filename,
                "PDF Files (*.pdf)"
            )
            if not file_path:
                return False

            doc = SimpleDocTemplate(
                file_path,
                pagesize=landscape(A4),
                leftMargin=10 * mm,
                rightMargin=10 * mm,
                topMargin=15 * mm,
                bottomMargin=15 * mm
            )

            elements = []
            elements.append(Paragraph(document_title, styles['Title']))
            elements.append(Spacer(1, 0.2 * 25.4))

            table = Table(
                table_data,
                colWidths=PDFExporter.calculate_column_widths(len(headers))
            )
            table.setStyle(PDFExporter.create_table_style(font_name))

            elements.append(table)
            doc.build(elements)

            QMessageBox.information(
                parent,
                "Успех",
                f"PDF-документ успешно сохранен:\n{file_path}"
            )
            return True

        except PermissionError:
            error_msg = "Нет прав для записи в выбранную директорию"
            logging.error(error_msg)
            QMessageBox.critical(parent, "Ошибка", error_msg)
            return False
        except Exception as e:
            logging.error(f"PDF Export Error: {str(e)}")
            QMessageBox.critical(parent, "Ошибка", f"Не удалось создать PDF:\n{str(e)}")
            return False

    @staticmethod
    def prepare_data(table_widget, styles):
        def format_text(text, is_header=False):
            style = styles['Header'] if is_header else styles['Body']
            text = str(text).strip() if text else ""
            return Paragraph(f"<b>{text}</b>" if is_header else text, style)

        headers = [
            table_widget.horizontalHeaderItem(i).text()
            for i in range(table_widget.columnCount())
        ]

        table_data = []
        if headers:
            table_data.append([format_text(h, True) for h in headers])

        for row in range(table_widget.rowCount()):
            formatted_row = []
            for col in range(table_widget.columnCount()):
                item = table_widget.item(row, col)
                text = item.text() if item else ""
                formatted_row.append(format_text(text))
            table_data.append(formatted_row)

        return headers, table_data

    @staticmethod
    def create_styles(font_name):
        styles = getSampleStyleSheet()

        styles.add(ParagraphStyle(
            name='Header',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=9,
            leading=11,
            alignment=1,
            textColor=colors.white,
            spaceBefore=2,
            spaceAfter=2
        ))

        styles.add(ParagraphStyle(
            name='Body',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=8,
            leading=10,
            alignment=1,
            textColor=colors.black,
            spaceBefore=2,
            spaceAfter=2
        ))

        styles['Title'].fontName = font_name
        styles['Title'].fontSize = 14
        styles['Title'].alignment = 1

        return styles

    @staticmethod
    def create_table_style(font_name):
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ])

    @staticmethod
    def register_fonts():
        font_name = 'Helvetica'
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
            font_name = 'DejaVuSans'
        except Exception:
            try:
                pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
                font_name = 'Arial'
            except Exception:
                logging.warning("Используется стандартный шрифт")
        return font_name

    @staticmethod
    def calculate_column_widths(columns_count):
        page_width = landscape(A4)[0] - 20 * mm
        return [page_width / columns_count * 0.95] * columns_count


class ExcelExporter:
    """Класс для экспорта данных таблицы в Excel-формат."""

    @staticmethod
    def export_to_excel(parent, table_widget, default_filename, sheet_name="Данные") -> bool:
        try:
            if table_widget.rowCount() == 0:
                QMessageBox.warning(parent, "Ошибка", "Нет данных для экспорта")
                return False

            headers = [
                table_widget.horizontalHeaderItem(i).text()
                for i in range(table_widget.columnCount())
            ]

            data = []
            for row in range(table_widget.rowCount()):
                row_data = []
                for col in range(table_widget.columnCount()):
                    item = table_widget.item(row, col)
                    row_data.append(item.text() if item else "")
                data.append(row_data)

            df = pd.DataFrame(data, columns=headers)

            file_path, _ = QFileDialog.getSaveFileName(
                parent,
                "Экспорт в Excel",
                default_filename,
                "Excel Files (*.xlsx)"
            )
            if not file_path:
                return False

            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)

            QMessageBox.information(
                parent,
                "Успех",
                f"Данные успешно экспортированы в файл:\n{file_path}"
            )
            return True

        except PermissionError:
            error_msg = "Нет прав для записи в выбранную директорию"
            logging.error(error_msg)
            QMessageBox.critical(parent, "Ошибка", error_msg)
            return False
        except Exception as e:
            logging.error(f"Excel Export Error: {str(e)}")
            QMessageBox.critical(
                parent,
                "Ошибка",
                f"Не удалось экспортировать данные:\n{str(e)}"
            )
            return False


class ExportService:
    @staticmethod
    def check_export_permission(user: dict) -> bool:
        try:
            check_permission(user, Permission.EXPORT_DATA)
            return True
        except Exception:
            return False

    @staticmethod
    def export_to_pdf(parent: QWidget, table_widget: QTableWidget, default_filename: str, document_title: str) -> bool:
        return PDFExporter.export_to_pdf(parent, table_widget, default_filename, document_title)

    @staticmethod
    def export_to_excel(parent: QWidget, table_widget: QTableWidget, default_filename: str, sheet_name: str = "Данные") -> bool:
        return ExcelExporter.export_to_excel(parent, table_widget, default_filename, sheet_name)

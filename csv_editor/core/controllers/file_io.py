import csv
import json
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QStandardItem
from PyQt5.QtCore import Qt
from openpyxl import Workbook
import sqlite3
import markdown
from pathlib import Path
import csv
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QObject, pyqtSignal

class FileIOController(QObject):
    file_loaded = pyqtSignal(list)
    file_saved = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)  # Передаём parent в QObject
        self.current_file = None
        self.model = None  # Добавляем атрибут model


    def open_file(self, parent_widget):
        filename, _ = QFileDialog.getOpenFileName(
            parent_widget,
            "Open CSV File",
            "",
            "CSV Files (*.csv);;Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        
        if not filename:
            return False
            
        self.current_file = filename
        
        try:
            if filename.endswith('.csv'):
                with open(filename, 'r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    data = list(reader)
            else:
                # Для Excel потребуется openpyxl
                from openpyxl import load_workbook
                wb = load_workbook(filename)
                sheet = wb.active
                data = []
                for row in sheet.iter_rows(values_only=True):
                    data.append(list(row))
            
            self.file_loaded.emit(data)
            return True
        except Exception as e:
            QMessageBox.critical(parent_widget, "Error", f"Failed to open file:\n{str(e)}")
            return False

    def save_file(self, parent_widget, data):
        if not self.current_file:
            return self.save_file_as(parent_widget, data)
            
        try:
            if self.current_file.endswith('.csv'):
                with open(self.current_file, 'w', encoding='utf-8', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(data)
            else:
                from openpyxl import Workbook
                wb = Workbook()
                ws = wb.active
                for row in data:
                    ws.append(row)
                wb.save(self.current_file)
            
            self.file_saved.emit(True)
            return True
        except Exception as e:
            QMessageBox.critical(parent_widget, "Error", f"Failed to save file:\n{str(e)}")
            return False

    def save_file_as(self, parent_widget, data):
        filename, _ = QFileDialog.getSaveFileName(
            parent_widget,
            "Save File As",
            self.current_file if self.current_file else "",
            "CSV Files (*.csv);;Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        
        if not filename:
            return False
            
        self.current_file = filename
        return self.save_file(parent_widget, data)
    

        
    def load_csv(self, filename, delimiter=','):
        try:
            with open(filename, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile, delimiter=delimiter)
                self._load_data(list(reader))
            return True
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to load CSV: {str(e)}")
            return False
    
    def save_csv(self, filename, delimiter=',', include_headers=True):
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=delimiter)
                if include_headers:
                    headers = [self.model.headerData(i, Qt.Horizontal) for i in range(self.model.columnCount())]
                    writer.writerow(headers)
                
                for row in range(self.model.rowCount()):
                    row_data = [self.model.data(self.model.index(row, col)) or "" 
                              for col in range(self.model.columnCount())]
                    writer.writerow(row_data)
            return True
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to save CSV: {str(e)}")
            return False
    
    def export_to_excel(self, filename):
        wb = Workbook()
        ws = wb.active
        
        # Заголовки
        for col in range(self.model.columnCount()):
            ws.cell(row=1, column=col+1, value=self.model.headerData(col, Qt.Horizontal))
        
        # Данные
        for row in range(self.model.rowCount()):
            for col in range(self.model.columnCount()):
                ws.cell(row=row+2, column=col+1, 
                       value=self.model.data(self.model.index(row, col)))
        
        wb.save(filename)
    
    def export_to_markdown(self, filename):
        md_content = "| " + " | ".join(
            str(self.model.headerData(col, Qt.Horizontal)) 
            for col in range(self.model.columnCount())
        ) + " |\n"
        
        md_content += "| " + " | ".join("---" for _ in range(self.model.columnCount())) + " |\n"
        
        for row in range(self.model.rowCount()):
            md_content += "| " + " | ".join(
                str(self.model.data(self.model.index(row, col)) or "")
                for col in range(self.model.columnCount())
            ) + " |\n"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(md_content)
    
    def _load_data(self, data):
        # Общая функция загрузки данных в модель
        self.model.removeRows(0, self.model.rowCount())
        
        if not data:
            return
            
        # Устанавливаем заголовки
        self.model.setColumnCount(len(data[0]))
        for col in range(len(data[0])):
            self.model.setHeaderData(col, Qt.Horizontal, f"Column {col}")
        
        # Добавляем данные
        for row_data in data:
            items = [QStandardItem(str(cell)) for cell in row_data]
            self.model.appendRow(items)
    def import_excel(self, filename):
        try:
            from openpyxl import load_workbook
            wb = load_workbook(filename)
            ws = wb.active
            
            data = []
            for row in ws.iter_rows(values_only=True):
                data.append(list(row))
            
            self._load_data(data)
            return True
        except Exception as e:
            QMessageBox.critical(None, "Excel Import Error", str(e))
            return False
    
    def import_sqlite(self, db_file, table_name):
        try:
            import sqlite3
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()
            
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            self.model.setColumnCount(len(columns))
            for col, name in enumerate(columns):
                self.model.setHeaderData(col, Qt.Horizontal, name)
            
            self._load_data(data)
            return True
        except Exception as e:
            QMessageBox.critical(None, "SQLite Import Error", str(e))
            return False
        finally:
            conn.close()
    
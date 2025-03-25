import sqlite3
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QStandardItem
from PyQt5.QtCore import Qt

class SQLiteImporter:
    def __init__(self, model):
        self.model = model
    
    def import_table(self, db_file, table_name):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Получаем данные таблицы
            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()
            
            # Получаем названия столбцов
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Загружаем в модель
            self.model.setColumnCount(len(columns))
            for col, name in enumerate(columns):
                self.model.setHeaderData(col, Qt.Horizontal, name)
            
            self.model.removeRows(0, self.model.rowCount())
            for row_data in data:
                items = [QStandardItem(str(item)) for item in row_data]
                self.model.appendRow(items)
            
            return True
        except Exception as e:
            QMessageBox.critical(None, "SQLite Import Error", str(e))
            return False
        finally:
            conn.close()

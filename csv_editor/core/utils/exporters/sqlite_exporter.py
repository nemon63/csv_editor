import sqlite3
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt

class SQLiteExporter:
    def __init__(self, model):
        self.model = model

    def export(self, db_file, table_name):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Создаем таблицу
            columns = [self.model.headerData(col, Qt.Horizontal) or f"col_{col}" 
                      for col in range(self.model.columnCount())]
            
            # Экранируем имена столбцов
            safe_columns = [f'"{col}" TEXT' for col in columns]
            create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(safe_columns)})"
            cursor.execute(create_sql)
            
            # Очищаем существующие данные
            cursor.execute(f"DELETE FROM {table_name}")
            
            # Вставляем данные
            for row in range(self.model.rowCount()):
                values = [self.model.data(self.model.index(row, col)) 
                         for col in range(self.model.columnCount())]
                placeholders = ", ".join(["?"] * len(values))
                cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", values)
            
            conn.commit()
            return True
        except Exception as e:
            QMessageBox.critical(None, "SQLite Export Error", str(e))
            return False
        finally:
            if 'conn' in locals():
                conn.close()

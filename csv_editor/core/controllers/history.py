from datetime import datetime
import json
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem

class HistoryController:
    def __init__(self, model, undo_stack):
        self.model = model
        self.undo_stack = undo_stack
        self.snapshots = []
        self.current_snapshot = -1
    
    def take_snapshot(self, description):
        snapshot = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'description': description,
            'data': self._get_model_data()
        }
        self.snapshots = self.snapshots[:self.current_snapshot + 1]
        self.snapshots.append(snapshot)
        self.current_snapshot = len(self.snapshots) - 1
    
    def _get_model_data(self):
        data = {
            'headers': [],
            'rows': []
        }
        
        # Сохраняем заголовки
        for col in range(self.model.columnCount()):
            data['headers'].append(self.model.headerData(col, Qt.Horizontal))
        
        # Сохраняем данные
        for row in range(self.model.rowCount()):
            row_data = []
            for col in range(self.model.columnCount()):
                row_data.append(self.model.data(self.model.index(row, col)))
            data['rows'].append(row_data)
        
        return data
    
    def restore_snapshot(self, index):
        if 0 <= index < len(self.snapshots):
            snapshot = self.snapshots[index]
            self._load_model_data(snapshot['data'])
            self.current_snapshot = index
    
    def _load_model_data(self, data):
        self.model.removeRows(0, self.model.rowCount())
        self.model.setColumnCount(len(data['headers']))
        
        # Восстанавливаем заголовки
        for col, header in enumerate(data['headers']):
            self.model.setHeaderData(col, Qt.Horizontal, header)
        
        # Восстанавливаем данные
        for row_data in data['rows']:
            items = [QStandardItem(str(cell)) for cell in row_data]
            self.model.appendRow(items)
    
    def get_history(self):
        return [{
            'id': i,
            'timestamp': s['timestamp'],
            'description': s['description'],
            'current': (i == self.current_snapshot)
        } for i, s in enumerate(self.snapshots)]

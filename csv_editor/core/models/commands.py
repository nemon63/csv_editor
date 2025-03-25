from PyQt5.QtWidgets import QUndoCommand
from PyQt5.QtCore import QPersistentModelIndex, Qt
from PyQt5.QtGui import QStandardItem
from .base_model import UndoableStandardItemModel # Добавлен импорт

class EditCellCommand(QUndoCommand):
    def __init__(self, model, index, old_value, new_value):
        super().__init__()
        self.model = model
        self.index = index
        self.old_value = old_value
        self.new_value = new_value
        self.setText(f"Edit cell ({index.row()}, {index.column()})")

    def undo(self):
        self.model.setData(self.index, self.old_value)

    def redo(self):
        self.model.setData(self.index, self.new_value)

class RemoveColumnCommand(QUndoCommand):
    def __init__(self, model, column, description="Remove Column"):
        super().__init__(description)
        self.model = model
        self.column = column
        self.column_data = []
        self.header = model.headerData(column, Qt.Horizontal)

    def undo(self):
        self.model.insertColumn(self.column)
        self.model.setHeaderData(self.column, Qt.Horizontal, self.header)
        for row, data in enumerate(self.column_data):
            item = QStandardItem(data)
            self.model.setItem(row, self.column, item)

    def redo(self):
        self.column_data.clear()
        for row in range(self.model.rowCount()):
            index = self.model.index(row, self.column)
            data = self.model.data(index)
            self.column_data.append(data)
        self.model.removeColumn(self.column)

from PyQt5.QtWidgets import QUndoCommand
from PyQt5.QtCore import QPersistentModelIndex, Qt
from PyQt5.QtGui import QStandardItem
from .base_model import UndoableStandardItemModel # Добавлен импорт

class EditCellCommand(QUndoCommand):
    def __init__(self, model: UndoableStandardItemModel, index, oldValue, newValue):
        super().__init__("Edit Cell")
        self.model = model
        self.pIndex = QPersistentModelIndex(index)
        self.oldValue = oldValue
        self.newValue = newValue

    def undo(self):
        if self.pIndex.isValid():
            row = self.pIndex.row()
            col = self.pIndex.column()
            index = self.model.index(row, col)
            self.model.setData(index, self.oldValue, Qt.EditRole)  # Упростили вызов

    def redo(self):
        if self.pIndex.isValid():
            row = self.pIndex.row()
            col = self.pIndex.column()
            index = self.model.index(row, col)
            self.model.setData(index, self.newValue, Qt.EditRole)  # Упростили вызов

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

from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem

class UndoableStandardItemModel(QStandardItemModel):
    def __init__(self, rows=0, cols=0, parent=None):
        super().__init__(rows, cols, parent)
        self.undo_stack = None  # Будет установлен извне

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or role != Qt.EditRole:
            return False
            
        old_value = self.data(index, role)
        if old_value == value:
            return True
            
        # Если есть undo_stack, создаём команду для отмены
        if self.undo_stack:
            from .commands import EditCellCommand
            command = EditCellCommand(self, index, old_value, value)
            self.undo_stack.push(command)
        
        return super().setData(index, value, role)

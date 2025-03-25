from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from .base_model import UndoableStandardItemModel
from .commands import EditCellCommand

class UndoableStandardItemModel(QStandardItemModel):
    def __init__(self, rows=0, columns=0, parent=None, undo_stack=None):
        super().__init__(rows, columns, parent)
        self.undo_stack = undo_stack

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole and index.isValid():
            old_value = self.data(index, role)
            if old_value != value:
                if self.undo_stack is not None:
                    cmd = EditCellCommand(self, index, old_value, value)
                    self.undo_stack.push(cmd)
                    return True
        return super().setData(index, value, role)

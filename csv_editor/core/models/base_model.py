# csv_editor/core/models/base_model.py
from PyQt5.QtGui import QStandardItemModel

class UndoableStandardItemModel(QStandardItemModel):
    """Базовый класс модели с поддержкой отмены"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.undo_stack = None

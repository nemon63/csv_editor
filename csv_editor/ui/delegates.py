from PyQt5.QtWidgets import QStyledItemDelegate, QTextEdit
from PyQt5.QtCore import Qt

class MultiLineDelegate(QStyledItemDelegate):
    """Делегат для многострочного редактирования"""
    def createEditor(self, parent, option, index):
        editor = QTextEdit(parent)
        editor.setFrameStyle(QTextEdit.NoFrame)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        editor.setPlainText(value if value else "")

    def setModelData(self, editor, model, index):
        model.setData(index, editor.toPlainText(), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

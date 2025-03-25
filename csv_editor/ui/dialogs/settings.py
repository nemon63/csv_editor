from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QGridLayout, QLabel, 
                            QComboBox, QCheckBox, QHBoxLayout, QPushButton,
                            QFontDialog)
from PyQt5.QtGui import QFont

class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_font=None, highlight_enabled=True):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.current_font = current_font
        self.highlight_enabled = highlight_enabled
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        grid = QGridLayout()

        # ... (остальная реализация диалога настроек)
        
        self.setLayout(layout)

    def get_settings(self):
        return {
            'delimiter': self.delimiter_combo.currentData(),
            'dark_theme': self.dark_theme_checkbox.isChecked(),
            'highlight': self.highlight_checkbox.isChecked(),
            'font': self.current_font
        }

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QComboBox, 
                            QCheckBox, QDialogButtonBox, QLabel)

class GroupDialog(QDialog):
    def __init__(self, headers, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Group Data")
        self.headers = headers
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Выбор столбца для группировки
        layout.addWidget(QLabel("Group by column:"))
        self.group_combo = QComboBox()
        self.group_combo.addItems(self.headers)
        layout.addWidget(self.group_combo)
        
        # Выбор агрегатных функций
        layout.addWidget(QLabel("Aggregate functions:"))
        self.agg_checkboxes = {}
        
        for func in ['Sum', 'Average', 'Count', 'Min', 'Max']:
            cb = QCheckBox(func)
            self.agg_checkboxes[func] = cb
            layout.addWidget(cb)
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)

    def get_selections(self):
        return {
            'group_column': self.group_combo.currentText(),
            'aggregations': [func for func, cb in self.agg_checkboxes.items() if cb.isChecked()]
        }

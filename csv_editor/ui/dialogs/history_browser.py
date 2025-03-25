from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QListWidget, 
                            QDialogButtonBox, QLabel)

class HistoryBrowserDialog(QDialog):
    def __init__(self, history_controller, parent=None):
        super().__init__(parent)
        self.history = history_controller
        self.setWindowTitle("History Browser")
        self.resize(600, 400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.list_widget = QListWidget()
        self.update_history_list()
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(QLabel("Select a snapshot to restore:"))
        layout.addWidget(self.list_widget)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def update_history_list(self):
        self.list_widget.clear()
        for item in self.history.get_history():
            text = f"{item['timestamp']} - {item['description']}"
            if item['current']:
                text = "✓ " + text
            self.list_widget.addItem(text)
            if item['current']:
                self.list_widget.setCurrentRow(self.list_widget.count() - 1)
    
    def get_selected_snapshot(self):
        return self.list_widget.currentRow()

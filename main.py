# main.py
import sys
from PyQt5.QtWidgets import QApplication
from csv_editor.ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Настройка стиля приложения
    app.setStyle('Fusion')
    app.setApplicationName("CSV Editor")
    app.setApplicationVersion("1.0")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

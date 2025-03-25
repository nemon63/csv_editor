import json
import sys

# Импорты PyQt5
from PyQt5.QtWidgets import (QMainWindow, QTableView, QToolBar, QAction, 
                            QStatusBar, QMenuBar, QFileDialog, QMessageBox,
                            QInputDialog, QUndoStack)
from PyQt5.QtGui import QIcon, QStandardItem
from PyQt5.QtCore import Qt, QTimer

# Абсолютные импорты из вашего пакета csv_editor
from csv_editor.core.models.csv_table_model import UndoableStandardItemModel
from csv_editor.core.models.proxy_model import MySortFilterProxyModel
from csv_editor.core.controllers.file_io import FileIOController
from csv_editor.core.controllers.history import HistoryController
from csv_editor.core.controllers.data_operations import DataOperationsController
from csv_editor.core.utils.audit_log import AuditLogger
from csv_editor.core.utils.exporters.excel import ExcelExporter

# Импорты UI-компонентов
from csv_editor.ui.dialogs.settings import SettingsDialog
from csv_editor.ui.dialogs.history_browser import HistoryBrowserDialog
from csv_editor.ui.dialogs.comparison import TableComparisonDialog
from csv_editor.ui.dialogs.group_dialog import GroupDialog
from csv_editor.ui.delegates import MultiLineDelegate


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced CSV Editor")
        self.resize(1000, 600)
        
        # Инициализация компонентов
        self.init_models()
        self.init_controllers()
        self.init_ui()
        self.init_connections()
        
        # Загрузка настроек
        self.load_settings()
        
        # Таймер автосохранения
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(300000)  # 5 минут
    
    def init_models(self):
        self.undo_stack = QUndoStack(self)
        self.model = UndoableStandardItemModel(0, 0, self, self.undo_stack)
        self.proxy_model = MySortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
    
    def init_controllers(self):
        self.file_io = FileIOController(self.model)
        self.history = HistoryController(self.model, self.undo_stack)  # Передаем model
        self.data_ops = DataOperationsController(self.model, self.undo_stack)
        self.audit_log = AuditLogger()
        self.excel_exporter = ExcelExporter(self.model)  # Инициализация экспортера
    
    def init_ui(self):
        # Создание виджетов
        self.view = QTableView()
        self.view.setModel(self.proxy_model)
        self.setCentralWidget(self.view)
        
        # Создание меню и панели инструментов
        self.create_menus()
        self.create_toolbars()
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Настройка делегатов
        self.setup_delegates()
    
    def create_menus(self):
        menubar = self.menuBar()
        
        # Меню File
        file_menu = menubar.addMenu("File")
        
        # Стандартные действия
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        # Подменю Import
        import_menu = file_menu.addMenu("Import")
        
        import_csv = QAction("From CSV", self)
        import_csv.triggered.connect(lambda: self.open_file('csv'))
        import_menu.addAction(import_csv)
        
        import_excel = QAction("From Excel", self)
        import_excel.triggered.connect(self.import_excel)
        import_menu.addAction(import_excel)
        
        import_sqlite = QAction("From SQLite", self)
        import_sqlite.triggered.connect(self.import_sqlite)
        import_menu.addAction(import_sqlite)
        
        # Подменю Export
        export_menu = file_menu.addMenu("Export")
        
        export_csv = QAction("To CSV", self)
        export_csv.triggered.connect(lambda: self.save_file('csv'))
        export_menu.addAction(export_csv)
        
        export_excel = QAction("To Excel", self)
        export_excel.triggered.connect(self.export_to_excel)
        export_menu.addAction(export_excel)
        
        export_sqlite = QAction("To SQLite", self)
        export_sqlite.triggered.connect(self.export_sqlite)
        export_menu.addAction(export_sqlite)
        
        export_md = QAction("To Markdown", self)
        export_md.triggered.connect(self.export_markdown)
        export_menu.addAction(export_md)
        
        # Меню Edit
        edit_menu = menubar.addMenu("Edit")
        
        undo_action = QAction("Undo", self)
        undo_action.triggered.connect(self.undo_stack.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.triggered.connect(self.undo_stack.redo)
        edit_menu.addAction(redo_action)
        
        # Меню Data
        data_menu = menubar.addMenu("Data")
        
        group_action = QAction("Group Data", self)
        group_action.triggered.connect(self.show_group_dialog)
        data_menu.addAction(group_action)
        
        # Меню History
        history_menu = menubar.addMenu("History")
        show_history = QAction("Show History", self)
        show_history.triggered.connect(self.show_history)
        history_menu.addAction(show_history)
        
        # Меню Tools
        tools_menu = menubar.addMenu("Tools")
        compare_tables = QAction("Compare Tables", self)
        compare_tables.triggered.connect(self.compare_tables)
        tools_menu.addAction(compare_tables)
    
    def create_toolbars(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # Добавление действий на панель инструментов
        open_action = QAction(QIcon.fromTheme("document-open"), "Open", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        save_action = QAction(QIcon.fromTheme("document-save"), "Save", self)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
    
    def setup_delegates(self):
        self.multi_line_delegate = MultiLineDelegate()
        self.view.setItemDelegateForColumn(2, self.multi_line_delegate)
    
    def open_file(self, file_type='csv'):
        if file_type == 'csv':
            filename, _ = QFileDialog.getOpenFileName(
                self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)"
            )
            if filename:
                self.file_io.load_csv(filename)
                self.history.take_snapshot(f"Opened file: {filename}")
    
    def save_file(self, file_type='csv'):
        if file_type == 'csv':
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save CSV File", "", "CSV Files (*.csv);;All Files (*)"
            )
            if filename:
                self.file_io.save_csv(filename)
    
    def import_excel(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Import Excel", "", "Excel Files (*.xlsx)"
        )
        if filename:
            if self.file_io.import_excel(filename):
                self.history.take_snapshot(f"Imported from Excel: {filename}")
                self.audit_log.log(
                    "import_excel", 
                    {"file": filename}
                )
    
    def export_to_excel(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Excel", "", "Excel Files (*.xlsx)"
        )
        if filename:
            if self.excel_exporter.export(filename):
                self.audit_log.log(
                    "export_excel", 
                    {"file": filename}
                )
    
    def export_markdown(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Markdown", "", "Markdown Files (*.md);;All Files (*)"
        )
        if filename:
            # Реализация экспорта в Markdown
            pass
    
    def import_sqlite(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Import SQLite", "", "SQLite Databases (*.db *.sqlite)"
        )
        if filename:
            table_name, ok = QInputDialog.getText(
                self, "Select Table", "Enter table name:"
            )
            if ok and table_name:
                if self.file_io.import_sqlite(filename, table_name):
                    self.history.take_snapshot(f"Imported from SQLite: {table_name}")
    
    def export_sqlite(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export SQLite", "", "SQLite Databases (*.db *.sqlite)"
        )
        if filename:
            table_name, ok = QInputDialog.getText(
                self, "Table Name", "Enter table name for export:"
            )
            if ok and table_name:
                if self.file_io.export_sqlite(filename, table_name):
                    self.audit_log.log(
                        "export_sqlite", 
                        {"file": filename, "table": table_name}
                    )
    
    def show_group_dialog(self):
        headers = [self.model.headerData(col, Qt.Horizontal) or f"Column {col}" 
                  for col in range(self.model.columnCount())]
        dialog = GroupDialog(headers, self)
        if dialog.exec_():
            selections = dialog.get_selections()
            # Применяем группировку
            result = self.data_ops.group_data(
                selections['group_column'],
                selections['aggregations']
            )
            # Показываем результат
            QMessageBox.information(
                self, 
                "Grouping Result", 
                f"Data grouped by {selections['group_column']}\n"
                f"Found {len(result)} groups"
            )
            self.audit_log.log(
                "group_data", 
                selections
            )
    
    def show_history(self):
        dialog = HistoryBrowserDialog(self.history, self)
        if dialog.exec_():
            selected = dialog.get_selected_snapshot()
            self.history.restore_snapshot(selected)
    
    def compare_tables(self):
        dialog = TableComparisonDialog(self.model, self)
        if dialog.exec_():
            # Обработка результатов сравнения
            pass
    
    def autosave(self):
        data = self.history._get_model_data()
        try:
            with open("autosave.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Autosave failed: {e}")
    
    def load_settings(self):
        # Здесь будет загрузка настроек
        pass
    
    def init_connections(self):
        self.model.dataChanged.connect(self.on_data_changed)
    
    def on_data_changed(self):
        self.status_bar.showMessage("Data changed")
        self.history.take_snapshot("Data edit")

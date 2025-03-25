import json
import sys
from PyQt5.QtWidgets import (QMainWindow, QTableView, QToolBar, QAction, 
                            QStatusBar, QFileDialog, QMessageBox,
                            QInputDialog, QUndoStack)
from PyQt5.QtGui import QIcon, QStandardItem
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal

# Импорты из вашего пакета
from csv_editor.core.models.csv_table_model import UndoableStandardItemModel
from csv_editor.core.models.proxy_model import MySortFilterProxyModel
from csv_editor.core.controllers.file_io import FileIOController
from csv_editor.core.controllers.history import HistoryController
from csv_editor.core.controllers.data_operations import DataOperationsController
from csv_editor.core.utils.audit_log import AuditLogger
from csv_editor.core.utils.exporters.excel import ExcelExporter
from csv_editor.ui.dialogs.group_dialog import GroupDialog
from csv_editor.ui.dialogs.history_browser import HistoryBrowserDialog
from csv_editor.ui.dialogs.comparison import TableComparisonDialog
from csv_editor.ui.delegates import MultiLineDelegate

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced CSV Editor")
        self.resize(1000, 600)
        
        # Инициализация основных компонентов
        self.undo_stack = QUndoStack(self)
        self.model = UndoableStandardItemModel(0, 0, parent=self)
        self.model.undo_stack = self.undo_stack
        
        # Инициализация UI
        self.init_ui()
        self.init_controllers()
        self.init_connections()
        
        # Настройка автосохранения
        self.setup_autosave()
        
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        # Основная таблица
        self.proxy_model = MySortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        
        self.view = QTableView()
        self.view.setModel(self.proxy_model)
        self.setCentralWidget(self.view)
        
        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Меню и тулбары
        self.create_actions()
        self.create_menus()
        self.create_toolbars()
        
        # Делегаты
        self.setup_delegates()
    
    def init_controllers(self):
        """Инициализация контроллеров"""
        self.file_io = FileIOController(parent=self)
        self.file_io.file_loaded.connect(self.load_data)
        
        self.history = HistoryController(self.model, self.undo_stack)
        self.data_ops = DataOperationsController(self.model, self.undo_stack)
        self.audit_log = AuditLogger()
        self.excel_exporter = ExcelExporter(self.model)
    
    def init_connections(self):
        """Настройка сигналов и слотов"""
        self.model.dataChanged.connect(self.on_data_changed)
        self.undo_stack.indexChanged.connect(self.on_undo_stack_changed)
    
    def setup_autosave(self):
        """Настройка таймера автосохранения"""
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(300000)  # 5 минут
    
    def create_actions(self):
        """Создание действий для меню и тулбаров"""
        # File Actions
        self.open_action = QAction(QIcon.fromTheme("document-open"), "&Open...", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.open_file)
        
        self.save_action = QAction(QIcon.fromTheme("document-save"), "&Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_file)
        
        self.save_as_action = QAction("Save &As...", self)
        self.save_as_action.triggered.connect(self.save_file_as)
        
        # Import Actions
        self.import_csv_action = QAction("From CSV", self)
        self.import_csv_action.triggered.connect(lambda: self.open_file('csv'))
        
        self.import_excel_action = QAction("From Excel", self)
        self.import_excel_action.triggered.connect(self.import_excel)
        
        self.import_sqlite_action = QAction("From SQLite", self)
        self.import_sqlite_action.triggered.connect(self.import_sqlite)
        
        # Export Actions
        self.export_csv_action = QAction("To CSV", self)
        self.export_csv_action.triggered.connect(lambda: self.save_file('csv'))
        
        self.export_excel_action = QAction("To Excel", self)
        self.export_excel_action.triggered.connect(self.export_to_excel)
        
        self.export_sqlite_action = QAction("To SQLite", self)
        self.export_sqlite_action.triggered.connect(self.export_sqlite)
        
        self.export_md_action = QAction("To Markdown", self)
        self.export_md_action.triggered.connect(self.export_markdown)
        
        # Edit Actions
        self.undo_action = QAction("&Undo", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.triggered.connect(self.undo_stack.undo)
        
        self.redo_action = QAction("&Redo", self)
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.triggered.connect(self.undo_stack.redo)
        
        # Data Actions
        self.group_action = QAction("Group Data", self)
        self.group_action.triggered.connect(self.show_group_dialog)
        
        # History Actions
        self.show_history_action = QAction("Show History", self)
        self.show_history_action.triggered.connect(self.show_history)
        
        # Tools Actions
        self.compare_tables_action = QAction("Compare Tables", self)
        self.compare_tables_action.triggered.connect(self.compare_tables)
    
    def create_menus(self):
        """Создание меню"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        
        # Import Submenu
        import_menu = file_menu.addMenu("&Import")
        import_menu.addAction(self.import_csv_action)
        import_menu.addAction(self.import_excel_action)
        import_menu.addAction(self.import_sqlite_action)
        
        # Export Submenu
        export_menu = file_menu.addMenu("&Export")
        export_menu.addAction(self.export_csv_action)
        export_menu.addAction(self.export_excel_action)
        export_menu.addAction(self.export_sqlite_action)
        export_menu.addAction(self.export_md_action)
        
        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        
        # Data Menu
        data_menu = menubar.addMenu("&Data")
        data_menu.addAction(self.group_action)
        
        # History Menu
        history_menu = menubar.addMenu("&History")
        history_menu.addAction(self.show_history_action)
        
        # Tools Menu
        tools_menu = menubar.addMenu("&Tools")
        tools_menu.addAction(self.compare_tables_action)
    
    def create_toolbars(self):
        """Создание панелей инструментов"""
        # Main Toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addSeparator()
        toolbar.addAction(self.undo_action)
        toolbar.addAction(self.redo_action)
    
    def setup_delegates(self):
        """Настройка делегатов для таблицы"""
        self.multi_line_delegate = MultiLineDelegate()
        self.view.setItemDelegateForColumn(2, self.multi_line_delegate)
    
    # Основные методы работы с файлами
    def open_file(self, file_type=None):
        """Открытие файла с учетом типа"""
        if self.file_io.open_file(self, file_type):
            self.status_bar.showMessage(f"Opened: {self.file_io.current_file}", 3000)
            self.history.take_snapshot(f"Opened file: {self.file_io.current_file}")
    
    def save_file(self, file_type=None):
        """Сохранение файла"""
        if self.file_io.save_file(self, self.get_model_data(), file_type):
            self.undo_stack.setClean()
            self.status_bar.showMessage(f"Saved: {self.file_io.current_file}", 3000)
            self.history.take_snapshot(f"Saved file: {self.file_io.current_file}")
            return True
        return False
    
    def save_file_as(self, file_type=None):
        """Сохранение файла с выбором имени"""
        if self.file_io.save_file_as(self, self.get_model_data(), file_type):
            self.undo_stack.setClean()
            self.status_bar.showMessage(f"Saved as: {self.file_io.current_file}", 3000)
            self.history.take_snapshot(f"Saved file as: {self.file_io.current_file}")
            return True
        return False
    
    def get_model_data(self):
        """Получение данных из модели"""
        return [
            [self.model.data(self.model.index(row, col)) or ""
             for col in range(self.model.columnCount())]
            for row in range(self.model.rowCount())
        ]
    
    def load_data(self, data):
        """Загрузка данных в модель"""
        self.model.clear()
        
        if not data:
            return
            
        rows = len(data)
        cols = len(data[0]) if data else 0
        
        self.model.setRowCount(rows)
        self.model.setColumnCount(cols)
        
        for row_idx, row in enumerate(data):
            for col_idx, value in enumerate(row):
                item = QStandardItem(str(value) if value is not None else "")
                self.model.setItem(row_idx, col_idx, item)
    
    # Импорт/экспорт
    def import_excel(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Import Excel", "", "Excel Files (*.xlsx)"
        )
        if filename and self.file_io.import_excel(filename):
            self.status_bar.showMessage(f"Imported from Excel: {filename}", 3000)
            self.history.take_snapshot(f"Imported from Excel: {filename}")
    
    def export_to_excel(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Excel", "", "Excel Files (*.xlsx)"
        )
        if filename and self.excel_exporter.export(filename):
            self.status_bar.showMessage(f"Exported to Excel: {filename}", 3000)
    
    def export_markdown(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Markdown", "", "Markdown Files (*.md)"
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
            if ok and table_name and self.file_io.import_sqlite(filename, table_name):
                self.status_bar.showMessage(f"Imported from SQLite: {table_name}", 3000)
                self.history.take_snapshot(f"Imported from SQLite: {table_name}")
    
    def export_sqlite(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export SQLite", "", "SQLite Databases (*.db *.sqlite)"
        )
        if filename:
            table_name, ok = QInputDialog.getText(
                self, "Table Name", "Enter table name for export:"
            )
            if ok and table_name and self.file_io.export_sqlite(filename, table_name):
                self.status_bar.showMessage(f"Exported to SQLite: {table_name}", 3000)
    
    # Диалоги и специальные функции
    def show_group_dialog(self):
        headers = [self.model.headerData(col, Qt.Horizontal) or f"Column {col}" 
                  for col in range(self.model.columnCount())]
        dialog = GroupDialog(headers, self)
        if dialog.exec_():
            selections = dialog.get_selections()
            result = self.data_ops.group_data(
                selections['group_column'],
                selections['aggregations']
            )
            QMessageBox.information(
                self, 
                "Grouping Result", 
                f"Data grouped by {selections['group_column']}\nFound {len(result)} groups"
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
    
    # Обработчики событий
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        if not self.undo_stack or self.undo_stack.isClean():
            event.accept()
            return
            
        reply = QMessageBox.question(
            self,
            "Unsaved Changes",
            "You have unsaved changes. Save before closing?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save
        )
        
        if reply == QMessageBox.Save:
            if self.save_file():
                event.accept()
            else:
                event.ignore()
        elif reply == QMessageBox.Discard:
            event.accept()
        else:
            event.ignore()
    
    def on_data_changed(self):
        """Обработка изменения данных"""
        self.status_bar.showMessage("Data changed", 2000)
        self.history.take_snapshot("Data edit")
    
    def on_undo_stack_changed(self):
        """Обновление состояния undo/redo"""
        self.undo_action.setEnabled(self.undo_stack.canUndo())
        self.redo_action.setEnabled(self.undo_stack.canRedo())
        if self.undo_stack.canUndo():
            self.undo_action.setText(f"Undo ({self.undo_stack.undoText()})")
        else:
            self.undo_action.setText("Undo")
        
        if self.undo_stack.canRedo():
            self.redo_action.setText(f"Redo ({self.undo_stack.redoText()})")
        else:
            self.redo_action.setText("Redo")
    
    def autosave(self):
        """Автоматическое сохранение"""
        if not self.undo_stack.isClean():
            data = self.get_model_data()
            try:
                with open("autosave.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
            except Exception as e:
                print(f"Autosave failed: {e}")

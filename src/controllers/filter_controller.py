from typing import Optional
from PySide6.QtCore import QObject, QRunnable, Signal, QThreadPool
from models.data_processor import DataProcessor
from controllers.table_controller import TableController
from views.components.custom_combobox import SmartComboBox

class FilterWorkerSignals(QObject):
    finished = Signal()
    error = Signal(str)

class FilterWorker(QRunnable):
    def __init__(self, table_controller, column: str, filter_text: str):
        super().__init__()
        self.table_controller = table_controller
        self.column = column
        self.filter_text = filter_text
        self.signals = FilterWorkerSignals()

    def run(self):
        try:
            self.table_controller.filter_data(self.column, self.filter_text)
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))

class FilterController(QObject):
    def __init__(self, 
                 column_box: SmartComboBox,
                 keyword_edit: SmartComboBox,
                 table_controller: TableController):
        super().__init__()
        
        self.column_box = column_box
        self.keyword_edit = keyword_edit
        self.table_controller = table_controller
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(4)
        self.current_filter_worker = None
        self.data_processor = DataProcessor()

    def update_columns(self, columns: list):
        """Обновление списка колонок"""
        self.column_box.clear()
        self.column_box.addItems(columns)

    def on_column_change(self, index: int):
        """Обработка изменения выбранной колонки"""
        self.keyword_edit.clear()
        if index < 0:
            return
        
        column_name = self.column_box.currentText()
        if column_name == "Место работы (учебы)":
            # Специальная обработка для колонки места работы
            similar_groups = self.data_processor.analyze_column(column_name)
            unique_values = set()
            for group_key, group_values in similar_groups.items():
                unique_values.add(group_key)
            self.keyword_edit.addItems(sorted(unique_values))
        else:
            # Обычная обработка для других колонок
            values = self.table_controller.get_column_values(column_name)
            self.keyword_edit.addItems(sorted(str(v) for v in values if str(v).strip()))
        
        self.keyword_edit.setEditable(True)

    def apply_filter(self):
        """Применение фильтра"""
        if self.current_filter_worker is not None:
            self.current_filter_worker.signals.finished.disconnect()
            self.current_filter_worker = None

        column = self.column_box.currentText()
        filter_text = self.keyword_edit.currentText().strip()

        worker = FilterWorker(self.table_controller, column, filter_text)
        worker.signals.finished.connect(self._on_filter_complete)
        self.current_filter_worker = worker
        self.threadpool.start(worker)

    def _on_filter_complete(self):
        """Обработка завершения фильтрации"""
        self.current_filter_worker = None

    def reset_filter(self):
        """Сброс фильтра"""
        self.keyword_edit.setCurrentText("")
        self.table_controller.reset_filter()
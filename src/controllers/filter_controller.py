from PySide6.QtCore import QObject, QRunnable, Signal, QThreadPool, Qt
from models.data_processor import DataProcessor
from controllers.table_controller import TableController
from ui.components.custom_combobox import SmartComboBox
import pandas as pd

class FilterWorkerSignals(QObject):
    finished = Signal(pd.DataFrame)
    error = Signal(str)

class FilterWorker(QRunnable):
    def __init__(self, data_processor, column: str, filter_text: str):
        super().__init__()
        self.data_processor = data_processor
        self.column = column
        self.filter_text = filter_text
        self.signals = FilterWorkerSignals()

    def run(self):
        try:
            result_df = self.data_processor.filter_data(self.column, self.filter_text)
            self.signals.finished.emit(result_df)
        except Exception as e:
            self.signals.error.emit(str(e))

class FilterController(QObject):
    def __init__(self, column_box: SmartComboBox, keyword_edit: SmartComboBox, table_controller: TableController):
        super().__init__()
        self.column_box = column_box
        self.keyword_edit = keyword_edit
        self.table_controller = table_controller
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(4)
        self.current_filter_worker = None
        self.data_processor = self.table_controller.data_processor
        
        # Устанавливаем поле выбора колонки нередактируемым
        self.column_box.setEditable(False)

    def update_columns(self, columns: list):
        # Обновляем список колонок и делаем поле нередактируемым
        self.column_box.setup(columns, editable=False)

    def is_numeric_column(self, values):
        """Проверяет, являются ли значения числовыми (целыми или с плавающей точкой)."""
        try:
            # Если хотя бы 80% значений можно привести к числу — считаем колонку числовой
            num_values = [float(v) for v in values if str(v).strip() != ""]
            return len(num_values) >= 0.8 * len(values)
        except Exception:
            return False

    def on_column_change(self, index: int):
        # Очищаем поле ключевых слов
        self.keyword_edit.clear()
        if index < 0:
            return

        column_name = self.column_box.currentText()
        
        try:
            # Получаем все уникальные значения колонки
            values = self.table_controller.get_column_values(column_name)
            
            # Определяем, является ли колонка числовой
            if self.is_numeric_column(values):
                try:
                    # Обрабатываем числовые значения
                    numeric_values = sorted(
                        [float(v) for v in values if str(v).strip() != ""]
                    )
                    # Оставим отображение в исходном виде (без .0 если целое)
                    display_values = [str(int(v)) if float(v).is_integer() else str(v) for v in numeric_values]
                    self.keyword_edit.setup(display_values)
                except Exception as e:
                    print(f"Ошибка при обработке числовых значений: {e}")
                    filtered_values = sorted([str(v).strip() for v in values if str(v).strip()])
                    self.keyword_edit.setup(filtered_values)
            else:
                # Для текстовых колонок применяем группировку схожих значений
                # Это поможет избежать дублирования схожих записей в списке
                try:
                    # Анализируем колонку для поиска схожих значений
                    similar_groups = self.data_processor.analyze_column(column_name)
                    
                    # Собираем уникальные значения, избегая дублирования
                    unique_values = []
                    used_values = set()
                    
                    # Сначала добавляем представителей групп (обычно более полные названия)
                    for key in similar_groups.keys():
                        unique_values.append(key)
                        used_values.add(key)
                        used_values.update(similar_groups[key])
                    
                    # Затем добавляем остальные значения, которые не попали в группы
                    for value in values:
                        value_str = str(value).strip()
                        if value_str and value_str not in used_values:
                            unique_values.append(value_str)
                            used_values.add(value_str)
                    
                    # Настраиваем комбобокс с уникальными значениями
                    self.keyword_edit.setup(sorted(unique_values))
                    
                except Exception as e:
                    print(f"Ошибка при анализе колонки: {e}")
                    # В случае ошибки просто добавляем все уникальные значения
                    filtered_values = sorted(set([str(v).strip() for v in values if str(v).strip()]))
                    self.keyword_edit.setup(filtered_values)
        except Exception as e:
            print(f"Ошибка при обновлении списка значений: {e}")
            # Если что-то пошло не так, просто очищаем список
            self.keyword_edit.clear()

    def apply_filter(self):
        if self.current_filter_worker is not None:
            self.current_filter_worker.signals.finished.disconnect()
            self.current_filter_worker = None

        column = self.column_box.currentText()
        filter_text = self.keyword_edit.currentText().strip()

        if column.lower().strip() in ["excel #", "№"]:
            self.table_controller.set_number_mode("excel")

        worker = FilterWorker(self.data_processor, column, filter_text)
        worker.signals.finished.connect(self._on_filter_complete)
        self.current_filter_worker = worker
        self.threadpool.start(worker)

    def _on_filter_complete(self, result_df):
        self.table_controller.set_filtered_dataframe(result_df)
        self.current_filter_worker = None

    def reset_all(self):
        self.keyword_edit.setCurrentText("")
        self.table_controller.reset_all()
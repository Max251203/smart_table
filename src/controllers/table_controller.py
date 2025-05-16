from typing import List, Optional
from PySide6.QtCore import QObject, Qt
from models.table_model import SmartTableModel
from models.data_processor import DataProcessor
from views.table_view import SmartTableView

class TableController(QObject):
    def __init__(self, view: SmartTableView):
        super().__init__()
        self.view = view
        self.data_processor = DataProcessor()
        self.model: Optional[SmartTableModel] = None
        self.num_mode = "excel"
        self.num_col_index = 0

    def load_file(self, file_path: str) -> bool:
        """Загрузка файла Excel"""
        try:
            # Загружаем данные через процессор
            df, num_col_index = self.data_processor.load_excel(file_path)
            
            # Обновляем модель
            self.num_col_index = num_col_index
            self.num_mode = "excel"
            
            # Создаем новую модель
            self.model = SmartTableModel(df, self.num_mode, self.num_col_index)
            self.view.setModel(self.model)
            
            # Настраиваем отображение
            self.view.adjust_columns()
            return True
            
        except Exception as e:
            print(f"Ошибка при загрузке файла: {e}")
            return False

    def get_columns(self) -> List[str]:
        """Получение списка колонок"""
        if self.model is None:
            return []
        return [self.model.headerData(i, Qt.Horizontal) for i in range(self.model.columnCount())]

    def toggle_number_mode(self):
        """Переключение режима отображения номеров"""
        if self.model is None:
            return
            
        self.num_mode = "order" if self.num_mode == "excel" else "excel"
        self.model.num_mode = self.num_mode
        
        # Обновляем отображение
        self.model.layoutChanged.emit()
        self.view.adjust_columns()

    def sort_column(self, column: int, order: Qt.SortOrder):
        """Сортировка по колонке"""
        if self.model is None:
            return
            
        if column == self.num_col_index and self.num_mode == "order":
            return
            
        self.model.sort(column, order)

    def filter_data(self, column_name: str, filter_text: str):
        """Фильтрация данных"""
        if self.model is None or not self.data_processor.current_df is not None:
            return
            
        filtered_df = self.data_processor.filter_data(column_name, filter_text)
        
        if not filtered_df.empty:
            self.model.set_dataframe(filtered_df)
            self.view.adjust_columns()

    def reset_filter(self):
        """Сброс фильтрации"""
        if self.model is None or self.data_processor.current_df is None:
            return
            
        self.model.set_dataframe(self.data_processor.current_df)
        self.view.adjust_columns()

    def get_cell_value(self, row: int, column: int) -> str:
        """Получение значения ячейки"""
        if self.model is None:
            return ""
            
        return self.model.data(self.model.index(row, column), Qt.DisplayRole)

    def get_column_values(self, column_name: str) -> List[str]:
        """Получение всех значений колонки"""
        if self.model is None or self.data_processor.current_df is None:
            return []
            
        return self.data_processor.current_df[column_name].unique().tolist()
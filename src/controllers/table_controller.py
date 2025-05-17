from typing import List, Optional
from PySide6.QtCore import QObject, Qt
from models.table_model import SmartTableModel
from models.data_processor import DataProcessor
from ui.components.table_view import SmartTableView
import pandas as pd

class TableController(QObject):
    def __init__(self, view: SmartTableView):
        super().__init__()
        self.view = view
        self.data_processor = DataProcessor()
        self.model: Optional[SmartTableModel] = None
        self.num_mode = "excel"
        self.num_col_index = 0

    def load_file(self, file_path: str) -> bool:
        try:
            df, num_col_index = self.data_processor.load_excel(file_path)
            self.num_col_index = num_col_index
            self.num_mode = "excel"
            self.model = SmartTableModel(df, self.num_mode, self.num_col_index)
            self.view.setModel(self.model)
            self.view.adjust_columns()
            return True
        except Exception as e:
            print(f"Ошибка при загрузке файла: {e}")
            return False

    def get_columns(self) -> List[str]:
        if self.model is None:
            return []
        return [self.model.headerData(i, Qt.Horizontal) for i in range(self.model.columnCount())]

    def toggle_number_mode(self):
        if self.model is None:
            return
        self.num_mode = "order" if self.num_mode == "excel" else "excel"
        self.model.num_mode = self.num_mode
        self.model.layoutChanged.emit()
        self.view.adjust_columns()

    def sort_column(self, column: int, order: Qt.SortOrder):
        if self.model is None:
            return
        if column == self.num_col_index and self.num_mode == "order":
            return
        self.model.sort(column, order)
        self.view.header.setSortIndicator(column, order)
        self.view.adjust_columns()

    def set_number_mode(self, mode):
        if self.model is not None:
            self.num_mode = mode
            self.model.num_mode = mode
            self.model.layoutChanged.emit()
            self.view.adjust_columns()

    def set_filtered_dataframe(self, df: pd.DataFrame):
        if self.model is not None:
            self.model.set_dataframe(df)
            self.view.adjust_columns()

    def reset_all(self):
        if self.model is None or self.data_processor.current_df is None:
            return
        self.model.set_dataframe(self.data_processor.current_df)
        index = self.num_col_index
        self.model.sort(index, Qt.AscendingOrder)
        self.num_mode = "excel"
        self.model.num_mode = "excel"
        self.view.header.setSortIndicator(-1)  # <--- Сброс!
        self.view.adjust_columns()

    def get_cell_value(self, row: int, column: int) -> str:
        if self.model is None:
            return ""
        return self.model.data(self.model.index(row, column), Qt.DisplayRole)

    def get_column_values(self, column_name: str) -> List[str]:
        if self.model is None or self.data_processor.current_df is None:
            return []
        return self.data_processor.current_df[column_name].unique().tolist()
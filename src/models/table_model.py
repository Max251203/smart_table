from typing import Any, Optional
from PySide6.QtCore import Qt, QAbstractTableModel
import pandas as pd

class SmartTableModel(QAbstractTableModel):
    def __init__(self, df: Optional[pd.DataFrame] = None, num_mode: str = "excel", num_col_index: int = 0):
        super().__init__()
        self._df = df if df is not None else pd.DataFrame()
        self.num_mode = num_mode  # "excel" или "order"
        self.num_col_index = num_col_index

    def rowCount(self, parent=None) -> int:
        return len(self._df)

    def columnCount(self, parent=None) -> int:
        return len(self._df.columns)

    def data(self, index, role=Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            value = self._df.iloc[index.row(), index.column()]
            if index.column() == self.num_col_index:
                if self.num_mode == "order":
                    return str(index.row() + 1)
                return str(value)
            return str(value)

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignLeft | Qt.AlignVCenter

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == self.num_col_index:
                    return "№ (порядок)" if self.num_mode == "order" else str(self._df.columns[section])
                return str(self._df.columns[section])
            return str(section + 1)
        return None

    def setData(self, index, value: Any, role=Qt.EditRole) -> bool:
        if role == Qt.EditRole:
            self._df.iloc[index.row(), index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index) -> Qt.ItemFlags:
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def get_dataframe(self) -> pd.DataFrame:
        return self._df.copy()

    def set_dataframe(self, df: pd.DataFrame) -> None:
        self.beginResetModel()
        self._df = df.copy()
        self.endResetModel()

    def get_column_data(self, column_index: int) -> pd.Series:
        return self._df.iloc[:, column_index]

    def sort(self, column: int, order: Qt.SortOrder) -> None:
        """Сортировка данных по указанному столбцу"""
        self.beginResetModel()
        ascending = order == Qt.AscendingOrder
        if column == self.num_col_index and self.num_mode == "order":
            pass  # Игнорируем сортировку для столбца с порядковыми номерами
        else:
            self._df.sort_values(by=self._df.columns[column], 
                               ascending=ascending, 
                               inplace=True)
        self.endResetModel()